# ForeverHome — Project Brief

> Read this first at the start of every session. Update it at the end of every session.

## Goal
Design a custom-built family home over a multi-year planning process. Deliverables:
1. Builder-ready CAD / construction documents (plans, elevations, sections, schedules).
2. A virtual walkthrough viewable in a phone browser via a shareable link.

## Status
- **Phase:** Discovery (room program drafted; lot, budget, size not yet defined)
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

## Repo Layout (planned)
- `docs/` — this brief, decision log, research notes
- `design/` — parametric source models (single source of truth)
- `exports/` — generated CAD/PDF/IFC files for the builder
- `web/` — phone-friendly 3D walkthrough

## Session Log
- 2026-10-25: Repo created, docs scaffolding started. Room program captured and expanded (garage, laundry, primary suite, pantry, patio). Size is derived from rooms, not fixed.
