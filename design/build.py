"""Generate every deliverable from house.py:  python design/build.py"""
import csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Arc
import ezdxf
import house as H
import geometry as G
import export

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "exports")
WEB = os.path.join(ROOT, "web")
CUT = 4.0                      # plan cut height above floor (ft)
LEVEL_TITLES = {"basement": "BASEMENT PLAN", "main": "MAIN FLOOR PLAN", "upper": "UPPER FLOOR PLAN"}
NOT_LIVING = {"Garage", "Covered Patio", "Mechanical", "Stair"}
DRAFT = "DRAFT v0 - NOT FOR CONSTRUCTION"

DATA = {l: G.boxes_for_level(l) for l in H.LEVELS}


def fmt(ft):
    f = int(ft)
    i = round((ft - f) * 12)
    if i == 12:
        f, i = f + 1, 0
    return f"{f}'-{i}\"" if i else f"{f}'"


def cut_boxes(level):
    elev = H.LEVELS[level][0]
    return [b for b in DATA[level][0]
            if b["mat"] in ("wallExt", "wallInt") and b["z"] <= elev + CUT < b["z"] + b["h"]]


def glass_boxes(level):
    elev = H.LEVELS[level][0]
    return [b for b in DATA[level][0]
            if b["mat"] in ("glass", "garageDoor", "doorExt") and not b.get("furn")
            and b["z"] <= elev + CUT <= b["z"] + b["h"] + 1e-6]


def room_label(r):
    x0, y0, x1, y1 = G.bounds(r)
    if "poly" in r:  # L-shaped rooms: area instead of dimensions
        lx, ly = r.get("label_at", ((x0 + x1) / 2, (y0 + y1) / 2))
        return [(r["name"], lx, ly, G.room_area(r), None)]
    return [(r["name"], (x0 + x1) / 2, (y0 + y1) / 2, None, (x1 - x0, y1 - y0))]


def draw_plan(ax, level, ox=0.0):
    for r in H.ROOMS[level]:
        if r.get("kind") == "outdoor":
            for rc in G.decompose(r):
                ax.add_patch(Rectangle((rc[0], rc[1]), rc[2] - rc[0], rc[3] - rc[1], fill=False,
                                       ls=(0, (6, 4)), lw=0.6, ec="#555"))
    for b in cut_boxes(level):
        ax.add_patch(Rectangle((b["x"], b["y"]), b["w"], b["d"], fc="#222", ec="#222", lw=0.3, zorder=3))
    for b in glass_boxes(level):
        ax.add_patch(Rectangle((b["x"], b["y"]), max(b["w"], 0.15), max(b["d"], 0.15),
                               fc="#9ad0e6" if b["mat"] == "glass" else "#bbb", ec="#246", lw=0.4, zorder=4))
    for o in DATA[level][2]:
        if o["kind"] == "door":
            r = o["w"]
            if o["axis"] == "h":
                ax.plot([o["pos"] - r / 2, o["pos"] - r / 2], [o["c"], o["c"] + r], c="#333", lw=0.5, zorder=5)
                ax.add_patch(Arc((o["pos"] - r / 2, o["c"]), 2 * r, 2 * r, theta1=0, theta2=90, lw=0.4, zorder=5))
            else:
                ax.plot([o["c"], o["c"] + r], [o["pos"] - r / 2, o["pos"] - r / 2], c="#333", lw=0.5, zorder=5)
                ax.add_patch(Arc((o["c"], o["pos"] - r / 2), 2 * r, 2 * r, theta1=0, theta2=90, lw=0.4, zorder=5))
    for b in DATA[level][0]:
        if b["mat"] == "stair":
            ax.add_patch(Rectangle((b["x"], b["y"]), b["w"], b["d"], fill=False, ec="#444", lw=0.35, zorder=2))
    for _, (fx0, fy0, fx1, fy1), label in G.furniture(level):
        if label:
            ax.add_patch(Rectangle((fx0, fy0), fx1 - fx0, fy1 - fy0, fc="none", ec="#777", lw=0.5, ls="--", zorder=2))
            ax.text((fx0 + fx1) / 2, (fy0 + fy1) / 2, label, fontsize=3, ha="center", va="center", color="#777")
    for r in H.ROOMS[level]:
        for name, x, y, area, dims in room_label(r):
            if r.get("stair") and level != "basement" and False:
                continue
            txt = name
            if dims:
                txt += f"\n{fmt(dims[0])} x {fmt(dims[1])}"
            elif area:
                txt += f"\n{area:.0f} sq ft"
            ax.text(x, y, txt, fontsize=5, ha="center", va="center", zorder=6, fontweight="bold")
        for zname, zr in r.get("zones", []):
            ax.add_patch(Rectangle((zr[0], zr[1]), zr[2] - zr[0], zr[3] - zr[1], fill=False,
                                   ec="#999", lw=0.4, ls=":", zorder=1))
            ax.text((zr[0] + zr[2]) / 2, (zr[1] + zr[3]) / 2 - (3 if zname == "Kitchen" else 0), zname.upper(),
                    fontsize=6, ha="center", va="center", color="#666", zorder=1)


def sheet_frame(fig, title, sheet, scale="1/8\" = 1'-0\""):
    fig.patches.append(Rectangle((0.01, 0.01), 0.98, 0.98, transform=fig.transFigure, fill=False, lw=1.2, ec="k"))
    fig.text(0.02, 0.965, title, fontsize=14, fontweight="bold")
    fig.text(0.02, 0.945, f"ForeverHome  -  Scale {scale}", fontsize=8)
    fig.text(0.98, 0.965, sheet, fontsize=14, fontweight="bold", ha="right")
    fig.text(0.98, 0.945, DRAFT, fontsize=8, ha="right", color="#b00")


def write_plans():
    path = os.path.join(EXP, "ForeverHome_plans.pdf")
    W, Hh = 17, 11
    with PdfPages(path) as pdf:
        for i, level in enumerate(["basement", "main", "upper"]):
            fig = plt.figure(figsize=(W, Hh))
            x0, x1, y0, y1 = -4, 98, -4, 66
            axw, axh = (x1 - x0) / 8, (y1 - y0) / 8
            ax = fig.add_axes([0.5 - axw / 2 / W, 0.44 - axh / 2 / Hh, axw / W, axh / Hh])
            ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.axis("off")
            draw_plan(ax, level)
            ax.annotate("N", (2, 62), fontsize=12, fontweight="bold", ha="center")
            sheet_frame(fig, LEVEL_TITLES[level], f"A-{i + 1}.0")
            pdf.savefig(fig); plt.close(fig)
        write_elev_pages(pdf)
    print("wrote", path)


MAT_COL = {"wallExt": "#d8d2c4", "wallInt": "#d8d2c4", "glass": "#9ad0e6", "garageDoor": "#b9bcc0", "doorExt": "#6b4f3a"}


def elevation(ax, view):
    ax.set_aspect("equal"); ax.axis("off")
    items = []
    for level in H.LEVELS:
        for b in DATA[level][0]:
            if b["mat"] in MAT_COL and b["z"] + b["h"] > 0 and not b.get("furn"):
                items.append(b)
    if view in ("S", "N"):
        key = lambda b: (b["x"], b["w"])
        flip = view == "N"
        items.sort(key=(lambda b: b["y"]) if view == "N" else (lambda b: -b["y"]))   # far first
    else:
        key = lambda b: (b["y"], b["d"])
        flip = view == "E"
        items.sort(key=(lambda b: b["x"]) if view == "E" else (lambda b: -b["x"]))
    xs = []
    for b in items:
        u0, du = key(b)
        z0 = max(b["z"], 0); dz = b["z"] + b["h"] - z0
        if flip:
            u0 = -(u0 + du)
        xs += [u0, u0 + du]
        ax.add_patch(Rectangle((u0, z0), du, dz, fc=MAT_COL[b["mat"]], ec="#333", lw=0.25))
    ax.plot([min(xs) - 5, max(xs) + 5], [0, 0], c="#444", lw=1.2)
    ax.set_xlim(min(xs) - 6, max(xs) + 6); ax.set_ylim(-3, 24)
    ax.set_title({"S": "SOUTH (FRONT) ELEVATION", "N": "NORTH (REAR) ELEVATION",
                  "E": "EAST ELEVATION", "W": "WEST ELEVATION"}[view], fontsize=8, loc="left")


def write_elev_pages(pdf):
    for pg, views in enumerate([("S", "N"), ("E", "W")]):
        fig = plt.figure(figsize=(17, 11))
        for k, v in enumerate(views):
            ax = fig.add_axes([0.05, 0.50 - k * 0.42 + 0.03, 0.9, 0.38])
            elevation(ax, v)
        sheet_frame(fig, "EXTERIOR ELEVATIONS", f"A-{4 + pg}.0", scale="NTS (roof not yet modeled)")
        pdf.savefig(fig); plt.close(fig)


def write_dxf():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.FT
    msp = doc.modelspace()
    for name, col in (("WALL", 7), ("GLAZ", 5), ("DOOR", 3), ("TEXT", 2), ("FIXT", 8)):
        for i in range(1, 4):
            doc.layers.add(f"L{i}-A-{name}", color=col)
    for i, level in enumerate(["basement", "main", "upper"], 1):
        dx = (i - 1) * 120.0
        for b in cut_boxes(level):
            msp.add_lwpolyline([(b["x"] + dx, b["y"]), (b["x"] + b["w"] + dx, b["y"]),
                                (b["x"] + b["w"] + dx, b["y"] + b["d"]), (b["x"] + dx, b["y"] + b["d"])],
                               close=True, dxfattribs={"layer": f"L{i}-A-WALL"})
        for b in glass_boxes(level):
            msp.add_lwpolyline([(b["x"] + dx, b["y"]), (b["x"] + b["w"] + dx, b["y"]),
                                (b["x"] + b["w"] + dx, b["y"] + max(b["d"], .1)), (b["x"] + dx, b["y"] + max(b["d"], .1))],
                               close=True, dxfattribs={"layer": f"L{i}-A-GLAZ"})
        for _, (fx0, fy0, fx1, fy1), label in G.furniture(level):
            if label:
                msp.add_lwpolyline([(fx0 + dx, fy0), (fx1 + dx, fy0), (fx1 + dx, fy1), (fx0 + dx, fy1)],
                                   close=True, dxfattribs={"layer": f"L{i}-A-FIXT"})
        for r in H.ROOMS[level]:
            for name, x, y, area, dims in room_label(r):
                t = name + (f" {fmt(dims[0])}x{fmt(dims[1])}" if dims else "")
                msp.add_text(t, height=0.8, dxfattribs={"layer": f"L{i}-A-TEXT"}).set_placement((x + dx - len(t) * .3, y))
        msp.add_text(LEVEL_TITLES[level] + "  (DRAFT)", height=2,
                     dxfattribs={"layer": f"L{i}-A-TEXT"}).set_placement((dx, -8))
    path = os.path.join(EXP, "ForeverHome_plans.dxf")
    doc.saveas(path)
    print("wrote", path)


def write_schedules():
    os.makedirs(os.path.join(EXP, "schedules"), exist_ok=True)
    rows, totals = [], {}
    for level in H.LEVELS:
        for r in H.ROOMS[level]:
            x0, y0, x1, y1 = G.bounds(r)
            area = G.room_area(r)
            rows.append([level, r["name"], f"{x1 - x0:g}", f"{y1 - y0:g}", f"{area:g}", r.get("note", "")])
            if r["name"] not in NOT_LIVING and r.get("kind") != "outdoor":
                totals[level] = totals.get(level, 0) + area
    with open(os.path.join(EXP, "schedules", "rooms.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "room", "bbox_width_ft", "bbox_depth_ft", "area_sqft", "note"])
        w.writerows(rows)
    with open(os.path.join(EXP, "schedules", "openings.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "kind", "width_ft", "height_ft", "sill_ft", "x_or_y_position_ft", "wall_axis"])
        for level in H.LEVELS:
            for o in DATA[level][2]:
                w.writerow([level, o["kind"], f"{o['w']:g}", f"{o['h']:g}", f"{o['sill']:g}", f"{o['pos']:.1f}", o["axis"]])
    return totals


def write_model_json():
    out = {"levels": {}, "rooms": []}
    for level, (elev, height) in H.LEVELS.items():
        boxes = []
        for b in DATA[level][0]:
            boxes.append([round(b[k], 3) for k in ("x", "y", "z", "w", "d", "h")] +
                         [b["mat"], 1 if b["c"] else 0, b.get("label", "")])
        out["levels"][level] = {"elev": elev, "height": height, "boxes": boxes}
        for r in H.ROOMS[level]:
            for name, x, y, area, dims in room_label(r):
                out["rooms"].append({"level": level, "name": name, "x": round(x, 2), "y": round(y, 2)})
    path = os.path.join(WEB, "model.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(EXP, exist_ok=True)
    totals = write_schedules()
    write_plans()
    write_dxf()
    write_model_json()
    export.write(DATA, EXP)
    print("finished sq ft by level:", {k: round(v) for k, v in totals.items()}, "total", round(sum(totals.values())))
