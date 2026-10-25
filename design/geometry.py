"""Turns house.py room data into walls, openings and 3D boxes (feet)."""
from collections import defaultdict
import house as H

DOOR_W, DOOR_H = 3.0, 6.67
CASED_W, CASED_H = 6.0, 8.0
PATIO_W, PATIO_H = 12.0, 8.0
WIN_W, WIN_H, WIN_SILL = 4.0, 4.5, 3.0
SIDE_NORMAL = {"S": (0, -1), "N": (0, 1), "W": (-1, 0), "E": (1, 0)}


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
        w = min(w, b - a - 0.5)
        ops.append(dict(axis=ax, c=c, pos=pos, w=w, sill=0.0, h=h, kind=kind))
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
            ops.append(dict(axis=w["axis"], c=w["c"], pos=pos, w=min(ww, length - 1),
                            sill=sill, h=wh, kind="window", auto=True))
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

    def add(ax, c, a, b, t, z0, z1, mat, collide=True):
        if b - a < 1e-6 or z1 - z0 < 1e-6:
            return
        if ax == "h":
            boxes.append(dict(x=a, y=c - t / 2, z=z0, w=b - a, d=t, h=z1 - z0, mat=mat, c=collide))
        else:
            boxes.append(dict(x=c - t / 2, y=a, z=z0, w=t, d=b - a, h=z1 - z0, mat=mat, c=collide))

    z_floor, z_top = elev, elev + height
    for i, w in enumerate(walls):
        mine = sorted([o for o in ops if o.get("wall") == i], key=lambda o: o["pos"])
        ext = w["ext"]
        mat = "wallExt" if ext else "wallInt"
        ex = w["t"] / 2
        a, b = w["a"] - ex, w["b"] + ex
        cur = a
        for o in mine:
            lo, hi = o["pos"] - o["w"] / 2, o["pos"] + o["w"] / 2
            add(w["axis"], w["c"], cur, lo, w["t"], z_floor, z_top, mat)
            if o["sill"] > 0:
                add(w["axis"], w["c"], lo, hi, w["t"], z_floor, z_floor + o["sill"], mat)
            head = z_floor + o["sill"] + o["h"]
            add(w["axis"], w["c"], lo, hi, w["t"], head, z_top, mat)
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

    for r in H.ROOMS[level]:
        if r.get("slab", True) and not (level == "basement" and False):
            x0, y0, x1, y1 = bounds(r)
            outdoor = r.get("kind") == "outdoor"
            for rect in decompose(r):
                bx0, by0, bx1, by1 = rect
                boxes.append(dict(x=bx0, y=by0, z=elev - H.FLOOR_T, w=bx1 - bx0, d=by1 - by0,
                                  h=H.FLOOR_T, mat="slabOut" if outdoor else "floor", c=False,
                                  room=r["name"]))
        if r.get("stair") == "up" and level in ("basement", "main"):
            x0, y0, x1, y1 = r["rect"]
            n = 17 if level == "main" else 16
            rise = (11.0 if level == "main" else 10.0) / n
            sx0 = x0 + 1.0
            for k in range(n):
                run = (y1 - y0 - 2) / n
                boxes.append(dict(x=sx0, y=y0 + 1 + k * run, z=elev + k * rise, w=4.0, d=run,
                                  h=rise, mat="stair", c=False))
    for f in H.FIXTURES:
        if f[0] == level:
            _, label, x, y, w, d, h, col = f
            boxes.append(dict(x=x, y=y, z=elev, w=w, d=d, h=h, mat="fix:" + col, c=True, label=label))
    return boxes, walls, ops


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
