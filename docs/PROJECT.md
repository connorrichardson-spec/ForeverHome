# ForeverHome — Project Brief

> Read this first at the start of every session. Update it at the end of every session.

## Goal
Design a custom-built family home over a multi-year planning process. Deliverables:
1. Builder-ready CAD / construction documents (plans, elevations, sections, schedules).
2. A virtual walkthrough viewable in a phone browser via a shareable link.

## Status
- **Phase:** Discovery. Draft v0 layout + tooling pipeline built (placeholder sizes, no lot yet). Walkthrough is furnished with placeholder finishes.
- **Last updated:** 2026-10-26

## Key Decisions
- 2026-10-26: Shrink to cut cost. Great room 30 -> 24 ft deep (whole house 46 -> 40 ft deep on main, 41.5 -> 40 upper),
  upper hall 5.5 -> 4.5 ft, basement hall 8 -> 5 ft. Reason: size/cost well over what owners want.
- 2026-10-26: Removed a 4 ft north-south strip at x=18-22 on every floor (house 60 -> 56 ft wide main block):
  foyer 14 -> 10 ft wide, living 26 -> 22, playroom 26 -> 22, Bedroom 2 28 -> 24, primary bedroom 22 -> 18 ft wide.
- 2026-10-26: Bedroom 3 over the garage shrunk to 14x14 + 8x4.5 walk-in; rest of the space is unfinished attic
  storage off the hall. Keeps 4 bedrooms upstairs.
- 2026-10-26: Basement = full footprint of the main block (56x40; playroom bump-out and garage on slab/crawl).
  Finished: gym (18x24), sauna, bedroom, bath, hall. ~1,090 sq ft unfinished (storage now, future play/rec area).
  Reason: a partial basement still needs foundation walls around the rest; unfinished basement is the cheapest
  space in the house and can be finished later.
- 2026-10-26 (for <$1M): Basement left unfinished: one open space (stair + future-room zones on the plan),
  egress window installed at the future bedroom, plumbing rough-in for the future bath, sauna circuit.
  Kids Playroom bump-out removed (living room gets its north windows back). Covered patio -> open pavers (no roof,
  posts or beams). Upper floor cut to 34.5 ft deep everywhere so the main roof is one gable plus one rear shed:
  primary bedroom 18x16, galley closet 16x7 (no island), primary bath 16x9 + WC.
- 2026-10-26: Kids are teenagers. Bedroom 2 split back into two 12x14 teen rooms (Bedrooms 2 + 3: queen bed, desk,
  dresser, 8.5x2.5 reach-in with sliding doors, ~147 sq ft each). No room over the garage any more: garage gets a
  one-story 8:12 gable (attic-truss storage, pull-down stair). Laundry stays windowless (garage roof is in the way).

## Open Questions
- Lot: not selected yet. Likely Tennessee or Missouri (affects frost depth, basement norms, code, climate zone).
- Budget: owners want to be **under $1M** (2026-10-26; excl. land/site work). Rough estimates (TN/MO, not builder
  quotes): ~8,150 sq ft start was $1.9M-2.7M. Now ~4,170 finished + ~2,240 unfinished basement:
  custom builder ($250-350/sf) ~$1.2M-1.7M; semi-custom/production builder ($175-225/sf) ~$0.87M-1.18M.
  So <$1M likely needs a semi-custom builder with mid-grade finishes, or another ~500-800 sq ft cut.
  Rule of thumb: every 500 finished sq ft ~ $90k-175k depending on builder tier.
- Shared Bath 2 serves 3 teenagers, so it is compartmented (2026-10-26): toilet + tub/shower + shower in a 10x7 room
  behind a door, double vanity in the 10x7 room off the hall. Vanity side has no window (could add a skylight/tube).
- Lot slope matters: a walk-out basement lot changes the design (basement windows/daylight).
- Preferred CAD output formats the builder wants (DWG, PDF, IFC)?

## Requirements (room program, v1 — 2026-10-25)
Owners are flexible on which floor a room lands on.

**Basement** (2026-10-26: built unfinished; these are the future rooms, see Key Decisions)
- Bedroom (needs egress window) + full bathroom
- Storage area
- Small play area
- Home gym: fits squat rack, small cold plunge, small sauna

**Main floor**
- Open plan: living room, kitchen, dining
- Separate office
- Half bath
- Mudroom entering from the garage

**Upper floor**
- Primary bedroom + 3 additional bedrooms (4 total)

**Added (2026-10-25 answers)**
- Garage: 3-car, attached, with a little storage and some workspace (not a full shop)
- Laundry: upstairs
- Primary suite: primary bath + walk-in closet (center island dropped 2026-10-26 for the simpler roof: 16x7 galley)
- One shared bathroom for the other 3 upstairs bedrooms
- Walk-in pantry (off kitchen)
- Open paver patio with fireplace (2026-10-26: no roof; outdoor kitchen deferred, stub gas/power/water now)

**Added (2026-10-25, Tasks.md round 2)**
- Upper hall widened 4 ft -> 5.5 ft (back bedroom wing moved north 1.5 ft)
- Primary bath: separate water closet (3.5x5) with its own door; bath->bedroom door now swings into the bedroom
- Basement bath is a Jack-and-Jill: doors from the hall (via small entry) and the bedroom; basement closet shrank to 4x4
- Pantry: real doors at both ends, base cabinets + counters both sides, upper cabinets / open shelves above
- Bedrooms 2 and 3: 5x2.5 reach-in closets with sliding doors
- Bonus room (26x26 play/flex) + storage (8x26) over the garage, off the east end of the upper hall.
  Modeled with full-height walls for now; sloped ceiling / knee walls depend on the roofline (not designed yet).
  Side effect: laundry lost its exterior window (its east wall now backs onto the bonus room).

**Added (2026-10-25, Tasks.md round 3)**
- Front row (office, foyer, stair hall) 2 ft deeper: stair walkway foyer <-> hall is now 5.2 ft (was 3.2), office 14x16,
  wider cased openings into it (4.5 ft from the foyer, 3.5 ft from the hall). Living/dining lose 2 ft on the south side.
- Kids Playroom (26x12) bumped out north of the living room, 8 ft cased opening from the living room and 8 ft sliding
  doors to the covered patio. Single story; roof TBD. Living room's north windows are gone (wall is now interior).
- Bonus room: storage door moved to the south end (was behind the TV); bookcase moved between windows.

**Added (2026-10-25, Tasks.md round 4)**
- Kids Playroom opening widened to ~16.4 ft (wall west of the old opening removed)
- Pantry: floor-to-ceiling cabinet (5 ft) on the east wall; counter + uppers continue beside it
- Mudroom: built-in locker wall on the south wall (shoe cubbies, bench, hooks, upper cubbies); bench-only bay under the window
- Foyer coat closet (3.5x3) in the SE corner, opening toward the stair

**Changed (2026-10-25, upper-floor re-plan)**
- The two small south bedrooms are combined into one 28x14 Bedroom 2 with a 7x5 walk-in closet (king bed + desk/reading nook)
- The bonus room over the garage is now Bedroom 3 (26x26: king bed + sitting area), with an 8x10 walk-in closet
  and 8x16 attic storage in the old bonus-storage strip. No bonus/play room upstairs any more (kids playroom is on main).
- Shared Bath 2 grew from 10x10 to 10x14 (absorbed the hall linen closet): tub/shower, separate walk-in shower,
  toilet, double vanity, window. Linen moved to the old storage closet off the laundry.
- Bedroom count unchanged: primary + 3 (Bedrooms 2, 3, 4).

**Exterior (2026-10-25, draft)** — modern farmhouse read of "modern meets traditional":
- White board-and-batten siding, ledgestone base (2.5 ft) on the main level, white trim, black window frames with
  2-over-2 grilles, black front door, carriage-style garage doors with a glass top row.
- Roof (simplified 2026-10-26): one 8:12 side gable (charcoal architectural shingles) over the 56x34.5 two-story
  block, one full-width 4:12 metal shed over the 5.5 ft one-story strip at the back, a one-story 8:12 garage gable,
  and the 8:12 metal gable front porch on cedar posts. Ridges ~31.5 ft (main), ~19 ft (garage) above main floor.
- Patio: open pavers, no roof; stone chimney for the outdoor fireplace.
- Site placeholders: driveway, front walk, sidewalk/street, shrubs, trees, exterior lights. No lot yet, so all of
  this (and grade = main floor) is a stand-in.
- Open: gutters/downspouts, basement window wells (egress well at the future bedroom).

**Changed (2026-10-26, size/cost cut)**
- Great room 1,700 -> 1,340 sq ft: back wall moved 6 ft south (living 26x24, dining 22x12, kitchen 34x12 with the
  island and a 4 ft working aisle). Kids Playroom and covered patio moved with it (same sizes).
- Upper hall 4.5 ft wide (reverses part of round 2's 5.5 ft); primary suite, Bedroom 4 + closet shift south 1 ft.
  Upper back wall now lines up with main (40 ft), so the west rear shed roof is gone. Primary bath ~0.5 ft shallower.
- Basement hall 5 ft wide; gym 22x19 (was 22x22); play area + storage moved 3 ft south (same sizes).

**Changed (2026-10-26, cost cut round 2)** — see Key Decisions. Basement play area is now unfinished (future);
the main-floor Kids Playroom covers play for now. Front porch recentred on the moved front door (12x7).
Rooms can be flagged `unfinished=True` in house.py: no trim, excluded from finished sq ft, `finished` column in rooms.csv.

**Still unspecified:** exact garage door layout. Finishes in the model are placeholders to react to (see Design Notes).

## Design Notes / Constraints
- Style: modern meets traditional.
- Squat rack needs ~9 ft finished basement ceiling (rack ~7.5-8 ft + bar clearance).
- Sauna and cold plunge need drainage, ventilation/moisture control, and electrical (dedicated circuit for sauna); plan them near the basement bathroom plumbing.
- Basement bedroom requires code egress window (window well); confirm with local code.
- Stack wet walls (basement bath / main half bath / upstairs baths) to simplify plumbing.
- Placeholder finishes (2026-10-25): white-oak hardwood in finished rooms; wet rooms (all 4 baths + laundry) are
  12x24 porcelain tile; garage + mechanical concrete, gym rubber mats (squat rack), sauna cedar, patio stone pavers.
  One `floor=` edit per room to change.
- Stair (2026-10-25): stacked U-shaped (switchback) stairs in the 10x14 stair hall, basement->main 16 risers @ 7.5",
  main->upper 18 risers @ 7.33", 10" treads, ~4.5 ft flights, full-width landing on the south wall. Both flights
  start/end at y=10.8, leaving a 3.2 ft walkway along the north wall on every floor; foyer and hall open onto that
  walkway (3 ft cased openings). Verify headroom/landing depth with the builder (main landing is ~3.9 ft deep).
  Paint colors per room (`paint=` in house.py): greige common areas, green office, navy half bath, soft blues/greens in bedrooms.

## Repo Layout
- `design/house.py` — **single source of truth**: levels, rooms (rectangles, ft, with `paint=`/`floor=` finishes), doors
  (first room listed = side the door swings into), and `FURNITURE` placements. Edit this.
- `design/furniture.py` — furniture/cabinet/appliance/fixture library (each piece built from boxes; `facing` = which way its front points).
- `design/exterior.py` — roofs (gable / hip / shed from `ROOFS` in house.py) and site (`SITE`: paving, porches,
  lights, chimneys, shrubs, trees) as sloped polygons + boxes. Siding/stone/trim are applied to walls in geometry.py.
- `design/export.py` — writes `exports/house.json` (semantic model: rooms, finishes, walls, openings, stairs, furniture;
  feet) and `exports/house.glb` (glTF, meters; one named object per wall/floor/ceiling/stair/furniture piece, materials
  named by finish, furniture origins at footprint center with kind/facing/size as custom properties). **Blender
  handoff:** File > Import > glTF 2.0, then swap furniture objects for real assets by name/properties.
- `design/geometry.py` — turns rooms into walls, openings (doors/windows auto-placed), 3D boxes.
- `design/build.py` — generates everything below. Run: `.venv/bin/python design/build.py`
  (first time: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`)
- `exports/` — builder-facing output (commit these): `ForeverHome_plans.pdf` (3 floor plans at 1/8"=1' + 4 elevations),
  `ForeverHome_plans.dxf` (CAD, layers per level, feet), `schedules/rooms.csv`, `schedules/openings.csv`
- `web/` — phone walkthrough (Three.js, vendored in `web/vendor/`, no build step). `model.json` is generated.
  Textures (plank floors, tile, fabric, pavers) are drawn procedurally in `viewer.js`; geometry is merged per material for phones.
  Lighting: sky HDRI (`web/vendor/hdri/`, Poly Haven CC0), ACES tone mapping, soft sun shadows, GTAO ambient occlusion
  (HQ button; default on for desktop, off for phones). Stair openings have invisible blockers (walk mode doesn't climb).
  Deep link to a view: `index.html#main/38/27/60` (level/x/y/heading deg, 0 = north), `#doll`, or
  `#doll/35/28/120` (azimuth from the front, elevation, distance). Dollhouse opens as an exterior view; turn off
  Roof (and Upper) to look inside.
- `.github/workflows/pages.yml` — publishes `web/` + `exports/` to GitHub Pages on every push to main.
- Live site (once Pages is enabled): https://connorrichardson-spec.github.io/ForeverHome/
- Preview locally: `./run-local.sh` (serves web/ + exports/ on http://localhost:8000 and opens a separate Firefox
  instance on the NVIDIA GPU; plain Firefox on this laptop runs on the slower Intel iGPU). Ctrl+C to stop.

## Draft v0 Status / Known Gaps
- Layout is a **placeholder** to react to, not a design. Rooms are rectangles; all sizes are guesses.
- Area (from `rooms.csv`, excl. garage + patio, 2026-10-26): **finished ~4,170 sq ft** incl. stairs
  (main ~2,240, upper ~1,930); build.py prints ~3,870 (excludes stairs). Basement ~2,240 all unfinished.
  Was ~8,150 all finished at the start of 2026-10-26.
- Not modeled yet: foundation, structure, MEP, sections, IFC export, real lot/grading, gutters, window wells.
  Furniture is blocky (boxes only); walk mode can't climb stairs. PDF now has a roof plan (A-6.0) and elevations with roofs.
- Viewer verified in headless Chromium (software WebGL, no console errors) on 2026-10-25; still verify on a real phone,
  especially frame rate with shadows (and HQ/AO if turned on).
- `house.glb` checked programmatically (parses; all 340 objects match source geometry), not yet opened in Blender.
- DXF/PDF are drafting aids; stamped construction documents must come from a licensed architect/engineer.
- Public repo: the design is publicly viewable. Make private (and lose free Pages) or move hosting if that matters.

## Session Log
- 2026-10-26 (evening): toward <$1M: unfinished basement, no playroom, open paver patio, one-gable roof
  (primary suite re-planned). Doors' `at` now also picks which shared wall they go on.
- 2026-10-26: Outdoor kitchen removed from the covered patio (future add).
- 2026-10-26: Bath 2 compartmented for three teens.
- 2026-10-26 (later still): Bedroom 2 split into two teen rooms; garage bedroom removed, garage roof lowered.
- 2026-10-26 (later): 4 ft strip out of the west side (foyer, living, primary, Bedroom 2), Bedroom 3 -> 14x14 +
  unfinished attic, full-footprint basement with ~1,090 unfinished. Added `unfinished` room flag.
- 2026-10-26: Size/cost cut: great room 6 ft shallower, narrower upper + basement halls (~8,150 -> ~7,530 sq ft).
- 2026-10-25 (late night): upper re-plan: south bedrooms combined, bonus room -> Bedroom 3, Bath 2 enlarged.
- 2026-10-25 (night, round 4): wider playroom opening, pantry tall cabinet, mudroom lockers, foyer coat closet.
- 2026-10-25 (night): Exterior: siding, stone base, trim, window frames, full roof system, front porch, covered-patio
  structure, site (driveway, walks, plants, lights). Roof plan sheet + roofed elevations; roofs in DXF and glb.
- 2026-10-25 (late, round 3): wider stair walkway + bigger office, Kids Playroom bump-out with patio sliders,
  bonus-room door/bookcase fixes.
- 2026-10-25 (late): Tasks.md round 2 done (wider hall, primary WC + door swing, Jack-and-Jill basement bath, pantry
  doors/cabinets, bonus room over garage, closets for bedrooms 2/3, island sink rebuilt with real cut-out). Added
  run-local.sh (local preview on the NVIDIA GPU).
- 2026-10-25 (night): Blender handoff exports (house.json + house.glb). Tasks.md cleared: HDRI, soft shadows + GTAO,
  door/window casings (baseboards already done), stair rebuilt as stacked U-stairs with walkway + guard, wet rooms to tile.
- 2026-10-25 (evening): Made the walkthrough realistic: furniture in every room, kitchen cabinets/appliances/island, baths
  (vanities, toilets, showers, tubs), laundry, closets, gym, garage cars/workbench, patio furniture; per-room paint, baseboards,
  ceilings, open interior doors, hardwood floors; textured materials + reflections in viewer. Plans/DXF draw furniture footprints.
- 2026-10-25 (later): Built pipeline: design/ -> PDF plans/elevations, DXF, CSV schedules, Three.js phone walkthrough, Pages workflow. Pages must be enabled by hand (Settings > Pages > Source: GitHub Actions).
- 2026-10-25: Repo created, docs scaffolding started. Room program captured and expanded (garage, laundry, primary suite, pantry, patio). Size is derived from rooms, not fixed.
