"""Forecasting engine for P01, version 2.0.

The module implements the thirteen models, the rolling origin scheme, the
scaled loss and the panel aggregation that are fixed in
protocol/p01_protocol.yaml. Every model receives only the training window and
returns a path of five forecasts. No statistic in this file looks at data
beyond the origin.

Author: Armin Kajevic
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, Ridge
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")

HORIZON = 5
MIN_TRAIN = 15
SEED = 20261125
RIDGE_GRID = np.logspace(-2, 2, 9)

MODELS = [
    "naive",
    "mean",
    "drift",
    "linear_trend",
    "loglinear_trend",
    "holt_damped",
    "ets_aaa",
    "arima_110",
    "ar2_diff",
    "ridge_lags",
    "lasso_lags",
    "random_forest",
    "theta",
]


def mase_scale(y: np.ndarray) -> float:
    """Mean absolute first difference of the training window."""
    if len(y) < 2:
        return float(abs(y[-1])) or 1.0
    scale = float(np.mean(np.abs(np.diff(y))))
    if scale == 0.0:
        scale = float(np.mean(np.abs(y)))
    return scale or 1.0


def _holt_damped(y: np.ndarray) -> np.ndarray:
    best = (np.inf, 0.5, 0.1, 0.9)
    for alpha in np.arange(0.1, 1.0, 0.1):
        for beta in np.arange(0.1, 1.0, 0.1):
            for phi in np.arange(0.1, 1.0, 0.1):
                level = y[0]
                trend = y[1] - y[0]
                sse = 0.0
                for t in range(1, len(y)):
                    pred = level + phi * trend
                    err = y[t] - pred
                    sse += err * err
                    new_level = alpha * y[t] + (1 - alpha) * pred
                    trend = beta * (new_level - level) + (1 - beta) * phi * trend
                    level = new_level
                if sse < best[0]:
                    best = (sse, alpha, beta, phi)
    _, alpha, beta, phi = best
    level = y[0]
    trend = y[1] - y[0]
    for t in range(1, len(y)):
        pred = level + phi * trend
        new_level = alpha * y[t] + (1 - alpha) * pred
        trend = beta * (new_level - level) + (1 - beta) * phi * trend
        level = new_level
    path = []
    damp = 0.0
    power = 1.0
    for _ in range(HORIZON):
        power *= phi
        damp += power
        path.append(level + damp * trend)
    return np.array(path)


def _theta(y: np.ndarray) -> np.ndarray:
    t = np.arange(1, len(y) + 1)
    b, a = np.polyfit(t, y, 1)
    trend_line = a + b * (len(y) + np.arange(1, HORIZON + 1))
    z = 2.0 * y - (a + b * t)
    alpha = 0.5
    level = z[0]
    for value in z[1:]:
        level = alpha * value + (1 - alpha) * level
    return 0.5 * level + 0.5 * trend_line


def _ar_features(dy: np.ndarray, lags: int = 3) -> tuple[np.ndarray, np.ndarray]:
    X, target = [], []
    for i in range(lags, len(dy)):
        X.append(dy[i - lags:i][::-1])
        target.append(dy[i])
    return np.array(X), np.array(target)


def _recursive_ml(y: np.ndarray, kind: str) -> np.ndarray:
    dy = np.diff(y)
    X, target = _ar_features(dy)
    if len(target) < 8:
        raise ValueError("not enough observations for lag model")
    if kind == "ridge":
        pipe = Pipeline([("scale", StandardScaler()), ("model", Ridge())])
        search = GridSearchCV(
            pipe,
            {"model__alpha": RIDGE_GRID},
            cv=TimeSeriesSplit(n_splits=3),
            scoring="neg_mean_squared_error",
        )
    elif kind == "lasso":
        pipe = Pipeline([("scale", StandardScaler()), ("model", Lasso(max_iter=50000))])
        search = GridSearchCV(
            pipe,
            {"model__alpha": RIDGE_GRID},
            cv=TimeSeriesSplit(n_splits=3),
            scoring="neg_mean_squared_error",
        )
    else:
        search = RandomForestRegressor(
            n_estimators=300,
            max_depth=3,
            min_samples_leaf=5,
            random_state=SEED,
            n_jobs=1,
        )
    search.fit(X, target)
    history = list(dy[-3:][::-1])
    path = []
    level = y[-1]
    for _ in range(HORIZON):
        step = float(search.predict(np.array(history).reshape(1, -1))[0])
        level += step
        path.append(level)
        history = [step] + history[:-1]
    return np.array(path)


def forecast_path(y: np.ndarray, model: str) -> np.ndarray:
    """Return five forecasts conditional on the training window y."""
    y = np.asarray(y, dtype=float)
    if model == "naive":
        return np.repeat(y[-1], HORIZON)
    if model == "mean":
        return np.repeat(y.mean(), HORIZON)
    if model == "drift":
        slope = (y[-1] - y[0]) / (len(y) - 1)
        return y[-1] + slope * np.arange(1, HORIZON + 1)
    if model == "linear_trend":
        t = np.arange(1, len(y) + 1)
        b, a = np.polyfit(t, y, 1)
        return a + b * (len(y) + np.arange(1, HORIZON + 1))
    if model == "loglinear_trend":
        t = np.arange(1, len(y) + 1)
        b, a = np.polyfit(t, np.log(y), 1)
        return np.exp(a + b * (len(y) + np.arange(1, HORIZON + 1)))
    if model == "holt_damped":
        return _holt_damped(y)
    if model == "ets_aaa":
        fit = ExponentialSmoothing(y, trend="add", seasonal=None, damped_trend=False).fit()
        return np.asarray(fit.forecast(HORIZON), dtype=float)
    if model == "arima_110":
        # With one unit root the constant enters the differenced equation, so
        # statsmodels requires trend="t" rather than trend="c".
        fit = ARIMA(y, order=(1, 1, 0), trend="t").fit()
        return np.asarray(fit.forecast(HORIZON), dtype=float)
    if model == "ar2_diff":
        dy = np.diff(y)
        X = np.column_stack([dy[1:-1], dy[:-2]])
        target = dy[2:]
        X = np.column_stack([np.ones(len(X)), X])
        coef, *_ = np.linalg.lstsq(X, target, rcond=None)
        d1, d2 = dy[-1], dy[-2]
        path = []
        level = y[-1]
        for _ in range(HORIZON):
            step = coef[0] + coef[1] * d1 + coef[2] * d2
            level += step
            path.append(level)
            d2, d1 = d1, step
        return np.array(path)
    if model == "ridge_lags":
        return _recursive_ml(y, "ridge")
    if model == "lasso_lags":
        return _recursive_ml(y, "lasso")
    if model == "random_forest":
        return _recursive_ml(y, "forest")
    if model == "theta":
        return _theta(y)
    raise ValueError(model)


def run_series(y: np.ndarray, years: np.ndarray, country: str) -> pd.DataFrame:
    records = []
    n = len(y)
    for origin in range(MIN_TRAIN, n - HORIZON + 1):
        train = y[:origin]
        scale = mase_scale(train)
        actual = y[origin:origin + HORIZON]
        ceiling = 10.0 * float(np.max(train))
        for model in MODELS:
            try:
                path = forecast_path(train, model)
                fallback = 0
            except Exception:
                path = forecast_path(train, "drift")
                fallback = 1
            divergent = int(np.any(path <= 0) or np.any(path > ceiling))
            for h in range(1, HORIZON + 1):
                error = actual[h - 1] - path[h - 1]
                records.append(
                    {
                        "country": country,
                        "origin_year": int(years[origin - 1]),
                        "origin_index": origin,
                        "horizon": h,
                        "model": model,
                        "forecast": float(path[h - 1]),
                        "actual": float(actual[h - 1]),
                        "error": float(error),
                        "abs_error": float(abs(error)),
                        "mase": float(abs(error) / scale),
                        "fallback": fallback,
                        "divergent": divergent,
                    }
                )
    return pd.DataFrame(records)


def load_panel(path: str = "data/panel/p01_registrations_panel.csv") -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = frame[(frame.year >= 1991) & (frame.year <= 2024)].copy()
    frame = frame.dropna(subset=["registrations"])
    keep = []
    for geo, group in frame.groupby("geo"):
        years = sorted(group.year.tolist())
        runs, current = [], [years[0]]
        for a, b in zip(years, years[1:]):
            if b == a + 1:
                current.append(b)
            else:
                runs.append(current)
                current = [b]
        runs.append(current)
        best = max(runs, key=len)
        if len(best) >= 25 and best[-1] == 2024:
            keep.append((geo, best[0]))
    out = []
    for geo, start in keep:
        group = frame[(frame.geo == geo) & (frame.year >= start)].sort_values("year")
        if group.year.tolist() != list(range(start, 2025)):
            continue
        out.append(group)
    panel = pd.concat(out, ignore_index=True)
    return panel


def aggregate(records: pd.DataFrame) -> pd.DataFrame:
    records = records[records.divergent == 0]
    per_country = (
        records.groupby(["model", "country", "horizon"]).mase.mean().reset_index()
    )
    macro = per_country.groupby(["model", "horizon"]).mase.mean().reset_index()
    return macro


def overall(records: pd.DataFrame) -> pd.DataFrame:
    records = records[records.divergent == 0]
    per_country_horizon = records.groupby(["model", "country", "horizon"]).mase.mean()
    per_country = per_country_horizon.groupby(["model", "country"]).mean()
    return per_country.groupby("model").mean().sort_values().reset_index()


def main() -> None:
    panel = load_panel()
    print(f"countries {panel.geo.nunique()}, observations {len(panel)}")
    frames = []
    for geo, group in panel.groupby("geo"):
        group = group.sort_values("year")
        frames.append(run_series(group.registrations.to_numpy(float), group.year.to_numpy(), geo))
    records = pd.concat(frames, ignore_index=True)
    records.to_csv("data/model/p01_panel_results.csv", index=False)
    macro = aggregate(records)
    macro.to_csv("data/model/p01_panel_macro.csv", index=False)
    summary = overall(records)
    summary.to_csv("data/model/p01_panel_overall.csv", index=False)
    print(summary.to_string(index=False))
    print(f"errors {len(records)}, fallbacks {int(records.fallback.max())}")


if __name__ == "__main__":
    main()
