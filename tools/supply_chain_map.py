"""Figure 21: the global supply chain of the Volkswagen Group, drawn from coordinates.

Every node carries an explicit longitude and latitude. Every flow is a quadratic
Bezier curve between two nodes, so the picture can be redrawn from the table
without manual drawing. Country outlines come from Natural Earth 110m, stored in
data/geo, and are context only. Europe is repeated in an inset because the
German and Central European plants sit within a few degrees of each other.

Run with /usr/bin/python3 tools/supply_chain_map.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "data" / "geo" / "ne_110m_countries.geojson"
OUT = ROOT / "figures" / "fig21_supply_chain_map.png"

NAVY = "#1C2E3A"
TEAL = "#12857F"
GOLD = "#C3955E"
BROWN = "#886133"
GREY = "#5F6E75"
LAND = "#E9EEEF"
EDGE = "#C9D2D5"
SEA = "#F7F9F9"

TIERS = {
    "extraction": ("Extraction", BROWN),
    "processing": ("Processing", GOLD),
    "components": ("Components", TEAL),
    "assembly": ("Assembly", NAVY),
    "market": ("Market", GREY),
}

NODES = {
    "Atacama": (-69.13, -23.86, "extraction"),
    "Perth": (115.86, -31.95, "extraction"),
    "Jakarta": (106.85, -6.21, "processing"),
    "Jadar": (19.10, 44.55, "extraction"),
    "Bayan Obo": (109.97, 41.77, "extraction"),
    "Antwerp": (4.40, 51.22, "processing"),
    "Shanghai": (121.47, 31.23, "components"),
    "Seoul": (126.98, 37.57, "components"),
    "Taipei": (121.57, 25.03, "components"),
    "Bengaluru": (77.59, 12.97, "components"),
    "Tel Aviv": (34.78, 32.09, "components"),
    "Kassel": (9.49, 51.31, "components"),
    "Salzgitter": (10.33, 52.15, "components"),
    "Brunswick": (10.52, 52.27, "components"),
    "Wolfsburg": (10.79, 52.42, "assembly"),
    "Zwickau": (12.50, 50.72, "assembly"),
    "Ingolstadt": (11.43, 48.77, "assembly"),
    "Neckarsulm": (9.22, 49.19, "assembly"),
    "Stuttgart": (9.18, 48.78, "assembly"),
    "Munich": (11.58, 48.14, "assembly"),
    "Gyor": (17.63, 47.69, "assembly"),
    "Bratislava": (17.11, 48.15, "assembly"),
    "Mlada Boleslav": (14.90, 50.41, "assembly"),
    "Poznan": (16.93, 52.41, "assembly"),
    "Pamplona": (-1.64, 42.81, "assembly"),
    "Martorell": (1.93, 41.47, "assembly"),
    "Palmela": (-8.90, 38.57, "assembly"),
    "Brussels": (4.35, 50.85, "assembly"),
    "Chattanooga": (-85.31, 35.05, "assembly"),
    "Puebla": (-98.20, 19.04, "assembly"),
    "Sao Paulo": (-46.63, -23.55, "assembly"),
    "Uitenhage": (25.40, -33.77, "assembly"),
    "Changchun": (125.32, 43.82, "assembly"),
    "Hefei": (117.23, 31.82, "assembly"),
    "Urumqi": (87.62, 43.83, "assembly"),
    "Bremerhaven": (8.58, 53.54, "market"),
    "Lagos": (3.38, 6.52, "market"),
    "Accra": (-0.19, 5.60, "market"),
    "Casablanca": (-7.59, 33.57, "market"),
    "Alexandria": (29.92, 31.20, "market"),
    "Istanbul": (28.98, 41.01, "market"),
    "Belgrade": (20.46, 44.79, "market"),
    "Riyadh": (46.68, 24.71, "market"),
}

FLOWS = [
    ("Atacama", "Antwerp"), ("Perth", "Antwerp"), ("Jakarta", "Shanghai"),
    ("Bayan Obo", "Shanghai"), ("Antwerp", "Salzgitter"), ("Salzgitter", "Wolfsburg"),
    ("Brunswick", "Wolfsburg"), ("Kassel", "Wolfsburg"), ("Shanghai", "Wolfsburg"),
    ("Seoul", "Wolfsburg"), ("Taipei", "Wolfsburg"), ("Bengaluru", "Wolfsburg"),
    ("Tel Aviv", "Wolfsburg"), ("Wolfsburg", "Zwickau"), ("Wolfsburg", "Ingolstadt"),
    ("Wolfsburg", "Neckarsulm"), ("Wolfsburg", "Stuttgart"), ("Wolfsburg", "Munich"),
    ("Wolfsburg", "Gyor"), ("Wolfsburg", "Bratislava"), ("Wolfsburg", "Mlada Boleslav"),
    ("Wolfsburg", "Poznan"), ("Wolfsburg", "Pamplona"), ("Wolfsburg", "Martorell"),
    ("Wolfsburg", "Palmela"), ("Wolfsburg", "Brussels"), ("Wolfsburg", "Chattanooga"),
    ("Wolfsburg", "Puebla"), ("Wolfsburg", "Sao Paulo"), ("Wolfsburg", "Uitenhage"),
    ("Wolfsburg", "Changchun"), ("Wolfsburg", "Hefei"), ("Wolfsburg", "Urumqi"),
    ("Wolfsburg", "Bremerhaven"), ("Bremerhaven", "Lagos"), ("Bremerhaven", "Accra"),
    ("Bremerhaven", "Casablanca"), ("Bremerhaven", "Alexandria"),
    ("Bremerhaven", "Istanbul"), ("Bremerhaven", "Belgrade"), ("Urumqi", "Riyadh"),
]

EUROPE = {
    "Antwerp", "Kassel", "Salzgitter", "Brunswick", "Wolfsburg", "Zwickau",
    "Ingolstadt", "Neckarsulm", "Stuttgart", "Munich", "Gyor", "Bratislava",
    "Mlada Boleslav", "Poznan", "Pamplona", "Martorell", "Palmela", "Brussels",
    "Bremerhaven", "Belgrade", "Jadar",
}

# Only the assembly plants and the mining case are labelled in the inset. The
# component plants remain visible as dots, which keeps the panel readable.
INSET_LABELS = {
    "Wolfsburg", "Zwickau", "Ingolstadt", "Neckarsulm", "Stuttgart", "Munich",
    "Gyor", "Bratislava", "Mlada Boleslav", "Poznan", "Pamplona", "Martorell",
    "Palmela", "Brussels", "Bremerhaven", "Belgrade", "Jadar",
}

# Offsets are in degrees and are tuned so that no two labels collide in the inset.
INSET_OFFSETS = {
    "Bremerhaven": (0.30, 0.35), "Wolfsburg": (0.30, 0.45), "Poznan": (0.30, 0.20),
    "Mlada Boleslav": (0.30, -0.55), "Zwickau": (0.30, -0.55), "Ingolstadt": (0.30, 0.20),
    "Neckarsulm": (-2.5, 0.15), "Stuttgart": (-2.0, -0.55), "Munich": (0.30, -0.55),
    "Brussels": (-2.1, 0.20), "Bratislava": (0.30, 0.20), "Gyor": (0.30, -0.55),
    "Pamplona": (-2.7, -0.45), "Martorell": (0.30, -0.55), "Palmela": (-2.5, -0.55),
    "Belgrade": (0.30, -0.55), "Jadar": (-2.1, -0.55),
}


def load_shapes() -> list[list[tuple[float, float]]]:
    data = json.loads(GEO.read_text())
    shapes = []
    for feature in data["features"]:
        geom = feature["geometry"]
        if geom is None:
            continue
        if geom["type"] == "Polygon":
            rings = geom["coordinates"]
        elif geom["type"] == "MultiPolygon":
            rings = [ring for poly in geom["coordinates"] for ring in poly]
        else:
            continue
        for ring in rings:
            shapes.append([(float(lon), float(lat)) for lon, lat in ring])
    return shapes


SHAPES = load_shapes()


def draw_countries(ax, linewidth=0.35) -> None:
    for ring in SHAPES:
        codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(ring) - 2) + [MplPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MplPath(ring, codes), facecolor=LAND,
                               edgecolor=EDGE, linewidth=linewidth, zorder=1))


def bezier(start, end, bend=0.16):
    (x1, y1), (x2, y2) = start, end
    dx, dy = x2 - x1, y2 - y1
    cx, cy = (x1 + x2) / 2 - dy * bend, (y1 + y2) / 2 + dx * bend
    return MplPath([(x1, y1), (cx, cy), (x2, y2)],
                   [MplPath.MOVETO, MplPath.CURVE3, MplPath.CURVE3])


def draw_flows(ax, names, linewidth=0.8, alpha=0.55) -> None:
    for source, target in FLOWS:
        if source not in names or target not in names:
            continue
        x1, y1, _ = NODES[source]
        x2, y2, _ = NODES[target]
        ax.add_patch(PathPatch(bezier((x1, y1), (x2, y2)), facecolor="none",
                               edgecolor=TEAL, linewidth=linewidth, alpha=alpha,
                               zorder=2, capstyle="round"))


def draw_nodes(ax, names, scale=1.0, zorder=4) -> None:
    for name in names:
        lon, lat, tier = NODES[name]
        size = (30 if tier == "assembly" else 18) * scale
        ax.scatter([lon], [lat], s=size, color=TIERS[tier][1], edgecolor="white",
                   linewidth=0.6, zorder=zorder)


def main() -> int:
    fig = plt.figure(figsize=(14.2, 7.4), dpi=200)
    fig.patch.set_facecolor(SEA)
    ax = fig.add_axes([0.0, 0.02, 0.695, 0.86])
    ax.set_facecolor(SEA)
    ax.set_xlim(-125, 150)
    ax.set_ylim(-48, 75)
    ax.set_aspect("equal")
    ax.axis("off")

    draw_countries(ax)
    draw_flows(ax, set(NODES))
    draw_nodes(ax, set(NODES))

    world_labels = {n for n in NODES if n not in EUROPE} | {"Wolfsburg"}
    offsets = {
        "Wolfsburg": (1.8, 2.6), "Puebla": (-5.2, -3.4), "Chattanooga": (1.8, -3.0),
        "Sao Paulo": (1.8, -3.2), "Uitenhage": (1.8, -3.2), "Atacama": (1.8, -3.2),
        "Perth": (1.8, -3.4), "Jakarta": (1.8, -3.2), "Shanghai": (1.8, -3.0),
        "Seoul": (1.8, 2.2), "Taipei": (1.8, -3.0), "Bengaluru": (1.8, -3.2),
        "Tel Aviv": (1.8, -2.9), "Bayan Obo": (-9.5, 2.2), "Changchun": (1.8, 2.2),
        "Hefei": (1.8, -3.0), "Urumqi": (-9.5, 2.2), "Lagos": (1.8, -3.0),
        "Accra": (-8.5, -3.2), "Casablanca": (-9.5, -3.2), "Alexandria": (1.8, -3.0),
        "Istanbul": (1.8, 2.0), "Riyadh": (1.8, -3.0), "Belgrade": (1.8, 2.0),
        "Bremerhaven": (1.8, 2.4),
    }
    for name in world_labels:
        lon, lat, tier = NODES[name]
        dx, dy = offsets.get(name, (1.6, 1.6))
        ax.text(lon + dx, lat + dy, name, fontsize=6.6, color=NAVY, zorder=5,
                weight="bold" if tier == "assembly" else "normal",
                family="DejaVu Sans")

    # Europe inset sits in its own column to the right of the world map. Plants
    # carry numbers and the key below the panel carries the names, which is the
    # only way to keep seventeen labels apart at this scale.
    inset = fig.add_axes([0.715, 0.46, 0.275, 0.44])
    inset.set_facecolor("#FFFFFF")
    inset.set_xlim(-10.5, 23.5)
    inset.set_ylim(37.2, 55.6)
    inset.set_aspect("equal")
    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_color("#D5DBDE")
        spine.set_linewidth(0.8)
    draw_countries(inset, linewidth=0.3)
    draw_flows(inset, EUROPE, linewidth=1.0, alpha=0.75)
    draw_nodes(inset, EUROPE, scale=0.9)

    order = ["Wolfsburg", "Zwickau", "Ingolstadt", "Neckarsulm", "Stuttgart",
             "Munich", "Gyor", "Bratislava", "Mlada Boleslav", "Poznan",
             "Pamplona", "Martorell", "Palmela", "Brussels", "Bremerhaven",
             "Belgrade", "Jadar"]
    for index, name in enumerate(order, start=1):
        lon, lat, _ = NODES[name]
        inset.text(lon + 0.45, lat + 0.45, str(index), fontsize=5.6, color=NAVY,
                   zorder=6, weight="bold", family="DejaVu Sans", clip_on=True,
                   ha="center", va="center",
                   bbox=dict(boxstyle="circle,pad=0.18", facecolor="white",
                             edgecolor="none", alpha=0.85))
    inset.text(0.02, 0.97, "Europe, enlarged", transform=inset.transAxes,
               fontsize=7.2, color=GREY, va="top", family="DejaVu Sans")

    for column in range(2):
        chunk = order[column * 9:(column + 1) * 9]
        for row, name in enumerate(chunk):
            number = order.index(name) + 1
            fig.text(0.715 + column * 0.145, 0.405 - row * 0.024,
                     f"{number}  {name}", fontsize=6.3, color=NAVY,
                     family="DejaVu Sans")

    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=6,
                          markerfacecolor=c, markeredgecolor="white", label=label)
               for label, c in TIERS.values()]
    handles.append(plt.Line2D([], [], color=TEAL, linewidth=1.2, alpha=0.7,
                              label="Material and vehicle flow"))
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=7.2,
              ncol=2, handletextpad=0.6, columnspacing=1.2,
              bbox_to_anchor=(0.005, 0.0))

    fig.text(0.012, 0.965, "Volkswagen Group, 2025 network", ha="left", va="top",
             fontsize=11.5, color=NAVY, weight="bold", family="DejaVu Sans")
    fig.text(0.012, 0.925, f"{len(NODES)} nodes, {len(FLOWS)} flows, coordinates from the plant register",
             ha="left", va="top", fontsize=7.6, color=GREY, family="DejaVu Sans")

    fig.savefig(OUT, facecolor=SEA)
    print("saved", OUT, len(NODES), len(FLOWS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
