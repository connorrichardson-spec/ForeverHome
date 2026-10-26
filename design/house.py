"""ForeverHome — single source of truth for the house design (DRAFT v0).

Units: feet. x = east/west, y = south(front)/north(back). All rooms are
axis-aligned polygons given as (x0, y0, x1, y1) rectangles or point lists.
Everything else (plans, DXF, schedules, 3D walkthrough) is generated from here.
Edit this file, then run `python design/build.py`.
"""

LEVELS = {
    # name: (finished floor elevation, wall height)
    "basement": (-10.0, 9.0),
    "main": (0.0, 10.0),
    "upper": (11.0, 9.0),
}
FLOOR_T = 1.0          # floor system thickness (ft)
EXT_T, INT_T = 0.5, 0.33

# kind: indoor | outdoor ; win: normal | small | none | high
# paint: wall color (hex, or "wood:#hex"); floor: hardwood (default) | tile | concrete | rubber | cedar | pavers | subfloor
# unfinished=True: shell space (no trim, left out of finished sq ft)
# win_over: [(rect, dict(w,h,sill))] overrides auto windows that land inside rect
# stair="up": U-stair to the next level (both flights start/end at stair_line); "landing": arriving floor.
# floor_rect / ceil_rect limit the slab / ceiling to one rect (stair openings)
ROOMS = {
 "basement": [
  # Left unfinished to save cost: rough-in plumbing for the future bath, sauna circuit, egress window installed now.
  dict(name="Stair", rect=(24, 0, 34, 14), win="none", stair="up", stair_line=10.8,
       ceil_rect=(24, 10.8, 34, 14)),
  dict(name="Unfinished", paint="#d8d6d0", floor="concrete", unfinished=True, win="high",
       poly=[(0, 0), (24, 0), (24, 14), (34, 14), (34, 0), (56, 0), (56, 40), (0, 40)],
       note="Unfinished basement; future rooms shown as zones",
       zones=[("Future gym", (0, 0, 18, 24)), ("Mech / future sauna", (18, 0, 24, 14)),
              ("Future bath (rough-in)", (34, 0, 44, 14)), ("Future bedroom", (44, 0, 56, 14)),
              ("Storage / future rec room", (0, 24, 56, 40))],
       win_over=[((44, 0, 56, 0), dict(w=3.5, h=4.0, sill=2.5))]),
 ],
 "main": [
  dict(name="Office", paint="#4f5e53", rect=(0, 0, 14, 16)),
  dict(name="Foyer", poly=[(14, 0), (20.5, 0), (20.5, 3), (24, 3), (24, 16), (14, 16)]),
  dict(name="Foyer Closet", rect=(20.5, 0, 24, 3), win="none", note="Coat closet"),
  dict(name="Stair", rect=(24, 0, 34, 16), win="none", stair="up", stair_line=10.8,
       floor_rect=(24, 10.8, 34, 16), ceil_rect=(24, 10.8, 34, 16), note="5.2 ft walkway foyer <-> hall"),
  dict(name="Half Bath", floor="tile", paint="#2f4a5c", rect=(34, 0, 42, 8), win="small"),
  dict(name="Hall", rect=(34, 8, 42, 14), win="none"),
  dict(name="Mudroom", paint="#cfd9dc", rect=(42, 0, 56, 14), win="small"),
  dict(name="Pantry", paint="#f0ede6", rect=(44, 14, 56, 26), win="none", note="Walk-in"),
  dict(name="Great Room", label_at=(11, 30), poly=[(0, 16), (34, 16), (34, 14), (44, 14), (44, 26), (56, 26), (56, 40), (0, 40)],
       note="Open plan: living / dining / kitchen",
       zones=[("Living", (0, 16, 22, 40)), ("Dining", (22, 16, 44, 28)),
              ("Kitchen", (22, 28, 56, 40))],
       win_over=[((22, 28, 56, 40), dict(w=5.0, h=4.0, sill=3.6))]),
  dict(name="Garage", paint="#e8e6e0", floor="concrete", rect=(56, 0, 90, 26), win="garage", note="3-car + storage/workspace",
       zones=[("Storage / Workspace", (56, 19, 90, 26))]),
  dict(name="Patio", floor="pavers", rect=(22, 40, 56, 56), kind="outdoor",
       note="Open paver patio + fireplace; outdoor kitchen deferred (stub gas/power/water for later)"),
 ],
 "upper": [
  dict(name="Bedroom 2", paint="#c6d4de", poly=[(0, 0), (12, 0), (12, 14), (8.5, 14), (8.5, 11.5), (0, 11.5)],
       note="Teen room: queen, desk, dresser"),
  dict(name="Bed 2 Closet", paint="#c6d4de", rect=(0, 11.5, 8.5, 14), win="none", note="Reach-in, sliding doors"),
  dict(name="Bedroom 3", paint="#d9dfd6", poly=[(12, 0), (24, 0), (24, 11.5), (15.5, 11.5), (15.5, 14), (12, 14)],
       note="Teen room: queen, desk, dresser"),
  dict(name="Bed 3 Closet", paint="#d9dfd6", rect=(15.5, 11.5, 24, 14), win="none", note="Reach-in, sliding doors"),
  dict(name="Stair", rect=(24, 0, 34, 14), win="none", stair="landing", floor_rect=(24, 10.8, 34, 14)),
  dict(name="Bath 2 Tub/WC", floor="tile", paint="#eef0ee", rect=(34, 0, 44, 7), win="small",
       note="Toilet, tub/shower + separate shower behind a door"),
  dict(name="Bath 2", floor="tile", paint="#eef0ee", rect=(34, 7, 44, 14), win="none",
       note="Shared double vanity (Bedrooms 2-4); compartmented so two or three can use it at once"),
  dict(name="Laundry", floor="tile", paint="#d3dde0", rect=(44, 4, 56, 14), win="none"),
  dict(name="Linen", rect=(44, 0, 56, 4), win="none", note="Linen / storage, off the laundry"),
  dict(name="Upper Hall", rect=(0, 14, 56, 18.5), win="none", note="4.5 ft wide"),
  dict(name="Primary Bedroom", paint="#cfd5d0", rect=(0, 18.5, 18, 34.5)),
  dict(name="Primary Closet", paint="#ece7dd", rect=(18, 18.5, 34, 25.5), win="none", note="Galley walk-in"),
  dict(name="Primary Bath", floor="tile", paint="#e5e9e6",
       poly=[(18, 25.5), (34, 25.5), (34, 29.5), (30.5, 29.5), (30.5, 34.5), (18, 34.5)]),
  dict(name="Primary WC", floor="tile", paint="#e5e9e6", rect=(30.5, 29.5, 34, 34.5), win="none",
       note="Water closet"),
  dict(name="Bedroom 4", paint="#e3d7c5", rect=(38, 18.5, 56, 34.5)),
  dict(name="Bed 4 Closet", rect=(34, 18.5, 38, 34.5), win="none"),
 ],
}

# Doors between rooms: (level, room A, room B, kind). B=None -> exterior on side of A.
# Interior doors swing into room A.
# kinds: door | closet (sliding pair) | cased (wide opening) | patio | garage | none
# optional 5th item: dict(at=(x,y)) to force position, w= width, side="S|N|E|W" for exterior
DOORS = [
 ("basement", "Stair", "Unfinished", "cased", dict(at=(29, 14))),
 ("main", "Foyer", None, "door", dict(side="S", at=(17, 0))),
 ("main", "Garage", None, "door", dict(side="N", at=(71, 26))),
 ("main", "Office", "Foyer", "door"), ("main", "Foyer", "Stair", "cased", dict(at=(24, 13.4), w=4.5)),
 ("main", "Foyer", "Great Room", "cased"),
 ("main", "Foyer", "Foyer Closet", "door", dict(w=2.5)), ("main", "Stair", "Hall", "cased", dict(at=(34, 12.0), w=3.5)),
 ("main", "Half Bath", "Hall", "door"), ("main", "Hall", "Great Room", "cased"),
 ("main", "Hall", "Mudroom", "cased"),
 ("main", "Mudroom", "Garage", "door"), ("main", "Pantry", "Mudroom", "door"),
 ("main", "Pantry", "Great Room", "door"),
 ("main", "Great Room", "Patio", "patio"),
 ("upper", "Bedroom 2", "Upper Hall", "door", dict(at=(10.25, 14))),
 ("upper", "Bed 2 Closet", "Bedroom 2", "closet"),
 ("upper", "Bedroom 3", "Upper Hall", "door", dict(at=(13.75, 14))),
 ("upper", "Bed 3 Closet", "Bedroom 3", "closet"),
 ("upper", "Stair", "Upper Hall", "cased"), 
 ("upper", "Laundry", "Upper Hall", "door"), ("upper", "Laundry", "Linen", "door"),
 ("upper", "Bath 2", "Upper Hall", "door"), ("upper", "Bath 2", "Bath 2 Tub/WC", "door", dict(at=(37.5, 7), w=2.5)),
 ("upper", "Primary Bedroom", "Upper Hall", "door"),
 ("upper", "Primary Closet", "Primary Bedroom", "door", dict(at=(18, 22), w=2.5)),
 ("upper", "Primary Bedroom", "Primary Bath", "door"),
 ("upper", "Primary Bath", "Primary WC", "door", dict(w=2.5)),
 ("upper", "Primary Closet", "Primary Bath", "door"),
 ("upper", "Bedroom 4", "Upper Hall", "door"), ("upper", "Bedroom 4", "Bed 4 Closet", "door"),
 ]

# Garage overhead doors (centered x positions on the south wall)
GARAGE_DOORS = [62.5, 73.5, 84.5]

# Furniture, cabinets, appliances and plumbing fixtures (see furniture.py for kinds).
# (level, kind, x, y, facing, opts): x,y = footprint min corner; facing = direction the front points.
# E/W-facing pieces occupy D along x and W along y.
F_WALNUT = "wood:#6e4f37"
FURNITURE = [
 # ---------------- basement (unfinished: gym gear on mats, mechanical, storage)
 ("basement", "squat_rack", 5, 7, "S", {}),
 ("basement", "dumbbell_rack", 2, 22.1, "S", {}),
 ("basement", "weight_bench", 11, 9, "N", {}),
 ("basement", "treadmill", 10, 19.5, "E", {}),
 ("basement", "furnace", 18.3, 8.3, "N", {}),
 ("basement", "elec_panel", 23.4, 11, "W", {}),
 *[("basement", "shelving_metal", sx, 37.75, "S", dict(seed=sx)) for sx in (30, 36.5, 43, 49.5)],
 ("basement", "shelving_metal", 53.75, 24, "W", dict(seed=3)), ("basement", "shelving_metal", 53.75, 30.5, "W", dict(seed=4)),
 # ---------------- main: living
 ("main", "rug", 3.5, 22, "N", dict(W=13, D=12)),
 ("main", "fireplace", 0.3, 24.5, "E", {}),
 ("main", "sofa", 13, 23, "W", dict(W=10, D=3.3, label="Sofa")),
 ("main", "coffee_table", 8.5, 25.75, "W", dict(W=4.5, D=2.4)),
 ("main", "armchair", 4.6, 20.0, "N", {}), ("main", "armchair", 8.8, 20.0, "N", dict(color="fabric:#8a6f5a")),
 ("main", "side_table", 14.2, 21.3, "N", {}), ("main", "side_table", 14.2, 33.1, "N", {}),
 ("main", "floor_lamp", 2.6, 20.2, "N", {}),
 ("main", "plant", 0.4, 22.9, "N", {}), ("main", "plant", 20.0, 38.0, "N", {}),
 ("main", "console_table", 3, 16.25, "N", dict(W=6)),
 ("main", "art", 4, 16.2, "N", dict(W=4, color="fix:#c9a36b")),
 # dining
 ("main", "rug", 27, 17.5, "N", dict(W=12, D=9, color="fabric:#b9b0a1", border="fabric:#6e6457")),
 ("main", "dining_table", 29, 20.2, "N", {}),
 *[("main", "chair", cx, 18.8, "N", {}) for cx in (30.0, 32.2, 34.4)],
 *[("main", "chair", cx, 23.5, "S", {}) for cx in (30.0, 32.2, 34.4)],
 ("main", "chair", 27.4, 21.2, "E", {}), ("main", "chair", 36.9, 21.2, "W", {}),
 *[("main", "pendant", px, 21.3, "N", dict(z=6.8, ceil=10.0)) for px in (30.3, 32.3, 34.3)],
 ("main", "media_console", 23, 16.25, "N", dict(W=7, label="Buffet")),
 ("main", "art", 24.5, 16.2, "N", dict(W=4, z=4.8, color="fix:#5f7f8f")),
 # kitchen
 ("main", "fridge", 53.25, 26.5, "W", {}),
 ("main", "base_cab", 53.75, 29.5, "W", dict(W=4.0, sink=0.7, label="Sink")),
 ("main", "dishwasher", 53.75, 33.5, "W", {}),
 ("main", "base_cab", 53.75, 35.5, "W", dict(W=4.25, drawers=True)),
 ("main", "base_cab", 45.5, 37.75, "S", dict(W=2.25)),
 ("main", "range", 47.75, 37.55, "S", {}),
 ("main", "base_cab", 50.75, 37.75, "S", dict(W=3.0, drawers=True)),
 ("main", "hood", 47.5, 37.75, "S", {}),
 ("main", "upper_cab", 54.65, 35.75, "W", dict(W=4.0)),
 ("main", "upper_cab", 45.5, 38.65, "S", dict(W=2.0)),
 ("main", "upper_cab", 51.0, 38.65, "S", dict(W=3.65)),
 ("main", "island", 39, 29.25, "S", {}),
 *[("main", "stool", sx, 27.95, "N", {}) for sx in (40.0, 42.3, 44.6, 46.9)],
 *[("main", "pendant", px, 30.85, "N", dict(z=6.8, ceil=10.0)) for px in (40.8, 43.3, 45.8)],
 ("main", "base_cab", 24, 37.75, "S", dict(W=8, label="Coffee bar")),
 ("main", "upper_cab", 24.5, 38.65, "S", dict(W=7)),
 # pantry
 ("main", "base_cab", 44.2, 14.4, "E", dict(W=11.2, label="Pantry cabs")),
 ("main", "pantry_shelves", 44.2, 14.4, "E", dict(W=11.2, D=1.2, z0=4.2, label=None)),
 ("main", "tall_cab", 53.8, 14.4, "W", dict(W=5.0, H=9.6)),
 ("main", "base_cab", 53.8, 19.4, "W", dict(W=6.2, drawers=True, label="Pantry cabs")),
 ("main", "upper_cab", 54.7, 19.4, "W", dict(W=6.2, z=4.6, H=3.6)),
 # office
 ("main", "desk", 5, 4, "W", {}),
 ("main", "office_chair", 2.8, 5.75, "E", {}),
 *[("main", "bookcase", bx, 14.6, "S", dict(seed=bx)) for bx in (1, 5, 9)],
 ("main", "rug", 2, 3.5, "N", dict(W=8, D=6, color="fabric:#8c6a55", border="fabric:#4a3a30")),
 ("main", "plant", 12, 0.5, "N", {}),
 # foyer / half bath / hall / mudroom
 ("main", "bench", 14.2, 9, "E", {}),
 ("main", "art", 14.18, 9.5, "E", dict(W=3, color="fix:#a7745a")),
 ("main", "console_table", 14.2, 1.0, "E", {}),
 ("main", "closet_rod", 20.7, 0.3, "N", dict(W=3.1, D=2.0, seed=41, label="Coats")),
 ("main", "rug", 16, 2, "N", dict(W=5, D=8, color="fabric:#3e4a5c", border="fabric:#c9b98f")),
 ("main", "pendant", 18, 7, "N", dict(W=2, D=2, z=7.5, ceil=10.0)),
 ("main", "plant", 22.2, 7.0, "N", {}),
 ("main", "vanity", 34.2, 1.5, "E", dict(W=3, D=1.8)),
 ("main", "toilet", 39.4, 2, "W", {}),
 ("main", "rug", 35, 8.8, "N", dict(W=6, D=4.4, color="fabric:#b7a98f")),
 ("main", "wardrobe_wall", 42.2, 0.4, "E", dict(W=7, D=1.75, label="Lockers")),
 ("main", "mudroom_lockers", 45.55, 0.3, "N", dict(W=9.2, sections=4, open_section=1)),
 ("main", "rug", 47, 3.5, "N", dict(W=3, D=8, color="fabric:#5d5f61", border="fabric:#3a3b3c")),
 # garage
 ("main", "car", 59.35, 1.5, "S", {}),
 ("main", "car", 70.35, 1.5, "S", dict(color="gloss:#b8bcc0")),
 ("main", "workbench", 58, 23.25, "S", {}),
 ("main", "shelving_metal", 76, 23.6, "S", {}), ("main", "shelving_metal", 82, 23.6, "S", dict(seed=6)),
 # patio
 ("main", "outdoor_fireplace", 24, 53.6, "S", {}),
 ("main", "sofa", 25.5, 45, "N", dict(W=7, D=3.2, color="fabric:#cfc8b8", pillow="fabric:#3e6a7a")),
 ("main", "coffee_table", 27.2, 49, "N", dict(W=3.5, D=2, top="wood:#8c7058")),
 ("main", "outdoor_table", 39, 45.8, "N", {}),
 *[("main", "chair", cx, 44.3, "N", dict(seat="fabric:#d8d2c4", frame="metal:#2b2c2e")) for cx in (40.0, 41.7, 43.4)],
 *[("main", "chair", cx, 49.0, "S", dict(seat="fabric:#d8d2c4", frame="metal:#2b2c2e")) for cx in (40.0, 41.7, 43.4)],
 # ---------------- upper
 # bedrooms 2 + 3 (teen rooms, 12 ft wide): queen bed on the outside wall, desk under the window, dresser
 ("upper", "rug", 1.5, 3, "N", dict(W=8, D=7.5, color="fabric:#e7e3da", border="fabric:#8c9cab")),
 ("upper", "bed", 0.3, 4, "E", dict(W=5, D=6.7, throw="fabric:#6a86a3", label="Queen bed")),
 ("upper", "nightstand", 0.3, 9.2, "E", dict(W=1.6)),
 ("upper", "desk", 6.8, 0.3, "N", dict(W=4.5)), ("upper", "office_chair", 8.3, 2.9, "S", dict(color="fabric:#8a9aa8")),
 ("upper", "dresser", 10.05, 4.5, "W", dict(W=4.5)),
 ("upper", "closet_rod", 0.4, 12.6, "S", dict(W=7.8, D=1.2, seed=31)),
 ("upper", "rug", 14.5, 3, "N", dict(W=8, D=7.5, color="fabric:#d6c9b0", border="fabric:#8c6a55")),
 ("upper", "bed", 17.1, 4, "W", dict(W=5, D=6.7, frame="fabric:#7d8a7a", throw="fabric:#b39a7a", label="Queen bed")),
 ("upper", "nightstand", 22.3, 9.2, "W", dict(W=1.6)),
 ("upper", "desk", 12.7, 0.3, "N", dict(W=4.5)), ("upper", "office_chair", 14.2, 2.9, "S", dict(color="fabric:#8a9aa8")),
 ("upper", "dresser", 12.2, 4.5, "E", dict(W=4.5)),
 ("upper", "closet_rod", 15.9, 12.6, "S", dict(W=7.8, D=1.2, seed=33)),
 # bath 2: tub/shower, shower + toilet behind a door; double vanity outside it
 ("upper", "tub", 34.2, 0.3, "N", dict(shower_walls=True, label="Tub/shower")),
 ("upper", "shower", 39.5, 0.3, "N", dict(W=4.3, D=4.0, glass="F")),
 ("upper", "toilet", 34.2, 4.5, "E", {}),
 ("upper", "vanity", 42, 7.5, "W", dict(W=6, sinks=2)),
 ("upper", "rug", 37.5, 9.8, "N", dict(W=3.5, D=2.2, color="fabric:#d8dee2")),
 ("upper", "pantry_shelves", 44.5, 0.3, "N", dict(W=11, wood="gloss:#f2f0ea", label="Linen shelves", seed=8)),
 # laundry
 ("upper", "washer", 44.2, 5.5, "E", {}), ("upper", "dryer", 44.2, 7.9, "E", {}),
 ("upper", "upper_cab", 44.2, 5.3, "E", dict(W=5, z=5.0, H=2.5)),
 ("upper", "utility_sink", 53.75, 5, "W", {}),
 ("upper", "rug", 3, 14.75, "N", dict(W=20, D=3, color="fabric:#a49a8b", border="fabric:#5d564d")),
 ("upper", "rug", 34, 14.75, "N", dict(W=20, D=3, color="fabric:#a49a8b", border="fabric:#5d564d")),
 # primary suite (18x16 bedroom, 16x7 galley closet, 16x9 bath + WC)
 ("upper", "bed", 0.3, 23.25, "E", dict(W=6.5, D=7, frame="fabric:#5b6470", throw="fabric:#b39a7a", label="King bed")),
 ("upper", "nightstand", 0.3, 21.35, "E", {}), ("upper", "nightstand", 0.3, 29.85, "E", {}),
 ("upper", "bench", 7.5, 24.5, "E", dict(cushion="fabric:#b39a7a")),
 ("upper", "rug", 3, 21, "N", dict(W=10, D=11, color="fabric:#d9d3c7", border="fabric:#a39a8e")),
 ("upper", "armchair", 9.0, 31.25, "S", dict(color="fabric:#c7b79c")), ("upper", "armchair", 12.9, 31.25, "S", dict(color="fabric:#c7b79c")),
 ("upper", "media_console", 16.2, 21.5, "W", dict(W=6)),
 ("upper", "tv_wall", 17.68, 22.0, "W", dict(W=5)),
 ("upper", "wardrobe_wall", 18.3, 18.7, "N", dict(W=15.4)),
 ("upper", "wardrobe_wall", 18.3, 23.55, "S", dict(W=6, seed=21)),
 ("upper", "wardrobe_wall", 27.7, 23.55, "S", dict(W=6.1, seed=25)),
 ("upper", "pendant", 25.5, 21.5, "N", dict(z=6.6, ceil=9.0)),
 ("upper", "shower", 29.3, 25.7, "W", dict(W=3.6, D=4.5, glass="FR")),
 ("upper", "vanity", 18.3, 25.7, "N", dict(W=6, sinks=2)),
 ("upper", "tub", 21.75, 31.4, "S", dict(freestanding=True, label="Soaking tub")),
 ("upper", "toilet", 31.4, 31.2, "W", {}),
 ("upper", "rug", 23, 28.6, "N", dict(W=4, D=2.2, color="fabric:#d8dee2")),
 ("upper", "plant", 27.5, 33.6, "N", {}),
 # bedroom 4
 ("upper", "bed", 50.5, 18.7, "N", dict(W=5, D=7, throw="fabric:#a3786a")),
 ("upper", "nightstand", 48.8, 18.7, "N", dict(W=1.6)),
 ("upper", "dresser", 38.2, 29, "E", dict(W=5)),
 ("upper", "desk", 45, 31.75, "S", dict(W=4.5)),
 ("upper", "office_chair", 46.3, 29.7, "N", dict(color="fabric:#8a9aa8")),
 ("upper", "rug", 46.5, 22.5, "N", dict(W=9, D=7, color="fabric:#e7e3da")),
 ("upper", "closet_rod", 34.2, 19, "E", dict(W=15)),
 ]

# Roofs (see exterior.py). base = height of the roof's underside at the wall line (top of wall).
# gable: ridge along "x" or "y"; ends = which gable ends get a sided triangle (others die into a taller roof/wall).
# shed: low = side of the low eave. hip: all sides slope. ovh: overhang (ft), number or per-side dict.
# finish: shingle (charcoal architectural asphalt) | metal (black standing seam)
ROOFS = [
 dict(name="Main roof", kind="gable", rect=(0, 0, 56, 34.5), ridge="x", base=20.0, pitch=8 / 12,
      ovh=dict(S=1.5, N=1.5, W=1.0, E=0), ends="WE", finish="shingle"),
 dict(name="Garage roof", kind="gable", rect=(56, 0, 90, 26), ridge="x", base=10.0, pitch=8 / 12,
      ovh=dict(S=1.5, N=1.5, W=0, E=1.0), ends="E", finish="shingle",
      note="One-story; attic trusses for storage (pull-down stair from the garage)"),
 dict(name="Rear roof", kind="shed", rect=(0, 34.5, 56, 40), low="N", base=10.0, pitch=4 / 12,
      ovh=dict(N=1.5, W=1.0, E=1.0), ends="WE", finish="metal"),
 dict(name="Front porch roof", kind="gable", rect=(11, -7, 23, 0), ridge="y", base=9.0, pitch=8 / 12,
      ovh=dict(S=0.8, N=0, W=1.0, E=1.0), ends="S", finish="metal"),
]

# Site: paving (name, rect, material), porches (posts + beams + ceiling), lights (x, y, z, facing),
# chimneys (x0, y0, x1, y1, z0, z1), shrubs (x, y, r), trees (x, y, canopy r, trunk height)
SITE = dict(
 paving=[("street", (-60, -48, 156, -37), "fix:#3b3c3e"), ("sidewalk", (-60, -37, 156, -32), "concrete"),
         ("driveway", (57, -32, 89.5, 0), "concrete"), ("front walk", (15, -32, 19, -7), "concrete"),
         ("porch deck", (11, -7, 23, 0), "pavers")],
 porches=[dict(name="front porch", rect=(11, -7, 23, 0), beam_top=9.0, posts=[(11.35, -6.65), (22.65, -6.65)],
               open="SWE")],
 lights=[(14.7, -0.33, 5.4, "S"), (19.3, -0.33, 5.4, "S"), (68.0, -0.33, 8.2, "S"), (79.0, -0.33, 8.2, "S"),
         (73.0, 26.33, 6.8, "N"), (32.0, 40.25, 7.0, "N"), (46.5, 40.25, 7.0, "N")],
 chimneys=[(25.4, 54.0, 28.6, 55.6, 8.0, 15.5)],
 shrubs=[(2, -2.1, 1.3), (5.5, -2.3, 1.5), (9, -2.1, 1.3), (25.6, -2.1, 1.2), (28.6, -2.3, 1.5),
         (32, -2.1, 1.3), (36, -2.2, 1.2), (40, -2.3, 1.5), (44, -2.1, 1.3), (48, -2.2, 1.4), (52, -2.1, 1.2),
         (54.9, -2.0, 1.0), (-2.1, 18, 1.2), (-2.3, 30, 1.5), (-2.1, 38, 1.2)],
 trees=[(6, -22, 7, 8), (42, -24, 6, 7), (104, -8, 7, 9), (-16, 30, 8, 9), (78, 54, 8, 10), (108, 40, 7, 8)],
)
