"""Replication of the version 1 model set, on Germany and on the panel.

Version 1 of P01 compared thirteen candidates on the German series from 1991 to
2025 with origins from 2006 to 2020 and reported that ridge regression beat the
naive benchmark by about 19.5 percent. This script re-estimates that model set
with the specifications written in version 1 and evaluates it twice: on the
German series and on the seventeen country panel. The comparison shows whether
the version 1 ranking is a property of the market or of the sample.

Author: Armin Kajevic
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import Holt

from p01_protocol import load_panel, mase_scale

warnings.filterwarnings("ignore")

H = 5
SEED = 20261125
MODELS_V1 = [
    "naive",
    "drift",
    "loglinear",
    "ar1_growth",
    "ar1_levels",
    "holt",
    "holt_damped",
    "arima_111",
    "combination",
    "ridge_lags",
    "ridge_ml",
    "random_forest",
    "gradient_boosting",
]


def _features_levels(y: np.ndarray, six: bool) -> tuple[np.ndarray, np.ndarray]:
    X, target = [], []
    start = 3
    for t in range(start, len(y)):
        lags = [y[t - 1], y[t - 2], y[t - 3]]
        if six:
            g1 = (y[t - 1] - y[t - 2]) / max(y[t - 2], 1.0)
            g2 = (y[t - 2] - y[t - 3]) / max(y[t - 3], 1.0)
            lags += [g1, g2, float(t + 1)]
        X.append(lags)
        target.append(y[t])
    return np.array(X), np.array(target)


def _ridge_levels(y: np.ndarray, six: bool, penalty: float = 1.0) -> np.ndarray:
    X, target = _features_levels(y, six)
    Xc = X - X.mean(axis=0)
    yc = target - target.mean()
    beta = np.linalg.solve(Xc.T @ Xc + penalty * np.eye(Xc.shape[1]), Xc.T @ yc)
    intercept = target.mean() - X.mean(axis=0) @ beta
    history = list(y[-3:])
    path = []
    for step in range(H):
        row = list(history[-1:-4:-1])
        if six:
            g1 = (history[-1] - history[-2]) / max(history[-2], 1.0)
            g2 = (history[-2] - history[-3]) / max(history[-3], 1.0)
            row += [g1, g2, float(len(y) + step + 1)]
        value = float(np.dot(row, beta) + intercept)
        path.append(value)
        history.append(value)
    return np.array(path)


def _tree_levels(y: np.ndarray, kind: str) -> np.ndarray:
    X, target = _features_levels(y, True)
    if kind == "forest":
        model = RandomForestRegressor(
            n_estimators=400, min_samples_leaf=2, random_state=SEED, n_jobs=1
        )
    else:
        model = GradientBoostingRegressor(
            n_estimators=300, max_depth=2, learning_rate=0.05, random_state=SEED
        )
    model.fit(X, target)
    history = list(y[-3:])
    path = []
    for step in range(H):
        g1 = (history[-1] - history[-2]) / max(history[-2], 1.0)
        g2 = (history[-2] - history[-3]) / max(history[-3], 1.0)
        row = [history[-1], history[-2], history[-3], g1, g2, float(len(y) + step + 1)]
        value = float(model.predict(np.array(row).reshape(1, -1))[0])
        path.append(value)
        history.append(value)
    return np.array(path)


def _holt(y: np.ndarray, damped: bool) -> np.ndarray:
    best = (np.inf, 0.5, 0.1)
    for alpha in np.arange(0.1, 1.0, 0.1):
        for beta in np.arange(0.1, 1.0, 0.1):
            try:
                fit = Holt(y, damped_trend=damped, initialization_method="estimated").fit(
                    smoothing_level=alpha, smoothing_trend=beta, optimized=False
                )
                sse = float(np.sum(np.asarray(fit.fittedvalues) - y) ** 2)
            except Exception:
                continue
            if sse < best[0]:
                best = (sse, alpha, beta)
    _, alpha, beta = best
    fit = Holt(y, damped_trend=damped, initialization_method="estimated").fit(
        smoothing_level=alpha, smoothing_trend=beta, optimized=False
    )
    return np.asarray(fit.forecast(H), dtype=float)


def _ar1(y: np.ndarray, growth: bool) -> np.ndarray:
    series = np.diff(y) / np.maximum(y[:-1], 1.0) if growth else y
    X = np.column_stack([np.ones(len(series) - 1), series[:-1]])
    target = series[1:]
    coef, *_ = np.linalg.lstsq(X, target, rcond=None)
    value = series[-1]
    path = []
    level = y[-1]
    for _ in range(H):
        value = coef[0] + coef[1] * value
        if growth:
            level = level * (1.0 + value)
            path.append(level)
        else:
            path.append(value)
    return np.array(path)


def forecast_v1(y: np.ndarray, model: str) -> np.ndarray:
    if model == "naive":
        return np.repeat(y[-1], H)
    if model == "drift":
        slope = (y[-1] - y[0]) / (len(y) - 1)
        return y[-1] + slope * np.arange(1, H + 1)
    if model == "loglinear":
        b, a = np.polyfit(np.arange(1, len(y) + 1), np.log(y), 1)
        return np.exp(a + b * (len(y) + np.arange(1, H + 1)))
    if model == "ar1_growth":
        return _ar1(y, True)
    if model == "ar1_levels":
        return _ar1(y, False)
    if model == "holt":
        return _holt(y, False)
    if model == "holt_damped":
        return _holt(y, True)
    if model == "arima_111":
        fit = ARIMA(y, order=(1, 1, 1), trend="t").fit()
        return np.asarray(fit.forecast(H), dtype=float)
    if model == "ridge_lags":
        return _ridge_levels(y, False)
    if model == "ridge_ml":
        return _ridge_levels(y, True)
    if model == "random_forest":
        return _tree_levels(y, "forest")
    if model == "gradient_boosting":
        return _tree_levels(y, "boost")
    if model == "combination":
        parts = np.vstack([forecast_v1(y, m) for m in ("drift", "holt", "ridge_lags")])
        return parts.mean(axis=0)
    raise ValueError(model)


def evaluate(y: np.ndarray, years: np.ndarray, country: str, models: list[str]) -> pd.DataFrame:
    rows = []
    for origin in range(15, len(y) - H + 1):
        scale = mase_scale(y[:origin])
        actual = y[origin:origin + H]
        ceiling = 10.0 * float(np.max(y[:origin]))
        for model in models:
            try:
                path = forecast_v1(y[:origin], model)
            except Exception:
                path = forecast_v1(y[:origin], "drift")
            divergent = int(np.any(path <= 0) or np.any(path > ceiling))
            for h in range(1, H + 1):
                rows.append(
                    {
                        "country": country,
                        "origin_year": int(years[origin - 1]),
                        "horizon": h,
                        "model": model,
                        "mase": abs(actual[h - 1] - path[h - 1]) / scale,
                        "divergent": divergent,
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    panel = load_panel()
    frames = []
    for geo, group in panel.groupby("geo"):
        group = group.sort_values("year")
        years = group.year.to_numpy()
        frames.append(evaluate(group.registrations.to_numpy(float), years, geo, MODELS_V1))
    rec = pd.concat(frames, ignore_index=True)
    rec.to_csv("data/model/p01_v1_panel_results.csv", index=False)
    clean = rec[rec.divergent == 0]
    overall = clean.groupby(["model", "country", "horizon"]).mase.mean().groupby(["model", "country"]).mean().groupby("model").mean()
    overall = overall.sort_values().rename("mase_panel")
    divergence = rec.groupby("model").divergent.mean().rename("divergent_share")

    german = pd.read_csv("data/raw/destatis_pkw_neuzulassungen_jahre.csv").sort_values("time")
    german = german[german.time <= 2025]
    de = evaluate(german.value.to_numpy(float), german.time.to_numpy(), "DE", MODELS_V1)
    de.to_csv("data/model/p01_v1_germany_results.csv", index=False)
    de_overall = de.groupby("model").mase.mean().sort_values().rename("mase_germany")

    table = pd.concat([de_overall, overall], axis=1)
    table = table.join(divergence)
    table["rank_germany"] = table.mase_germany.rank().astype(int)
    table["rank_panel"] = table.mase_panel.rank().astype(int)
    table.to_csv("data/model/p01_v1_comparison.csv")
    print(table.round(4).to_string())
    print(f"countries {rec.country.nunique()}, errors {len(rec)}, divergent {int(rec.divergent.sum())}")
    best_de = table.mase_germany.idxmin()
    best_panel = table.mase_panel.idxmin()
    gain_de = 1 - table.loc[best_de, "mase_germany"] / table.loc["naive", "mase_germany"]
    gain_panel = 1 - table.loc[best_panel, "mase_panel"] / table.loc["naive", "mase_panel"]
    print(f"\nbest Germany {best_de}, gain over naive {gain_de:.4f}")
    print(f"best panel {best_panel}, gain over naive {gain_panel:.4f}")
    print(f"ridge_ml Germany rank {table.loc['ridge_ml','rank_germany']}, panel rank {table.loc['ridge_ml','rank_panel']}")


if __name__ == "__main__":
    main()
