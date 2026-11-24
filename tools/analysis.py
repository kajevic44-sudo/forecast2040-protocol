"""Full analytical run: backtest, comparison, intervals and figures.

This script is the one that produces every number and every chart used in the
dissertation chapter on forecasting. It is deliberately separate from the CLI so
that a reader can rerun the whole analysis with one command and get identical
output, given identical inputs.

Usage:
    python tools/analysis.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from forecast2040.ml import feature_importance, learning_curve, ml_models
from forecast2040.models import (
    ModelError,
    default_models,
    diebold_mariano,
    project,
    rolling_origin,
    score_models,
    select_model,
)

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / "data" / "panel" / "panel_annual.csv"
OUT = ROOT / "data" / "model"
FIG = ROOT / "figures"

SERIES = {
    "vw_group_china_deliveries": {"label": "Volkswagen Group deliveries in China", "min_train": 18},
    "destatis_pkw_neuzulassungen_jahre": {
        "label": "Passenger car registrations in Germany",
        "min_train": 15,
    },
}

COLORS = [
    "#1f3b57",
    "#c8553d",
    "#588157",
    "#bc6c25",
    "#6d597a",
    "#457b9d",
    "#a44a3f",
    "#7f5539",
    "#3d5a80",
    "#9a8c98",
    "#4f772d",
]
CRISIS = {1993, 2001, 2008, 2009, 2020, 2022}
BOOM = set(range(2009, 2015))


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#444444",
            "axes.grid": True,
            "grid.color": "#dddddd",
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "figure.dpi": 110,
            "font.family": "DejaVu Sans",
        }
    )


def load_series(column: str) -> pd.Series:
    frame = pd.read_csv(PANEL)
    subset = frame[["period", column]].dropna()
    index = pd.Index([str(p)[:4] for p in subset["period"]], name="year")
    return pd.Series(np.asarray(subset[column].to_numpy(), dtype=np.float64), index=index)


def dm_matrix(rows: list, models: list[str]) -> pd.DataFrame:
    """Pairwise Diebold-Mariano p values at horizon one."""
    errors: dict[str, dict[int, float]] = {}
    for row in rows:
        if row.horizon == 1:
            errors.setdefault(row.model, {})[row.origin_year] = row.error
    common = sorted(set.intersection(*(set(v) for v in errors.values()))) if errors else []
    matrix = pd.DataFrame(1.0, index=models, columns=models)
    for i, first in enumerate(models):
        for second in models[i + 1 :]:
            a = [errors[first][year] for year in common]
            b = [errors[second][year] for year in common]
            try:
                _, p_value = diebold_mariano(a, b)
            except ModelError:
                p_value = float("nan")
            matrix.loc[first, second] = p_value
            matrix.loc[second, first] = p_value
    return matrix


def run_series(column: str, label: str, min_train: int, last_year: int = 2040) -> dict[str, object]:
    series = load_series(column)
    models = default_models() + ml_models()
    rows = rolling_origin(series, models, horizons=(1, 2, 3, 4, 5), min_train=min_train)
    scores = score_models(rows, series, models, min_train)
    best = select_model(scores)
    chosen = next(m for m in models if m.name == best.model)
    forecast = project(series, chosen, rows, last_year=last_year)

    OUT.mkdir(parents=True, exist_ok=True)
    metrics = pd.DataFrame([s.as_dict() for s in scores]).sort_values("mase")
    metrics.to_csv(OUT / f"metrics_full_{column}.csv", index=False)

    backtest = pd.DataFrame(
        [
            {
                "model": r.model,
                "origin_year": r.origin_year,
                "regime": r.regime,
                "horizon": r.horizon,
                "actual": r.actual,
                "forecast": r.forecast,
                "error": r.error,
                "abs_pct_error": abs(r.error) / r.actual if r.actual else np.nan,
            }
            for r in rows
        ]
    )
    backtest.to_csv(OUT / f"backtest_full_{column}.csv", index=False)

    names = [m.name for m in models if m.name in set(backtest["model"])]
    matrix = dm_matrix(rows, names)
    matrix.round(4).to_csv(OUT / f"dm_matrix_{column}.csv")

    regime = (
        backtest.groupby(["model", "regime"])["abs_pct_error"].mean().unstack("regime").round(4)
    )
    regime.to_csv(OUT / f"regime_errors_{column}.csv")
    forecast.round(2).to_csv(OUT / f"forecast_full_{column}.csv", index=False)

    return {
        "series": series,
        "label": label,
        "rows": backtest,
        "metrics": metrics,
        "matrix": matrix,
        "regime": regime,
        "forecast": forecast,
        "best": best,
        "chosen": chosen,
    }


def fig_overview(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=False)
    for axis, (column, result) in zip(axes, results.items(), strict=True):
        series = result["series"]
        years = [int(y) for y in series.index]
        axis.plot(years, series.to_numpy() / 1e6, color=COLORS[0], linewidth=2.0)
        for year in years:
            if year in CRISIS:
                axis.axvspan(year - 0.5, year + 0.5, color=COLORS[1], alpha=0.10, linewidth=0)
            elif year in BOOM:
                axis.axvspan(year - 0.5, year + 0.5, color=COLORS[2], alpha=0.08, linewidth=0)
        axis.set_title(f"{result['label']}, millions of vehicles")
        axis.set_ylabel("millions")
    axes[0].text(
        0.01,
        0.92,
        "red bands: crisis years, green bands: China boom",
        transform=axes[0].transAxes,
        fontsize=9,
        color="#555555",
    )
    fig.suptitle("Two series, two regimes", fontsize=14, fontweight="bold", x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig01_series_overview.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_fan(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for axis, (column, result) in zip(axes, results.items(), strict=True):
        series = result["series"]
        forecast = result["forecast"]
        years = [int(y) for y in series.index]
        axis.plot(years, series.to_numpy() / 1e6, color="#222222", linewidth=2.0, label="observed")
        axis.plot(
            forecast["year"],
            forecast["point"] / 1e6,
            color=COLORS[0],
            linewidth=2.0,
            label=f"forecast, {result['best'].model}",
        )
        for level, alpha in ((95, 0.12), (80, 0.18), (50, 0.28)):
            axis.fill_between(
                forecast["year"],
                forecast[f"lo{level}"] / 1e6,
                forecast[f"hi{level}"] / 1e6,
                color=COLORS[0],
                alpha=alpha,
                linewidth=0,
                label=f"{level} percent interval",
            )
        axis.axvline(years[-1], color="#999999", linestyle=":", linewidth=1)
        axis.set_title(result["label"])
        axis.set_ylabel("millions of vehicles")
        axis.legend(fontsize=8, frameon=False, loc="upper left")
    fig.suptitle(
        "Projection to 2040 with empirical prediction intervals",
        fontsize=14,
        fontweight="bold",
        x=0.01,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig02_forecast_fan.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_model_comparison(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for axis, (_column, result) in zip(axes, results.items(), strict=True):
        metrics = result["metrics"].sort_values("mase_h1")
        positions = np.arange(len(metrics))
        axis.barh(
            positions - 0.2, metrics["mase_h1"], height=0.38, color=COLORS[0], label="horizon 1"
        )
        axis.barh(
            positions + 0.2, metrics["mase_h3"], height=0.38, color=COLORS[3], label="horizon 3"
        )
        axis.set_yticks(positions, metrics["model"], fontsize=8)
        axis.axvline(1.0, color="#888888", linestyle="--", linewidth=1)
        axis.set_title(result["label"])
        axis.set_xlabel("MASE, lower is better, 1.0 equals the naive benchmark")
        axis.legend(fontsize=8, frameon=False)
    fig.suptitle("Accuracy by model and horizon", fontsize=14, fontweight="bold", x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig03_model_comparison.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_error_heatmap(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for axis, (column, result) in zip(axes, results.items(), strict=True):
        metrics = result["metrics"].set_index("model")
        columns = [c for c in metrics.columns if c.startswith("mase_h")]
        data = metrics[columns].astype(float)
        data = data.loc[data.mean(axis=1).sort_values().index]
        image = axis.imshow(
            data.to_numpy(),
            aspect="auto",
            cmap="YlOrRd",
            vmin=0,
            vmax=min(data.to_numpy().max(), 20),
        )
        axis.set_xticks(
            range(len(columns)), [c.replace("mase_h", "h=") for c in columns], fontsize=8
        )
        axis.set_yticks(range(len(data)), data.index, fontsize=8)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                axis.text(
                    col,
                    row,
                    f"{data.iloc[row, col]:.1f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="#222222",
                )
        axis.set_title(result["label"])
        fig.colorbar(image, ax=axis, fraction=0.03, pad=0.02)
    fig.suptitle(
        "MASE by model and forecast horizon", fontsize=14, fontweight="bold", x=0.01, ha="left"
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig04_error_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_dm_matrix(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    cmap = LinearSegmentedColormap.from_list("dm", ["#c8553d", "#f2e8cf", "#588157"])
    for axis, (column, result) in zip(axes, results.items(), strict=True):
        matrix = result["matrix"]
        image = axis.imshow(matrix.to_numpy(), cmap=cmap, vmin=0, vmax=1)
        axis.set_xticks(range(len(matrix)), matrix.columns, rotation=90, fontsize=7)
        axis.set_yticks(range(len(matrix)), matrix.index, fontsize=7)
        for row in range(len(matrix)):
            for col in range(len(matrix)):
                value = matrix.iloc[row, col]
                axis.text(col, row, f"{value:.2f}", ha="center", va="center", fontsize=6)
        axis.set_title(result["label"])
        fig.colorbar(image, ax=axis, fraction=0.03, pad=0.02)
    fig.suptitle(
        "Diebold-Mariano p values, green means different accuracy",
        fontsize=14,
        fontweight="bold",
        x=0.01,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig05_dm_matrix.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_regime(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    order = ["boom", "normal", "crisis"]
    for axis, (column, result) in zip(axes, results.items(), strict=True):
        rows = result["rows"]
        data = [rows[rows["regime"] == name]["abs_pct_error"].dropna() * 100 for name in order]
        box = axis.boxplot(
            data, tick_labels=order, patch_artist=True, widths=0.55, showfliers=False
        )
        for patch, color in zip(box["boxes"], [COLORS[2], COLORS[0], COLORS[1]], strict=True):
            patch.set_facecolor(color)
            patch.set_alpha(0.55)
        axis.set_ylabel("absolute percentage error")
        axis.set_title(result["label"])
    fig.suptitle(
        "Error by regime, all models pooled", fontsize=14, fontweight="bold", x=0.01, ha="left"
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig06_regime_errors.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_correlation() -> None:
    frame = pd.read_csv(PANEL)
    numeric = frame.drop(columns=["period"])
    keep = [c for c in numeric.columns if numeric[c].notna().sum() >= 20]
    data = numeric[keep].corr(method="spearman")
    fig, axis = plt.subplots(figsize=(10, 8))
    image = axis.imshow(data.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
    axis.set_xticks(range(len(keep)), keep, rotation=90, fontsize=7)
    axis.set_yticks(range(len(keep)), keep, fontsize=7)
    for row in range(len(keep)):
        for col in range(len(keep)):
            axis.text(col, row, f"{data.iloc[row, col]:.2f}", ha="center", va="center", fontsize=5)
    fig.colorbar(image, ax=axis, fraction=0.03, pad=0.02)
    axis.set_title("Spearman correlation, annual panel series with at least 20 observations")
    fig.tight_layout()
    fig.savefig(FIG / "fig07_correlation.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_importance_and_learning(results: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    result = results["vw_group_china_deliveries"]
    importance = feature_importance(np.asarray(result["series"].to_numpy(), dtype=np.float64))
    names = [row.feature for row in importance]
    values = [row.importance for row in importance]
    axes[0].barh(names[::-1], values[::-1], color=COLORS[0])
    axes[0].set_title("Random forest importance, China series")
    axes[0].set_xlabel("share of impurity reduction")

    for axis, key in zip(
        axes[1:], ["vw_group_china_deliveries", "destatis_pkw_neuzulassungen_jahre"], strict=True
    ):
        series = results[key]["series"]
        for color, model in zip(
            COLORS,
            [results[key]["chosen"], *[m for m in ml_models() if m.name == "random_forest"]],
            strict=False,
        ):
            curve = learning_curve(series, model, horizons=(1,))
            if curve.empty:
                continue
            axis.plot(
                curve["train_size"],
                curve["abs_error"] / 1e3,
                marker="o",
                markersize=3,
                color=color,
                label=model.name,
            )
        axis.set_title(f"Learning curve, {key.split('_')[0]}")
        axis.set_xlabel("training observations")
        axis.set_ylabel("mean absolute error, thousands")
        axis.legend(fontsize=8, frameon=False)
    fig.suptitle(
        "What drives the forest, and whether more data helps",
        fontsize=14,
        fontweight="bold",
        x=0.01,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig08_importance_learning.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    style()
    FIG.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, object]] = {}
    for column, config in SERIES.items():
        print(f"running {column}")
        results[column] = run_series(column, config["label"], config["min_train"])
        best = results[column]["best"]
        print(f"  selected {best.model}  MASE {best.mase:.3f}  p vs naive {best.dm_p_value:.3f}")
    fig_overview(results)
    fig_fan(results)
    fig_model_comparison(results)
    fig_error_heatmap(results)
    fig_dm_matrix(results)
    fig_regime(results)
    fig_correlation()
    fig_importance_and_learning(results)
    figures = sorted(FIG.glob("fig*.png"))
    print(f"figures written {len(figures)}")
    for path in figures:
        print(f"  {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
