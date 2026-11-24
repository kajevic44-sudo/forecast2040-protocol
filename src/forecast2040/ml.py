"""Supervised learning and state space models for the 2040 study.

The design principle is the same as in models.py: every forecaster is a pure
function of the history it is allowed to see. Machine learning models are
wrapped so that they produce a recursive multi step forecast from a single
history array, which makes them comparable with the statistical benchmarks on
exactly the same information set.

Feature construction is deliberately explicit and small. With 35 annual
observations a large feature set would overfit before it could generalise, so
each model sees three lags, two growth rates and a time index, and nothing else.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor  # type: ignore[import-untyped]
from sklearn.linear_model import Ridge  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]
from statsmodels.tsa.arima.model import ARIMA  # type: ignore[import-untyped]

from .models import FloatArray, ModelError, ModelSpec

LAGS: int = 3


def _features(values: FloatArray, lags: int, position: int) -> FloatArray:
    """Feature row for the observation at `position`, using only earlier values."""
    window = values[position - lags : position][::-1]
    growth = (window[:-1] - window[1:]) / np.maximum(window[1:], 1e-9)
    return np.concatenate([window, growth, np.array([float(position)])])


def design_matrix(values: FloatArray, lags: int = LAGS) -> tuple[FloatArray, FloatArray]:
    """Build the supervised learning matrix from a single series."""
    if values.size <= lags + 2:
        raise ModelError("series too short for the requested lag structure")
    rows = values.size - lags
    features = np.empty((rows, 2 * lags), dtype=np.float64)
    target = np.empty(rows, dtype=np.float64)
    for offset in range(rows):
        position = lags + offset
        features[offset] = _features(values, lags, position)
        target[offset] = values[position]
    return features, target


def _recursive(model: object, values: FloatArray, h: int, lags: int) -> FloatArray:
    """Forecast h steps ahead by feeding each prediction back as a lag."""
    extended = values.astype(np.float64).copy()
    out = np.empty(h, dtype=np.float64)
    for step in range(h):
        position = extended.size
        row = _features(extended, lags, position).reshape(1, -1)
        prediction = float(np.asarray(model.predict(row)).ravel()[0])  # type: ignore[attr-defined]
        prediction = max(prediction, 0.0)
        out[step] = prediction
        extended = np.append(extended, prediction)
    return out


def ridge_forecast(history: FloatArray, h: int, alpha: float = 1.0) -> FloatArray:
    features, target = design_matrix(history)
    model = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=alpha))])
    model.fit(features, target)
    return _recursive(model, history, h, LAGS)


def forest_forecast(history: FloatArray, h: int, trees: int = 400, seed: int = 42) -> FloatArray:
    features, target = design_matrix(history)
    model = RandomForestRegressor(n_estimators=trees, random_state=seed, min_samples_leaf=2)
    model.fit(features, target)
    return _recursive(model, history, h, LAGS)


def boosting_forecast(history: FloatArray, h: int, seed: int = 42) -> FloatArray:
    features, target = design_matrix(history)
    model = GradientBoostingRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=2, random_state=seed
    )
    model.fit(features, target)
    return _recursive(model, history, h, LAGS)


def arima_forecast(
    history: FloatArray, h: int, order: tuple[int, int, int] = (1, 1, 1)
) -> FloatArray:
    """ARIMA on the level series, with a linear trend term."""
    try:
        fitted = ARIMA(history, order=order, trend="t").fit()
    except Exception as exc:
        raise ModelError(f"arima failed: {exc}") from exc
    forecast = np.asarray(fitted.forecast(h), dtype=np.float64)
    return np.maximum(forecast, 0.0)


def ml_models() -> list[ModelSpec]:
    """The learning models, fixed before any result is inspected."""
    return [
        ModelSpec("ridge_ml", "machine_learning", ridge_forecast, {"alpha": 1.0, "lags": LAGS}),
        ModelSpec("random_forest", "machine_learning", forest_forecast, {"trees": 400, "seed": 42}),
        ModelSpec(
            "gradient_boosting", "machine_learning", boosting_forecast, {"trees": 300, "seed": 42}
        ),
        ModelSpec("arima_111", "econometric", arima_forecast, {"order": "1,1,1", "trend": "t"}),
    ]


@dataclass(frozen=True)
class ImportanceRow:
    """Feature importance reported in the dissertation appendix."""

    feature: str
    importance: float


def feature_importance(history: FloatArray) -> list[ImportanceRow]:
    """Impurity importance of the forest, with readable feature names."""
    features, target = design_matrix(history)
    model = RandomForestRegressor(n_estimators=400, random_state=42, min_samples_leaf=2)
    model.fit(features, target)
    names = [f"lag_{i + 1}" for i in range(LAGS)] + [f"growth_{i + 1}" for i in range(LAGS - 1)]
    names.append("time_index")
    return [
        ImportanceRow(name, float(value))
        for name, value in sorted(
            zip(names, model.feature_importances_, strict=True), key=lambda p: -p[1]
        )
    ]


def learning_curve(
    series: pd.Series, model: ModelSpec, horizons: Sequence[int] = (1, 2, 3)
) -> pd.DataFrame:
    """Mean absolute error as the training window grows.

    This answers the question a committee always asks: is the model improving
    with more data, or has it already saturated.
    """
    values = np.asarray(series.to_numpy(), dtype=np.float64)
    rows = []
    for size in range(12, values.size - max(horizons)):
        history = values[:size]
        try:
            forecast = model.run(history, max(horizons))
        except ModelError:
            continue
        for h in horizons:
            actual = float(values[size + h - 1])
            rows.append(
                {"train_size": size, "horizon": h, "abs_error": abs(actual - forecast[h - 1])}
            )
    return pd.DataFrame(rows)
