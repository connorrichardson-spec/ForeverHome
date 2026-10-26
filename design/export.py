"""Exports for other tools (Blender, etc.):

exports/house.json  semantic model: levels, rooms + finishes, walls, openings, stairs, furniture.
                    Units: feet. Axes: x = east, y = north (front of house faces south / -y), z = up.
exports/house.glb   glTF 2.0 of the full model, in METERS (glTF/Blender convention). Blender:
                    File > Import > glTF 2.0. One named object per wall / floor / ceiling / stair /
                    furniture piece, grouped under one empty per level. Materials are named after
                    their finish (paint_4f5e53, hardwood, floorTile, ...) so each can be re-styled once.
                    Furniture objects sit at their footprint center on the floor, rotated so the
                    piece's front faces glTF +Z when facing S, and carry custom properties
                    (kind, facing, width/depth, opts) for swapping in real assets.
"""
import json, math, os, struct
import numpy as np
import house as H
import geometry as G

FT = 0.3048
FACING_YAW = {"S": 0.0, "E": 90.0, "N": 180.0, "W": -90.0}   # rotation about glTF +Y (up)

# viewer material key -> (hex color, metallic, roughness, extra)
BASE = {
    "hardwood": ("#b08a5e", 0, 0.45), "stair": ("#b08a5e", 0, 0.45), "floorTile": ("#d8d3ca", 0, 0.35),
    "concrete": ("#c9c7c2", 0, 0.85), "rubber": ("#2a2b2d", 0, 0.95), "pavers": ("#a39d92", 0, 0.9),
    "trim": ("#f7f6f2", 0, 0.5), "door": ("#f4f3ef", 0, 0.5), "ceiling": ("#f8f7f3", 0, 0.95),
    "wallExt": ("#e7e1d3", 0, 0.85), "wallInt": ("#f4f1ea", 0, 0.85), "garageDoor": ("#c3c6ca", 0, 0.6),
    "doorExt": ("#6b4f3a", 0, 0.6), "glass": ("#bfe3f0", 0, 0.05), "mirror": ("#e8eef2", 1, 0.03),
}
KIND_PBR = {"paint": (0, 0.9), "fix": (0, 0.75), "gloss": (0, 0.22), "metal": (0.85, 0.3), "wood": (0, 0.55),
            "fabric": (0, 1.0), "tile": (0, 0.25), "lamp": (0, 0.5)}


def _lin(hexstr):
    h = hexstr.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def gltf_material(key):
    if ":" in key:
        kind, hexstr = key.split(":", 1)
        metal, rough = KIND_PBR.get(kind, (0, 0.8))
    else:
        kind, (hexstr, metal, rough) = key, BASE.get(key, ("#cccccc", 0, 0.8))
    m = {"name": key.replace(":#", "_").replace(":", "_"),
         "pbrMetallicRoughness": {"baseColorFactor": _lin(hexstr) + [1.0], "metallicFactor": metal,
                                  "roughnessFactor": rough},
         "extras": {"forever_home_material": key}}
    if key == "glass":
        m["pbrMetallicRoughness"]["baseColorFactor"][3] = 0.25
        m["alphaMode"] = "BLEND"
    if kind == "lamp":
        m["emissiveFactor"] = _lin(hexstr)
    return m


def _box_mesh(boxes):
    """24-vertex boxes in house feet -> (pos, nor, idx) arrays in house coords."""
    P, N, I = [], [], []
    for b in boxes:
        x0, y0, z0 = b["x"], b["y"], b["z"]
        x1, y1, z1 = x0 + b["w"], y0 + b["d"], z0 + b["h"]
        faces = [((1, 0, 0), [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]),
                 ((-1, 0, 0), [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)]),
                 ((0, 1, 0), [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)]),
                 ((0, -1, 0), [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]),
                 ((0, 0, 1), [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
                 ((0, 0, -1), [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)])]
        for n, quad in faces:
            base = len(P)
            P += quad
            N += [n] * 4
            I += [base, base + 1, base + 2, base, base + 2, base + 3]
    return np.array(P, float), np.array(N, float), np.array(I, np.uint32)


def _to_gltf(v):
    """house (x east, y north, z up) -> glTF (x, y up, z south)."""
    return np.stack([v[:, 0], v[:, 2], -v[:, 1]], axis=1)


class GLB:
    def __init__(self):
        self.g = {"asset": {"version": "2.0", "generator": "ForeverHome design/export.py"},
                  "scene": 0, "scenes": [{"name": "ForeverHome", "nodes": []}],
                  "nodes": [], "meshes": [], "materials": [], "accessors": [], "bufferViews": [],
                  "buffers": [{"byteLength": 0}]}
        self.bin = bytearray()
        self.mat_index = {}

    def material(self, key):
        if key not in self.mat_index:
            self.mat_index[key] = len(self.g["materials"])
            self.g["materials"].append(gltf_material(key))
        return self.mat_index[key]

    def _view(self, arr, target):
        while len(self.bin) % 4:
            self.bin.append(0)
        off = len(self.bin)
        self.bin += arr.tobytes()
        self.g["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": arr.nbytes, "target": target})
        return len(self.g["bufferViews"]) - 1

    def _acc(self, arr, ctype, typ, target, minmax=False):
        a = {"bufferView": self._view(arr, target), "componentType": ctype, "count": len(arr), "type": typ}
        if minmax:
            a["min"], a["max"] = arr.min(0).tolist(), arr.max(0).tolist()
        self.g["accessors"].append(a)
        return len(self.g["accessors"]) - 1

    def mesh(self, name, by_mat, origin=(0, 0, 0), yaw=0.0):
        """by_mat: {material key: [boxes]} in house feet. Vertices are made local to `origin`
        (house feet) and un-rotated by `yaw` so the node transform places them."""
        prims = []
        c, s = math.cos(math.radians(-yaw)), math.sin(math.radians(-yaw))
        for key, boxes in by_mat.items():
            p, n, idx = _box_mesh(boxes)
            p = _to_gltf((p - np.array(origin)) * FT)
            n = _to_gltf(n)
            rot = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])            # Ry(-yaw)
            p, n = p @ rot.T, n @ rot.T
            uv = np.stack([p[:, 0] + p[:, 2], p[:, 1] - p[:, 2]], axis=1)   # rough planar UVs (meters)
            prims.append({"attributes": {
                "POSITION": self._acc(p.astype(np.float32), 5126, "VEC3", 34962, True),
                "NORMAL": self._acc(n.astype(np.float32), 5126, "VEC3", 34962),
                "TEXCOORD_0": self._acc(uv.astype(np.float32), 5126, "VEC2", 34962)},
                "indices": self._acc(idx, 5125, "SCALAR", 34963), "material": self.material(key)})
        self.g["meshes"].append({"name": name, "primitives": prims})
        return len(self.g["meshes"]) - 1

    def node(self, name, mesh=None, children=None, origin=(0, 0, 0), yaw=0.0, extras=None):
        nd = {"name": name}
        if mesh is not None:
            nd["mesh"] = mesh
        if children:
            nd["children"] = children
        if any(origin):
            nd["translation"] = _to_gltf(np.array([origin], float) * FT)[0].tolist()
        if yaw:
            h = math.radians(yaw) / 2
            nd["rotation"] = [0.0, math.sin(h), 0.0, math.cos(h)]
        if extras:
            nd["extras"] = extras
        self.g["nodes"].append(nd)
        return len(self.g["nodes"]) - 1

    def save(self, path):
        while len(self.bin) % 4:
            self.bin.append(0)
        self.g["buffers"][0]["byteLength"] = len(self.bin)
        js = json.dumps(self.g, separators=(",", ":")).encode()
        js += b" " * (-len(js) % 4)
        with open(path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.bin)))
            f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
            f.write(struct.pack("<II", len(self.bin), 0x004E4942) + bytes(self.bin))


def _room_at(level, x, y):
    for r in H.ROOMS[level]:
        if G.inside(G.room_poly(r), x, y):
            return r["name"]
    return None


def _furniture_records(level):
    out = []
    pieces = G.furniture(level)
    for n, ((lvl, kind, x, y, facing, opts), (_, fp, label)) in enumerate(
            zip([f for f in H.FURNITURE if f[0] == level], pieces)):
        cx, cy = (fp[0] + fp[2]) / 2, (fp[1] + fp[3]) / 2
        W, D = (fp[2] - fp[0], fp[3] - fp[1]) if facing in "NS" else (fp[3] - fp[1], fp[2] - fp[0])
        room = _room_at(level, cx, cy)
        out.append(dict(id=f"furn{n}", level=level, room=room, kind=kind, label=label, facing=facing,
                        center=[round(cx, 3), round(cy, 3)], width=round(W, 3), depth=round(D, 3),
                        footprint=[round(v, 3) for v in fp],
                        node=f"{level}/furniture/{room}/{label or kind} {n}",
                        opts={k: v for k, v in opts.items()}))
    return out


def write(data, exp_dir):
    """data: {level: (boxes, walls, ops)} from geometry.boxes_for_level."""
    doc = {"units": "feet", "axes": "x east, y north (front faces south, -y), z up",
           "glb": "house.glb (meters, glTF y-up; node names match the 'node' fields below)",
           "levels": {}, "rooms": [], "walls": [], "openings": [], "stairs": [], "furniture": []}
    glb = GLB()
    for level, (elev, height) in H.LEVELS.items():
        boxes, walls, ops = data[level]
        doc["levels"][level] = dict(floor_elevation=elev, wall_height=height, floor_thickness=H.FLOOR_T)
        for r in H.ROOMS[level]:
            doc["rooms"].append(dict(
                level=level, name=r["name"], kind=r.get("kind", "indoor"),
                polygon=[list(p) for p in G.room_poly(r)], area_sqft=round(G.room_area(r), 1),
                paint=r.get("paint", G.DEFAULT_PAINT), floor=r.get("floor", "pavers" if r.get("kind") == "outdoor"
                                                                     else "hardwood"),
                windows=r.get("win", "normal"), note=r.get("note", ""),
                zones=[dict(name=z, rect=list(rc)) for z, rc in r.get("zones", [])],
                **({"floor_rect": list(r["floor_rect"])} if "floor_rect" in r else {}),
                **({"ceiling_rect": list(r["ceil_rect"])} if "ceil_rect" in r else {})))
            if r.get("stair") == "up":
                L = G.stair_layout(level, r)
                doc["stairs"].append(dict(level=level, room=r["name"], type="U (switchback)", risers=L["n"],
                                          riser_in=round(L["r"] * 12, 2), tread_in=round(G.TREAD * 12, 2),
                                          flight_width=round(L["fw"], 2), landing_depth=round(L["land"] - L["Y0"], 2),
                                          walkway_line_y=L["Y"], rise=L["rise"]))
        for i, w in enumerate(walls):
            start = (w["a"], w["c"]) if w["axis"] == "h" else (w["c"], w["a"])
            end = (w["b"], w["c"]) if w["axis"] == "h" else (w["c"], w["b"])
            doc["walls"].append(dict(id=f"wall{i}", level=level, start=list(start), end=list(end),
                                     thickness=w["t"], exterior=w["ext"], rooms=w["rooms"],
                                     node=f"{level}/wall/{i:02d} {' | '.join(w['rooms'])}"))
        for o in ops:
            center = (o["pos"], o["c"]) if o["axis"] == "h" else (o["c"], o["pos"])
            doc["openings"].append(dict(level=level, wall=f"wall{o['wall']}", kind=o["kind"],
                                        center=[round(v, 3) for v in center], width=o["w"], height=o["h"],
                                        sill=o["sill"], swings_into=o.get("swing")))
        furn = _furniture_records(level)
        doc["furniture"] += furn

        # ---- glb: group boxes by object tag
        groups = {}
        for b in boxes:
            if b["mat"] == "block":
                continue
            groups.setdefault(b["obj"], {}).setdefault(b["mat"], []).append(b)
        children = []
        fmap = {f["id"]: f for f in furn}
        for tag, by_mat in groups.items():
            origin, yaw, extras = (0, 0, 0), 0.0, None
            if tag.startswith("wall"):
                name = doc["walls"][-len(walls) + int(tag[4:])]["node"]
            elif tag.startswith("furn"):
                f = fmap[tag]
                name, origin, yaw = f["node"], (f["center"][0], f["center"][1], elev), FACING_YAW[f["facing"]]
                extras = dict(kind=f["kind"], label=f["label"], facing=f["facing"], width_ft=f["width"],
                              depth_ft=f["depth"], room=f["room"], opts=json.dumps(f["opts"]))
            else:
                kind, room = tag.split("/", 1)
                name = f"{level}/{kind}/{room}"
            children.append(glb.node(name, glb.mesh(name, by_mat, origin, yaw), origin=origin, yaw=yaw,
                                     extras=extras))
        glb.g["scenes"][0]["nodes"].append(glb.node(level, children=children))

    with open(os.path.join(exp_dir, "house.json"), "w") as f:
        json.dump(doc, f, indent=1)
    glb.save(os.path.join(exp_dir, "house.glb"))
    print("wrote", os.path.join(exp_dir, "house.json"), "and house.glb")
