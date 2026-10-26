"""Furniture / fixture library. Each piece is a handful of boxes in a local frame.

Local frame: u = width (left->right), v = depth (v=0 is the BACK, against the wall;
v=D is the front), z = up from the floor. `facing` (N/S/E/W) is the direction the
front points; (x, y) in house.py is the world min corner of the footprint, so an
E/W-facing piece occupies D along x and W along y.

Materials (understood by web/viewer.js):
  fix:#hex matte, gloss:#hex porcelain/stone, metal:#hex, wood:#hex grain,
  fabric:#hex, tile:#hex, lamp:#hex (emissive), glass, mirror
"""
import random

# finish palette
OAK, WALNUT, WHITE_OAK = "wood:#b08860", "wood:#6e4f37", "wood:#c9ad88"
CAB, CAB_ISLAND = "gloss:#f2f0ea", "gloss:#3f4b57"           # painted shaker cabinets
QUARTZ = "gloss:#ecebe7"
STEEL, BLACK_METAL, BRASS = "metal:#c7cacc", "metal:#2b2c2e", "metal:#b8955a"
PORCELAIN = "gloss:#f7f7f5"
SUBWAY = "tile:#f4f3ef"
LINEN = "fabric:#f1efe9"


def _box(parts, u, v, z, w, d, h, mat, c=True):
    parts.append((u, v, z, w, d, h, mat, c))


def _legs(p, W, D, h, t=0.15, mat=BLACK_METAL, inset=0.1):
    for u in (inset, W - inset - t):
        for v in (inset, D - inset - t):
            _box(p, u, v, 0, t, t, h, mat, False)


def _cab_fronts(p, u0, W, D, z0, h, mat, pull=STEEL, door_w=1.5, drawers=False, out=1):
    """Slightly proud door/drawer fronts with gaps + pulls on the face at v=D.
    out=1: the face looks toward +v (the piece's front); out=-1: toward -v (its back)."""
    n = max(1, round(W / door_w))
    dw = W / n
    fv = D if out > 0 else D - 0.04          # front panel slab
    pv = D + 0.04 if out > 0 else D - 0.09   # pull
    for i in range(n):
        if drawers:
            rows = 3
            dh = h / rows
            for r in range(rows):
                _box(p, u0 + i * dw + 0.02, fv, z0 + r * dh + 0.02, dw - 0.04, 0.04, dh - 0.04, mat, False)
                _box(p, u0 + i * dw + dw / 2 - 0.25, pv, z0 + r * dh + dh * 0.7, 0.5, 0.05, 0.05, pull, False)
        else:
            _box(p, u0 + i * dw + 0.02, fv, z0 + 0.02, dw - 0.04, 0.04, h - 0.04, mat, False)
            pu = u0 + i * dw + (dw - 0.2 if i % 2 == 0 else 0.15)
            pz = z0 + h - 0.6 if z0 < 2 else z0 + 0.25
            _box(p, pu, pv, pz, 0.05, 0.05, 0.4, pull, False)


def _carcass(p, u0, w, v0, d, z0, z1, mat, hole=None):
    """Cabinet body; hole=(su, sw, sv0, sv1, zh) leaves room for a basin above height zh."""
    if hole is None:
        _box(p, u0, v0, z0, w, d, z1 - z0, mat)
        return
    su, sw, sv0, sv1, zh = hole
    _box(p, u0, v0, z0, w, d, zh - z0, mat)
    _box(p, u0, v0, zh, su - u0, d, z1 - zh, mat)
    _box(p, su + sw, v0, zh, u0 + w - su - sw, d, z1 - zh, mat)
    _box(p, su, v0, zh, sw, max(0, sv0 - v0), z1 - zh, mat, False)
    _box(p, su, sv1, zh, sw, max(0, v0 + d - sv1), z1 - zh, mat, False)


def _sink_cutout(p, u0, u1, v0, v1, ct, top, su, sw, sv0, sv1, basin=STEEL, depth=0.75):
    """Counter slab u0..u1 x v0..v1 at height ct with a sw x (sv1-sv0) hole at u=su, plus a hollow
    undermount basin hanging below the hole."""
    t = 0.12
    _box(p, u0, v0, ct, su - u0, v1 - v0, t, top)
    _box(p, su + sw, v0, ct, u1 - su - sw, v1 - v0, t, top)
    _box(p, su, v0, ct, sw, sv0 - v0, t, top)
    _box(p, su, sv1, ct, sw, v1 - sv1, t, top)
    zb = ct - depth
    _box(p, su, sv0, zb, sw, sv1 - sv0, 0.05, basin, False)                       # basin floor
    for u, v, w, d in ((su, sv0, sw, 0.04), (su, sv1 - 0.04, sw, 0.04),
                       (su, sv0, 0.04, sv1 - sv0), (su + sw - 0.04, sv0, 0.04, sv1 - sv0)):
        _box(p, u, v, zb, w, d, depth + 0.02, basin, False)                       # basin walls
    _box(p, su + sw / 2 - 0.12, (sv0 + sv1) / 2 - 0.12, zb + 0.05, 0.24, 0.24, 0.01, "fix:#3a3a3a", False)


# ---------------------------------------------------------------- living
def sofa(W=8.0, D=3.2, color="fabric:#8b939b", leg=WALNUT, pillow="fabric:#d8c7a6"):
    p = []
    _legs(p, W, D, 0.35, mat=leg)
    _box(p, 0, 0, 0.35, W, D, 1.0, color)                       # base
    _box(p, 0, 0, 1.35, W, 0.75, 1.5, color)                    # back
    _box(p, 0, 0, 1.35, 0.6, D, 0.75, color)                    # arms
    _box(p, W - 0.6, 0, 1.35, 0.6, D, 0.75, color)
    n = max(1, round((W - 1.2) / 2.6))
    cw = (W - 1.2) / n
    for i in range(n):                                          # seat + back cushions
        _box(p, 0.62 + i * cw, 0.78, 1.35, cw - 0.04, D - 0.8, 0.35, color, False)
        _box(p, 0.62 + i * cw, 0.75, 1.7, cw - 0.04, 0.5, 1.05, color, False)
    _box(p, 0.7, 1.2, 1.7, 1.4, 0.35, 1.1, pillow, False)          # throw pillows
    _box(p, W - 2.1, 1.2, 1.7, 1.4, 0.35, 1.1, pillow, False)
    return p


def armchair(W=2.8, D=2.9, color="fabric:#b9a58a"):
    return sofa(W, D, color, pillow=color)


def coffee_table(W=4.5, D=2.2, top=WHITE_OAK):
    p = []
    _box(p, 0, 0, 1.25, W, D, 0.15, top)
    _box(p, 0.2, 0.2, 0.25, W - 0.4, D - 0.4, 0.08, top, False)   # lower shelf
    _legs(p, W, D, 1.25, t=0.18, mat=top, inset=0.05)
    _box(p, W * 0.6, D * 0.3, 1.4, 0.9, 0.7, 0.25, "fabric:#7a6a58", False)  # books
    return p


def side_table(W=1.6, D=1.6, top=WALNUT, lamp=True):
    p = []
    _box(p, 0, 0, 1.9, W, D, 0.12, top)
    _legs(p, W, D, 1.9, t=0.12, mat=top, inset=0.05)
    if lamp:
        _table_lamp(p, W / 2, D / 2, 2.02)
    return p


def _table_lamp(p, cu, cv, z):
    _box(p, cu - 0.2, cv - 0.2, z, 0.4, 0.4, 0.8, "gloss:#d9d4c8", False)
    _box(p, cu - 0.45, cv - 0.45, z + 0.8, 0.9, 0.9, 0.75, "lamp:#fff1d6", False)


def floor_lamp(W=1.2, D=1.2):
    p = []
    _box(p, 0.2, 0.2, 0, W - 0.4, D - 0.4, 0.1, BLACK_METAL, False)
    _box(p, W / 2 - 0.05, D / 2 - 0.05, 0.1, 0.1, 0.1, 4.7, BLACK_METAL, False)
    _box(p, 0, 0, 4.8, W, D, 0.9, "lamp:#fff1d6", False)
    return p


def rug(W=9.0, D=12.0, color="fabric:#c8bba6", border="fabric:#8c7a66"):
    p = []
    _box(p, 0, 0, 0, W, D, 0.03, border, False)
    _box(p, 0.5, 0.5, 0.03, W - 1, D - 1, 0.01, color, False)
    return p


def fireplace(W=7.0, D=1.6, tv=True):
    p = []
    _box(p, 0, 0, 0, W, D, 4.4, "gloss:#e8e4dc")                 # surround
    _box(p, W / 2 - 1.75, D - 0.02, 0.6, 3.5, 0.06, 2.2, "fix:#1b1b1b", False)   # firebox
    _box(p, W / 2 - 1.5, D + 0.02, 0.7, 3.0, 0.04, 0.35, "lamp:#ff8a3d", False)  # flame glow
    _box(p, -0.3, 0, 4.4, W + 0.6, D + 0.3, 0.3, WALNUT)          # mantel
    _box(p, -0.5, D, 0, W + 1.0, 1.4, 0.15, "gloss:#3a3a3a", False)  # hearth
    if tv:
        _box(p, W / 2 - 2.6, 0.05, 5.3, 5.2, 0.12, 2.9, "gloss:#111214", False)
    return p


def media_console(W=7.0, D=1.6, H=2.0):
    p = []
    _box(p, 0, 0, 0.35, W, D, H - 0.35, WALNUT)
    _legs(p, W, D, 0.35, mat=BLACK_METAL)
    _cab_fronts(p, 0, W, D, 0.4, H - 0.45, WALNUT, BRASS, door_w=1.75)
    return p


def plant(W=1.5, D=1.5, H=4.5):
    p = []
    _box(p, 0.25, 0.25, 0, W - 0.5, D - 0.5, 1.2, "gloss:#d5cfc4", False)
    _box(p, 0, 0, 1.2, W, D, H - 2.0, "fabric:#4f7a45", False)
    _box(p, 0.25, 0.25, H - 0.8, W - 0.5, D - 0.5, 0.8, "fabric:#5e8c50", False)
    return p


def art(W=3.0, D=0.1, z=4.5, H=2.4, color="fix:#7d97a8"):
    p = []
    _box(p, 0, 0, z, W, D, H, BLACK_METAL, False)
    _box(p, 0.15, D, z + 0.15, W - 0.3, 0.02, H - 0.3, color, False)
    return p


def bench(W=4.0, D=1.4, seat=WHITE_OAK, cushion="fabric:#6f7d6a"):
    p = []
    _box(p, 0, 0, 1.3, W, D, 0.15, seat)
    _legs(p, W, D, 1.3, t=0.15, mat=seat, inset=0.05)
    _box(p, 0.1, 0.1, 1.45, W - 0.2, D - 0.2, 0.15, cushion, False)
    return p


def console_table(W=4.0, D=1.25):
    p = []
    _box(p, 0, 0, 2.6, W, D, 0.12, WALNUT)
    _legs(p, W, D, 2.6, t=0.12, mat=BLACK_METAL, inset=0.05)
    _table_lamp(p, 0.6, D / 2, 2.72)
    _box(p, W - 1.2, 0.3, 2.72, 0.5, 0.5, 1.0, "gloss:#3e5c6e", False)   # vase
    return p


# ---------------------------------------------------------------- dining
def dining_table(W=8.0, D=3.6, top=OAK):
    p = []
    _box(p, 0, 0, 2.35, W, D, 0.15, top)
    for u in (0.5, W - 0.85):                                   # trestle legs
        _box(p, u, 0.4, 0, 0.35, D - 0.8, 2.35, top, False)
    _box(p, 0.85, D / 2 - 0.15, 0.6, W - 1.7, 0.3, 0.25, top, False)
    return p


def chair(W=1.6, D=1.7, seat="fabric:#d9cdb8", frame=WALNUT):
    p = []
    _legs(p, W, D, 1.5, t=0.12, mat=frame, inset=0.05)
    _box(p, 0, 0, 1.5, W, D, 0.2, seat, False)
    _box(p, 0, 0, 1.7, W, 0.15, 1.5, seat, False)
    return p


def stool(W=1.4, D=1.4, seat="fabric:#6b4d3a"):
    p = []
    _box(p, 0.2, 0.2, 0, W - 0.4, D - 0.4, 0.08, BLACK_METAL, False)
    _box(p, W / 2 - 0.08, D / 2 - 0.08, 0.08, 0.16, 0.16, 2.3, BLACK_METAL, False)
    _box(p, 0.25, 0.25, 0.9, W - 0.5, D - 0.5, 0.06, BLACK_METAL, False)
    _box(p, 0, 0, 2.38, W, D, 0.22, seat, False)
    _box(p, 0, 0, 2.6, W, 0.12, 0.9, seat, False)
    return p


def pendant(W=1.4, D=1.4, z=7.0, ceil=10.0):
    p = []
    _box(p, W / 2 - 0.02, D / 2 - 0.02, z + 0.8, 0.04, 0.04, ceil - z - 0.8, BLACK_METAL, False)
    _box(p, 0, 0, z + 0.25, W, D, 0.55, BLACK_METAL, False)
    _box(p, 0.1, 0.1, z, W - 0.2, D - 0.2, 0.25, "lamp:#fff1d6", False)
    return p


# ---------------------------------------------------------------- kitchen
def base_cab(W=6.0, D=2.0, color=CAB, top=QUARTZ, sink=None, drawers=False):
    """Base cabinet run with counter. sink=u offset of a 2.6 ft wide basin."""
    p = []
    _box(p, 0, 0, 0, W, D - 0.25, 0.35, "fix:#2a2a2a")            # toe kick
    hole = None if sink is None else (sink, 2.6, 0.5, D - 0.22, 2.95 - 0.8)
    _carcass(p, 0, W, 0, D - 0.05, 0.35, 2.95, color, hole)
    _cab_fronts(p, 0, W, D - 0.05, 0.4, 2.5, color, drawers=drawers)
    ct, cd = 2.95, D + 0.08
    if sink is None:
        _box(p, 0, 0, ct, W, cd, 0.12, top)
    else:
        su, sw = sink, 2.6
        _sink_cutout(p, 0, W, 0, cd, ct, top, su, sw, 0.5, cd - 0.3)
        _faucet(p, su + sw / 2, 0.25, ct + 0.12)
    return p


def _faucet(p, cu, cv, z, mat=STEEL, reach=0.6):
    _box(p, cu - 0.06, cv - 0.06, z, 0.12, 0.12, 1.1, mat, False)
    _box(p, cu - 0.05, cv, z + 1.0, 0.1, reach, 0.1, mat, False)
    _box(p, cu - 0.05, cv + reach - 0.1, z + 0.8, 0.1, 0.1, 0.25, mat, False)


def upper_cab(W=6.0, D=1.1, z=4.6, H=2.8, color=CAB):
    p = []
    _box(p, 0, 0, z, W, D, H, color, False)
    _cab_fronts(p, 0, W, D, z + 0.02, H - 0.04, color, door_w=1.5)
    _box(p, 0, 0, z - 0.03, W, D, 0.03, "lamp:#fff6e6", False)       # under-cabinet light
    return p


def tall_cab(W=6.0, D=2.0, H=9.6, color=CAB):
    """Floor-to-ceiling pantry cabinets: tall lower doors + short upper doors, toe kick."""
    p = []
    _box(p, 0, 0, 0, W, D - 0.25, 0.35, "fix:#2a2a2a")
    _box(p, 0, 0, 0.35, W, D - 0.05, H - 0.35, color)
    _cab_fronts(p, 0, W, D - 0.05, 0.4, 6.3, color, door_w=1.5)
    _cab_fronts(p, 0, W, D - 0.05, 6.75, H - 6.85, color, door_w=1.5)
    _box(p, -0.05, -0.02, H - 0.15, W + 0.1, D + 0.05, 0.15, "trim", False)        # crown
    return p


def mudroom_lockers(W=12.0, D=1.75, H=7.6, sections=5, open_section=2, color="gloss:#e9ece8",
                    seat="wood:#b08860", seed=19):
    """Built-in locker wall: shoe cubbies under a bench, open hook bays, upper cubbies with baskets.
    `open_section` is left bench-only (no dividers/uppers) to keep a window above it clear."""
    p = []
    rnd = random.Random(seed)
    sw = W / sections
    baskets = ["fabric:#b9a07a", "fabric:#8f8a80", "fabric:#c7b79c"]
    _box(p, 0, 0, 0, W, D - 0.2, 0.3, "fix:#2a2a2a")                                 # toe kick
    _box(p, 0, 0, 0.3, W, D, 0.08, color)                                            # cubby floor
    _box(p, 0, 0, 1.5, W, D + 0.05, 0.15, seat)                                       # bench seat
    for i in range(sections):                                                         # back panel (stops at
        top = 1.65 if i == open_section else H                                        # the bench below a window)
        _box(p, i * sw, 0, 0, sw, 0.06, top, color, False)
    for i in range(sections + 1):                                                     # lower dividers
        _box(p, min(i * sw, W - 0.08), 0, 0.3, 0.08, D, 1.2, color)
    for i in range(sections):
        u0 = i * sw
        if rnd.random() < 0.8:                                                        # shoes
            _box(p, u0 + 0.3, 0.4, 0.38, 0.9, 0.9, 0.35, rnd.choice(["fix:#2b2b2b", "fix:#7a5a3c", "fix:#d5d0c6"]), False)
        if i == open_section:
            _box(p, u0 + 0.1, 0.1, 1.65, sw - 0.2, D - 0.2, 0.25, "fabric:#6f7d6a", False)   # cushion
            continue
        for x in (u0, u0 + sw - 0.08):                                                # tall dividers
            _box(p, x, 0, 1.65, 0.08, D, H - 1.65, color, False)
        _box(p, u0, 0, 6.2, sw, D, 0.08, color, False)                                # upper cubby shelf
        _box(p, u0, 0, H - 0.1, sw, D + 0.1, 0.1, color, False)                       # top cap
        _box(p, u0 + 0.25, D - 0.15 - 1.2, 6.3, sw - 0.5, 1.2, 0.95, rnd.choice(baskets), False)
        for hx in (u0 + sw * 0.3, u0 + sw * 0.7):                                     # hooks + a coat
            _box(p, hx - 0.04, 0.06, 5.0, 0.08, 0.25, 0.08, "metal:#2b2c2e", False)
        if rnd.random() < 0.7:
            _box(p, u0 + sw * 0.3 - 0.45, 0.12, 2.7, 0.9, 0.5, 2.35,
                 rnd.choice(["fabric:#2e3b4e", "fabric:#6d7a5c", "fabric:#9a3b3b", "fabric:#c8b38f"]), False)
    return p


def fridge(W=3.0, D=2.5, H=6.0):
    p = []
    _box(p, 0, 0, 0, W, D, H, STEEL)
    _box(p, W / 2 - 0.01, D, 2.2, 0.02, 0.02, H - 2.2, "fix:#333", False)    # french doors
    _box(p, 0, D, 2.18, W, 0.02, 0.04, "fix:#333", False)
    _box(p, W / 2 - 0.2, D + 0.02, 2.8, 0.06, 0.15, 2.4, STEEL, False)
    _box(p, W / 2 + 0.14, D + 0.02, 2.8, 0.06, 0.15, 2.4, STEEL, False)
    _box(p, 0.5, D + 0.02, 1.9, W - 1.0, 0.15, 0.06, STEEL, False)
    _box(p, -0.05, -0.05, H, W + 0.1, D + 0.1, 1.5, CAB, False)        # cabinet above
    return p


def range_oven(W=3.0, D=2.2):
    p = []
    _box(p, 0, 0, 0, W, D, 2.95, STEEL)
    _box(p, 0, 0, 2.95, W, D, 0.08, "gloss:#18191b")
    for u in (0.4, W - 1.0):
        for v in (0.3, D - 0.9):
            _box(p, u, v, 3.03, 0.6, 0.6, 0.06, "fix:#0d0d0d", False)
    _box(p, 0.25, D, 0.6, W - 0.5, 0.04, 1.6, "gloss:#121212", False)
    _box(p, 0.3, D + 0.04, 2.35, W - 0.6, 0.12, 0.08, STEEL, False)
    for i in range(5):
        _box(p, 0.35 + i * (W - 0.7) / 4 - 0.06, D, 2.6, 0.12, 0.1, 0.12, "fix:#222", False)
    return p


def hood(W=3.5, D=2.0, z=5.6, ceil=10.0):
    p = []
    _box(p, 0, 0, z, W, D, 0.9, STEEL, False)
    _box(p, W / 2 - 0.6, 0, z + 0.9, 1.2, 1.0, ceil - z - 0.9, STEEL, False)
    return p


def dishwasher(W=2.0, D=2.0):
    p = []
    _box(p, 0, 0, 0.35, W, D - 0.03, 2.6, STEEL)
    _box(p, 0.2, D - 0.03, 2.55, W - 0.4, 0.08, 0.08, STEEL, False)
    _box(p, 0, 0, 2.95, W, D + 0.08, 0.12, QUARTZ)
    return p


def island(W=10.0, D=4.5, color=CAB_ISLAND, top=QUARTZ, overhang=1.1):
    """Cabinets on the back (v=0, work) side, seating overhang on the front. Prep sink centered,
    faucet on the far side of the basin so it reaches back toward the cook."""
    p = []
    cd = D - overhang
    _box(p, 0.1, 0.1, 0, W - 0.2, cd - 0.25, 0.35, "fix:#222")
    ct = 2.95
    sw, su = 2.4, W / 2 - 1.2
    _carcass(p, 0, W, 0, cd, 0.35, ct, color, (su, sw, 0.4, 1.9, ct - 0.8))
    _cab_fronts(p, 0, W, 0, 0.4, 2.5, color, drawers=True, out=-1)      # fronts face the work side
    _sink_cutout(p, -0.1, W + 0.1, -0.08, D + 0.08, ct, top, su, sw, 0.4, 1.9)
    _box(p, -0.1, -0.08, 0, 0.12, D + 0.08, ct + 0.12, top)              # waterfall ends
    _box(p, W - 0.02, -0.08, 0, 0.12, D + 0.08, ct + 0.12, top)
    cu, z = W / 2, ct + 0.12                                              # brass faucet behind basin
    _box(p, cu - 0.07, 2.1, z, 0.14, 0.14, 1.2, BRASS, False)
    _box(p, cu - 0.05, 1.45, z + 1.1, 0.1, 0.75, 0.1, BRASS, False)
    _box(p, cu - 0.05, 1.45, z + 0.85, 0.1, 0.1, 0.3, BRASS, False)
    _box(p, cu + 0.25, 2.12, z, 0.1, 0.1, 0.45, BRASS, False)            # side handle
    return p


def pantry_shelves(W=10.0, D=1.4, H=7.5, wood=WHITE_OAK, seed=1, z0=0.0):
    """Open shelving stocked with jars/boxes; z0 > 0 starts it above a counter."""
    p = []
    rnd = random.Random(seed)
    goods = ["gloss:#f3efe6", "fix:#c94f3d", "fix:#e2b04a", "fix:#5a8c5a", "fix:#d8d2c2", "fix:#8a5a3c", "glass"]
    _box(p, 0, 0, z0, 0.1, D, H - z0, wood, z0 == 0)
    _box(p, W - 0.1, 0, z0, 0.1, D, H - z0, wood, z0 == 0)
    z = z0 + 0.4
    while z < H - 0.4:
        _box(p, 0, 0, z, W, D, 0.08, wood, z < 4.5)
        u = 0.2
        while u < W - 0.6 and z < H - 1.2:
            gw = rnd.choice((0.35, 0.5, 0.7, 1.0))
            gh = rnd.choice((0.5, 0.7, 0.9))
            if rnd.random() < 0.8:
                _box(p, u, 0.2, z + 0.08, gw, D - 0.4, gh, rnd.choice(goods), False)
            u += gw + 0.12
        z += 1.5
    return p


def bookcase(W=4.0, D=1.2, H=7.5, wood=WALNUT, seed=3):
    p = []
    rnd = random.Random(seed)
    books = ["fix:#8a3b2e", "fix:#2e4a6b", "fix:#d9c9a3", "fix:#4c6b4a", "fix:#1f1f1f", "fix:#b7793d", "fix:#efe9dc"]
    _box(p, 0, 0, 0, W, 0.1, H, wood)
    _box(p, 0, 0, 0, 0.12, D, H, wood)
    _box(p, W - 0.12, 0, 0, 0.12, D, H, wood)
    _box(p, 0, 0, H - 0.12, W, D, 0.12, wood)
    z = 0.3
    while z < H - 1.0:
        _box(p, 0.12, 0, z, W - 0.24, D, 0.08, wood, False)
        u = 0.2
        while u < W - 0.4:
            bw = rnd.uniform(0.1, 0.22)
            if rnd.random() < 0.85:
                _box(p, u, 0.15, z + 0.08, bw, D - 0.3, rnd.uniform(0.7, 1.1), rnd.choice(books), False)
            u += bw + 0.01
        z += 1.4
    return p


# ---------------------------------------------------------------- bedroom
def bed(W=5.0, D=7.0, bedding="fabric:#f1efe9", frame="fabric:#a39a8e", throw="fabric:#5d6e7e"):
    p = []
    _box(p, 0, 0, 0, W, 0.35, 4.3, frame)                        # headboard
    _box(p, 0, 0.35, 0.3, W, D - 0.35, 0.8, frame)               # platform
    _box(p, 0.15, 0.4, 1.1, W - 0.3, D - 0.6, 0.85, LINEN, False)  # mattress
    _box(p, 0.05, 2.3, 0.75, W - 0.1, D - 2.4, 1.3, bedding, False)   # duvet
    _box(p, 0.05, D - 1.8, 0.7, W - 0.1, 1.0, 1.38, throw, False)
    pw = (W - 0.6) / 2
    _box(p, 0.25, 0.5, 1.95, pw, 1.2, 0.45, LINEN, False)        # pillows
    _box(p, W - 0.25 - pw, 0.5, 1.95, pw, 1.2, 0.45, LINEN, False)
    return p


def nightstand(W=1.8, D=1.5):
    p = []
    _box(p, 0, 0, 0.3, W, D, 1.9, WALNUT)
    _legs(p, W, D, 0.3, t=0.12, mat=WALNUT, inset=0.05)
    _cab_fronts(p, 0, W, D, 0.35, 1.8, WALNUT, BRASS, door_w=W, drawers=True)
    _table_lamp(p, W / 2, D / 2, 2.2)
    return p


def dresser(W=5.0, D=1.75, H=2.8, wood=WALNUT):
    p = []
    _box(p, 0, 0, 0.3, W, D, H - 0.3, wood)
    _legs(p, W, D, 0.3, t=0.15, mat=wood, inset=0.05)
    _cab_fronts(p, 0, W, D, 0.35, H - 0.4, wood, BRASS, door_w=W / 2, drawers=True)
    _box(p, 0.4, 0.05, H + 1.0, W - 0.8, 0.06, 2.6, "mirror", False)
    return p


def desk(W=5.5, D=2.5, top=WALNUT):
    p = []
    _box(p, 0, 0, 2.4, W, D, 0.12, top)
    _box(p, 0.05, 0.1, 0, 0.12, D - 0.2, 2.4, BLACK_METAL, False)
    _box(p, W - 0.17, 0.1, 0, 0.12, D - 0.2, 2.4, BLACK_METAL, False)
    _box(p, W / 2 - 1.1, 0.25, 2.52, 2.2, 0.1, 0.1, BLACK_METAL, False)   # monitor
    _box(p, W / 2 - 0.08, 0.3, 2.52, 0.16, 0.08, 0.7, BLACK_METAL, False)
    _box(p, W / 2 - 1.4, 0.3, 3.0, 2.8, 0.08, 1.4, "gloss:#141518", False)
    _box(p, W / 2 - 0.8, D - 1.0, 2.52, 1.6, 0.5, 0.04, "fix:#2a2a2a", False)
    _table_lamp(p, W - 0.6, 0.6, 2.52)
    return p


def office_chair(W=2.0, D=2.0, color="fabric:#2f3338"):
    p = []
    _box(p, 0.1, 0.1, 0, W - 0.2, D - 0.2, 0.25, BLACK_METAL, False)
    _box(p, W / 2 - 0.1, D / 2 - 0.1, 0.25, 0.2, 0.2, 1.3, BLACK_METAL, False)
    _box(p, 0.15, 0.25, 1.55, W - 0.3, D - 0.4, 0.3, color, False)
    _box(p, 0.2, 0.05, 1.85, W - 0.4, 0.25, 1.9, color, False)
    return p


def closet_rod(W=8.0, D=2.0, seed=5, double=False):
    """Open closet: top shelf, rod, hanging clothes, shoe shelf."""
    p = []
    rnd = random.Random(seed)
    cloth = ["fabric:#2e3b4e", "fabric:#e9e4da", "fabric:#9a3b3b", "fabric:#6d7a5c", "fabric:#c8b38f",
             "fabric:#3c3c3c", "fabric:#7a8ea6", "fabric:#d7c7d6"]
    _box(p, 0, 0, 5.9, W, D, 0.08, WHITE_OAK, False)
    _box(p, 0, 0, 6.6, W, D, 0.08, WHITE_OAK, False)
    _box(p, 0, 0, 0.6, W, D, 0.08, WHITE_OAK, False)
    rods = [5.7, 2.9] if double else [5.7]
    for rz in rods:
        _box(p, 0, D / 2 - 0.05, rz, W, 0.1, 0.1, BRASS, False)
        u = 0.15
        while u < W - 0.2:
            cw = rnd.uniform(0.08, 0.2)
            ln = rnd.uniform(1.8, 2.6) if double else rnd.uniform(2.2, 4.0)
            _box(p, u, 0.2, rz - ln, cw, D - 0.4, ln, rnd.choice(cloth), False)
            u += cw + rnd.uniform(0.02, 0.12)
    _box(p, 0, 0, 0, W, 0.05, 6.7, "fix:#f0ede6", True)
    return p


def wardrobe_wall(W=10.0, D=1.75, H=7.5, seed=7):
    """Built-in closet system: open hanging sections between drawer towers."""
    p = []
    n = max(1, round(W / 4))
    sw = W / n
    for i in range(n):
        if i % 2 == 0:
            for part in closet_rod(sw - 0.1, D, seed + i, double=(i % 4 == 0)):
                p.append((part[0] + i * sw + 0.05,) + part[1:])
        else:
            _box(p, i * sw + 0.05, 0, 0, sw - 0.1, D, H, "gloss:#ece8df")
            _cab_fronts(p, i * sw + 0.05, sw - 0.1, D, 0.1, 3.0, "gloss:#ece8df", BRASS, door_w=sw, drawers=True)
            _cab_fronts(p, i * sw + 0.05, sw - 0.1, D, 3.2, H - 3.3, "gloss:#ece8df", BRASS, door_w=sw / 2)
    return p


def closet_island(W=6.0, D=2.5):
    p = []
    _box(p, 0, 0, 0, W, D, 3.0, "gloss:#ece8df")
    _cab_fronts(p, 0, W, D, 0.1, 2.8, "gloss:#ece8df", BRASS, door_w=1.5, drawers=True)
    _cab_fronts(p, 0, W, 0, 0.1, 2.8, "gloss:#ece8df", BRASS, door_w=1.5, drawers=True, out=-1)
    _box(p, -0.1, -0.1, 3.0, W + 0.2, D + 0.2, 0.12, QUARTZ)
    _box(p, 0.6, 0.6, 3.12, 1.0, 0.8, 0.5, "fix:#b98a5a", False)   # jewelry box / decor
    return p


# ---------------------------------------------------------------- bath
def toilet(W=1.7, D=2.4):
    p = []
    _box(p, 0.1, 0, 1.35, W - 0.2, 0.65, 1.35, PORCELAIN)
    _box(p, 0.35, 0.55, 0, W - 0.7, D - 0.75, 1.0, PORCELAIN)
    _box(p, 0.25, 0.6, 1.0, W - 0.5, D - 0.65, 0.35, PORCELAIN)
    _box(p, 0.25, 0.6, 1.35, W - 0.5, D - 0.65, 0.06, "gloss:#ffffff", False)
    _box(p, W - 0.45, 0.66, 2.45, 0.25, 0.06, 0.08, STEEL, False)
    return p


def vanity(W=5.0, D=1.8, sinks=1, color=CAB_ISLAND, top=QUARTZ, mirror=True):
    p = []
    _box(p, 0, 0, 0.3, W, D, 2.5, color)
    _legs(p, W, D, 0.3, t=0.12, mat=color, inset=0.05)
    _cab_fronts(p, 0, W, D, 0.35, 2.4, color, BRASS, door_w=1.25)
    _box(p, 0, 0, 2.8, W, D + 0.06, 0.12, top)
    for k in range(sinks):
        cu = W * (k + 0.5) / sinks
        _box(p, cu - 0.75, D / 2 - 0.4, 2.92, 1.5, 1.1, 0.35, PORCELAIN, False)   # vessel basin
        _box(p, cu - 0.65, D / 2 - 0.3, 3.2, 1.3, 0.9, 0.08, "fix:#dfe3e4", False)
        _faucet(p, cu, 0.15, 2.92, BRASS, 0.55)
        if mirror:
            _box(p, cu - 1.0, 0, 3.9, 2.0, 0.06, 2.8, BRASS, False)
            _box(p, cu - 0.92, 0.06, 3.98, 1.84, 0.02, 2.64, "mirror", False)
            _box(p, cu - 1.35, 0.05, 5.1, 0.2, 0.3, 0.8, "lamp:#fff1d6", False)   # sconces
            _box(p, cu + 1.15, 0.05, 5.1, 0.2, 0.3, 0.8, "lamp:#fff1d6", False)
    return p


def shower(W=4.0, D=4.0, glass="F", tile=SUBWAY, curb=0.35):
    """Walk-in shower. Back wall (v=0) is always tiled. glass: which of F/L/R are
    glass (the rest are tiled walls). Head on the back wall."""
    p = []
    _box(p, 0, 0, 0, W, D, curb, "tile:#d9d6cf", False)
    _box(p, 0.15, 0.15, curb, W - 0.3, D - 0.3, 0.01, "tile:#bdb8ad", False)
    _box(p, 0, 0, curb, W, 0.06, 7.2, tile, False)
    sides = {"L": (0, 0, 0.06, D), "R": (W - 0.06, 0, 0.06, D), "F": (0, D - 0.06, W, 0.06)}
    for k, (u, v, w, d) in sides.items():
        if k in glass:
            _box(p, u, v, curb, w, d, 6.6, "glass", False)
            _box(p, u, v, curb + 6.6, w, d, 0.05, BRASS, False)
        else:
            _box(p, u, v, curb, w, d, 7.2, tile, False)
    _box(p, W / 2 - 0.05, 0.06, 6.4, 0.1, 0.7, 0.1, BRASS, False)       # arm + head
    _box(p, W / 2 - 0.35, 0.5, 6.25, 0.7, 0.7, 0.12, BRASS, False)
    _box(p, W / 2 - 0.15, 0.06, 3.8, 0.3, 0.06, 0.4, BRASS, False)      # valve
    _box(p, 0.3, 0.06, 3.3, 1.4, 0.4, 0.06, "tile:#d9d6cf", False)       # niche shelf
    return p


def tub(W=5.0, D=2.6, shower_walls=False, freestanding=False):
    p = []
    rim, h = 0.28, 1.75 if not freestanding else 2.0
    _box(p, 0, 0, 0, W, D, 0.4, PORCELAIN)
    _box(p, 0, 0, 0, W, rim, h, PORCELAIN)
    _box(p, 0, D - rim, 0, W, rim, h, PORCELAIN)
    _box(p, 0, 0, 0, rim, D, h, PORCELAIN)
    _box(p, W - rim, 0, 0, rim, D, h, PORCELAIN)
    _box(p, rim, rim, 0.9, W - 2 * rim, D - 2 * rim, 0.02, "gloss:#bfe0ea", False)   # water
    if freestanding:
        _box(p, W + 0.4, D / 2 - 0.08, 0, 0.16, 0.16, 3.1, BRASS, False)        # floor filler
        _box(p, W - 0.15, D / 2 - 0.05, 2.95, 0.6, 0.1, 0.1, BRASS, False)
    if shower_walls:
        _box(p, 0, -0.06, h, W, 0.06, 5.5, SUBWAY, False)
        _box(p, -0.06, 0, h, 0.06, D, 5.5, SUBWAY, False)
        _box(p, W, 0, h, 0.06, D, 5.5, SUBWAY, False)
        _box(p, W * 0.45, D - 0.1, h, W * 0.55, 0.05, 4.8, "glass", False)
        _box(p, 0.4, 0.0, 6.4, 0.1, 0.7, 0.1, BRASS, False)
        _box(p, 0.3, 0.5, 6.25, 0.5, 0.5, 0.12, BRASS, False)
        _faucet(p, 0.6, 0.0, h - 0.6, BRASS, 0.4)
    return p


def towel_bar(W=2.5, D=0.25, z=4.0):
    p = []
    _box(p, 0, 0.1, z, W, 0.06, 0.06, BRASS, False)
    _box(p, 0.2, 0.05, z - 1.6, W - 0.4, 0.15, 1.65, "fabric:#e8e3d8", False)
    return p


# ---------------------------------------------------------------- laundry / utility
def washer(W=2.3, D=2.4, H=3.2, dryer=False):
    p = []
    _box(p, 0, 0, 0, W, D, H, "gloss:#f4f4f2")
    _box(p, 0.05, D, H - 0.55, W - 0.1, 0.04, 0.5, "gloss:#2f3236", False)
    _box(p, W / 2 - 0.75, D, 0.6, 1.5, 0.06, 1.5, BLACK_METAL if dryer else "glass", False)
    _box(p, W / 2 - 0.6, D + 0.06, 0.75, 1.2, 0.03, 1.2, "gloss:#3a3d42" if dryer else "gloss:#9fb6c2", False)
    return p


def utility_sink_counter(W=8.0, D=2.0):
    return base_cab(W, D, color="gloss:#cdd7d6", top="gloss:#f1f1ef", sink=0.6)


def shelving_metal(W=6.0, D=2.0, H=7.0, seed=9, bins=True):
    p = []
    rnd = random.Random(seed)
    for u in (0, W - 0.1):
        for v in (0, D - 0.1):
            _box(p, u, v, 0, 0.1, 0.1, H, BLACK_METAL, False)
    z = 0.4
    while z < H:
        _box(p, 0, 0, z, W, D, 0.06, STEEL, z < 4.5)
        if bins and z < H - 1:
            u = 0.2
            while u < W - 1.6:
                if rnd.random() < 0.75:
                    _box(p, u, 0.2, z + 0.06, 1.4, D - 0.4, 1.0,
                         rnd.choice(["gloss:#2f5d7c", "gloss:#e9e5d8", "fix:#b48a5a", "gloss:#3d3d3d"]), False)
                u += 1.6
        z += 1.6
    return p


def workbench(W=8.0, D=2.5):
    p = []
    _box(p, 0, 0, 2.9, W, D, 0.2, WHITE_OAK)
    _legs(p, W, D, 2.9, t=0.3, mat=WHITE_OAK, inset=0.05)
    _box(p, 0.1, 0.1, 0.5, W - 0.2, D - 0.2, 0.1, WHITE_OAK, False)
    _box(p, 0, 0, 3.6, W, 0.08, 3.4, "fix:#a8865c", False)         # pegboard
    _box(p, 0.5, 0.15, 3.1, 1.6, 1.0, 0.8, "gloss:#b22b2b", False)  # toolbox
    _box(p, W - 3.0, 0, 0, 2.6, 1.8, 3.4, "gloss:#b22b2b")          # rolling tool chest
    return p


def car(W=6.3, D=15.5, color="gloss:#2c3e57"):
    """Front faces `facing`; D is length."""
    p = []
    for u in (0.2, W - 0.95):
        for v in (2.5, D - 4.0):
            _box(p, u, v, 0, 0.75, 2.2, 2.2, "fix:#151515", False)
    _box(p, 0.15, 0.3, 0.9, W - 0.3, D - 0.6, 2.0, color)
    _box(p, 0.5, 4.0, 2.9, W - 1.0, D - 8.5, 1.8, "glass", False)
    _box(p, 0.6, 4.2, 4.65, W - 1.2, D - 9.0, 0.15, color, False)
    _box(p, 0.5, D - 0.32, 2.0, 1.1, 0.04, 0.4, "lamp:#ffffff", False)   # headlights
    _box(p, W - 1.6, D - 0.32, 2.0, 1.1, 0.04, 0.4, "lamp:#ffffff", False)
    _box(p, 0.5, 0.26, 2.0, 1.1, 0.04, 0.35, "lamp:#d42424", False)
    _box(p, W - 1.6, 0.26, 2.0, 1.1, 0.04, 0.35, "lamp:#d42424", False)
    return p


def furnace(W=2.5, D=2.5, H=5.0):
    p = []
    _box(p, 0, 0, 0, W, D, H, "gloss:#d9d9d6")
    _box(p, 0.3, 0.3, H, W - 0.6, D - 0.6, 3.5, STEEL, False)     # plenum
    _box(p, W + 0.3, 0.4, 0, 1.8, 1.8, 5.2, "gloss:#f2f2f0")       # water heater
    _box(p, W + 1.0, 1.0, 5.2, 0.3, 0.3, 3.3, STEEL, False)
    return p


def elec_panel(W=1.5, D=0.4):
    p = []
    _box(p, 0, 0, 3.6, W, D, 2.6, "gloss:#a9adb0", False)
    return p


# ---------------------------------------------------------------- gym / sauna
def squat_rack(W=4.5, D=5.0):
    p = []
    _box(p, -1.75, -1.5, 0, W + 3.5, D + 3.0, 0.12, "fix:#1f2022", False)      # platform
    _box(p, 0.5, -0.5, 0.12, W - 1.0, D + 1.0, 0.02, WHITE_OAK, False)
    for u in (0, W - 0.25):
        for v in (0.5, D - 0.75):
            _box(p, u, v, 0.12, 0.25, 0.25, 7.6, "metal:#1d1e20")
        _box(p, u, 0.5, 7.5, 0.25, D - 1.0, 0.25, "metal:#1d1e20", False)
    _box(p, 0, 0.5, 7.5, W, 0.25, 0.25, "metal:#1d1e20", False)
    _box(p, 0, D - 0.75, 7.5, W, 0.25, 0.25, "metal:#1d1e20", False)
    _box(p, -1.25, D - 0.9, 4.5, W + 2.5, 0.1, 0.1, STEEL, False)         # barbell
    for u in (-1.0, W + 0.6):
        _box(p, u, D - 1.95, 3.55, 0.25, 2.0, 2.0, "fix:#202022", False)    # plates
    _box(p, -0.35, -1.4, 0.12, 0.35, 1.2, 1.5, "metal:#1d1e20", False)   # plate tree
    return p


def weight_bench(W=1.4, D=4.2):
    p = []
    _box(p, 0.2, 0.3, 0, W - 0.4, D - 0.6, 0.15, BLACK_METAL, False)
    _box(p, W / 2 - 0.15, 0.6, 0.15, 0.3, D - 1.2, 1.2, BLACK_METAL, False)
    _box(p, 0, 0, 1.35, W, D, 0.3, "fabric:#151515")
    return p


def dumbbell_rack(W=6.0, D=1.6):
    p = []
    _box(p, 0, 0.3, 0, 0.15, 1.0, 3.0, BLACK_METAL, False)
    _box(p, W - 0.15, 0.3, 0, 0.15, 1.0, 3.0, BLACK_METAL, False)
    for z, v in ((1.2, 0.1), (2.3, 0.5)):
        _box(p, 0, v, z, W, 1.0, 0.1, BLACK_METAL)
        u = 0.25
        while u < W - 0.6:
            _box(p, u, v + 0.1, z + 0.1, 0.4, 0.8, 0.4, "fix:#2a2a2c", False)
            u += 0.55
    _box(p, 0, 0, 4.0, W, 0.05, 4.0, "mirror", False)
    return p


def treadmill(W=3.0, D=6.5):
    p = []
    _box(p, 0, 0.5, 0, W, D - 0.5, 0.7, BLACK_METAL)
    _box(p, 0.4, 0.8, 0.7, W - 0.8, D - 1.5, 0.03, "fix:#1a1a1a", False)
    _box(p, 0.05, D - 0.6, 0.7, 0.2, 0.2, 3.5, BLACK_METAL, False)
    _box(p, W - 0.25, D - 0.6, 0.7, 0.2, 0.2, 3.5, BLACK_METAL, False)
    _box(p, 0, D - 1.0, 4.0, W, 0.8, 0.4, "gloss:#2a2d31", False)
    return p


def cold_plunge(W=3.0, D=6.0):
    p = []
    _box(p, 0, 0, 0, W, D, 0.3, "gloss:#e9ecee")
    for u, v, w, d in ((0, 0, W, 0.3), (0, D - 0.3, W, 0.3), (0, 0, 0.3, D), (W - 0.3, 0, 0.3, D)):
        _box(p, u, v, 0, w, d, 2.6, "gloss:#e9ecee")
    _box(p, 0.3, 0.3, 2.0, W - 0.6, D - 0.6, 0.02, "gloss:#7cc4dc", False)
    _box(p, W / 2 - 0.8, -1.2, 0, 1.6, 1.1, 1.6, "gloss:#d6d9db", False)     # chiller
    return p


def sauna_benches(W=6.0, D=3.4, cedar="wood:#c48a57"):
    p = []
    _box(p, 0, 0, 0, W, D, 1.5, cedar)
    _box(p, 0, 0, 1.5, W, 1.8, 1.6, cedar)
    _box(p, 0, 0, 3.1, W, 0.4, 1.4, cedar, False)        # backrest
    return p


def sauna_heater(W=1.6, D=1.4):
    p = []
    _box(p, 0, 0, 0.3, W, D, 2.3, BLACK_METAL)
    _box(p, 0.15, 0.15, 2.6, W - 0.3, D - 0.3, 0.4, "fix:#6e6a66", False)   # stones
    _box(p, -0.1, -0.1, 0, W + 0.2, D + 0.2, 0.3, "wood:#c48a57", False)
    return p


# ---------------------------------------------------------------- kids
def kids_table(W=3.0, D=3.0):
    p = []
    _box(p, 0, 0, 1.75, W, D, 0.1, "gloss:#f3f0e8")
    _legs(p, W, D, 1.75, t=0.15, mat=WHITE_OAK, inset=0.2)
    for u, v in ((W / 2 - 0.5, -1.1), (W / 2 - 0.5, D + 0.1), (-1.1, D / 2 - 0.5), (W + 0.1, D / 2 - 0.5)):
        _box(p, u, v, 0, 1.0, 1.0, 1.0, "gloss:#e9a23b" if u < 0 or v < 0 else "gloss:#5a9bc4", False)
    return p


def toy_storage(W=8.0, D=1.4, H=3.0, seed=11):
    p = []
    rnd = random.Random(seed)
    _box(p, 0, 0, 0, W, D, H, "gloss:#f3f0e8")
    n = int(W // 1.2)
    for r in range(2):
        for i in range(n):
            _box(p, 0.08 + i * W / n, D, 0.1 + r * H / 2, W / n - 0.16, 0.04, H / 2 - 0.2,
                 rnd.choice(["fabric:#d98a6a", "fabric:#e8c96a", "fabric:#86b0a5", "fabric:#a6a3c9", "fabric:#e7e1d6"]), False)
    _box(p, W * 0.2, 0.3, H, 0.8, 0.8, 0.8, "gloss:#d64a3a", False)
    _box(p, W * 0.6, 0.3, H, 1.2, 0.6, 0.5, "gloss:#3a7bd6", False)
    return p


def beanbag(W=2.8, D=2.8, color="fabric:#d8a35d"):
    p = []
    _box(p, 0, 0, 0, W, D, 1.2, color)
    _box(p, 0.2, 0, 1.2, W - 0.4, 0.9, 1.0, color, False)
    return p


def tv_wall(W=5.5, D=0.15, z=3.6):
    p = []
    _box(p, 0, 0, z, W, D, W * 0.5625, "gloss:#111214", False)
    return p


# ---------------------------------------------------------------- outdoor
def outdoor_kitchen(W=14.0, D=2.5):
    p = base_cab(W, D, color="gloss:#5f6266", top="gloss:#3b3c3e", sink=W - 3.5)
    _box(p, 2.0, 0.2, 3.07, 3.2, 1.9, 0.5, STEEL, False)      # built-in grill
    _box(p, 2.0, 0.2, 3.57, 3.2, 0.5, 0.9, STEEL, False)      # open lid
    _box(p, 6.5, 0.4, 3.07, 2.0, 1.5, 0.25, "fix:#1b1b1b", False)  # side burner
    return p


def outdoor_fireplace(W=6.0, D=2.0, H=8.0):
    p = []
    _box(p, 0, 0, 0, W, D, H, "fix:#8d8174")
    _box(p, W / 2 - 1.6, D - 0.02, 1.2, 3.2, 0.06, 2.4, "fix:#141414", False)
    _box(p, W / 2 - 1.4, D + 0.02, 1.3, 2.8, 0.04, 0.4, "lamp:#ff8a3d", False)
    _box(p, -0.3, 0, 4.2, W + 0.6, D + 0.4, 0.3, "fix:#6f655b")
    _box(p, -0.4, D, 0, W + 0.8, 0.9, 1.2, "fix:#6f655b")
    return p


def outdoor_table(W=7.0, D=3.4):
    p = dining_table(W, D, top="wood:#8c7058")
    return p


# registry: kind -> (function, default label, show in plan)
KINDS = {
 "sofa": (sofa, "Sofa"), "armchair": (armchair, "Chair"), "coffee_table": (coffee_table, "Coffee tbl"),
 "side_table": (side_table, None), "floor_lamp": (floor_lamp, None), "rug": (rug, None),
 "fireplace": (fireplace, "Fireplace / TV"), "media_console": (media_console, "Media"), "plant": (plant, None),
 "art": (art, None), "bench": (bench, "Bench"), "console_table": (console_table, "Console"),
 "dining_table": (dining_table, "Dining table"), "chair": (chair, None), "stool": (stool, None),
 "pendant": (pendant, None), "base_cab": (base_cab, "Base cab"), "upper_cab": (upper_cab, None),
 "fridge": (fridge, "Ref"), "tall_cab": (tall_cab, "Pantry cab"),
 "mudroom_lockers": (mudroom_lockers, "Lockers / bench"), "range": (range_oven, "Range"), "hood": (hood, None),
 "dishwasher": (dishwasher, "DW"), "island": (island, "Island"), "pantry_shelves": (pantry_shelves, "Shelves"),
 "bookcase": (bookcase, "Books"), "bed": (bed, "Bed"), "nightstand": (nightstand, None),
 "dresser": (dresser, "Dresser"), "desk": (desk, "Desk"), "office_chair": (office_chair, None),
 "closet_rod": (closet_rod, "Rod/shelf"), "wardrobe_wall": (wardrobe_wall, "Closet system"),
 "closet_island": (closet_island, "Island"), "toilet": (toilet, "WC"), "vanity": (vanity, "Vanity"),
 "shower": (shower, "Shower"), "tub": (tub, "Tub"), "towel_bar": (towel_bar, None),
 "washer": (washer, "W"), "dryer": (lambda **k: washer(dryer=True, **k), "D"),
 "utility_sink": (utility_sink_counter, "Sink / counter"), "shelving_metal": (shelving_metal, "Shelving"),
 "workbench": (workbench, "Workbench"), "car": (car, "Car"), "furnace": (furnace, "Furnace / WH"),
 "elec_panel": (elec_panel, None), "squat_rack": (squat_rack, "Squat rack"),
 "weight_bench": (weight_bench, None), "dumbbell_rack": (dumbbell_rack, "Dumbbells"),
 "treadmill": (treadmill, "Treadmill"), "cold_plunge": (cold_plunge, "Cold plunge"),
 "sauna_benches": (sauna_benches, "Benches"), "sauna_heater": (sauna_heater, "Heater"),
 "kids_table": (kids_table, "Kids table"), "toy_storage": (toy_storage, "Toys"), "beanbag": (beanbag, None),
 "tv_wall": (tv_wall, None), "outdoor_kitchen": (outdoor_kitchen, "Outdoor kitchen"),
 "outdoor_fireplace": (outdoor_fireplace, "Fireplace"), "outdoor_table": (outdoor_table, "Table"),
}


def _extent(parts):
    us = [p[0] for p in parts] + [p[0] + p[3] for p in parts]
    vs = [p[1] for p in parts] + [p[1] + p[4] for p in parts]
    return min(us), min(vs), max(us), max(vs)


def place(kind, x, y, facing, opts):
    """-> (boxes in world coords [(x,y,z,w,d,h,mat,collide)], footprint (x0,y0,x1,y1), label)."""
    fn, label = KINDS[kind]
    opts = dict(opts)
    label = opts.pop("label", label)
    import inspect
    sig = inspect.signature(fn).parameters if not kind == "dryer" else inspect.signature(washer).parameters
    W = opts.get("W", sig["W"].default)
    D = opts.get("D", sig["D"].default)
    parts = fn(**opts)
    out = []
    for u, v, z, pw, pd, h, mat, c in parts:
        if min(pw, pd, h) <= 1e-6:
            continue
        if facing == "N":
            X, Y, w, d = x + u, y + v, pw, pd
        elif facing == "S":
            X, Y, w, d = x + W - u - pw, y + D - v - pd, pw, pd
        elif facing == "E":
            X, Y, w, d = x + v, y + W - u - pw, pd, pw
        else:  # W
            X, Y, w, d = x + D - v - pd, y + u, pd, pw
        out.append((X, Y, z, w, d, h, mat, c))
    fw, fd = (W, D) if facing in "NS" else (D, W)
    return out, (x, y, x + fw, y + fd), label
