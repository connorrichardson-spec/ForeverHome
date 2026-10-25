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
# slab=False leaves the floor open (stair openings)
ROOMS = {
 "basement": [
  dict(name="Gym", rect=(0, 0, 22, 22), win="high",
       note="Squat rack, cold plunge, sauna access"),
  dict(name="Sauna", rect=(22, 0, 28, 8), win="none"),
  dict(name="Mechanical", rect=(22, 8, 28, 14), win="none"),
  dict(name="Stair", rect=(28, 0, 38, 14), win="none", stair="up"),
  dict(name="Bsmt Hall", rect=(22, 14, 60, 22), win="none"),
  dict(name="Bsmt Bath", rect=(38, 0, 48, 10), win="small", note="Full bath"),
  dict(name="Bsmt Closet", rect=(38, 10, 48, 14), win="none"),
  dict(name="Bsmt Bedroom", rect=(48, 0, 60, 14), win="egress", note="Egress window required"),
  dict(name="Play Area", rect=(28, 22, 48, 38), win="high"),
  dict(name="Storage", rect=(48, 22, 60, 38), win="none"),
 ],
 "main": [
  dict(name="Office", rect=(0, 0, 14, 14)),
  dict(name="Foyer", rect=(14, 0, 28, 14)),
  dict(name="Stair", rect=(28, 0, 38, 14), win="none", stair="up", slab=False),
  dict(name="Half Bath", rect=(38, 0, 46, 8), win="small"),
  dict(name="Hall", rect=(38, 8, 46, 14), win="none"),
  dict(name="Mudroom", rect=(46, 0, 60, 14), win="small"),
  dict(name="Pantry", rect=(48, 14, 60, 26), win="none", note="Walk-in"),
  dict(name="Great Room", poly=[(0, 14), (48, 14), (48, 26), (60, 26), (60, 46), (0, 46)],
       note="Open plan: living / dining / kitchen",
       zones=[("Living", (0, 14, 26, 46)), ("Dining", (26, 14, 48, 30)),
              ("Kitchen", (26, 30, 60, 46))]),
  dict(name="Garage", rect=(60, 0, 94, 26), win="garage", note="3-car + storage/workspace",
       zones=[("Storage / Workspace", (60, 19, 94, 26))]),
  dict(name="Covered Patio", rect=(26, 46, 60, 62), kind="outdoor",
       note="Outdoor kitchen + fireplace"),
 ],
 "upper": [
  dict(name="Bedroom 2", rect=(0, 0, 14, 14)),
  dict(name="Bedroom 3", rect=(14, 0, 28, 14)),
  dict(name="Stair", rect=(28, 0, 38, 14), win="none", stair="landing"),
  dict(name="Bath 2", rect=(38, 4, 48, 14), win="small", note="Shared by bedrooms 2-4"),
  dict(name="Linen", rect=(38, 0, 48, 4), win="none"),
  dict(name="Laundry", rect=(48, 4, 60, 14)),
  dict(name="Storage Closet", rect=(48, 0, 60, 4), win="none"),
  dict(name="Upper Hall", rect=(0, 14, 60, 18), win="none"),
  dict(name="Primary Bedroom", rect=(0, 18, 22, 40)),
  dict(name="Primary Closet", rect=(22, 18, 38, 30), win="small", note="Center island"),
  dict(name="Primary Bath", rect=(22, 30, 38, 40)),
  dict(name="Bedroom 4", rect=(42, 18, 60, 34)),
  dict(name="Bed 4 Closet", rect=(38, 18, 42, 34), win="none"),
 ],
}

# Doors between rooms: (level, room A, room B, kind). B=None -> exterior on side of A.
# kinds: door | cased (wide opening) | patio | garage | none
# optional 5th item: dict(at=(x,y)) to force position, side="S|N|E|W" for exterior
DOORS = [
 ("basement", "Gym", "Sauna", "door"), ("basement", "Gym", "Bsmt Hall", "door"),
 ("basement", "Mechanical", "Bsmt Hall", "door"), ("basement", "Stair", "Bsmt Hall", "cased"),
 ("basement", "Bsmt Closet", "Bsmt Hall", "door"),
 ("basement", "Bsmt Bedroom", "Bsmt Hall", "door"), ("basement", "Bsmt Bedroom", "Bsmt Bath", "door"),
 ("basement", "Play Area", "Bsmt Hall", "cased"), ("basement", "Storage", "Bsmt Hall", "door"),
 ("main", "Foyer", None, "door", dict(side="S")),
 ("main", "Garage", None, "door", dict(side="N", at=(75, 26))),
 ("main", "Foyer", "Office", "door"), ("main", "Foyer", "Stair", "cased"),
 ("main", "Foyer", "Great Room", "cased"), ("main", "Stair", "Hall", "cased"),
 ("main", "Hall", "Half Bath", "door"), ("main", "Hall", "Great Room", "cased"),
 ("main", "Hall", "Mudroom", "cased"),
 ("main", "Mudroom", "Garage", "door"), ("main", "Mudroom", "Pantry", "cased"),
 ("main", "Pantry", "Great Room", "cased"),
 ("main", "Great Room", "Covered Patio", "patio"),
 ("upper", "Bedroom 2", "Upper Hall", "door"), ("upper", "Bedroom 3", "Upper Hall", "door"),
 ("upper", "Stair", "Upper Hall", "cased"), ("upper", "Bath 2", "Linen", "door"),
 ("upper", "Laundry", "Upper Hall", "door"), ("upper", "Laundry", "Storage Closet", "door"),
 ("upper", "Bath 2", "Upper Hall", "door"),
 ("upper", "Primary Bedroom", "Upper Hall", "door"),
 ("upper", "Primary Bedroom", "Primary Closet", "door"),
 ("upper", "Primary Bedroom", "Primary Bath", "door"),
 ("upper", "Primary Closet", "Primary Bath", "door"),
 ("upper", "Bedroom 4", "Upper Hall", "door"), ("upper", "Bed 4 Closet", "Bedroom 4", "door"),
]

# Garage overhead doors (centered x positions on the south wall)
GARAGE_DOORS = [66.5, 77.5, 88.5]

# Placeholder fixtures/furniture: (level, label, x, y, w, d, h, color)
FIXTURES = [
 ("basement", "Squat rack", 4, 4, 8, 10, 8, "#555b66"),
 ("basement", "Cold plunge", 15, 4, 3, 6, 2.5, "#4aa3c7"),
 ("basement", "Sauna bench", 23, 1, 4, 6, 1.5, "#b98a5a"),
 ("basement", "Bed", 53, 3, 5, 6.7, 2, "#8a7f9a"),
 ("basement", "Toys/play", 32, 26, 8, 8, 1.2, "#e0a458"),
 ("main", "Kitchen island", 38, 36, 12, 4, 3, "#c9c1b0"),
 ("main", "Dining table", 32, 19, 8, 4, 2.5, "#9b7653"),
 ("main", "Sofa", 6, 32, 9, 3.2, 2.7, "#7c8a99"),
 ("main", "Desk", 4, 1, 5, 2.5, 2.5, "#9b7653"),
 ("main", "Outdoor kitchen", 40, 59, 14, 2, 3, "#6b6f73"),
 ("main", "Fireplace", 28, 59, 6, 2, 5, "#7a5c4b"),
 ("upper", "Primary bed", 6, 33, 6.5, 7, 2.2, "#8a7f9a"),
 ("upper", "Closet island", 27, 22, 6, 3, 3, "#c9c1b0"),
 ("upper", "Bed 2", 5, 4, 5, 6.7, 2, "#8a7f9a"),
 ("upper", "Bed 3", 19, 4, 5, 6.7, 2, "#8a7f9a"),
 ("upper", "Bed 4", 48, 23, 5, 6.7, 2, "#8a7f9a"),
 ("upper", "Soaking tub", 33, 36, 5, 2.5, 2, "#e8eef2"),
]
