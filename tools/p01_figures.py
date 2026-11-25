"""Figures for P01 version 2.0.

Author: Armin Kajevic
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

FIG = Path("figures")
FIG.mkdir(exist_ok=True)
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.dpi": 300,
    }
)

NAVY = "#1f3b57"
TEAL = "#2a7f7f"
ORANGE = "#c46a2e"
GREY = "#8a8a8a"
LIGHT = "#d9d2c5"

NAMES = {
    "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus",
    "DE": "Germany", "EL": "Greece", "HR": "Croatia", "IE": "Ireland",
    "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "NL": "Netherlands", "PL": "Poland", "SE": "Sweden", "SI": "Slovenia",
    "TR": "Turkiye",
}


def series_grid(panel: pd.DataFrame) -> None:
    countries = sorted(panel.geo.unique())
    cols, rows = 6, 3
    fig, axes = plt.subplots(rows, cols, figsize=(11.5, 5.6), sharex=True)
    for ax, geo in zip(axes.ravel(), countries):
        block = panel[panel.geo == geo].sort_values("year")
        color = NAVY if geo == "DE" else TEAL
        ax.plot(block.year, block.registrations / 1e6, color=color, lw=1.3)
        ax.axvspan(2008.6, 2009.4, color=LIGHT, alpha=0.8, lw=0)
        ax.axvspan(2019.6, 2021.4, color=LIGHT, alpha=0.8, lw=0)
        ax.set_title(NAMES.get(geo, geo), fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_xlim(1990, 2025)
    for ax in axes.ravel()[len(countries):]:
        ax.axis("off")
    fig.text(0.5, 0.02, "Year", ha="center", fontsize=9)
    fig.text(0.02, 0.5, "New registrations, millions", va="center", rotation=90, fontsize=9)
    fig.suptitle("New passenger car registrations, seventeen European markets", fontsize=11)
    fig.tight_layout(rect=[0.03, 0.04, 1, 0.95])
    fig.savefig(FIG / "fig_p01_series.png", bbox_inches="tight")
    plt.close(fig)


def horizon_profile(macro: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for model, color, width in (
        ("naive", NAVY, 2.4),
        ("holt_damped", TEAL, 1.5),
        ("theta", ORANGE, 1.5),
        ("ridge_lags", GREY, 1.5),
    ):
        block = macro[macro.model == model].sort_values("horizon")
        ax.plot(block.horizon, block.mase, marker="o", ms=3.5, color=color, lw=width, label=model.replace("_", " "))
    ax.set_xlabel("Forecast horizon, years")
    ax.set_ylabel("Mean absolute scaled error")
    ax.set_xticks(range(1, 6))
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("The benchmark stays ahead at every horizon")
    fig.tight_layout()
    fig.savefig(FIG / "fig_p01_horizon.png", bbox_inches="tight")
    plt.close(fig)


def forest(dm: pd.DataFrame) -> None:
    block = dm.sort_values("mean_differential")
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    y = np.arange(len(block))
    ax.errorbar(
        block.mean_differential,
        y,
        xerr=[block.mean_differential - block.ci_low, block.ci_high - block.mean_differential],
        fmt="o",
        color=NAVY,
        ecolor=GREY,
        ms=4,
        lw=1.2,
        capsize=2,
    )
    ax.axvline(0, color=ORANGE, lw=1.2, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([m.replace("_", " ") for m in block.model], fontsize=8)
    ax.set_xlabel("Mean loss differential against the naive benchmark")
    ax.set_title("Two-way clustered intervals, negative means the model is better")
    fig.tight_layout()
    fig.savefig(FIG / "fig_p01_forest.png", bbox_inches="tight")
    plt.close(fig)


def fan(german: pd.DataFrame, projection: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.plot(german.time, german.value / 1e6, color=NAVY, lw=1.5, label="Observed")
    ax.plot(projection.year, projection.point / 1e6, color=TEAL, lw=1.6, label="Benchmark path")
    ax.fill_between(
        projection.year,
        projection.lower_90 / 1e6,
        projection.upper_90 / 1e6,
        color=TEAL,
        alpha=0.15,
        label="90 percent conformal band",
    )
    ax.set_xlim(1990, 2041)
    ax.set_ylabel("New registrations, millions")
    ax.set_xlabel("Year")
    ax.set_title("Germany to 2040, a flat benchmark with an honest band")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.annotate(
        f"{projection.point.iloc[-1]/1e6:.2f} million in 2040",
        xy=(2040, projection.point.iloc[-1] / 1e6),
        xytext=(2029, 3.55),
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8),
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig_p01_fan.png", bbox_inches="tight")
    plt.close(fig)


def country_gain(frame: pd.DataFrame) -> pd.DataFrame:
    per = frame.groupby(["country", "model"]).mase.mean().unstack()
    naive = per["naive"]
    others = per.drop(columns=["naive"]).min(axis=1)
    gain = (1 - others / naive) * 100
    return gain.rename("gain").reset_index()


def map_figure(gain: pd.DataFrame) -> None:
    with open("data/reference/geo/ne_110m_countries.geojson") as handle:
        geo = json.load(handle)
    values = dict(zip(gain.country, gain.gain))
    codes = {"EL": "GR", "UK": "GB"}
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    vmax = max(abs(min(values.values())), abs(max(values.values())))
    cmap = plt.get_cmap("RdYlGn")
    patches, colors = [], []
    for feature in geo["features"]:
        code = feature["properties"].get("ISO_A2")
        if code in ("RU", "BY", "MD", "UA", "GE", "AL", "RS", "BA", "ME", "MK", "XK"):
            continue
        geom = feature["geometry"]
        polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polygons:
            ring = poly[0]
            if min(p[0] for p in ring) < -30 or max(p[0] for p in ring) > 60:
                continue
            if min(p[1] for p in ring) < 30 or max(p[1] for p in ring) > 72:
                continue
            patches.append(Polygon(ring, closed=True))
            inverse = {v: k for k, v in codes.items()}
            local = inverse.get(code, code)
            if local in values:
                colors.append(cmap((values[local] + vmax) / (2 * vmax)))
            else:
                colors.append("#f0ece4")
    collection = PatchCollection(patches, facecolor=colors, edgecolor="white", linewidth=0.4)
    ax.add_collection(collection)
    ax.set_xlim(-12, 32)
    ax.set_ylim(34, 62)
    ax.set_aspect("equal")
    ax.axis("off")
    for code, value in values.items():
        label = NAMES.get(code, code)
        ax.text(0, 0, "", fontsize=1)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-vmax, vmax))
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Best model against naive, percent", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.set_title("Where a flexible model beats the benchmark, and where it does not", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig_p01_map.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    panel = pd.read_csv("data/panel/p01_registrations_panel.csv")
    panel = panel[(panel.year >= 1991) & (panel.year <= 2024)]
    keep = pd.read_csv("data/model/p01_panel_results.csv").country.unique()
    panel = panel[panel.geo.isin(keep)]
    series_grid(panel)
    macro = pd.read_csv("data/model/p01_panel_macro.csv")
    horizon_profile(macro)
    dm = pd.read_csv("data/model/p01_dm_table.csv")
    forest(dm)
    german = pd.read_csv("data/raw/destatis_pkw_neuzulassungen_jahre.csv").sort_values("time")
    german = german[(german.time >= 1991) & (german.time <= 2025)]
    projection = pd.read_csv("data/model/p01_forecast_2040.csv")
    fan(german, projection)
    frame = pd.read_csv("data/model/p01_panel_results.csv")
    frame = frame[frame.divergent == 0]
    gain = country_gain(frame)
    gain.to_csv("data/model/p01_country_gain.csv", index=False)
    map_figure(gain)
    print(gain.sort_values("gain").round(2).to_string(index=False))


if __name__ == "__main__":
    main()
