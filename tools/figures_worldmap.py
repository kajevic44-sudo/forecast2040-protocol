"""Figure F17, world map of plants and cell capacity that matter for the thesis.

Country outlines come from Natural Earth, 1 to 110 million scale, public domain,
downloaded 24 November 2026. Coordinates are published plant locations rounded
to two decimals, about one kilometre, which is enough at page size. The dashed
curves mark the two corridors the argument follows, Wolfsburg to Beijing and
Wolfsburg to Ningde. They are drawn as quadratic curves only to lift them off
the surface, not as transport routes.

A single world frame cannot hold eleven European points without collisions, so
the figure uses a locator map and an enlarged European frame, the standard
solution in an atlas.

Output  figures/fig17_world_map.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MapPolygon

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "data" / "reference" / "geo" / "ne_110m_admin_0_countries.geojson"
FIG = ROOT / "figures"

NAVY = "#1f3b57"
RED = "#c8553d"
GREEN = "#588157"
ORANGE = "#bc6c25"
GREY = "#666666"
LAND = "#e8e6e1"
SEA = "#f7f6f3"

EUROPE = [
    ("Wolfsburg", 10.79, 52.42, "German plant", (8, 6)),
    ("Emden", 7.21, 53.37, "German plant", (-34, 8)),
    ("Dresden", 13.74, 51.05, "German plant", (8, 8)),
    ("Ingolstadt", 11.42, 48.77, "German plant", (8, -12)),
    ("Munich", 11.58, 48.14, "German plant", (8, -24)),
    ("Stuttgart", 9.18, 48.78, "German plant", (-52, 2)),
    ("Brussels", 4.35, 50.85, "German plant", (-50, 4)),
    ("Turin", 7.69, 45.07, "German plant", (8, -12)),
    ("Tychy", 18.99, 50.13, "Chinese plant in Europe", (8, 6)),
    ("Szeged", 20.15, 46.25, "Chinese plant in Europe", (8, -12)),
    ("Debrecen", 21.62, 47.53, "Chinese plant in Europe", (-52, 8)),
    ("Barcelona", 2.17, 41.39, "Chinese plant in Europe", (8, -12)),
    ("Erfurt", 11.03, 50.98, "Battery cell plant", (-46, -12)),
    ("Salzgitter", 10.33, 52.15, "Battery cell plant", (-64, -6)),
]

ASIA = [
    ("Beijing", 116.41, 39.90, "Chinese plant or office", (-14, 12)),
    ("Changchun", 125.32, 43.82, "Chinese plant or office", (8, 6)),
    ("Shenyang", 123.43, 41.80, "Chinese plant or office", (8, -10)),
    ("Shanghai", 121.47, 31.23, "Chinese plant or office", (8, 2)),
    ("Hefei", 117.23, 31.82, "Chinese plant or office", (-42, -4)),
    ("Ningde", 119.52, 26.66, "Battery cell plant", (8, -10)),
]

COLOURS = {
    "German plant": NAVY,
    "Chinese plant in Europe": RED,
    "Chinese plant or office": ORANGE,
    "Battery cell plant": GREEN,
}


def draw_countries(axis: plt.Axes) -> None:
    data = json.loads(GEO.read_text())
    for feature in data["features"]:
        geometry = feature["geometry"]
        if geometry is None:
            continue
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            ring = polygon[0]
            if len(ring) < 3:
                continue
            axis.add_patch(
                MapPolygon(ring, closed=True, facecolor=LAND, edgecolor="#c9c6bf", linewidth=0.4, zorder=1)
            )


def draw_points(axis: plt.Axes, points: list[tuple[str, float, float, str, tuple[int, int]]], size: float, font: float) -> None:
    for name, lon, lat, group, offset in points:
        axis.scatter(lon, lat, s=size, color=COLOURS[group], edgecolor="white", linewidth=0.8, zorder=4)
        axis.annotate(name, xy=(lon, lat), xytext=offset, textcoords="offset points", fontsize=font, zorder=5)


def main() -> int:
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(13.5, 6.9))

    world = fig.add_axes((0.02, 0.14, 0.96, 0.74))
    world.set_facecolor(SEA)
    draw_countries(world)
    for start, end, colour in (
        ((10.79, 52.42), (116.41, 39.90), NAVY),
        ((10.79, 52.42), (119.52, 26.66), GREEN),
    ):
        midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 14)
        world.plot(
            [start[0], midpoint[0], end[0]],
            [start[1], midpoint[1], end[1]],
            color=colour,
            linewidth=1.1,
            linestyle=(0, (4, 3)),
            zorder=2,
        )
    draw_points(world, [point for point in ASIA], 34, 7)
    world.scatter(10.79, 52.42, s=60, color=NAVY, edgecolor="white", linewidth=1.0, zorder=4)
    world.annotate("Wolfsburg", xy=(10.79, 52.42), xytext=(-46, 8), textcoords="offset points", fontsize=7.5, zorder=5)
    world.set_xlim(-170, 180)
    world.set_ylim(-56, 78)
    world.set_aspect("equal", adjustable="box")
    world.set_xticks([])
    world.set_yticks([])
    for spine in world.spines.values():
        spine.set_visible(False)
    world.add_patch(
        plt.Rectangle((1.0, 40.0), 23.0, 16.0, fill=False, edgecolor=GREY, linewidth=0.9, linestyle="--", zorder=6)
    )

    europe = fig.add_axes((0.06, 0.17, 0.30, 0.31))
    europe.set_facecolor(SEA)
    draw_countries(europe)
    draw_points(europe, EUROPE, 40, 7)
    europe.set_xlim(1.0, 24.0)
    europe.set_ylim(40.0, 56.0)
    europe.set_xticks([])
    europe.set_yticks([])
    for spine in europe.spines.values():
        spine.set_edgecolor(GREY)
        spine.set_linewidth(0.9)
    europe.set_title("enlarged, central Europe", fontsize=8, color=GREY, loc="left", pad=2)

    handles = [
        plt.Line2D([], [], marker="o", linestyle="", color=COLOURS[key], label=key, markersize=6)
        for key in COLOURS
    ]
    fig.legend(handles=handles, fontsize=8.5, frameon=False, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.045))
    fig.text(0.02, 0.945, "Where the German and Chinese car industries meet", fontsize=13, fontweight="bold")
    fig.text(
        0.02,
        0.008,
        "boundaries Natural Earth 110m, public domain, accessed 24 November 2026; plant coordinates from company disclosures",
        fontsize=7,
        color=GREY,
    )
    fig.savefig(FIG / "fig17_world_map.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {FIG / 'fig17_world_map.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
