# ForeverHome — Project Brief

> Read this first at the start of every session. Update it at the end of every session.

## Goal
Design a custom-built family home over a multi-year planning process. Deliverables:
1. Builder-ready CAD / construction documents (plans, elevations, sections, schedules).
2. A virtual walkthrough viewable in a phone browser via a shareable link.

## Status
- **Phase:** Discovery. Draft v0 layout + tooling pipeline built (placeholder sizes, no lot yet). Walkthrough is furnished with placeholder finishes.
- **Last updated:** 2026-10-25

## Key Decisions
_None yet. Log each with date and reasoning._

## Open Questions
- Lot: not selected yet. Likely Tennessee or Missouri (affects frost depth, basement norms, code, climate zone).
- Budget: unknown. Size is intentionally not fixed; it will fall out of the room program.
- Lot slope matters: a walk-out basement lot changes the design (basement windows/daylight).
- Preferred CAD output formats the builder wants (DWG, PDF, IFC)?

## Requirements (room program, v1 — 2026-10-25)
Owners are flexible on which floor a room lands on.

**Basement**
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
- Primary suite: primary bath + large walk-in closet with a center island
- One shared bathroom for the other 3 upstairs bedrooms
- Walk-in pantry (off kitchen)
- Covered patio with outdoor kitchen and fireplace

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

**Exterior (2026-10-25, draft)** — modern farmhouse read of "modern meets traditional":
- White board-and-batten siding, ledgestone base (2.5 ft) on the main level, white trim, black window frames with
  2-over-2 grilles, black front door, carriage-style garage doors with a glass top row.
- Roof: 8:12 side gables (charcoal architectural shingles) over the two-story block and the bonus room, eaves at the
  upper wall top; 4:12 metal sheds on the rear one-story strip; 6:12 metal hips over the playroom and covered patio;
  8:12 metal gable front porch on cedar posts. Ridges ~34 ft (main), ~29 ft (bonus) above main floor.
- Covered patio: cedar posts/beams, tongue-and-groove ceiling, stone chimney for the outdoor fireplace.
- Site placeholders: driveway, front walk, sidewalk/street, shrubs, trees, exterior lights. No lot yet, so all of
  this (and grade = main floor) is a stand-in.
- Open: bonus-room roof/knee walls, gutters/downspouts, basement window wells, roof drainage at the valleys where
  the rear sheds meet the playroom/patio hips (needs crickets or a re-think once a roof designer looks at it).

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
- Finished area in draft: basement ~1,650 + main ~2,910 + upper ~3,100 (incl. ~880 bonus over garage) = **~7,700 sq ft**
  (excl. garage, patio).
  That is bigger than expected; generous great room, halls and basement. Trim once priorities are set.
- Not modeled yet: foundation, structure, MEP, sections, IFC export, real lot/grading, gutters, window wells.
  Furniture is blocky (boxes only); walk mode can't climb stairs. PDF now has a roof plan (A-6.0) and elevations with roofs.
- Viewer verified in headless Chromium (software WebGL, no console errors) on 2026-10-25; still verify on a real phone,
  especially frame rate with shadows (and HQ/AO if turned on).
- `house.glb` checked programmatically (parses; all 340 objects match source geometry), not yet opened in Blender.
- DXF/PDF are drafting aids; stamped construction documents must come from a licensed architect/engineer.
- Public repo: the design is publicly viewable. Make private (and lose free Pages) or move hosting if that matters.

## Session Log
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
