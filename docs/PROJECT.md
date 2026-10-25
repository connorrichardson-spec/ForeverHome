# ForeverHome — Project Brief

> Read this first at the start of every session. Update it at the end of every session.

## Goal
Design a custom-built family home over a multi-year planning process. Deliverables:
1. Builder-ready CAD / construction documents (plans, elevations, sections, schedules).
2. A virtual walkthrough viewable in a phone browser via a shareable link.

## Status
- **Phase:** Discovery. Draft v0 layout + tooling pipeline built (placeholder sizes, no lot yet)
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

**Still unspecified:** exact garage door layout, hall/bath fixtures, finishes.

## Design Notes / Constraints
- Style: modern meets traditional.
- Squat rack needs ~9 ft finished basement ceiling (rack ~7.5-8 ft + bar clearance).
- Sauna and cold plunge need drainage, ventilation/moisture control, and electrical (dedicated circuit for sauna); plan them near the basement bathroom plumbing.
- Basement bedroom requires code egress window (window well); confirm with local code.
- Stack wet walls (basement bath / main half bath / upstairs baths) to simplify plumbing.

## Repo Layout
- `design/house.py` — **single source of truth**: levels, rooms (rectangles, ft), doors, fixtures. Edit this.
- `design/geometry.py` — turns rooms into walls, openings (doors/windows auto-placed), 3D boxes.
- `design/build.py` — generates everything below. Run: `.venv/bin/python design/build.py`
  (first time: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`)
- `exports/` — builder-facing output (commit these): `ForeverHome_plans.pdf` (3 floor plans at 1/8"=1' + 4 elevations),
  `ForeverHome_plans.dxf` (CAD, layers per level, feet), `schedules/rooms.csv`, `schedules/openings.csv`
- `web/` — phone walkthrough (Three.js, vendored in `web/vendor/`, no build step). `model.json` is generated.
- `.github/workflows/pages.yml` — publishes `web/` + `exports/` to GitHub Pages on every push to main.
- Live site (once Pages is enabled): https://connorrichardson-spec.github.io/ForeverHome/
- Preview locally: `cd web && python3 -m http.server 8000`, open http://localhost:8000

## Draft v0 Status / Known Gaps
- Layout is a **placeholder** to react to, not a design. Rooms are rectangles; all sizes are guesses.
- Finished area in draft: basement ~1,650 + main ~2,620 + upper ~2,130 = **~6,400 sq ft** (excl. garage, patio).
  That is bigger than expected; generous great room, halls and basement. Trim once priorities are set.
- Not modeled yet: roof, foundation, stairs geometry (steps are visual only; use floor buttons in viewer),
  structure, MEP, sections, IFC export, real furniture, finishes, site/lot.
- Viewer was **not** tested in a real WebGL browser during creation (sandbox had none); verify on phone.
- DXF/PDF are drafting aids; stamped construction documents must come from a licensed architect/engineer.
- Public repo: the design is publicly viewable. Make private (and lose free Pages) or move hosting if that matters.

## Session Log
- 2026-10-25 (later): Built pipeline: design/ -> PDF plans/elevations, DXF, CSV schedules, Three.js phone walkthrough, Pages workflow. Pages must be enabled by hand (Settings > Pages > Source: GitHub Actions).
- 2026-10-25: Repo created, docs scaffolding started. Room program captured and expanded (garage, laundry, primary suite, pantry, patio). Size is derived from rooms, not fixed.
