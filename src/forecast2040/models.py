"""Rolling-origin forecast benchmark for the 2040 study.

Every forecaster is a pure function from a history array to an h-step forecast.
That keeps the backtest reproducible and the selection auditable: the same
history always yields the same forecast, and the winner is chosen by a rule
fixed before the result is seen, not by judgement afterwards.

The module deliberately depends only on numpy and pandas. The estimators are
written out in closed form so that every coefficient can be inspected in the
dissertation appendix instead of being hidden inside a library call.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
Forecaster = Callable[[FloatArray, int], FloatArray]

# Regime calendar. The labels are fixed in advance from the historical record,
# not chosen to flatter any model. Sources: Destatis registration series,
# KBA FZ 28, VW Group annual deliveries, and the crisis literature reviewed in
# STANDARD_KVALITETA.md.
CRISIS_YEARS: frozenset[int] = frozenset({1993, 2001, 2008, 2009, 2020, 2022})
BOOM_YEARS: frozenset[int] = frozenset(range(2009, 2015))

HORIZONS: tuple[int, ...] = (1, 2, 3, 4, 5)
INTERVAL_LEVELS: tuple[float, ...] = (0.5, 0.8, 0.95)


class ModelError(RuntimeError):
    """Raised when a series cannot be modelled under the stated assumptions."""


def classify_regime(year: int) -> str:
    """Return the regime label for a calendar year."""
    if year in CRISIS_YEARS:
        return "crisis"
    if year in BOOM_YEARS:
        return "boom"
    return "normal"


def _as_float(history: Sequence[float] | FloatArray) -> FloatArray:
    arr = np.asarray(history, dtype=np.float64)
    if arr.ndim != 1:
        raise ModelError("history must be one dimensional")
    if arr.size < 3:
        raise ModelError("history must contain at least three observations")
    if not np.all(np.isfinite(arr)):
        raise ModelError("history contains non finite values")
    return arr


def naive(history: FloatArray, h: int) -> FloatArray:
    """Random walk without drift: the last observed value is repeated."""
    return np.repeat(history[-1], h)


def drift(history: FloatArray, h: int) -> FloatArray:
    """Random walk with drift: mean absolute change per period."""
    slope = float(np.mean(np.diff(history)))
    steps = np.arange(1, h + 1, dtype=np.float64)
    return history[-1] + slope * steps


def loglinear(history: FloatArray, h: int) -> FloatArray:
    """Log linear trend fitted by ordinary least squares."""
    if np.any(history <= 0):
        raise ModelError("loglinear requires strictly positive values")
    n = history.size
    t = np.arange(n, dtype=np.float64)
    y = np.log(history)
    t_mean = float(t.mean())
    y_mean = float(y.mean())
    sxx = float(np.sum((t - t_mean) ** 2))
    if sxx == 0.0:
        raise ModelError("loglinear requires a non degenerate time index")
    beta = float(np.sum((t - t_mean) * (y - y_mean)) / sxx)
    alpha = y_mean - beta * t_mean
    steps = np.arange(n, n + h, dtype=np.float64)
    return np.exp(alpha + beta * steps)


def ar1_growth(history: FloatArray, h: int) -> FloatArray:
    """AR(1) on the growth rate, iterated forward from the last level."""
    if np.any(history <= 0):
        raise ModelError("ar1_growth requires strictly positive values")
    growth = np.diff(np.log(history))
    if growth.size < 3:
        raise ModelError("ar1_growth needs at least four observations")
    x = growth[:-1]
    y = growth[1:]
    x_mean = float(x.mean())
    y_mean = float(y.mean())
    sxx = float(np.sum((x - x_mean) ** 2))
    if sxx == 0.0:
        raise ModelError("growth series has no variation")
    phi = float(np.sum((x - x_mean) * (y - y_mean)) / sxx)
    phi = max(min(phi, 0.99), -0.99)
    const = y_mean - phi * x_mean
    last = float(growth[-1])
    out = np.empty(h, dtype=np.float64)
    level = float(history[-1])
    for step in range(h):
        last = const + phi * last
        level = level * math.exp(last)
        out[step] = level
    return out


def ridge_lags(history: FloatArray, h: int, lags: int = 3, alpha: float = 1.0) -> FloatArray:
    """Ridge regression on log level lags, applied recursively."""
    if np.any(history <= 0):
        raise ModelError("ridge_lags requires strictly positive values")
    if history.size <= lags + 1:
        raise ModelError("history too short for the requested number of lags")
    y = np.log(history)
    rows = y.size - lags
    design = np.empty((rows, lags + 1), dtype=np.float64)
    design[:, 0] = 1.0
    for lag in range(1, lags + 1):
        design[:, lag] = y[lags - lag : lags - lag + rows]
    target = y[lags:]
    penalty = alpha * np.eye(lags + 1, dtype=np.float64)
    penalty[0, 0] = 0.0
    gram = design.T @ design + penalty
    coef = np.linalg.solve(gram, design.T @ target)
    window = list(y[-lags:][::-1])
    out = np.empty(h, dtype=np.float64)
    for step in range(h):
        features = np.array([1.0, *window], dtype=np.float64)
        value = float(features @ coef)
        out[step] = math.exp(value)
        window = [value, *window[:-1]]
    return out


def holt(history: FloatArray, h: int) -> FloatArray:
    """Holt linear trend with the smoothing constants chosen by grid search.

    The grid is fixed in advance and scored on the one step in sample error of
    the training window only, so the choice is reproducible from the data the
    model is allowed to see.
    """
    best: tuple[float, float, float] | None = None
    for alpha in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        for beta in (0.01, 0.05, 0.1, 0.2, 0.3):
            level = float(history[0])
            trend = float(history[1] - history[0])
            sse = 0.0
            for value in history[1:]:
                predicted = level + trend
                sse += (float(value) - predicted) ** 2
                previous = level
                level = alpha * float(value) + (1.0 - alpha) * predicted
                trend = beta * (level - previous) + (1.0 - beta) * trend
            if best is None or sse < best[0]:
                best = (sse, alpha, beta)
    if best is None:
        raise ModelError("holt could not be fitted")
    _, alpha, beta = best
    level = float(history[0])
    trend = float(history[1] - history[0])
    for value in history[1:]:
        predicted = level + trend
        previous = level
        level = alpha * float(value) + (1.0 - alpha) * predicted
        trend = beta * (level - previous) + (1.0 - beta) * trend
    steps = np.arange(1, h + 1, dtype=np.float64)
    return level + trend * steps


def combination(history: FloatArray, h: int) -> FloatArray:
    """Equal weight combination of drift, Holt and ridge lag forecasts.

    Forecast combination is the cheapest robustness device available: it cannot
    beat the best member ex post, but it rarely loses to it out of sample.
    """
    members = [drift(history, h), holt(history, h), ridge_lags(history, h)]
    return np.mean(np.vstack(members), axis=0)


def holt_damped(history: FloatArray, h: int) -> FloatArray:
    """Holt with a damped trend, the standard fix for a trend that runs away.

    A linear trend fitted to a series that has turned down will cross zero and
    keep going. Damping multiplies the trend by a factor below one at every
    step, so the long run forecast flattens instead of collapsing. The three
    smoothing constants are chosen on the training window only.
    """
    best: tuple[float, float, float, float] | None = None
    for alpha in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        for beta in (0.01, 0.05, 0.1, 0.2):
            for phi in (0.80, 0.85, 0.90, 0.95, 0.98):
                level = float(history[0])
                trend = float(history[1] - history[0])
                sse = 0.0
                for value in history[1:]:
                    predicted = level + phi * trend
                    sse += (float(value) - predicted) ** 2
                    previous = level
                    level = alpha * float(value) + (1.0 - alpha) * predicted
                    trend = beta * (level - previous) + (1.0 - beta) * phi * trend
                if best is None or sse < best[0]:
                    best = (sse, alpha, beta, phi)
    if best is None:
        raise ModelError("holt_damped could not be fitted")
    _, alpha, beta, phi = best
    level = float(history[0])
    trend = float(history[1] - history[0])
    for value in history[1:]:
        predicted = level + phi * trend
        previous = level
        level = alpha * float(value) + (1.0 - alpha) * predicted
        trend = beta * (level - previous) + (1.0 - beta) * phi * trend
    out = np.empty(h, dtype=np.float64)
    damping = 0.0
    for step in range(h):
        damping += phi ** (step + 1)
        out[step] = level + damping * trend
    return out


def ar1_levels(history: FloatArray, h: int, window: int = 15) -> FloatArray:
    """AR(1) on the level, the simplest mean reverting model.

    A linear trend fitted to a series that has turned down will cross zero and
    keep going, which is not a forecast but an artefact. An AR(1) in levels
    instead converges to a long run mean, with the speed of convergence
    estimated from the data. The coefficient is clipped below one so that the
    process stays stationary.
    """
    sample = history[-min(window, history.size) :]
    if sample.size < 5:
        raise ModelError("ar1_levels needs at least five observations")
    x = sample[:-1]
    y = sample[1:]
    x_mean = float(x.mean())
    y_mean = float(y.mean())
    sxx = float(np.sum((x - x_mean) ** 2))
    if sxx == 0.0:
        raise ModelError("level series has no variation")
    rho = float(np.sum((x - x_mean) * (y - y_mean)) / sxx)
    rho = max(min(rho, 0.98), 0.0)
    const = y_mean - rho * x_mean
    level = float(history[-1])
    out = np.empty(h, dtype=np.float64)
    for step in range(h):
        level = const + rho * level
        out[step] = level
    return out


@dataclass(frozen=True)
class ModelSpec:
    """A named forecaster with its fixed hyper parameters."""

    name: str
    family: str
    fn: Forecaster
    params: dict[str, float | int | str]

    def run(self, history: FloatArray, h: int) -> FloatArray:
        forecast = np.asarray(self.fn(history, h), dtype=np.float64)
        if forecast.shape != (h,):
            raise ModelError(f"{self.name} returned shape {forecast.shape} for horizon {h}")
        return np.maximum(forecast, 0.0)


def default_models() -> list[ModelSpec]:
    """The benchmark set fixed before any result is inspected."""
    return [
        ModelSpec("naive", "benchmark", naive, {}),
        ModelSpec("drift", "benchmark", drift, {}),
        ModelSpec("loglinear", "econometric", loglinear, {}),
        ModelSpec("ar1_growth", "econometric", ar1_growth, {"phi_clip": 0.99}),
        ModelSpec("ridge_lags", "machine_learning", ridge_lags, {"lags": 3, "alpha": 1.0}),
        ModelSpec("holt", "econometric", holt, {"grid": "alpha 0.1-0.9, beta 0.01-0.3"}),
        ModelSpec(
            "holt_damped", "econometric", holt_damped, {"grid": "alpha, beta, phi 0.80-0.98"}
        ),
        ModelSpec("ar1_levels", "econometric", ar1_levels, {"window": 15}),
        ModelSpec("combination", "ensemble", combination, {"members": "drift,holt,ridge_lags"}),
    ]


@dataclass(frozen=True)
class BacktestRow:
    """One forecast produced at one origin for one horizon."""

    model: str
    origin_year: int
    regime: str
    horizon: int
    actual: float
    forecast: float

    @property
    def error(self) -> float:
        return self.actual - self.forecast


def rolling_origin(
    series: pd.Series,
    models: Sequence[ModelSpec],
    horizons: Sequence[int] = HORIZONS,
    min_train: int = 12,
) -> list[BacktestRow]:
    """Backtest every model at every origin, for every horizon.

    The origin advances one year at a time. At each origin the model sees only
    data up to and including that year, which is the non anticipativity
    condition proved in the Lean development.
    """
    values = np.asarray(series.to_numpy(), dtype=np.float64)
    years = np.asarray([int(str(p)[:4]) for p in series.index], dtype=np.int64)
    if values.size != years.size:
        raise ModelError("series index and values disagree in length")
    max_h = max(horizons)
    rows: list[BacktestRow] = []
    for origin in range(min_train, values.size - max_h):
        history = values[: origin + 1]
        for model in models:
            try:
                forecast = model.run(history, max_h)
            except ModelError:
                continue
            for h in horizons:
                rows.append(
                    BacktestRow(
                        model=model.name,
                        origin_year=int(years[origin]),
                        regime=classify_regime(int(years[origin + h])),
                        horizon=h,
                        actual=float(values[origin + h]),
                        forecast=float(forecast[h - 1]),
                    )
                )
    if not rows:
        raise ModelError("no model produced a forecast, series too short")
    return rows


def _naive_scale(history: FloatArray) -> float:
    diffs = np.abs(np.diff(history))
    scale = float(np.mean(diffs)) if diffs.size else 0.0
    return scale if scale > 0 else float("nan")


def per_origin_mase(
    rows: Sequence[BacktestRow], series: pd.Series, min_train: int = 12
) -> dict[str, float]:
    """Mean absolute scaled error, scaled by the in sample naive error."""
    values = np.asarray(series.to_numpy(), dtype=np.float64)
    years = [int(str(p)[:4]) for p in series.index]
    position = {year: idx for idx, year in enumerate(years)}
    buckets: dict[str, list[float]] = {}
    for row in rows:
        idx = position[row.origin_year]
        scale = _naive_scale(values[: idx + 1])
        if not math.isfinite(scale):
            continue
        buckets.setdefault(row.model, []).append(abs(row.error) / scale)
    return {model: float(np.mean(vals)) for model, vals in buckets.items()}


def diebold_mariano(
    errors_a: Sequence[float] | FloatArray,
    errors_b: Sequence[float] | FloatArray,
    horizon: int = 1,
) -> tuple[float, float]:
    """Diebold-Mariano statistic and two sided p value for equal accuracy.

    Loss is absolute error. Overlapping h step forecasts induce serial
    correlation in the loss differential, so the variance uses a Newey-West
    estimator truncated at h - 1 lags.
    """
    a = np.asarray(errors_a, dtype=np.float64)
    b = np.asarray(errors_b, dtype=np.float64)
    if a.shape != b.shape or a.size < 4:
        raise ModelError("DM test needs two error vectors of equal length, at least four")
    d = np.abs(a) - np.abs(b)
    n = d.size
    mean_d = float(d.mean())
    var = float(np.mean((d - mean_d) ** 2))
    for lag in range(1, min(horizon, n)):
        cov = float(np.mean(d[lag:] * d[:-lag]))
        var += 2.0 * (1.0 - lag / horizon) * cov
    if var <= 0:
        return 0.0, 1.0
    stat = mean_d / math.sqrt(var / n)
    p_value = math.erfc(abs(stat) / math.sqrt(2.0))
    return stat, p_value


@dataclass(frozen=True)
class ModelScore:
    """Aggregate accuracy of one model across all origins and horizons."""

    model: str
    family: str
    mase: float
    rmse: float
    mape: float
    bias: float
    observations: int
    dm_stat: float
    dm_p_value: float
    mase_by_horizon: dict[int, float]

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "model": self.model,
            "family": self.family,
            "mase": round(self.mase, 4),
            "rmse": round(self.rmse, 2),
            "mape": round(self.mape, 4),
            "bias": round(self.bias, 2),
            "observations": self.observations,
            "dm_stat": round(self.dm_stat, 3),
            "dm_p_value": round(self.dm_p_value, 4),
            **{
                f"mase_h{horizon}": round(value, 4)
                for horizon, value in sorted(self.mase_by_horizon.items())
            },
        }


def score_models(
    rows: Sequence[BacktestRow], series: pd.Series, models: Sequence[ModelSpec], min_train: int = 12
) -> list[ModelScore]:
    """Score every model and test it against the naive benchmark."""
    by_model: dict[str, list[BacktestRow]] = {}
    for row in rows:
        by_model.setdefault(row.model, []).append(row)
    mase = per_origin_mase(rows, series, min_train)
    by_horizon: dict[str, dict[int, float]] = {}
    for horizon in sorted({r.horizon for r in rows}):
        horizon_rows = [r for r in rows if r.horizon == horizon]
        for model_name, value in per_origin_mase(horizon_rows, series, min_train).items():
            by_horizon.setdefault(model_name, {})[horizon] = value
    naive_errors = [r.error for r in by_model.get("naive", [])]
    scores: list[ModelScore] = []
    for model in models:
        subset = by_model.get(model.name)
        if not subset:
            continue
        errors = np.asarray([r.error for r in subset], dtype=np.float64)
        actuals = np.asarray([r.actual for r in subset], dtype=np.float64)
        mask = actuals != 0
        mape = float(np.mean(np.abs(errors[mask] / actuals[mask]))) if mask.any() else float("nan")
        if model.name == "naive" or len(naive_errors) != len(errors):
            dm_stat, dm_p = 0.0, 1.0
        else:
            dm_stat, dm_p = diebold_mariano(errors, naive_errors)
        scores.append(
            ModelScore(
                model=model.name,
                family=model.family,
                mase=mase.get(model.name, float("nan")),
                rmse=float(np.sqrt(np.mean(errors**2))),
                mape=mape,
                bias=float(np.mean(errors)),
                observations=int(errors.size),
                dm_stat=dm_stat,
                dm_p_value=dm_p,
                mase_by_horizon=by_horizon.get(model.name, {}),
            )
        )
    return scores


def select_model(scores: Sequence[ModelScore]) -> ModelScore:
    """Lowest MASE wins; ties break on RMSE, then on the model name."""
    usable = [s for s in scores if math.isfinite(s.mase)]
    if not usable:
        raise ModelError("no model could be scored")
    return sorted(usable, key=lambda s: (s.mase, s.rmse, s.model))[0]


def interval_from_errors(
    forecast: FloatArray, residuals: FloatArray, levels: Sequence[float] = INTERVAL_LEVELS
) -> dict[str, FloatArray]:
    """Multiplicative prediction intervals from pooled relative errors.

    Relative errors keep the interval width proportional to the level, which
    matters over a fifteen year projection. The lower bound is clipped at zero.
    """
    finite = residuals[np.isfinite(residuals)]
    if finite.size < 5:
        raise ModelError("not enough residuals to build an interval")
    ratios = 1.0 + finite
    out: dict[str, FloatArray] = {}
    for level in levels:
        tail = (1.0 - level) / 2.0  # two sided tail probability
        low = float(np.quantile(ratios, tail))
        high = float(np.quantile(ratios, 1.0 - tail))
        key = f"{round(level * 100)}"
        out[f"lo{key}"] = np.maximum(forecast * low, 0.0)
        out[f"hi{key}"] = np.maximum(forecast * high, 0.0)
    return out


def project(
    series: pd.Series,
    model: ModelSpec,
    rows: Sequence[BacktestRow],
    last_year: int = 2040,
    levels: Sequence[float] = INTERVAL_LEVELS,
) -> pd.DataFrame:
    """Project the selected model forward and attach empirical intervals."""
    values = np.asarray(series.to_numpy(), dtype=np.float64)
    last_observed = int(str(series.index[-1])[:4])
    # index strings are calendar years, so the slice is already an integer
    h = last_year - last_observed
    if h <= 0:
        raise ModelError("projection horizon must be positive")
    point = model.run(values, h)
    residuals = np.asarray(
        [r.error / r.forecast for r in rows if r.model == model.name and r.forecast > 0],
        dtype=np.float64,
    )
    frame = pd.DataFrame(
        {
            "year": np.arange(last_observed + 1, last_year + 1, dtype=np.int64),
            "point": point,
        }
    )
    for name, band in interval_from_errors(point, residuals, levels).items():
        frame[name] = band
    frame["model"] = model.name
    return frame


def _series_from_panel(panel_path: Path, column: str) -> pd.Series:
    frame = pd.read_csv(panel_path)
    if column not in frame.columns:
        raise ModelError(f"column {column!r} not found in {panel_path.name}")
    subset = frame[["period", column]].dropna()
    if subset.empty:
        raise ModelError(f"column {column!r} is empty")
    index = pd.Index([str(p) for p in subset["period"]], name="period")
    return pd.Series(np.asarray(subset[column].to_numpy(), dtype=np.float64), index=index)


def run_benchmark(
    panel_path: Path,
    column: str,
    out_dir: Path,
    last_year: int = 2040,
    horizons: Sequence[int] = HORIZONS,
    min_train: int = 12,
) -> dict[str, Path]:
    """Full pipeline: backtest, score, select, project, write artefacts."""
    series = _series_from_panel(panel_path, column)
    models = default_models()
    rows = rolling_origin(series, models, horizons, min_train)
    scores = score_models(rows, series, models, min_train)
    best = select_model(scores)
    chosen = next(m for m in models if m.name == best.model)
    forecast = project(series, chosen, rows, last_year)

    out_dir.mkdir(parents=True, exist_ok=True)
    backtest_path = out_dir / f"backtest_{column}.csv"
    metrics_path = out_dir / f"metrics_{column}.csv"
    forecast_path = out_dir / f"forecast_{column}.csv"
    register_path = out_dir / "model_register.csv"

    pd.DataFrame(
        [
            {
                "model": r.model,
                "origin_year": r.origin_year,
                "regime": r.regime,
                "horizon": r.horizon,
                "actual": round(r.actual, 2),
                "forecast": round(r.forecast, 2),
                "error": round(r.error, 2),
            }
            for r in rows
        ]
    ).to_csv(backtest_path, index=False)
    pd.DataFrame([s.as_dict() for s in scores]).to_csv(metrics_path, index=False)
    forecast.round(2).to_csv(forecast_path, index=False)

    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {
        "run_utc": stamp,
        "series": column,
        "observations": int(series.size),
        "first_year": str(series.index[0]),
        "last_year": str(series.index[-1]),
        "origins": len({r.origin_year for r in rows}),
        "selected": best.model,
        "mase": round(best.mase, 4),
        "rmse": round(best.rmse, 2),
        "dm_p_vs_naive": round(best.dm_p_value, 4),
        "horizons": list(horizons),
        "min_train": min_train,
        "projection_to": last_year,
    }
    if register_path.exists():
        previous = pd.read_csv(register_path)
        register = pd.concat([previous, pd.DataFrame([entry])], ignore_index=True)
    else:
        register = pd.DataFrame([entry])
    register.to_csv(register_path, index=False)
    return {
        "backtest": backtest_path,
        "metrics": metrics_path,
        "forecast": forecast_path,
        "register": register_path,
    }


def format_register_line(path: Path) -> str:
    """Compact console summary of the latest register entry."""
    frame = pd.read_csv(path)
    last = frame.iloc[-1]
    return json.dumps(
        {
            "series": str(last["series"]),
            "selected": str(last["selected"]),
            "mase": float(last["mase"]),
            "dm_p_vs_naive": float(last["dm_p_vs_naive"]),
        }
    )
