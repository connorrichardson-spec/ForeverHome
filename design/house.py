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
# paint: wall color (hex, or "wood:#hex"); floor: hardwood (default) | tile | concrete | rubber | cedar | pavers
# win_over: [(rect, dict(w,h,sill))] overrides auto windows that land inside rect
# stair="up": U-stair to the next level (both flights start/end at stair_line); "landing": arriving floor.
# floor_rect / ceil_rect limit the slab / ceiling to one rect (stair openings)
ROOMS = {
 "basement": [
  dict(name="Gym", paint="#6e7378", floor="rubber", rect=(0, 0, 22, 22), win="high",
       note="Squat rack, cold plunge, sauna access"),
  dict(name="Sauna", paint="wood:#c48a57", floor="cedar", rect=(22, 0, 28, 8), win="none"),
  dict(name="Mechanical", paint="#e8e6e0", floor="concrete", rect=(22, 8, 28, 14), win="none"),
  dict(name="Stair", rect=(28, 0, 38, 14), win="none", stair="up", stair_line=10.8,
       ceil_rect=(28, 10.8, 38, 14)),
  dict(name="Bsmt Hall", rect=(22, 14, 60, 22), win="none"),
  dict(name="Bsmt Bath", floor="tile", paint="#e9ece8", rect=(38, 0, 48, 10), win="small", note="Full bath"),
  dict(name="Bsmt Closet", rect=(38, 10, 48, 14), win="none"),
  dict(name="Bsmt Bedroom", paint="#d9d2c4", rect=(48, 0, 60, 14), win="egress", note="Egress window required"),
  dict(name="Play Area", paint="#f0dfb4", rect=(28, 22, 48, 38), win="high"),
  dict(name="Storage", paint="#ece9e2", rect=(48, 22, 60, 38), win="none"),
 ],
 "main": [
  dict(name="Office", paint="#4f5e53", rect=(0, 0, 14, 14)),
  dict(name="Foyer", rect=(14, 0, 28, 14)),
  dict(name="Stair", rect=(28, 0, 38, 14), win="none", stair="up", stair_line=10.8,
       floor_rect=(28, 10.8, 38, 14), ceil_rect=(28, 10.8, 38, 14)),
  dict(name="Half Bath", floor="tile", paint="#2f4a5c", rect=(38, 0, 46, 8), win="small"),
  dict(name="Hall", rect=(38, 8, 46, 14), win="none"),
  dict(name="Mudroom", paint="#cfd9dc", rect=(46, 0, 60, 14), win="small"),
  dict(name="Pantry", paint="#f0ede6", rect=(48, 14, 60, 26), win="none", note="Walk-in"),
  dict(name="Great Room", poly=[(0, 14), (48, 14), (48, 26), (60, 26), (60, 46), (0, 46)],
       note="Open plan: living / dining / kitchen",
       zones=[("Living", (0, 14, 26, 46)), ("Dining", (26, 14, 48, 30)),
              ("Kitchen", (26, 30, 60, 46))],
       win_over=[((26, 30, 60, 46), dict(w=5.0, h=4.0, sill=3.6))]),
  dict(name="Garage", paint="#e8e6e0", floor="concrete", rect=(60, 0, 94, 26), win="garage", note="3-car + storage/workspace",
       zones=[("Storage / Workspace", (60, 19, 94, 26))]),
  dict(name="Covered Patio", floor="pavers", rect=(26, 46, 60, 62), kind="outdoor",
       note="Outdoor kitchen + fireplace"),
 ],
 "upper": [
  dict(name="Bedroom 2", paint="#c6d4de", rect=(0, 0, 14, 14)),
  dict(name="Bedroom 3", paint="#ccd6c3", rect=(14, 0, 28, 14)),
  dict(name="Stair", rect=(28, 0, 38, 14), win="none", stair="landing", floor_rect=(28, 10.8, 38, 14)),
  dict(name="Bath 2", floor="tile", paint="#eef0ee", rect=(38, 4, 48, 14), win="small", note="Shared by bedrooms 2-4"),
  dict(name="Linen", rect=(38, 0, 48, 4), win="none"),
  dict(name="Laundry", floor="tile", paint="#d3dde0", rect=(48, 4, 60, 14)),
  dict(name="Storage Closet", rect=(48, 0, 60, 4), win="none"),
  dict(name="Upper Hall", rect=(0, 14, 60, 18), win="none"),
  dict(name="Primary Bedroom", paint="#cfd5d0", rect=(0, 18, 22, 40)),
  dict(name="Primary Closet", paint="#ece7dd", rect=(22, 18, 38, 30), win="small", note="Center island"),
  dict(name="Primary Bath", floor="tile", paint="#e5e9e6", rect=(22, 30, 38, 40)),
  dict(name="Bedroom 4", paint="#e3d7c5", rect=(42, 18, 60, 34)),
  dict(name="Bed 4 Closet", rect=(38, 18, 42, 34), win="none"),
 ],
}

# Doors between rooms: (level, room A, room B, kind). B=None -> exterior on side of A.
# Interior doors swing into room A.
# kinds: door | cased (wide opening) | patio | garage | none
# optional 5th item: dict(at=(x,y)) to force position, w= width, side="S|N|E|W" for exterior
DOORS = [
 ("basement", "Gym", "Sauna", "door"), ("basement", "Gym", "Bsmt Hall", "door"),
 ("basement", "Mechanical", "Bsmt Hall", "door"), ("basement", "Stair", "Bsmt Hall", "cased"),
 ("basement", "Bsmt Hall", "Bsmt Closet", "door"),
 ("basement", "Bsmt Bedroom", "Bsmt Hall", "door", dict(at=(57.5, 14))), ("basement", "Bsmt Bedroom", "Bsmt Bath", "door"),
 ("basement", "Play Area", "Bsmt Hall", "cased"), ("basement", "Storage", "Bsmt Hall", "door"),
 ("main", "Foyer", None, "door", dict(side="S")),
 ("main", "Garage", None, "door", dict(side="N", at=(75, 26))),
 ("main", "Office", "Foyer", "door"), ("main", "Foyer", "Stair", "cased", dict(at=(28, 12.4), w=3.0)),
 ("main", "Foyer", "Great Room", "cased"), ("main", "Stair", "Hall", "cased", dict(at=(38, 12.4), w=3.0)),
 ("main", "Half Bath", "Hall", "door"), ("main", "Hall", "Great Room", "cased"),
 ("main", "Hall", "Mudroom", "cased"),
 ("main", "Mudroom", "Garage", "door"), ("main", "Mudroom", "Pantry", "cased"),
 ("main", "Pantry", "Great Room", "cased"),
 ("main", "Great Room", "Covered Patio", "patio"),
 ("upper", "Bedroom 2", "Upper Hall", "door"), ("upper", "Bedroom 3", "Upper Hall", "door"),
 ("upper", "Stair", "Upper Hall", "cased"), ("upper", "Bath 2", "Linen", "door"),
 ("upper", "Laundry", "Upper Hall", "door"), ("upper", "Laundry", "Storage Closet", "door"),
 ("upper", "Bath 2", "Upper Hall", "door"),
 ("upper", "Primary Bedroom", "Upper Hall", "door"),
 ("upper", "Primary Closet", "Primary Bedroom", "door"),
 ("upper", "Primary Bath", "Primary Bedroom", "door"),
 ("upper", "Primary Closet", "Primary Bath", "door"),
 ("upper", "Bedroom 4", "Upper Hall", "door"), ("upper", "Bedroom 4", "Bed 4 Closet", "door"),
]

# Garage overhead doors (centered x positions on the south wall)
GARAGE_DOORS = [66.5, 77.5, 88.5]

# Furniture, cabinets, appliances and plumbing fixtures (see furniture.py for kinds).
# (level, kind, x, y, facing, opts): x,y = footprint min corner; facing = direction the front points.
# E/W-facing pieces occupy D along x and W along y.
F_WALNUT = "wood:#6e4f37"
FURNITURE = [
 # ---------------- basement
 ("basement", "squat_rack", 5, 7, "S", {}),
 ("basement", "cold_plunge", 17, 8, "N", {}),
 ("basement", "dumbbell_rack", 2, 20.15, "S", {}),
 ("basement", "weight_bench", 12.5, 9, "N", {}),
 ("basement", "treadmill", 11, 18.5, "E", {}),
 ("basement", "sauna_benches", 24.4, 0.3, "W", dict(W=7.4)),
 ("basement", "sauna_heater", 22.4, 6.0, "E", {}),
 ("basement", "furnace", 22.3, 8.3, "N", {}),
 ("basement", "elec_panel", 27.4, 11, "W", {}),
 ("basement", "rug", 24, 15.5, "N", dict(W=34, D=3, color="fabric:#9a8f80", border="fabric:#5d564d")),
 ("basement", "shower", 38.2, 5.8, "S", dict(W=4, D=4, glass="FL")),
 ("basement", "vanity", 46, 0.4, "W", dict(W=3, D=1.8)),
 ("basement", "toilet", 38.2, 1.5, "E", {}),
 ("basement", "closet_rod", 38.5, 10.2, "N", dict(W=9, D=1.2)),
 ("basement", "bed", 48.2, 7, "E", dict(W=5, D=6.7, throw="fabric:#7b6a58")),
 ("basement", "nightstand", 48.2, 12.1, "E", dict(W=1.6)),
 ("basement", "dresser", 57.9, 0.4, "W", dict(W=4.5)),
 ("basement", "rug", 50, 5.5, "N", dict(W=7, D=8)),
 ("basement", "sofa", 28.3, 25, "E", dict(W=8, D=3.3, color="fabric:#6f8fa6")),
 ("basement", "media_console", 46.2, 26, "W", dict(W=6.5)),
 ("basement", "tv_wall", 47.68, 26.5, "W", {}),
 ("basement", "rug", 33, 24.5, "N", dict(W=11, D=9, color="fabric:#e8d9b8", border="fabric:#d98a6a")),
 ("basement", "kids_table", 34, 33.5, "N", {}),
 ("basement", "toy_storage", 39, 36.35, "S", {}),
 ("basement", "beanbag", 40, 25.2, "E", {}),
 ("basement", "beanbag", 40, 29, "E", dict(color="fabric:#7fa6b5")),
 ("basement", "shelving_metal", 48.2, 24, "E", {}), ("basement", "shelving_metal", 48.2, 30.5, "E", dict(seed=2)),
 ("basement", "shelving_metal", 57.75, 24, "W", dict(seed=3)), ("basement", "shelving_metal", 57.75, 30.5, "W", dict(seed=4)),
 ("basement", "shelving_metal", 51, 35.75, "S", dict(seed=5)),
 # ---------------- main: living
 ("main", "rug", 3.5, 24, "N", dict(W=13, D=12)),
 ("main", "fireplace", 0.3, 26.5, "E", {}),
 ("main", "sofa", 13, 25, "W", dict(W=10, D=3.3, label="Sofa")),
 ("main", "coffee_table", 8.5, 27.75, "W", dict(W=4.5, D=2.4)),
 ("main", "armchair", 4.6, 22.0, "N", {}), ("main", "armchair", 8.8, 22.0, "N", dict(color="fabric:#8a6f5a")),
 ("main", "side_table", 14.2, 23.3, "N", {}), ("main", "side_table", 14.2, 35.1, "N", {}),
 ("main", "floor_lamp", 2.6, 22.2, "N", {}),
 ("main", "plant", 0.4, 24.9, "N", {}), ("main", "plant", 24.0, 44.0, "N", {}),
 ("main", "console_table", 3, 14.25, "N", dict(W=6)),
 ("main", "art", 4, 14.2, "N", dict(W=4, color="fix:#c9a36b")),
 # dining
 ("main", "rug", 31, 17.5, "N", dict(W=12, D=9, color="fabric:#b9b0a1", border="fabric:#6e6457")),
 ("main", "dining_table", 33, 20.2, "N", {}),
 *[("main", "chair", cx, 18.8, "N", {}) for cx in (34.0, 36.2, 38.4)],
 *[("main", "chair", cx, 23.5, "S", {}) for cx in (34.0, 36.2, 38.4)],
 ("main", "chair", 31.4, 21.2, "E", {}), ("main", "chair", 40.9, 21.2, "W", {}),
 *[("main", "pendant", px, 21.3, "N", dict(z=6.8, ceil=10.0)) for px in (34.3, 36.3, 38.3)],
 ("main", "media_console", 27, 14.25, "N", dict(W=7, label="Buffet")),
 ("main", "art", 28.5, 14.2, "N", dict(W=4, z=4.8, color="fix:#5f7f8f")),
 # kitchen
 ("main", "fridge", 57.25, 26.5, "W", {}),
 ("main", "base_cab", 57.75, 29.5, "W", dict(W=4.5)),
 ("main", "base_cab", 57.75, 34.0, "W", dict(W=4.0, sink=0.7, label="Sink")),
 ("main", "dishwasher", 57.75, 38.0, "W", {}),
 ("main", "base_cab", 57.75, 40.0, "W", dict(W=5.75, drawers=True)),
 ("main", "base_cab", 49.5, 43.75, "S", dict(W=2.25)),
 ("main", "range", 51.75, 43.55, "S", {}),
 ("main", "base_cab", 54.75, 43.75, "S", dict(W=3.0, drawers=True)),
 ("main", "hood", 51.5, 43.75, "S", {}),
 ("main", "upper_cab", 58.65, 39.0, "W", dict(W=6.75)),
 ("main", "upper_cab", 49.5, 44.65, "S", dict(W=2.0)),
 ("main", "upper_cab", 55.0, 44.65, "S", dict(W=3.65)),
 ("main", "island", 43, 34.5, "S", {}),
 *[("main", "stool", sx, 33.2, "N", {}) for sx in (44.0, 46.3, 48.6, 50.9)],
 *[("main", "pendant", px, 36.1, "N", dict(z=6.8, ceil=10.0)) for px in (44.8, 47.3, 49.8)],
 ("main", "base_cab", 28, 43.75, "S", dict(W=8, label="Coffee bar")),
 ("main", "upper_cab", 28.5, 44.65, "S", dict(W=7)),
 # pantry
 ("main", "pantry_shelves", 48.2, 14.5, "E", dict(W=11)),
 ("main", "pantry_shelves", 58.4, 14.5, "W", dict(W=11, seed=2)),
 # office
 ("main", "desk", 5, 4, "W", {}),
 ("main", "office_chair", 2.8, 5.75, "E", {}),
 *[("main", "bookcase", bx, 12.6, "S", dict(seed=bx)) for bx in (1, 5, 9)],
 ("main", "rug", 2, 3.5, "N", dict(W=8, D=6, color="fabric:#8c6a55", border="fabric:#4a3a30")),
 ("main", "plant", 12, 0.5, "N", {}),
 # foyer / half bath / hall / mudroom
 ("main", "bench", 14.2, 9, "E", {}),
 ("main", "art", 14.18, 9.5, "E", dict(W=3, color="fix:#a7745a")),
 ("main", "console_table", 23.5, 0.3, "N", {}),
 ("main", "rug", 18.5, 2, "N", dict(W=5, D=8, color="fabric:#3e4a5c", border="fabric:#c9b98f")),
 ("main", "pendant", 20, 6, "N", dict(W=2, D=2, z=7.5, ceil=10.0)),
 ("main", "plant", 26.2, 7.0, "N", {}),
 ("main", "vanity", 38.2, 1.5, "E", dict(W=3, D=1.8)),
 ("main", "toilet", 43.4, 2, "W", {}),
 ("main", "rug", 39, 8.8, "N", dict(W=6, D=4.4, color="fabric:#b7a98f")),
 ("main", "wardrobe_wall", 46.2, 0.4, "E", dict(W=7, D=1.75, label="Lockers")),
 ("main", "bench", 49, 0.3, "N", dict(W=8)),
 ("main", "rug", 51, 3.5, "N", dict(W=3, D=8, color="fabric:#5d5f61", border="fabric:#3a3b3c")),
 # garage
 ("main", "car", 63.35, 1.5, "S", {}),
 ("main", "car", 74.35, 1.5, "S", dict(color="gloss:#b8bcc0")),
 ("main", "workbench", 62, 23.25, "S", {}),
 ("main", "shelving_metal", 80, 23.6, "S", {}), ("main", "shelving_metal", 86, 23.6, "S", dict(seed=6)),
 # covered patio
 ("main", "outdoor_kitchen", 40, 59.3, "S", {}),
 ("main", "outdoor_fireplace", 28, 59.6, "S", {}),
 ("main", "sofa", 27.5, 51, "N", dict(W=7, D=3.2, color="fabric:#cfc8b8", pillow="fabric:#3e6a7a")),
 ("main", "coffee_table", 29.2, 55, "N", dict(W=3.5, D=2, top="wood:#8c7058")),
 ("main", "outdoor_table", 43, 51.8, "N", {}),
 *[("main", "chair", cx, 50.3, "N", dict(seat="fabric:#d8d2c4", frame="metal:#2b2c2e")) for cx in (44.0, 45.7, 47.4)],
 *[("main", "chair", cx, 55.0, "S", dict(seat="fabric:#d8d2c4", frame="metal:#2b2c2e")) for cx in (44.0, 45.7, 47.4)],
 # ---------------- upper
 ("upper", "bed", 7.1, 4.5, "W", dict(W=5, D=6.7, throw="fabric:#6a86a3")),
 ("upper", "nightstand", 12.3, 2.6, "W", {}), ("upper", "nightstand", 12.3, 9.6, "W", {}),
 ("upper", "dresser", 8.8, 12.05, "S", dict(W=4)),
 ("upper", "rug", 4.5, 3, "N", dict(W=6, D=8, color="fabric:#e7e3da")),
 ("upper", "bed", 21.1, 4.5, "W", dict(W=5, D=6.7, throw="fabric:#7c9a6e")),
 ("upper", "nightstand", 26.3, 2.6, "W", {}), ("upper", "nightstand", 26.3, 9.6, "W", {}),
 ("upper", "dresser", 14.2, 5, "E", dict(W=4)),
 ("upper", "rug", 18.5, 3, "N", dict(W=6, D=8, color="fabric:#e7e3da")),
 ("upper", "tub", 38.2, 4.2, "E", dict(shower_walls=True, label="Tub/shower")),
 ("upper", "toilet", 38.2, 10.3, "E", {}),
 ("upper", "vanity", 46, 6, "W", dict(W=6, sinks=2)),
 ("upper", "rug", 41.5, 8, "N", dict(W=3.5, D=2.2, color="fabric:#d8dee2")),
 ("upper", "pantry_shelves", 38.5, 0.3, "N", dict(W=9, wood="gloss:#f2f0ea", label="Linen shelves", seed=8)),
 ("upper", "washer", 48.2, 5.5, "E", {}), ("upper", "dryer", 48.2, 7.9, "E", {}),
 ("upper", "upper_cab", 48.2, 5.3, "E", dict(W=5, z=5.0, H=2.5)),
 ("upper", "utility_sink", 57.75, 5, "W", {}),
 ("upper", "shelving_metal", 48.5, 0.3, "N", dict(D=1.5, seed=7)), ("upper", "shelving_metal", 54, 0.3, "N", dict(D=1.5, W=5.5, seed=8)),
 ("upper", "rug", 3, 14.7, "N", dict(W=24, D=2.6, color="fabric:#a49a8b", border="fabric:#5d564d")),
 ("upper", "rug", 38, 14.7, "N", dict(W=20, D=2.6, color="fabric:#a49a8b", border="fabric:#5d564d")),
 # primary suite
 ("upper", "bed", 0.3, 25.75, "E", dict(W=6.5, D=7, frame="fabric:#5b6470", throw="fabric:#b39a7a", label="King bed")),
 ("upper", "nightstand", 0.3, 23.85, "E", {}), ("upper", "nightstand", 0.3, 32.35, "E", {}),
 ("upper", "bench", 7.5, 27, "E", dict(cushion="fabric:#b39a7a")),
 ("upper", "rug", 3, 23.5, "N", dict(W=10, D=11, color="fabric:#d9d3c7", border="fabric:#a39a8e")),
 ("upper", "dresser", 1, 18.2, "N", dict(W=6)),
 ("upper", "armchair", 13.5, 36.6, "S", dict(color="fabric:#c7b79c")), ("upper", "armchair", 17.4, 36.6, "S", dict(color="fabric:#c7b79c")),
 ("upper", "media_console", 20.2, 26.5, "W", dict(W=6)),
 ("upper", "tv_wall", 21.68, 27, "W", dict(W=5)),
 ("upper", "wardrobe_wall", 22.3, 18.2, "N", dict(W=15.4)),
 ("upper", "wardrobe_wall", 35.95, 20.1, "W", dict(W=9.6, seed=17)),
 ("upper", "wardrobe_wall", 22.3, 28.05, "S", dict(W=6, seed=21)),
 ("upper", "wardrobe_wall", 31.7, 28.05, "S", dict(W=4.1, seed=25)),
 ("upper", "closet_island", 26.5, 22.6, "N", {}),
 ("upper", "pendant", 28.8, 23.15, "N", dict(z=6.6, ceil=9.0)),
 ("upper", "shower", 33.3, 30.2, "W", dict(W=4.5, D=4.5, glass="FR")),
 ("upper", "vanity", 22.3, 30.2, "N", dict(W=6, sinks=2)),
 ("upper", "tub", 27.5, 36.9, "S", dict(freestanding=True, label="Soaking tub")),
 ("upper", "toilet", 22.3, 37.5, "E", {}),
 ("upper", "rug", 28, 33.5, "N", dict(W=4, D=2.5, color="fabric:#d8dee2")),
 ("upper", "plant", 36, 37.8, "N", {}),
 # bedroom 4
 ("upper", "bed", 54.5, 18.2, "N", dict(W=5, D=7, throw="fabric:#a3786a")),
 ("upper", "nightstand", 52.8, 18.2, "N", dict(W=1.6)),
 ("upper", "dresser", 42.2, 28.5, "E", dict(W=5)),
 ("upper", "desk", 49, 31.25, "S", dict(W=4.5)),
 ("upper", "office_chair", 50.3, 29.2, "N", dict(color="fabric:#8a9aa8")),
 ("upper", "rug", 50.5, 22, "N", dict(W=9, D=7, color="fabric:#e7e3da")),
 ("upper", "closet_rod", 38.2, 18.5, "E", dict(W=15)),
]
