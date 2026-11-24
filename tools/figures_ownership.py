"""Figures F11 and F12 from the ownership and event register.

F11  Schematic map of plant openings and closures: German plants, and Chinese
     plants built in Europe. Coordinates are approximate and stated as such,
     because the figure is about geography of decisions, not cartography.
F12  Ownership timeline of the events that changed who controls whom, taken
     from data/reference/oem_history.csv.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "data" / "reference" / "oem_history.csv"
FIG = ROOT / "figures"

NAVY = "#1f3b57"
RED = "#c8553d"
GREEN = "#588157"
ORANGE = "#bc6c25"
GREY = "#666666"

PLANTS = [
    ("Wolfsburg", 52.42, 10.79, "German", "open", (6, 6)),
    ("Emden", 53.36, 7.19, "German", "open", (6, 6)),
    ("Dresden", 51.05, 13.74, "German", "closed 2025", (12, 6)),
    ("Zwickau", 50.72, 12.50, "German", "converted 2019", (-14, -26)),
    ("Ingolstadt", 48.77, 11.42, "German", "open", (6, -16)),
    ("Brussels", 50.85, 4.35, "German", "closed 2025", (6, 6)),
    ("Szeged", 46.25, 20.15, "Chinese", "from 2026", (-22, -22)),
    ("Debrecen", 47.53, 21.63, "Chinese", "from 2025", (6, 6)),
    ("Barcelona", 41.38, 2.17, "Chinese", "from 2026", (6, 6)),
    ("Tychy", 50.13, 18.99, "Chinese", "from 2024", (6, 6)),
    ("Turin", 45.05, 7.67, "German", "open", (6, 6)),
]


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.color": "#e5e5e5",
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
        }
    )


def figure_f11() -> Path:
    fig, axis = plt.subplots(figsize=(11, 7))
    for name, lat, lon, owner, status, offset in PLANTS:
        colour = NAVY if owner == "German" else RED
        marker = "o" if "open" in status or "from" in status else "X"
        size = 120 if owner == "German" else 150
        axis.scatter(lon, lat, s=size, color=colour, marker=marker, zorder=3, edgecolor="white", linewidth=1)
        axis.annotate(
            f"{name}\n{status}",
            xy=(lon, lat),
            xytext=offset,
            textcoords="offset points",
            fontsize=8,
            color="#222222",
        )
    axis.set_xlim(-6, 25)
    axis.set_ylim(38, 56)
    axis.set_xlabel("longitude")
    axis.set_ylabel("latitude")
    axis.set_title("Plants that matter for the German Chinese comparison, schematic positions")
    axis.text(
        0.01,
        0.02,
        "navy: German owned plants, red: Chinese owned plants in Europe, X marks a closure",
        transform=axis.transAxes,
        fontsize=8,
        color=GREY,
    )
    fig.tight_layout()
    target = FIG / "fig11_plant_map.png"
    fig.savefig(target, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return target


def figure_f12() -> Path:
    # Each tuple is row label, start year, end year, segment label, colour.
    # Years and owners follow data/reference/oem_history.csv, ids 5, 6, 7, 13,
    # 16, 17, 42 and 57.
    # Each tuple is row label, start year, end year, segment label, colour and
    # vertical label offset in points, zero meaning the label sits inside the
    # bar. Years and owners follow data/reference/oem_history.csv, ids 5, 6, 7,
    # 13, 16, 17, 42 and 57.
    segments = [
        ("Auto Union / Audi", 1932, 1958, "independent, later Soviet controlled", "#9e9e9e", 0),
        ("Auto Union / Audi", 1958, 1965, "Daimler-Benz", "#6d8ba6", -28),
        ("Auto Union / Audi", 1965, 1969, "Volkswagen", NAVY, 30),
        ("Auto Union / Audi", 1969, 1985, "Audi NSU", "#35597a", 0),
        ("Auto Union / Audi", 1985, 2026, "Audi / VW Group", "#12293d", 0),
        ("Lamborghini", 1963, 1987, "independent, receivership 1978", "#9e9e9e", 0),
        ("Lamborghini", 1987, 1994, "Chrysler", RED, 28),
        ("Lamborghini", 1994, 1998, "Megatech", ORANGE, 28),
        ("Lamborghini", 1998, 2026, "Audi / VW Group", "#12293d", 0),
        ("Italdesign Giugiaro", 1968, 2010, "independent", "#9e9e9e", 0),
        ("Italdesign Giugiaro", 2010, 2026, "Volkswagen", NAVY, 0),
        ("Italdesign Giugiaro", 2026, 2030, "UST majority", "#7b4b94", 28),
        ("Fiat to Stellantis", 1899, 2014, "Fiat", "#4f6f52", 0),
        ("Fiat to Stellantis", 2014, 2021, "Fiat Chrysler", "#3f5d43", 28),
        ("Fiat to Stellantis", 2021, 2030, "Stellantis", "#28402c", 0),
    ]
    rows = ["Auto Union / Audi", "Lamborghini", "Italdesign Giugiaro", "Fiat to Stellantis"]
    fig, axis = plt.subplots(figsize=(12, 6.2))
    for index, row in enumerate(rows):
        for name, start, end, label, colour, offset in segments:
            if name != row:
                continue
            axis.barh(index, end - start, left=start, height=0.5, color=colour, edgecolor="white", linewidth=1)
            if offset == 0:
                axis.text(
                    (start + end) / 2,
                    index,
                    label,
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white" if colour != "#9e9e9e" else "#222222",
                )
            else:
                axis.annotate(
                    label,
                    xy=((start + end) / 2, index),
                    xytext=(0, offset),
                    textcoords="offset points",
                    ha="center",
                    va="center",
                    fontsize=7.0,
                    color="#222222",
                )
    axis.set_yticks(range(len(rows)))
    axis.set_yticklabels(rows, fontsize=9)
    axis.set_xlim(1930, 2042)
    axis.set_ylim(-0.75, len(rows) - 0.25)
    axis.set_xlabel("year")
    axis.set_title("Ownership spells that the model treats as regimes, not as noise")
    axis.text(
        0.01,
        0.02,
        "source: data/reference/oem_history.csv, entries 5, 6, 7, 13, 16, 17, 42, 57",
        transform=axis.transAxes,
        fontsize=7.5,
        color=GREY,
    )
    fig.tight_layout()
    target = FIG / "fig12_ownership_timeline.png"
    fig.savefig(target, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return target


def figure_f14() -> Path:
    """Voting rights in Volkswagen AG at 31 December 2025.

    Values are taken from the Volkswagen Group Annual Report 2025, page
    Shareholder structure, accessed 24 November 2026. Only voting rights are
    plotted, because the annual report states voting rights in the text and
    shows capital shares only as a chart.
    """
    owners = ["Porsche SE", "Lower Saxony", "Qatar Holding", "free float"]
    colours = [NAVY, GREEN, ORANGE, "#c9c9c9"]
    votes = [53.3, 20.0, 17.0, 9.7]
    fig, axis = plt.subplots(figsize=(10, 2.9))
    left = 0.0
    for value, colour, owner in zip(votes, colours, owners, strict=True):
        axis.barh(0, value, left=left, color=colour, edgecolor="white", linewidth=1.5, height=0.5)
        axis.text(
            left + value / 2,
            0,
            f"{owner}\n{value:.1f}",
            ha="center",
            va="center",
            fontsize=7.5,
            color="white" if colour != "#c9c9c9" else "#222222",
        )
        left += value
    axis.set_yticks([])
    axis.set_xlim(0, 100)
    axis.set_ylim(-0.55, 0.95)
    axis.set_xlabel("percent of voting rights")
    axis.set_title("Four holders decide Volkswagen, voting rights at 31 December 2025")
    for threshold, label in ((20, "blocking minority"), (75, "supermajority")):
        axis.axvline(threshold, color=GREY, linewidth=0.8, linestyle="--")
        axis.text(threshold + 0.5, 0.30, label, fontsize=7, color=GREY, rotation=90, va="bottom")
    axis.text(
        0.0,
        -0.42,
        "source: Volkswagen Group Annual Report 2025, shareholder structure, accessed 24 November 2026",
        transform=axis.transAxes,
        fontsize=7.5,
        color=GREY,
    )
    fig.tight_layout()
    target = FIG / "fig14_control_layers.png"
    fig.savefig(target, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return target


def main() -> int:
    style()
    FIG.mkdir(parents=True, exist_ok=True)
    for path in (figure_f11(), figure_f12(), figure_f14()):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
