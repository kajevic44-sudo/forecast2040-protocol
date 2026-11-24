"""Historical figures F09 and F10 from data already in the repository.

F09  German equity index in real terms, 1870 to 2020, with every drawdown deeper
     than twenty percent shaded and labelled.
F10  Volkswagen Group deliveries in China, 1987 to 2025, with the four phases
     of the market marked.

Both figures use only files that already exist, so they can be regenerated
without any network access.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TIDY = ROOT / "data" / "historical" / "tidy"
RAW = ROOT / "data" / "raw"
FIG = ROOT / "figures"

NAVY = "#1f3b57"
RED = "#c8553d"
GREEN = "#588157"
GREY = "#666666"


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.color": "#dddddd",
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
        }
    )


def figure_f09() -> Path:
    frame = pd.read_csv(TIDY / "jst_germany.csv").dropna(subset=["eq_tr"]).sort_values("year")
    index = (1.0 + frame["eq_tr"].to_numpy()).cumprod()
    years = frame["year"].to_numpy()
    drawdowns = pd.read_csv(TIDY / "de_equity_drawdowns.csv")

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(11, 7.5), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    top.plot(years, index, color=NAVY, linewidth=1.8)
    top.set_yscale("log")
    top.set_ylabel("index, logarithmic scale, 1870 equals 1")
    top.set_title("German equities in real terms, 1870 to 2020")
    running_peak = np.maximum.accumulate(index)
    drawdown = index / running_peak - 1.0
    bottom.fill_between(years, drawdown * 100, 0, color=RED, alpha=0.35, linewidth=0)
    bottom.set_ylabel("drawdown, percent")
    bottom.set_xlabel("year")

    for _, row in drawdowns.iterrows():
        top.axvspan(row["peak_year"], row["trough_year"], color=RED, alpha=0.08, linewidth=0)
        bottom.annotate(
            f"{int(row['trough_year'])}: {row['depth_pct']:.0f}%",
            xy=(row["trough_year"], row["depth_pct"]),
            xytext=(3, -8),
            textcoords="offset points",
            fontsize=7,
            color=GREY,
        )
    top.text(
        0.01,
        0.93,
        "shaded periods are drawdowns deeper than twenty percent",
        transform=top.transAxes,
        fontsize=9,
        color=GREY,
    )
    fig.tight_layout()
    target = FIG / "fig09_german_drawdowns.png"
    fig.savefig(target, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return target


def figure_f10() -> Path:
    frame = pd.read_csv(RAW / "vw_group_china_deliveries.csv")
    frame = frame.dropna(subset=["value"]).sort_values("year")
    years = frame["year"].to_numpy(dtype=int)
    values = frame["value"].to_numpy(dtype=float) / 1e6

    phases = [
        (1987, 2000, "entry, joint ventures founded", "#e8e4d9"),
        (2000, 2009, "pre boom expansion", "#d9e2ec"),
        (2009, 2015, "stimulus boom", "#cfe3cf"),
        (2015, 2019, "plateau", "#f2e8cf"),
        (2019, 2025, "decline", "#f4d6cf"),
    ]
    fig, axis = plt.subplots(figsize=(11, 5.5))
    for start, end, label, colour in phases:
        axis.axvspan(start, end, color=colour, alpha=0.7, linewidth=0)
        axis.text(
            (start + end) / 2,
            max(values) * 1.02,
            label,
            ha="center",
            fontsize=8,
            color="#333333",
        )
    axis.plot(years, values, color=NAVY, linewidth=2.2, marker="o", markersize=2.5)
    peak_year = int(years[np.argmax(values)])
    peak_value = float(values.max())
    axis.annotate(
        f"peak {peak_value:.2f} million in {peak_year}",
        xy=(peak_year, peak_value),
        xytext=(-90, 18),
        textcoords="offset points",
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": GREY, "linewidth": 0.8},
    )
    axis.set_ylabel("millions of vehicles")
    axis.set_xlabel("year")
    axis.set_title("Volkswagen Group deliveries in China, 1987 to 2025, four phases")
    axis.set_ylim(0, max(values) * 1.12)
    fig.tight_layout()
    target = FIG / "fig10_china_phases.png"
    fig.savefig(target, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return target


def main() -> int:
    style()
    FIG.mkdir(parents=True, exist_ok=True)
    for path in (figure_f09(), figure_f10()):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
