"""Turns house.py room data into walls, openings and 3D boxes (feet)."""
from collections import defaultdict
import house as H
import furniture as F

DOOR_W, DOOR_H = 3.0, 6.67
CASED_W, CASED_H = 6.0, 8.0
PATIO_W, PATIO_H = 12.0, 8.0
WIN_W, WIN_H, WIN_SILL = 4.0, 4.5, 3.0
SIDE_NORMAL = {"S": (0, -1), "N": (0, 1), "W": (-1, 0), "E": (1, 0)}
DEFAULT_PAINT = "#e6e1d6"
SKIN, BASE_H, BASE_T = 0.02, 0.4, 0.05      # paint film, baseboard height / proud depth
FLOOR_MAT = {"hardwood": "hardwood", "concrete": "concrete", "rubber": "rubber",
             "cedar": "wood:#c48a57", "pavers": "pavers", "tile": "floorTile"}
CASE_W, CASE_T = 0.3, 0.06                   # door/window casing width, proud depth
TREAD, MAX_RISE, RAIL_H = 0.833, 0.646, 3.0  # 10" treads, 7.75" max riser (IRC), 36" guard


def room_poly(r):
    if "poly" in r:
        return list(r["poly"])
    x0, y0, x1, y1 = r["rect"]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def edges(poly):
    n = len(poly)
    for i in range(n):
        yield poly[i], poly[(i + 1) % n]


def seg_axis(p, q):
    if p[1] == q[1]:
        return "h", p[1], min(p[0], q[0]), max(p[0], q[0])   # along x at y=c
    return "v", p[0], min(p[1], q[1]), max(p[1], q[1])        # along y at x=c


def shared_interval(ra, rb):
    """Longest collinear overlap between edges of two rooms -> (axis,c,a,b)."""
    best = None
    for p, q in edges(room_poly(ra)):
        ax, c, a, b = seg_axis(p, q)
        for p2, q2 in edges(room_poly(rb)):
            ax2, c2, a2, b2 = seg_axis(p2, q2)
            if ax == ax2 and c == c2:
                lo, hi = max(a, a2), min(b, b2)
                if hi - lo > 0.01 and (best is None or hi - lo > best[3] - best[2]):
                    best = (ax, c, lo, hi)
    return best


def build_walls(level):
    """Wall segments for a level: list of dict(axis,c,a,b,t,ext,rooms)."""
    rooms = H.ROOMS[level]
    lines = defaultdict(list)       # (axis,c) -> [(a,b,roomname,indoor)]
    for r in rooms:
        indoor = r.get("kind", "indoor") == "indoor"
        for p, q in edges(room_poly(r)):
            ax, c, a, b = seg_axis(p, q)
            lines[(ax, c)].append((a, b, r["name"], indoor))
    walls = []
    for (ax, c), segs in lines.items():
        pts = sorted({v for a, b, _, _ in segs for v in (a, b)})
        for lo, hi in zip(pts, pts[1:]):
            cover = [s for s in segs if s[0] <= lo and s[1] >= hi]
            indoor = [s for s in cover if s[3]]
            if not indoor:
                continue
            ext = len(cover) == 1 or len({s[2] for s in cover}) == 1
            walls.append(dict(axis=ax, c=c, a=lo, b=hi, t=H.EXT_T if ext else H.INT_T,
                              ext=ext, rooms=sorted({s[2] for s in cover})))
    return walls


def find_room(level, name):
    for r in H.ROOMS[level]:
        if r["name"] == name:
            return r
    raise KeyError(f"{level}: no room {name}")


def build_openings(level, walls):
    """Openings: dict(axis,c,pos,w,sill,h,kind). Doors, windows, garage doors."""
    ops = []
    for d in H.DOORS:
        if d[0] != level:
            continue
        opt = d[4] if len(d) > 4 else {}
        kind = d[3]
        if kind == "none":
            continue
        ra = find_room(level, d[1])
        if d[2] is None:                                # exterior door
            side = opt["side"]
            nx, ny = SIDE_NORMAL[side]
            cand = []
            for p, q in edges(room_poly(ra)):
                ax, c, a, b = seg_axis(p, q)
                if (ax == "h" and ny and ((side == "S" and c == min(y for _, y in room_poly(ra))) or
                                           (side == "N" and c == max(y for _, y in room_poly(ra))))) or \
                   (ax == "v" and nx and ((side == "W" and c == min(x for x, _ in room_poly(ra))) or
                                           (side == "E" and c == max(x for x, _ in room_poly(ra))))):
                    cand.append((ax, c, a, b))
            iv = max(cand, key=lambda t: t[3] - t[2])
        else:
            iv = shared_interval(ra, find_room(level, d[2]))
            if iv is None:
                raise ValueError(f"{level}: {d[1]} and {d[2]} share no wall")
        ax, c, a, b = iv
        pos = (a + b) / 2
        if "at" in opt:
            pos = opt["at"][0] if ax == "h" else opt["at"][1]
        w, h = {"door": (DOOR_W, DOOR_H), "cased": (CASED_W, CASED_H),
                "patio": (PATIO_W, PATIO_H)}[kind]
        w = min(opt.get("w", w), b - a - 0.5)
        ops.append(dict(axis=ax, c=c, pos=pos, w=w, sill=0.0, h=h, kind=kind,
                        swing=None if d[2] is None else d[1]))
    if level == "main":
        g = next(r for r in H.ROOMS["main"] if r["name"] == "Garage")
        for x in H.GARAGE_DOORS:
            ops.append(dict(axis="h", c=g["rect"][1], pos=x, w=9.0, sill=0.0, h=8.0, kind="garage"))
    # auto windows on exterior walls
    for w in walls:
        if not w["ext"]:
            continue
        owner = next((find_room(level, n) for n in w["rooms"]
                      if find_room(level, n).get("kind", "indoor") == "indoor"), None)
        if owner is None:
            continue
        mode = owner.get("win", "normal")
        if mode == "garage":
            mode = "none"
        if mode == "none":
            continue
        length = w["b"] - w["a"]
        if length < 3:
            continue
        ww, wh, sill = WIN_W, WIN_H, WIN_SILL
        spacing = 8.0
        if mode == "small":
            ww, wh, sill, spacing = 2.0, 2.0, 5.0, 99
        elif mode == "high":
            ww, wh, sill, spacing = 4.0, 1.5, 6.0, 8.0
        elif mode == "egress":
            ww, wh, sill, spacing = 3.5, 4.0, 2.5, 99
        elif owner["name"] == "Great Room":
            ww, wh, sill, spacing = 6.0, 6.0, 2.0, 11.0
        n = max(1, int((length - 2) // spacing)) if spacing < 99 else 1
        for i in range(n):
            pos = w["a"] + length * (i + 0.5) / n
            px, py = (pos, w["c"]) if w["axis"] == "h" else (w["c"], pos)
            o_w, o_h, o_s = ww, wh, sill
            for (rx0, ry0, rx1, ry1), ov in owner.get("win_over", []):
                if rx0 <= px <= rx1 and ry0 <= py <= ry1:
                    o_w, o_h, o_s = ov.get("w", ww), ov.get("h", wh), ov.get("sill", sill)
            ops.append(dict(axis=w["axis"], c=w["c"], pos=pos, w=min(o_w, length - 1),
                            sill=o_s, h=o_h, kind="window", auto=True))
    # drop auto windows that collide with doors / each other
    keep = []
    for o in ops:
        if o.get("auto"):
            clash = any(p["axis"] == o["axis"] and p["c"] == o["c"] and not p.get("auto") or
                        False for p in [])
            bad = False
            for p in ops:
                if p is o or p["axis"] != o["axis"] or p["c"] != o["c"]:
                    continue
                if not p.get("auto") and abs(p["pos"] - o["pos"]) < (p["w"] + o["w"]) / 2 + 0.5:
                    bad = True
            if bad:
                continue
        keep.append(o)
    # snap each opening into its wall; discard those not inside any wall segment
    out = []
    for o in keep:
        for w in walls:
            if w["axis"] == o["axis"] and w["c"] == o["c"] and \
               w["a"] + o["w"] / 2 <= o["pos"] + 1e-6 and o["pos"] + o["w"] / 2 <= w["b"] + 1e-6:
                o = dict(o, wall=walls.index(w))
                out.append(o)
                break
    return out


def boxes_for_level(level):
    """3D boxes: dict(x,y,z,w,d,h,mat,collide,label)."""
    elev, height = H.LEVELS[level]
    walls = build_walls(level)
    ops = build_openings(level, walls)
    boxes = []
    tag = [None]            # object id stamped on every box (groups boxes for the Blender export)

    def box(**b):
        boxes.append(dict(b, obj=tag[0]))

    def add(ax, c, a, b, t, z0, z1, mat, collide=True):
        if b - a < 1e-6 or z1 - z0 < 1e-6:
            return
        if ax == "h":
            box(x=a, y=c - t / 2, z=z0, w=b - a, d=t, h=z1 - z0, mat=mat, c=collide)
        else:
            box(x=c - t / 2, y=a, z=z0, w=t, d=b - a, h=z1 - z0, mat=mat, c=collide)

    z_floor, z_top = elev, elev + height
    rooms = H.ROOMS[level]

    def room_at(x, y):
        for r in rooms:
            if r.get("kind", "indoor") == "indoor" and inside(room_poly(r), x, y):
                return r
        return None

    def door_panel(w, o, lo, head):
        """Interior door slab standing open 90 deg, hinged at the low end."""
        ra = find_room(level, o["swing"])
        probe = (o["pos"], w["c"] + 0.5) if w["axis"] == "h" else (w["c"] + 0.5, o["pos"])
        s = 1 if inside(room_poly(ra), *probe) else -1
        face = w["c"] + s * w["t"] / 2
        y0, y1 = sorted((face, face + s * (o["w"] - 0.05)))
        if w["axis"] == "h":
            box(x=lo + 0.02, y=y0, z=z_floor, w=0.15, d=y1 - y0, h=head - z_floor - 0.03, mat="door", c=False)
        else:
            box(x=y0, y=lo + 0.02, z=z_floor, w=y1 - y0, d=0.15, h=head - z_floor - 0.03, mat="door", c=False)

    def casing(w, o, lo, hi, head):
        """Trim around an opening on each indoor face, plus jamb liners in the reveal."""
        if o["kind"] == "garage":
            return
        sill = z_floor + o["sill"]
        add(w["axis"], w["c"], lo, lo + 0.04, w["t"], sill, head, "trim", False)      # jambs
        add(w["axis"], w["c"], hi - 0.04, hi, w["t"], sill, head, "trim", False)
        add(w["axis"], w["c"], lo, hi, w["t"], head - 0.04, head, "trim", False)
        for s in (-1, 1):
            off = s * (w["t"] / 2 + 0.05)
            pos = o["pos"]
            if (room_at(pos, w["c"] + off) if w["axis"] == "h" else room_at(w["c"] + off, pos)) is None:
                continue
            face = w["c"] + s * w["t"] / 2

            def strip(a, b, z0, z1, t=CASE_T):
                a, b = max(a, w["a"]), min(b, w["b"])
                add(w["axis"], face + s * t / 2, a, b, t, z0, min(z1, z_top), "trim", False)
            strip(lo - CASE_W, lo, sill, head)
            strip(hi, hi + CASE_W, sill, head)
            strip(lo - CASE_W, hi + CASE_W, head, head + CASE_W + 0.05)
            if o["kind"] == "window":
                strip(lo - CASE_W - 0.1, hi + CASE_W + 0.1, sill - 0.08, sill, 0.25)    # stool
                strip(lo - CASE_W, hi + CASE_W, sill - 0.45, sill - 0.08)                # apron

    def skins(w, lo, hi, z0, z1):
        """Paint film (and baseboard if it starts at the floor) on each indoor face."""
        lo, hi = max(lo, w["a"]), min(hi, w["b"])
        if hi - lo < 1e-6:
            return
        mid = (lo + hi) / 2
        for s in (-1, 1):
            off = s * (w["t"] / 2 + 0.05)
            r = room_at(mid, w["c"] + off) if w["axis"] == "h" else room_at(w["c"] + off, mid)
            if r is None:
                continue
            paint = r.get("paint", DEFAULT_PAINT)
            mat = paint if ":" in paint else "paint:" + paint
            face = w["c"] + s * w["t"] / 2
            for t, za, zb, m in ((SKIN, z0, z1, mat), (BASE_T, z0, z0 + BASE_H, "trim")):
                if m == "trim" and (z0 > z_floor + 1e-6 or r["name"] in ("Garage", "Sauna", "Mechanical")):
                    continue
                c0 = face if s > 0 else face - t
                add(w["axis"], c0 + t / 2, lo, hi, t, za, min(zb, z1), m, False)

    for i, w in enumerate(walls):
        tag[0] = f"wall{i}"
        mine = sorted([o for o in ops if o.get("wall") == i], key=lambda o: o["pos"])
        ext = w["ext"]
        mat = "wallExt" if ext else "wallInt"
        ex = w["t"] / 2
        a, b = w["a"] - ex, w["b"] + ex
        cur = a
        for o in mine:
            lo, hi = o["pos"] - o["w"] / 2, o["pos"] + o["w"] / 2
            add(w["axis"], w["c"], cur, lo, w["t"], z_floor, z_top, mat)
            skins(w, cur, lo, z_floor, z_top)
            if o["sill"] > 0:
                add(w["axis"], w["c"], lo, hi, w["t"], z_floor, z_floor + o["sill"], mat)
                skins(w, lo, hi, z_floor, z_floor + o["sill"])
            head = z_floor + o["sill"] + o["h"]
            add(w["axis"], w["c"], lo, hi, w["t"], head, z_top, mat)
            skins(w, lo, hi, head, z_top)
            if o["kind"] == "door" and o.get("swing"):
                door_panel(w, o, lo, head)
            casing(w, o, lo, hi, head)
            if o["kind"] == "window":
                add(w["axis"], w["c"], lo, hi, 0.1, z_floor + o["sill"], head, "glass", False)
            elif o["kind"] == "garage":
                add(w["axis"], w["c"], lo, hi, 0.2, z_floor, head, "garageDoor", False)
            elif o["kind"] == "patio":
                add(w["axis"], w["c"], lo, hi, 0.1, z_floor, head, "glass", False)
            elif o["kind"] == "door" and w["ext"]:
                add(w["axis"], w["c"], lo, hi, 0.2, z_floor, head, "doorExt", False)
            cur = hi
        add(w["axis"], w["c"], cur, b, w["t"], z_floor, z_top, mat)
        skins(w, cur, b, z_floor, z_top)

    for r in H.ROOMS[level]:
        outdoor = r.get("kind") == "outdoor"
        tag[0] = f"floor/{r['name']}"
        fmat = FLOOR_MAT[r.get("floor", "pavers" if outdoor else "hardwood")]
        for bx0, by0, bx1, by1 in ([r["floor_rect"]] if "floor_rect" in r else decompose(r)):
            box(x=bx0, y=by0, z=elev - H.FLOOR_T, w=bx1 - bx0, d=by1 - by0, h=H.FLOOR_T, mat=fmat, c=False,
                room=r["name"])
        if "floor_rect" in r:
            # partial slab (stair opening): close the floor-thickness band in the room's walls
            paint = r.get("paint", DEFAULT_PAINT)
            paint = paint if ":" in paint else "paint:" + paint
            x0, y0, x1, y1 = r["rect"]
            for ax, c, a0, a1, s in (("h", y0, x0, x1, 1), ("h", y1, x0, x1, -1),
                                     ("v", x0, y0, y1, 1), ("v", x1, y0, y1, -1)):
                add(ax, c, a0 - H.EXT_T / 2, a1 + H.EXT_T / 2, H.EXT_T, elev - H.FLOOR_T, elev, "wallExt", False)
                add(ax, c + s * (H.EXT_T / 2 + SKIN / 2), a0, a1, SKIN, elev - H.FLOOR_T, elev, paint, False)
        if not outdoor:
            tag[0] = f"ceiling/{r['name']}"
            for bx0, by0, bx1, by1 in ([r["ceil_rect"]] if "ceil_rect" in r else decompose(r)):
                box(x=bx0, y=by0, z=z_top - 0.05, w=bx1 - bx0, d=by1 - by0, h=0.05, mat="ceiling", c=False)
        if "stair" in r:
            tag[0] = f"stair/{r['name']}"
            stair_boxes(level, r, box)
    for n, (parts, _, _) in enumerate(furniture(level)):
        tag[0] = f"furn{n}"
        for x, y, z, w, d, h, m, c in parts:
            box(x=x, y=y, z=elev + z, w=w, d=d, h=h, mat=m, c=c, furn=True)
    return boxes, walls, ops


def stair_layout(level, r):
    """U-shaped (switchback) stair inside room r: flight 1 climbs south on the west side, a full-width
    landing at the south wall, flight 2 climbs back north on the east side. Both flights start/end at
    `stair_line`, leaving a clear walkway between it and the north wall on every floor."""
    x0, y0, x1, y1 = r["rect"]
    X0, X1, Y0, Y = x0 + 0.2, x1 - 0.2, y0 + 0.27, r["stair_line"]
    names = list(H.LEVELS)
    rise = H.LEVELS[names[names.index(level) + 1]][0] - H.LEVELS[level][0]
    n = -(-rise // MAX_RISE)
    n = int(n + n % 2)                                   # even riser count -> equal flights
    k = n // 2
    fw = (X1 - X0 - 0.5) / 2
    land = Y - (k - 1) * TREAD
    assert land - Y0 >= fw - 0.8, f"{level} stair: landing only {land - Y0:.2f} ft deep"
    return dict(X0=X0, X1=X1, Y0=Y0, Y=Y, rise=rise, n=n, r=rise / n, k=k, fw=fw, land=land)


def stair_boxes(level, r, box):
    elev = H.LEVELS[level][0]
    paint = r.get("paint", DEFAULT_PAINT)
    paint = paint if ":" in paint else "paint:" + paint
    if r["stair"] == "up":
        L = stair_layout(level, r)
        X0, X1, Y, T, rr, k, n, fw = L["X0"], L["X1"], L["Y"], TREAD, L["r"], L["k"], L["n"], L["fw"]
        for i in range(k - 1):                                         # flight 1 (west, climbing south)
            top = elev + (i + 1) * rr
            box(x=X0, y=Y - (i + 1) * T, z=max(elev, top - 0.9), w=fw, d=T, h=min(0.9, top - elev),
                mat="stair", c=False)
        top = elev + k * rr                                            # landing
        box(x=X0, y=L["Y0"], z=top - 0.9, w=X1 - X0, d=L["land"] - L["Y0"], h=0.9, mat="stair", c=False)
        for j in range(n - k - 1):                                     # flight 2 (east, climbing north)
            top = elev + (k + j + 1) * rr
            ys = L["land"] + j * T
            box(x=X1 - fw, y=ys, z=top - 0.9, w=fw, d=T, h=0.9, mat="stair", c=False)
            # center divider doubles as the guard between flights (36" above the higher flight)
            box(x=X0 + fw + 0.05, y=ys, z=elev, w=X1 - X0 - 2 * fw - 0.1, d=T, h=top + RAIL_H - elev,
                mat=paint, c=True)
            box(x=X0 + fw, y=ys, z=top + RAIL_H, w=X1 - X0 - 2 * fw, d=T, h=0.12, mat="wood:#6e4f37", c=False)
        # invisible blocker: the walkthrough doesn't climb stairs (use the floor buttons)
        box(x=X0, y=L["Y0"], z=elev + 0.3, w=X1 - X0, d=Y - L["Y0"], h=4.5, mat="block", c=True)
    else:
        # arriving floor: guard along the open edge west of the arriving flight, and block the opening
        below = list(H.LEVELS)[list(H.LEVELS).index(level) - 1]
        rb = next(q for q in H.ROOMS[below] if q["name"] == r["name"])
        L = stair_layout(below, rb)
        gx1 = L["X1"] - L["fw"]
        box(x=L["X0"], y=L["Y"] - 0.3, z=elev, w=gx1 - L["X0"], d=0.3, h=RAIL_H, mat=paint, c=True)
        box(x=L["X0"], y=L["Y"] - 0.35, z=elev + RAIL_H, w=gx1 - L["X0"], d=0.4, h=0.12, mat="wood:#6e4f37",
            c=False)
        box(x=L["X0"], y=L["Y0"], z=elev + 0.3, w=L["X1"] - L["X0"], d=L["Y"] - L["Y0"], h=4.5, mat="block",
            c=True)


def furniture(level):
    """[(world boxes, footprint, label)] for every piece on a level."""
    return [F.place(kind, x, y, facing, opts)
            for lvl, kind, x, y, facing, opts in H.FURNITURE if lvl == level]


def bounds(r):
    xs = [p[0] for p in room_poly(r)]
    ys = [p[1] for p in room_poly(r)]
    return min(xs), min(ys), max(xs), max(ys)


def decompose(r):
    """Rect list covering a room (handles the one L-shaped polygon)."""
    if "rect" in r:
        return [r["rect"]]
    pts = room_poly(r)
    xs = sorted({p[0] for p in pts})
    ys = sorted({p[1] for p in pts})
    rects = []
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in zip(ys, ys[1:]):
            if inside(pts, (xa + xb) / 2, (ya + yb) / 2):
                rects.append((xa, ya, xb, yb))
    # merge cells in each column strip (good enough for slabs)
    return rects


def inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def room_area(r):
    return sum((b[2] - b[0]) * (b[3] - b[1]) for b in decompose(r))
