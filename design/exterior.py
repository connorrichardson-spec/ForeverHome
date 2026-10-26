"""Roofs and site (sloped geometry as polygons, plus site boxes). Driven by house.ROOFS / house.SITE.

Polygons are dicts: {mat, pts: [(x, y, z), ...] (planar, convex), obj}. Units feet, house axes
(x east, y north, z up). Viewer/exports treat polygon materials as double-sided, so winding is free.
"""
import math, random
import house as H

ROOF_T = 0.6                         # roof thickness (deck + shingles) -> fascia depth
FINISH = {"shingle": "shingle", "metal": "metalRoof"}


def _poly(out, mat, pts, obj):
    out.append(dict(mat=mat, pts=[tuple(round(c, 4) for c in p) for p in pts], obj=obj))


def _slab(out, faces, mat, obj, edges_out=True):
    """faces: bottom-surface polygons of a roof. Emits top (+T, roof finish), underside (soffit),
    and fascia on every boundary edge (edges used by only one face)."""
    top = [[(x, y, z + ROOF_T) for x, y, z in f] for f in faces]
    for f in top:
        _poly(out, mat, f, obj)
    for f in faces:
        _poly(out, "soffit", f, obj)
    count = {}
    for f in faces:
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            k = tuple(sorted((tuple(round(c, 3) for c in a), tuple(round(c, 3) for c in b))))
            count[k] = count.get(k, 0) + 1
    for (a, b), n in count.items():
        if n == 1 and edges_out:
            _poly(out, "trim", [a, b, (b[0], b[1], b[2] + ROOF_T), (a[0], a[1], a[2] + ROOF_T)], obj)


def _ovh(r, side, default=1.0):
    o = r.get("ovh", default)
    return o.get(side, default) if isinstance(o, dict) else o


def gable(r, out):
    x0, y0, x1, y1 = r["rect"]
    p, base, obj = r["pitch"], r["base"], f"roof/{r['name']}"
    mat = FINISH[r.get("finish", "shingle")]
    if r["ridge"] == "x":                 # eaves on S/N, rakes (gable ends) on W/E
        ym, half = (y0 + y1) / 2, (y1 - y0) / 2
        zr = base + half * p
        ys, yn = y0 - _ovh(r, "S"), y1 + _ovh(r, "N")
        zs, zn = base - _ovh(r, "S") * p, base - _ovh(r, "N") * p
        xa, xb = x0 - _ovh(r, "W"), x1 + _ovh(r, "E")
        faces = [[(xa, ys, zs), (xb, ys, zs), (xb, ym, zr), (xa, ym, zr)],
                 [(xa, ym, zr), (xb, ym, zr), (xb, yn, zn), (xa, yn, zn)]]
        _slab(out, faces, mat, obj)
        for end, x in (("W", x0), ("E", x1)):
            if end in r.get("ends", "WE"):
                _poly(out, "siding", [(x, y0, base), (x, y1, base), (x, ym, zr)], obj)
    else:                                 # ridge along y: eaves on W/E, rakes on S/N
        xm, half = (x0 + x1) / 2, (x1 - x0) / 2
        zr = base + half * p
        xw, xe = x0 - _ovh(r, "W"), x1 + _ovh(r, "E")
        zw, ze = base - _ovh(r, "W") * p, base - _ovh(r, "E") * p
        ya, yb = y0 - _ovh(r, "S"), y1 + _ovh(r, "N")
        faces = [[(xw, ya, zw), (xm, ya, zr), (xm, yb, zr), (xw, yb, zw)],
                 [(xm, ya, zr), (xe, ya, ze), (xe, yb, ze), (xm, yb, zr)]]
        _slab(out, faces, mat, obj)
        for end, y in (("S", y0), ("N", y1)):
            if end in r.get("ends", "SN"):
                _poly(out, "siding", [(x0, y, base), (x1, y, base), (xm, y, zr)], obj)
    return zr


def hip(r, out):
    o = r.get("ovh", 1.0)
    x0, y0, x1, y1 = r["rect"]
    X0, Y0, X1, Y1 = x0 - o, y0 - o, x1 + o, y1 + o
    p, obj = r["pitch"], f"roof/{r['name']}"
    ze = r["base"] - o * p
    mat = FINISH[r.get("finish", "shingle")]
    if X1 - X0 >= Y1 - Y0:
        h = (Y1 - Y0) / 2
        zr, ym = ze + h * p, (Y0 + Y1) / 2
        faces = [[(X0, Y0, ze), (X1, Y0, ze), (X1 - h, ym, zr), (X0 + h, ym, zr)],
                 [(X0 + h, ym, zr), (X1 - h, ym, zr), (X1, Y1, ze), (X0, Y1, ze)],
                 [(X0, Y0, ze), (X0 + h, ym, zr), (X0, Y1, ze)],
                 [(X1, Y0, ze), (X1, Y1, ze), (X1 - h, ym, zr)]]
    else:
        h = (X1 - X0) / 2
        zr, xm = ze + h * p, (X0 + X1) / 2
        faces = [[(X0, Y0, ze), (xm, Y0 + h, zr), (xm, Y1 - h, zr), (X0, Y1, ze)],
                 [(xm, Y0 + h, zr), (X1, Y0, ze), (X1, Y1, ze), (xm, Y1 - h, zr)],
                 [(X0, Y0, ze), (X1, Y0, ze), (xm, Y0 + h, zr)],
                 [(X0, Y1, ze), (xm, Y1 - h, zr), (X1, Y1, ze)]]
    _slab(out, faces, mat, obj)
    return zr


def shed(r, out):
    """Single slope; `low` = side of the low eave (N/S). The high edge dies into a taller wall."""
    x0, y0, x1, y1 = r["rect"]
    p, base, obj = r["pitch"], r["base"], f"roof/{r['name']}"
    mat = FINISH[r.get("finish", "metal")]
    depth = y1 - y0
    zl_wall, zh_wall = base, base + depth * p
    if r["low"] == "N":
        yl, yh = y1 + _ovh(r, "N", 0), y0 - _ovh(r, "S", 0)
    else:
        yl, yh = y0 - _ovh(r, "S", 0), y1 + _ovh(r, "N", 0)
    wall_low = y1 if r["low"] == "N" else y0
    up = -1 if r["low"] == "N" else 1                    # +y direction climbs when the low eave is south

    def z_at(y):
        return base + (y - wall_low) * up * p
    xa, xb = x0 - _ovh(r, "W", 0), x1 + _ovh(r, "E", 0)
    face = [(xa, yl, z_at(yl)), (xb, yl, z_at(yl)), (xb, yh, z_at(yh)), (xa, yh, z_at(yh))]
    _slab(out, [face], mat, obj)
    wall_high = y0 if r["low"] == "N" else y1
    for end, x in (("W", x0), ("E", x1)):
        if end in r.get("ends", ""):
            _poly(out, "siding", [(x, wall_low, zl_wall), (x, wall_high, zl_wall), (x, wall_high, zh_wall)], obj)
    return zh_wall


def roof_polys():
    out = []
    for r in H.ROOFS:
        {"gable": gable, "hip": hip, "shed": shed}[r["kind"]](r, out)
    return out


def ridge_height(r):
    x0, y0, x1, y1 = r["rect"]
    if r["kind"] == "gable":
        span = (y1 - y0) if r["ridge"] == "x" else (x1 - x0)
        return r["base"] + span / 2 * r["pitch"]
    if r["kind"] == "hip":
        o = r.get("ovh", 1.0)
        return r["base"] - o * r["pitch"] + min(x1 - x0 + 2 * o, y1 - y0 + 2 * o) / 2 * r["pitch"]
    return r["base"] + (y1 - y0) * r["pitch"]


# ---------------------------------------------------------------- site
def icosphere(cx, cy, cz, r, mat, obj, out, squash=1.0, seed=0, jitter=0.12):
    t = (1 + 5 ** 0.5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    f = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
         (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
         (8, 6, 7), (9, 8, 1)]
    v = [tuple(c / math.sqrt(sum(k * k for k in p)) for c in p) for p in v]
    mid = {}

    def m(a, b):
        k = (min(a, b), max(a, b))
        if k not in mid:
            p = [(v[a][i] + v[b][i]) / 2 for i in range(3)]
            n = math.sqrt(sum(c * c for c in p))
            v.append(tuple(c / n for c in p))
            mid[k] = len(v) - 1
        return mid[k]
    f = [g for a, b, c in f for g in ((a, m(a, b), m(a, c)), (b, m(b, c), m(a, b)), (c, m(a, c), m(b, c)),
                                      (m(a, b), m(b, c), m(a, c)))]
    rnd = random.Random(seed)
    s = [1 + rnd.uniform(-jitter, jitter) for _ in v]
    pts = [(cx + p[0] * r * s[i], cy + p[1] * r * s[i], cz + p[2] * r * squash * s[i]) for i, p in enumerate(v)]
    for a, b, c in f:
        _poly(out, mat, [pts[a], pts[b], pts[c]], obj)


def site():
    """-> (boxes, polys) for the main level: hardscape, porch, patio structure, lights, plants."""
    S = H.SITE
    boxes, polys = [], []

    def box(obj, x, y, z, w, d, h, mat, c=False):
        boxes.append(dict(x=x, y=y, z=z, w=w, d=d, h=h, mat=mat, c=c, obj=obj))
    for name, (x0, y0, x1, y1), mat in S["paving"]:
        box(f"site/{name}", x0, y0, -0.3, x1 - x0, y1 - y0, 0.31, mat)
    for P in S["porches"]:
        o, (x0, y0, x1, y1), z_beam = f"site/{P['name']}", P["rect"], P["beam_top"]
        for px, py in P["posts"]:
            box(o, px - 0.33, py - 0.33, 0, 0.67, 0.67, z_beam - 0.8, "wood:#8a6a4a", True)
            box(o, px - 0.42, py - 0.42, 0, 0.84, 0.84, 0.5, "stone")                     # post base
        # beams on the open sides, then a tongue-and-groove ceiling
        for bx0, by0, bx1, by1 in _open_edges(x0, y0, x1, y1, P["open"]):
            box(o, bx0, by0, z_beam - 0.8, bx1 - bx0, by1 - by0, 0.8, "wood:#8a6a4a")
        box(o, x0, y0, z_beam - 0.06, x1 - x0, y1 - y0, 0.06, "wood:#b48a60")
    for x, y, z, facing in S["lights"]:
        o = "site/lights"
        dx, dy = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0)}[facing]
        w, d = (0.5, 0.45) if dy else (0.45, 0.5)
        bx = x - w / 2 + dx * 0.22
        by = y - d / 2 + dy * 0.22
        box(o, bx, by, z, w, d, 0.85, "lamp:#ffd59a")
        box(o, bx - 0.05, by - 0.05, z + 0.85, w + 0.1, d + 0.1, 0.12, "metal:#1d1e20")
        box(o, bx - 0.05, by - 0.05, z - 0.08, w + 0.1, d + 0.1, 0.08, "metal:#1d1e20")
    for (x0, y0, x1, y1, z0, z1) in S["chimneys"]:
        box("site/chimney", x0, y0, z0, x1 - x0, y1 - y0, z1 - z0, "stone", True)
        box("site/chimney", x0 - 0.2, y0 - 0.2, z1, x1 - x0 + 0.4, y1 - y0 + 0.4, 0.3, "fix:#6f655b")
    for i, (x, y, r) in enumerate(S["shrubs"]):
        icosphere(x, y, r * 0.75, r, "fabric:#3f6b3a" if i % 3 else "fabric:#557d3f", "site/shrubs", polys,
                  squash=0.8, seed=i)
    for i, (x, y, r, trunk) in enumerate(S["trees"]):
        box("site/trees", x - 0.45, y - 0.45, 0, 0.9, 0.9, trunk + r * 0.4, "wood:#5a4636", True)
        icosphere(x, y, trunk + r * 0.8, r, "fabric:#4d7a3e", "site/trees", polys, squash=0.9, seed=100 + i, jitter=0.18)
        icosphere(x + r * 0.35, y - r * 0.25, trunk + r * 1.35, r * 0.65, "fabric:#5b8a47", "site/trees", polys,
                  seed=200 + i, jitter=0.2)
    return boxes, polys


def _open_edges(x0, y0, x1, y1, sides):
    """Beam strips (0.6 ft wide) along the porch edges that aren't against the house."""
    t = 0.6
    edges = {"S": (x0, y0, x1, y0 + t), "N": (x0, y1 - t, x1, y1), "W": (x0, y0, x0 + t, y1), "E": (x1 - t, y0, x1, y1)}
    return [edges[k] for k in sides]
