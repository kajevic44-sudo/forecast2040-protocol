"""Three additional diagnostics for the forecast evaluation.

Figure 18  MASE by horizon for six models, Germany.
Figure 19  Kernel density of the absolute percentage error, by horizon.
Figure 20  Mean absolute percentage error by origin year, one line per horizon.

The data are read from the model directory, so the figures cannot drift from the
tables. Style follows the dissertation: no dashes in labels, no asterisks.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "data" / "model"
FIG = ROOT / "figures"

INK = "#1C2326"
MUTED = "#5A6B73"
GRID = "#D0D8DB"
ACCENT = "#C3955E"
PRIMARY = "#304C59"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "axes.titlesize": 11,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def read_metrics(name: str) -> list[dict[str, str]]:
    with (MODEL / name).open() as handle:
        return list(csv.DictReader(handle))


def read_backtest(name: str) -> list[dict[str, str]]:
    with (MODEL / name).open() as handle:
        return list(csv.DictReader(handle))


def figure_horizon_curves() -> None:
    rows = {r["model"]: r for r in read_metrics("metrics_full_destatis_pkw_neuzulassungen_jahre.csv")}
    chosen = [
        ("ridge_lags", "Ridge on lags", ACCENT, 2.4),
        ("ar1_levels", "AR(1) levels", PRIMARY, 1.6),
        ("random_forest", "Random forest", "#7A8C94", 1.4),
        ("ridge_ml", "Ridge ML", "#9AA9B0", 1.2),
        ("naive", "Random walk", INK, 1.8),
        ("arima_111", "ARIMA(1,1,1)", "#B9C4C9", 1.2),
    ]
    horizons = np.arange(1, 6)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for key, label, color, width in chosen:
        values = [float(rows[key][f"mase_h{h}"]) for h in horizons]
        ax.plot(horizons, values, marker="o", markersize=4, linewidth=width, color=color, label=label)
        if key == "ridge_lags":
            for h, value in zip(horizons, values):
                ax.annotate(f"{value:.2f}", (h, value), textcoords="offset points", xytext=(0, 7),
                            ha="center", fontsize=7.5, color=ACCENT)
    ax.axhline(1.0, color=MUTED, linewidth=0.9, linestyle=":")
    ax.text(5.05, 1.03, "parity", va="bottom", fontsize=7.5, color=MUTED)
    ax.set_xticks(horizons)
    ax.set_xlabel("forecast horizon, years")
    ax.set_ylabel("mean absolute scaled error")
    ax.set_title("Skill decays with the horizon, and the random walk decays fastest")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
    ax.set_xlim(0.8, 5.6)
    fig.savefig(FIG / "fig18_horizon_curves.png")
    plt.close(fig)


def figure_error_waves() -> None:
    rows = read_backtest("backtest_full_destatis_pkw_neuzulassungen_jahre.csv")
    errors: dict[int, list[float]] = {h: [] for h in range(1, 6)}
    for row in rows:
        if row["model"] == "ridge_lags":
            errors[int(row["horizon"])].append(float(row["abs_pct_error"]))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    grid = np.linspace(0.0, 0.45, 400)
    shades = ["#304C59", "#4A6672", "#6E858E", "#9AA9B0", "#C3955E"]
    for horizon, color in zip(range(1, 6), shades):
        data = np.array(errors[horizon])
        if len(data) < 5:
            continue
        density = gaussian_kde(data, bw_method=0.35)(grid)
        ax.plot(grid, density, color=color, linewidth=1.8, label=f"horizon {horizon}")
        ax.fill_between(grid, density, color=color, alpha=0.08)
    ax.set_xlabel("absolute percentage error")
    ax.set_ylabel("density")
    ax.set_title("The error distribution moves right and flattens as the horizon lengthens")
    ax.legend(frameon=False, fontsize=7.5)
    ax.set_xlim(0, 0.45)
    fig.savefig(FIG / "fig19_error_waves.png")
    plt.close(fig)


def figure_origin_waves() -> None:
    rows = read_backtest("backtest_full_destatis_pkw_neuzulassungen_jahre.csv")
    by_origin: dict[int, dict[int, list[float]]] = {}
    for row in rows:
        if row["model"] != "ridge_lags":
            continue
        origin = int(row["origin_year"])
        horizon = int(row["horizon"])
        by_origin.setdefault(origin, {h: [] for h in range(1, 6)})[horizon].append(float(row["abs_pct_error"]))
    years = sorted(by_origin)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    shades = ["#304C59", "#4A6672", "#6E858E", "#9AA9B0", "#C3955E"]
    for horizon, color in zip(range(1, 6), shades):
        series = [np.mean(by_origin[y][horizon]) if by_origin[y][horizon] else np.nan for y in years]
        ax.plot(years, series, color=color, linewidth=1.5, label=f"horizon {horizon}")
    ax.axvspan(2008.5, 2009.5, color=GRID, alpha=0.5, linewidth=0)
    ax.text(2009, ax.get_ylim()[1] * 0.95, "2009", ha="center", fontsize=7, color=MUTED)
    ax.axvspan(2019.5, 2020.5, color=GRID, alpha=0.5, linewidth=0)
    ax.text(2020, ax.get_ylim()[1] * 0.95, "2020", ha="center", fontsize=7, color=MUTED)
    ax.set_xlabel("origin year")
    ax.set_ylabel("mean absolute percentage error")
    ax.set_title("Errors arrive in waves, and the waves are shared by every horizon")
    ax.legend(frameon=False, fontsize=7.5, ncol=2, loc="upper left")
    fig.savefig(FIG / "fig20_origin_waves.png")
    plt.close(fig)


def main() -> None:
    FIG.mkdir(exist_ok=True)
    figure_horizon_curves()
    figure_error_waves()
    figure_origin_waves()
    print("written fig18, fig19, fig20")


if __name__ == "__main__":
    main()
