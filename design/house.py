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
  # Left unfinished to save cost: rough-in plumbing for the future bath, sauna circuit. No windows (likely not
  # possible on the lot), so the future room can't be a legal bedroom without adding an egress window + well.
  dict(name="Stair", rect=(24, -3, 34, 14), win="none", stair="up", stair_line=10.8,
       ceil_rect=(24, 10.8, 34, 14)),
  dict(name="Unfinished", paint="#d8d6d0", floor="concrete", unfinished=True, win="none",
       poly=[(0, 0), (14, 0), (14, -3), (24, -3), (24, 14), (34, 14), (34, 0), (56, 0), (56, 40), (0, 40)],
       note="Unfinished basement; future rooms shown as zones",
       zones=[("Future gym", (0, 0, 18, 24)), ("Future sauna", (18, 0, 24, 14)),
              ("Future bath (rough-in)", (34, 0, 44, 14)), ("Mechanical", (44, 0, 56, 7)),
              ("Future flex room", (44, 7, 56, 20)),
              ("Storage / future rec room", (0, 24, 56, 40))]),
 ],
 "main": [
  dict(name="Office", paint="#4f5e53", rect=(0, 0, 14, 16)),
  dict(name="Foyer", poly=[(14, -3), (20.5, -3), (20.5, 0), (24, 0), (24, 16), (14, 16)],
       note="In the 3 ft entry bay under the front gable"),
  dict(name="Foyer Closet", rect=(20.5, -3, 24, 0), win="none", note="Coat closet"),
  dict(name="Stair", rect=(24, -3, 34, 16), stair="up", stair_line=10.8,
       floor_rect=(24, 10.8, 34, 16), ceil_rect=(24, 10.8, 34, 16), note="5.2 ft walkway foyer <-> hall; open to above",
       win_over=[((24, -3, 34, -3), dict(w=6.0, h=3.0, sill=6.5))]),
  dict(name="Main Bath", floor="tile", paint="#2f4a5c", rect=(34, 0, 42, 10), win="small",
       note="3/4 bath (shower, no tub) so the office can become a main-floor bedroom later"),
  dict(name="Hall", rect=(34, 10, 42, 16), win="none"),
  dict(name="Mudroom", paint="#cfd9dc", rect=(42, 0, 56, 16), win="small"),
  dict(name="Pantry", paint="#f0ede6", rect=(44, 16, 56, 26), win="none",
       note="Walk-in; south wall on the y=16 line that runs across the house"),
  dict(name="Great Room", label_at=(11, 30), poly=[(0, 16), (44, 16), (44, 26), (56, 26), (56, 40), (0, 40)],
       note="Open plan: living / dining / kitchen",
       zones=[("Living", (0, 16, 22, 40)), ("Dining", (22, 16, 44, 28)),
              ("Kitchen", (22, 28, 56, 40))],
       win_over=[((22, 28, 56, 40), dict(w=5.0, h=4.0, sill=3.6))]),
  dict(name="Garage", paint="#e8e6e0", floor="concrete", rect=(56, 0, 82, 30), note="3-car side-load + storage/workspace",
       zones=[("Storage / Workspace", (56, 14, 61, 30))]),
  dict(name="Patio", floor="pavers", rect=(22, 40, 56, 56), kind="outdoor",
       note="Open paver patio + fireplace; outdoor kitchen deferred (stub gas/power/water for later)"),
 ],
 "upper": [
  dict(name="Bedroom 2", paint="#c6d4de", rect=(0, 0, 12, 18), note="Teen room: queen, desk, dresser"),
  dict(name="Bed 2 Closet", paint="#c6d4de", rect=(0, 18, 8.5, 22.5), win="none",
       note="Walk-in in the old west end of the hall"),
  dict(name="Bedroom 3", paint="#d9dfd6",
       poly=[(12, 0), (14, 0), (14, -3), (24, -3), (24, 18), (12, 18)],
       note="Teen room: queen, desk (in the entry-bay nook), dresser"),
  dict(name="Bed 3 Closet", paint="#d9dfd6", rect=(24, 10.8, 29, 18), win="none",
       note="Walk-in on the west half of the stair landing (was beside the guard)"),
  dict(name="Stair", poly=[(24, -3), (34, -3), (34, 18), (29, 18), (29, 10.8), (24, 10.8)], stair="landing",
       floor_rect=(29, 10.8, 34, 18),
       note="Two-story stair hall; tall window stacked over the main-floor one",
       win_over=[((24, -3, 34, -3), dict(w=6.0, h=6.5, sill=1.0))]),
  dict(name="Bath 2 Tub/WC", floor="tile", paint="#eef0ee", win="small",
       poly=[(34, 0), (39.5, 0), (39.5, 3), (45.5, 3), (45.5, 8), (34, 8)],
       note="Toilet + tub/shower behind a door"),
  dict(name="Bath 2 Closet", paint="#eef0ee", rect=(39.5, 0, 45.5, 3), win="none",
       note="Linen/towel closet, sliding doors (where the separate shower was)"),
  dict(name="Bath 2", floor="tile", paint="#eef0ee", rect=(34, 8, 45.5, 18), win="none",
       note="Shared double vanity (Bedrooms 2-4); compartmented so two or three can use it at once"),
  dict(name="Laundry", floor="tile", paint="#d3dde0", rect=(45.5, 4, 56, 18), win="none", note="10.5x14"),
  dict(name="Linen", rect=(45.5, 0, 56, 4), win="none", note="Linen / storage, off the laundry"),
  dict(name="Upper Hall", rect=(8.5, 18, 48.5, 22.5), win="none", note="4.5 ft wide; ends at the last doors"),
  dict(name="Primary Bedroom", paint="#cfd5d0", rect=(0, 22.5, 20, 40), note="20x17.5, sitting area at the rear windows; dresser + TV centered on the bed"),
  dict(name="Primary Bath", floor="tile", paint="#e5e9e6",
       poly=[(20, 22.5), (26.5, 22.5), (26.5, 27.5), (31, 27.5), (31, 40), (20, 40)]),
  dict(name="Primary WC", floor="tile", paint="#e5e9e6", rect=(26.5, 22.5, 31, 27.5), win="none",
       note="Water closet"),
  dict(name="Primary Closet", paint="#ece7dd", rect=(31, 22.5, 42, 40), win="none", note="Walk-in, center island"),
  dict(name="Bedroom 4", paint="#e3d7c5", rect=(42, 22.5, 56, 40)),
  dict(name="Bed 4 Closet", paint="#e3d7c5", rect=(48.5, 18, 56, 22.5), win="none",
       note="Walk-in in the old east end of the hall"),
 ],
}

# Doors between rooms: (level, room A, room B, kind). B=None -> exterior on side of A.
# Interior doors swing into room A.
# kinds: door | closet (sliding pair) | cased (wide opening) | patio | garage | none
# optional 5th item: dict(at=(x,y)) to force position, w= width, side="S|N|E|W" for exterior
DOORS = [
 ("basement", "Stair", "Unfinished", "cased", dict(at=(29, 14))),
 ("main", "Foyer", None, "door", dict(side="S", at=(17.25, -3))),
 ("main", "Garage", None, "door", dict(side="N", at=(69, 30))),
 ("main", "Office", "Foyer", "door"), ("main", "Foyer", "Stair", "cased", dict(at=(24, 13.4), w=4.5)),
 ("main", "Foyer", "Great Room", "cased"),
 ("main", "Foyer", "Foyer Closet", "door", dict(w=2.5)), ("main", "Stair", "Hall", "cased", dict(at=(34, 12.4), w=3.0)),
 ("main", "Main Bath", "Hall", "door", dict(at=(36, 10), w=2.5)), ("main", "Hall", "Great Room", "cased"),
 ("main", "Hall", "Mudroom", "cased"),
 ("main", "Mudroom", "Garage", "door"), ("main", "Pantry", "Mudroom", "door"),
 ("main", "Pantry", "Great Room", "door"),
 ("main", "Great Room", "Patio", "patio"),
 ("upper", "Bedroom 2", "Upper Hall", "door", dict(at=(10.25, 18))),
 ("upper", "Bed 2 Closet", "Bedroom 2", "door", dict(at=(4.25, 18), w=2.5)),
 ("upper", "Bedroom 3", "Upper Hall", "door", dict(at=(13.75, 18))),
 ("upper", "Bed 3 Closet", "Bedroom 3", "door", dict(at=(24, 16.5), w=2.5)),
 ("upper", "Stair", "Upper Hall", "cased"), 
 ("upper", "Laundry", "Upper Hall", "door", dict(at=(47, 18), w=2.5)), ("upper", "Laundry", "Linen", "door"),
 ("upper", "Bath 2", "Upper Hall", "door", dict(at=(35.75, 18))), ("upper", "Bath 2", "Bath 2 Tub/WC", "door", dict(at=(37.5, 8), w=2.5)),
 ("upper", "Bath 2 Closet", "Bath 2 Tub/WC", "closet"),
 ("upper", "Primary Bedroom", "Upper Hall", "door", dict(at=(12, 22.5))),
 ("upper", "Primary Bedroom", "Primary Bath", "door", dict(at=(20, 38))),
 ("upper", "Primary Bath", "Primary WC", "door", dict(at=(28.75, 27.5), w=2.5)),
 ("upper", "Primary Closet", "Primary Bath", "door", dict(at=(31, 30.5), w=2.5)),
 ("upper", "Bedroom 4", "Upper Hall", "door", dict(at=(47, 22.5))), ("upper", "Bed 4 Closet", "Bedroom 4", "door", dict(at=(52.25, 22.5), w=2.5)),
 ]

# Garage overhead doors: (wall side, center position along that wall, width)
GARAGE_DOORS = [("E", 9.75, 16.0), ("E", 23.75, 9.0)]

# Furniture, cabinets, appliances and plumbing fixtures (see furniture.py for kinds).
# (level, kind, x, y, facing, opts): x,y = footprint min corner; facing = direction the front points.
# E/W-facing pieces occupy D along x and W along y.
F_WALNUT = "wood:#6e4f37"
FURNITURE = [
 # ---------------- basement (unfinished: gym gear on mats, rack on the west wall, mechanical, storage)
 ("basement", "squat_rack", 1.8, 8, "E", {}),
 ("basement", "dumbbell_rack", 0.3, 15.5, "E", {}),       # mirror on the west wall, beside the rack
 ("basement", "weight_bench", 3.8, 17.8, "E", {}),
 # mechanical grouped in the SE corner (garage side): furnace + water heater on the south wall, panel on the east
 ("basement", "furnace", 50.6, 0.3, "N", {}),
 ("basement", "water_heater", 53.9, 0.3, "N", {}),
 ("basement", "elec_panel", 55.4, 3.8, "W", {}),
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
 # 9.5 ft table running north-south, centered in the open floor between the sofa and the island; seats 10
 ("main", "rug", 23, 21, "N", dict(W=9, D=12, color="fabric:#b9b0a1", border="fabric:#6e6457")),
 ("main", "dining_table", 25.7, 22.25, "E", dict(W=9.5)),
 *[("main", "chair", 24.3, cy, "E", {}) for cy in (22.9, 25.1, 27.3, 29.5)],
 *[("main", "chair", 29.0, cy, "W", {}) for cy in (22.9, 25.1, 27.3, 29.5)],
 ("main", "chair", 26.7, 20.85, "N", {}), ("main", "chair", 26.7, 31.45, "S", {}),
 *[("main", "pendant", 26.8, py, "N", dict(z=6.8, ceil=10.0)) for py in (24.3, 26.3, 28.3)],
 ("main", "media_console", 23, 16.25, "N", dict(W=7, label="Buffet")),
 ("main", "art", 24.5, 16.2, "N", dict(W=4, z=4.8, color="fix:#5f7f8f")),
 # kitchen
 ("main", "fridge", 53.25, 26.5, "W", {}),
 ("main", "dishwasher", 53.75, 29.5, "W", {}),
 ("main", "base_cab", 53.75, 31.5, "W", dict(W=1.5, drawers=True)),
 ("main", "base_cab", 53.75, 33.0, "W", dict(W=4.0, sink=0.7, label="Sink")),
 ("main", "base_cab", 53.75, 37.0, "W", dict(W=2.75, drawers=True)),
 ("main", "base_cab", 45.5, 37.75, "S", dict(W=2.25)),
 ("main", "range", 47.75, 37.55, "S", {}),
 ("main", "base_cab", 50.75, 37.75, "S", dict(W=3.0, drawers=True)),
 ("main", "hood", 47.5, 37.75, "S", {}),
 ("main", "upper_cab", 54.65, 29.5, "W", dict(W=2.9)), ("main", "upper_cab", 54.65, 37.6, "W", dict(W=2.15)),
 ("main", "upper_cab", 45.5, 38.65, "S", dict(W=2.0)),
 ("main", "upper_cab", 51.0, 38.65, "S", dict(W=3.65)),
 ("main", "island", 39, 29.25, "S", {}),
 *[("main", "stool", sx, 27.95, "N", {}) for sx in (40.0, 42.3, 44.6, 46.9)],
 *[("main", "pendant", px, 30.85, "N", dict(z=6.8, ceil=10.0)) for px in (40.8, 43.3, 45.8)],
 ("main", "base_cab", 24, 37.75, "S", dict(W=8, label="Coffee bar")),
 ("main", "upper_cab", 24.5, 38.65, "S", dict(W=7)),
 # bar on the pantry's west wall: 8 ft counter (no sink), open bottle shelves above
 ("main", "base_cab", 41.8, 17, "W", dict(W=8, label="Bar")),
 ("main", "pantry_shelves", 42.7, 17, "W", dict(W=8, D=1.1, H=8.0, z0=4.6, wood="wood:#6e4f37", seed=12, label=None)),
 # pantry
 ("main", "base_cab", 44.2, 16.4, "E", dict(W=9.2, label="Pantry cabs")),
 ("main", "pantry_shelves", 44.2, 16.4, "E", dict(W=9.2, D=1.2, z0=4.2, label=None)),
 ("main", "tall_cab", 53.8, 16.4, "W", dict(W=5.0, H=9.6)),
 ("main", "base_cab", 53.8, 21.4, "W", dict(W=4.2, drawers=True, label="Pantry cabs")),
 ("main", "upper_cab", 54.7, 21.4, "W", dict(W=4.2, z=4.6, H=3.6)),
 # office
 ("main", "desk", 5, 4, "W", {}),
 ("main", "office_chair", 2.8, 5.75, "E", {}),
 *[("main", "bookcase", bx, 14.6, "S", dict(seed=bx)) for bx in (1, 5, 9)],
 ("main", "rug", 2, 3.5, "N", dict(W=8, D=6, color="fabric:#8c6a55", border="fabric:#4a3a30")),
 ("main", "plant", 12, 0.5, "N", {}),
 # foyer / main bath (3/4) / hall / mudroom
 ("main", "bench", 14.2, 10, "E", {}),
 ("main", "art", 14.18, 10.5, "E", dict(W=3, color="fix:#a7745a")),
 ("main", "console_table", 14.2, -2.0, "E", {}),
 ("main", "closet_rod", 20.7, -2.7, "N", dict(W=3.1, D=2.0, seed=41, label="Coats")),
 ("main", "rug", 15.5, -1.5, "N", dict(W=5, D=8, color="fabric:#3e4a5c", border="fabric:#c9b98f")),
 ("main", "pendant", 17, 3, "N", dict(W=2, D=2, z=7.5, ceil=10.0)),
 ("main", "plant", 22.2, 7.0, "N", {}),
 ("main", "vanity", 34.2, 1.0, "E", dict(W=4, D=1.8)),
 ("main", "toilet", 39.4, 0.6, "W", {}),
 ("main", "shower", 38.2, 5.3, "W", dict(W=4.5, D=3.6, glass="F")),
 ("main", "rug", 35, 10.8, "N", dict(W=6, D=4.4, color="fabric:#b7a98f")),
 ("main", "wardrobe_wall", 42.2, 0.4, "E", dict(W=7, D=1.75, label="Lockers")),
 ("main", "mudroom_lockers", 45.55, 0.3, "N", dict(W=9.2, sections=4, open_section=1)),
 ("main", "rug", 47, 3.5, "N", dict(W=3, D=8, color="fabric:#5d5f61", border="fabric:#3a3b3c")),
 # garage (side-load: cars pull in from the east)
 ("main", "car", 62.5, 2.8, "W", {}),
 ("main", "car", 62.5, 10.4, "W", dict(color="gloss:#b8bcc0")),
 ("main", "shelving_metal", 56.2, 15, "E", {}),
 ("main", "workbench", 56.2, 21.5, "E", {}),
 # patio
 ("main", "outdoor_fireplace", 24, 53.6, "S", {}),
 ("main", "sofa", 25.5, 45, "N", dict(W=7, D=3.2, color="fabric:#cfc8b8", pillow="fabric:#3e6a7a")),
 ("main", "coffee_table", 27.2, 49, "N", dict(W=3.5, D=2, top="wood:#8c7058")),
 ("main", "outdoor_table", 39, 45.8, "N", {}),
 *[("main", "chair", cx, 44.3, "N", dict(seat="fabric:#d8d2c4", frame="metal:#2b2c2e")) for cx in (40.0, 41.7, 43.4)],
 *[("main", "chair", cx, 49.0, "S", dict(seat="fabric:#d8d2c4", frame="metal:#2b2c2e")) for cx in (40.0, 41.7, 43.4)],
 # ---------------- upper
 # bedrooms 2 + 3 (teen rooms, 12 ft wide): queen bed on the outside wall, desk under the window, dresser
 ("upper", "rug", 1.5, 4, "N", dict(W=8, D=9, color="fabric:#e7e3da", border="fabric:#8c9cab")),
 ("upper", "bed", 0.3, 5.75, "E", dict(W=5, D=6.7, throw="fabric:#6a86a3", label="Queen bed")),
 ("upper", "nightstand", 0.3, 10.95, "E", dict(W=1.6)),
 ("upper", "desk", 6.8, 0.3, "N", dict(W=4.5)), ("upper", "office_chair", 8.3, 2.9, "S", dict(color="fabric:#8a9aa8")),
 ("upper", "dresser", 10.05, 6.5, "W", dict(W=4.5)),
 ("upper", "closet_rod", 0.2, 21.1, "S", dict(W=8.1, D=1.2, seed=31)),
 ("upper", "rug", 14.5, 4, "N", dict(W=8, D=9, color="fabric:#d6c9b0", border="fabric:#8c6a55")),
 ("upper", "bed", 17.1, 5.75, "W", dict(W=5, D=6.7, frame="fabric:#7d8a7a", throw="fabric:#b39a7a", label="Queen bed")),
 ("upper", "nightstand", 22.3, 10.95, "W", dict(W=1.6)),
 ("upper", "desk", 15, -2.7, "N", dict(W=4.5)), ("upper", "office_chair", 16.5, -0.1, "S", dict(color="fabric:#8a9aa8")),
 ("upper", "dresser", 12.2, 6.5, "E", dict(W=4.5)),
 ("upper", "closet_rod", 24.2, 11.0, "N", dict(W=4.6, D=1.2, seed=33)),
 ("upper", "closet_rod", 27.6, 12.3, "W", dict(W=5.5, D=1.2, seed=34)),
 # bath 2: tub/shower + toilet behind a door, linen closet in the old shower spot; double vanity outside it
 ("upper", "tub", 34.2, 0.3, "N", dict(shower_walls=True, label="Tub/shower")),
 ("upper", "pantry_shelves", 39.8, 0.3, "N", dict(W=5.4, D=2.0, wood="gloss:#f2f0ea", label="Towels / linen", seed=9)),
 ("upper", "toilet", 34.2, 4.5, "E", {}),
 ("upper", "vanity", 43.5, 9.5, "W", dict(W=7, sinks=2)),
 ("upper", "rug", 37.5, 11.5, "N", dict(W=3.5, D=2.2, color="fabric:#d8dee2")),
 ("upper", "pantry_shelves", 46.0, 0.3, "N", dict(W=9.5, wood="gloss:#f2f0ea", label="Linen shelves", seed=8)),
 # laundry
 ("upper", "washer", 45.7, 5.5, "E", {}), ("upper", "dryer", 45.7, 7.9, "E", {}),
 ("upper", "upper_cab", 45.7, 5.3, "E", dict(W=5, z=5.0, H=2.5)),
 ("upper", "utility_sink", 53.75, 5, "W", {}),
 ("upper", "rug", 10, 18.75, "N", dict(W=13, D=3, color="fabric:#a49a8b", border="fabric:#5d564d")),
 ("upper", "rug", 34, 18.75, "N", dict(W=13, D=3, color="fabric:#a49a8b", border="fabric:#5d564d")),
 # primary bedroom (20x17.5): king on the west wall, sitting area at the rear windows
 ("upper", "bed", 0.3, 26.5, "E", dict(W=6.5, D=7, frame="fabric:#5b6470", throw="fabric:#b39a7a", label="King bed")),
 ("upper", "nightstand", 0.3, 24.6, "E", {}), ("upper", "nightstand", 0.3, 33.1, "E", {}),
 ("upper", "bench", 7.5, 27.75, "E", dict(cushion="fabric:#b39a7a")),
 ("upper", "rug", 3, 24.75, "N", dict(W=10, D=10, color="fabric:#d9d3c7", border="fabric:#a39a8e")),
 ("upper", "armchair", 10.0, 36.75, "S", dict(color="fabric:#c7b79c")), ("upper", "armchair", 13.9, 36.75, "S", dict(color="fabric:#c7b79c")),
 ("upper", "dresser", 18.05, 26.75, "W", dict(W=6)),                       # centered on the bed (y 29.75)
 ("upper", "tv_wall", 19.68, 27.25, "W", dict(W=5, z=4.2)),
 # primary bath (11x17.5 + WC; no tub, the bedroom door is where it was)
 ("upper", "vanity", 20.3, 22.7, "N", dict(W=6, sinks=2)),
 ("upper", "toilet", 28.0, 22.7, "N", {}),
 ("upper", "shower", 26.5, 35.3, "W", dict(W=4.5, D=4.3, glass="FR")),
 ("upper", "rug", 22.5, 30.5, "N", dict(W=4, D=2.2, color="fabric:#d8dee2")),
 ("upper", "plant", 20.4, 34.5, "N", {}),
 # primary closet (11x17.5, center island)
 ("upper", "wardrobe_wall", 31.3, 22.7, "N", dict(W=10.4)),
 ("upper", "wardrobe_wall", 31.3, 38.05, "S", dict(W=10.4, seed=21)),
 ("upper", "wardrobe_wall", 40.085, 24.6, "W", dict(W=13.3, seed=17)),
 ("upper", "closet_island", 34.3, 28.75, "E", dict(W=5)),
 ("upper", "pendant", 34.85, 30.55, "N", dict(z=6.6, ceil=9.0)),
 # bedroom 4 (14x17.5 + walk-in off its south wall)
 ("upper", "bed", 42.3, 28.75, "E", dict(W=5, D=7, throw="fabric:#a3786a")),
 ("upper", "nightstand", 42.3, 27.05, "E", dict(W=1.6)), ("upper", "nightstand", 42.3, 33.85, "E", dict(W=1.6)),
 ("upper", "dresser", 54.05, 24.8, "W", dict(W=5)),
 ("upper", "desk", 50.5, 37.25, "S", dict(W=4.5)),
 ("upper", "office_chair", 51.8, 35.2, "N", dict(color="fabric:#8a9aa8")),
 ("upper", "rug", 45.5, 27.25, "N", dict(W=8, D=8, color="fabric:#e7e3da")),
 ("upper", "closet_rod", 48.7, 18.2, "N", dict(W=7.1, D=1.2)),
 ]

# Roofs (see exterior.py). base = height of the roof's underside at the wall line (top of wall).
# gable: ridge along "x" or "y"; ends = which gable ends get a sided triangle (others die into a taller roof/wall).
# shed: low = side of the low eave. hip: all sides slope. ovh: overhang (ft), number or per-side dict.
# finish: shingle (charcoal architectural asphalt) | metal (black standing seam)
ROOFS = [
 # main gable in three coplanar pieces so the middle one can stop at the entry bay
 dict(name="Main roof W", kind="gable", rect=(0, 0, 14, 40), ridge="x", base=20.0, pitch=8 / 12,
      ovh=dict(S=1.5, N=1.5, W=1.0, E=0), ends="W", finish="shingle"),
 dict(name="Main roof C", kind="gable", rect=(14, 0, 34, 40), ridge="x", base=20.0, pitch=8 / 12,
      ovh=dict(S=0, N=1.5, W=0, E=0), ends="", finish="shingle"),
 dict(name="Main roof E", kind="gable", rect=(34, 0, 56, 40), ridge="x", base=20.0, pitch=8 / 12,
      ovh=dict(S=1.5, N=1.5, W=0, E=0), ends="E", finish="shingle"),
 # entry gable in two coplanar pieces: side overhangs only over the bay, none inside the main block
 dict(name="Entry gable", kind="gable", rect=(14, -3, 34, 0), ridge="y", base=20.0, pitch=8 / 12,
      ovh=dict(S=1.0, N=0, W=0.5, E=0.5), ends="S", finish="shingle",
      note="Front-facing gable over the entry bay; ridge dies into the main roof"),
 dict(name="Entry gable back", kind="gable", rect=(14, 0, 34, 10), ridge="y", base=20.0, pitch=8 / 12,
      ovh=0, ends="", finish="shingle", label=False),
 dict(name="Garage roof", kind="gable", rect=(56, 0, 82, 30), ridge="x", base=10.0, pitch=8 / 12,
      ovh=dict(S=1.5, N=1.5, W=0, E=1.0), ends="E", finish="shingle",
      note="One-story side-load garage; gable end over the doors; attic-truss storage"),
 # full-width front porch: one 4:12 shed plane, split around the entry bay
 dict(name="Porch roof W", kind="shed", rect=(0, -10, 14, 0), low="S", base=9.0, pitch=4 / 12,
      ovh=dict(S=1.0, W=1.0), ends="", finish="metal"),
 dict(name="Porch roof C", kind="shed", rect=(14, -10, 34, -3), low="S", base=9.0, pitch=4 / 12,
      ovh=dict(S=1.0), ends="", finish="metal"),
 dict(name="Porch roof E", kind="shed", rect=(34, -10, 56, 0), low="S", base=9.0, pitch=4 / 12,
      ovh=dict(S=1.0, E=1.0), ends="", finish="metal"),
]

# Site: paving (name, rect, material), porches (posts + beams + ceiling), lights (x, y, z, facing),
# chimneys (x0, y0, x1, y1, z0, z1), shrubs (x, y, r), trees (x, y, canopy r, trunk height)
SITE = dict(
 paving=[("street", (-60, -48, 156, -37), "fix:#3b3c3e"), ("sidewalk", (-60, -37, 156, -32), "concrete"),
         ("driveway", (84, -32, 96, 0), "concrete"), ("garage court", (82, 0, 112, 32), "concrete"),
         ("front walk", (15.25, -32, 19.25, -10), "concrete"), ("porch deck", (0, -10, 56, 0), "wood:#8c7058")],
 porches=[dict(name="front porch W", rect=(0, -10, 14, 0), beam_top=9.0, posts=[(0.35, -9.65), (11.5, -9.65)], open="SW"),
          dict(name="front porch C", rect=(14, -10, 34, -3), beam_top=9.0, posts=[(23.5, -9.65)], open="S"),
          dict(name="front porch E", rect=(34, -10, 56, 0), beam_top=9.0,
               posts=[(34.5, -9.65), (45, -9.65), (55.65, -9.65)], open="SE")],
 lights=[(15.0, -3.33, 5.4, "S"), (19.5, -3.33, 5.4, "S"), (82.33, 0.9, 8.2, "E"), (82.33, 18.5, 8.2, "E"),
         (82.33, 29.1, 8.2, "E"), (71.0, 30.33, 6.8, "N"), (32.0, 40.25, 7.0, "N"), (46.5, 40.25, 7.0, "N")],
 chimneys=[(25.4, 54.0, 28.6, 55.6, 8.0, 15.5)],
 shrubs=[*[(x, -11.4, 1.2 + 0.3 * (i % 2)) for i, x in enumerate((2, 5.5, 9, 12.3, 22, 25.5, 29, 32.5, 36, 39.5,
                                                                   43, 46.5, 50, 53.5))],
         *[(x, -2.1, 1.1 + 0.3 * (i % 2)) for i, x in enumerate((58.5, 62, 65.5, 69, 72.5, 76, 79.5))],
         (-2.1, 18, 1.2), (-2.3, 30, 1.5), (-2.1, 38, 1.2)],
 trees=[(6, -22, 7, 8), (42, -24, 6, 7), (122, -12, 7, 9), (-16, 30, 8, 9), (78, 54, 8, 10), (118, 44, 7, 8)],
)
