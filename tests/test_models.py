"""Tests for the rolling-origin benchmark.

Each estimator is checked against a series whose answer is known in closed
form, so a regression in the code cannot hide behind a plausible number.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forecast2040.models import (
    ModelError,
    ar1_growth,
    classify_regime,
    combination,
    default_models,
    diebold_mariano,
    drift,
    holt,
    interval_from_errors,
    loglinear,
    naive,
    project,
    ridge_lags,
    rolling_origin,
    score_models,
    select_model,
)


def _series(values: list[float], start: int = 2000) -> pd.Series:
    index = pd.Index([str(start + i) for i in range(len(values))], name="period")
    return pd.Series(np.asarray(values, dtype=np.float64), index=index)


def test_naive_repeats_last_value() -> None:
    history = np.array([1.0, 2.0, 3.0, 4.0])
    assert np.allclose(naive(history, 3), [4.0, 4.0, 4.0])


def test_drift_is_exact_on_linear_series() -> None:
    history = np.arange(10, dtype=np.float64) * 5.0
    forecast = drift(history, 4)
    assert np.allclose(forecast, [50.0, 55.0, 60.0, 65.0])


def test_loglinear_recovers_exponential_growth() -> None:
    growth = 0.07
    history = 100.0 * np.exp(growth * np.arange(20, dtype=np.float64))
    forecast = loglinear(history, 3)
    expected = 100.0 * np.exp(growth * np.arange(20, 23, dtype=np.float64))
    assert np.allclose(forecast, expected, rtol=1e-8)


def test_loglinear_rejects_non_positive_values() -> None:
    with pytest.raises(ModelError):
        loglinear(np.array([1.0, 0.0, 2.0]), 1)


def test_ar1_growth_keeps_positive_levels() -> None:
    history = 1000.0 * np.exp(0.03 * np.arange(15, dtype=np.float64))
    forecast = ar1_growth(history, 5)
    assert np.all(forecast > 0)
    assert np.all(np.diff(forecast) > 0)


def test_ridge_lags_is_deterministic() -> None:
    history = 500.0 * np.exp(0.02 * np.arange(20, dtype=np.float64))
    first = ridge_lags(history, 3)
    second = ridge_lags(history, 3)
    assert np.array_equal(first, second)
    assert np.all(first > 0)


def test_regime_calendar_is_fixed() -> None:
    assert classify_regime(2009) == "crisis"
    assert classify_regime(2010) == "boom"
    assert classify_regime(2020) == "crisis"
    assert classify_regime(2016) == "normal"


def test_rolling_origin_respects_horizon_window() -> None:
    series = _series([float(100 + i) for i in range(25)])
    rows = rolling_origin(series, default_models(), horizons=(1, 2), min_train=10)
    assert {r.horizon for r in rows} == {1, 2}
    assert max(r.origin_year for r in rows) == 2022
    assert min(r.origin_year for r in rows) == 2010


def test_scores_rank_naive_against_itself() -> None:
    series = _series([float(100 + i) for i in range(25)])
    models = default_models()
    rows = rolling_origin(series, models, horizons=(1,), min_train=10)
    scores = score_models(rows, series, models, min_train=10)
    naive_score = next(s for s in scores if s.model == "naive")
    assert math.isclose(naive_score.mase, 1.0, rel_tol=1e-9)
    assert naive_score.dm_p_value == 1.0


def test_selection_is_deterministic() -> None:
    series = _series([float(100 + i) for i in range(30)])
    models = default_models()
    rows = rolling_origin(series, models, horizons=(1, 2), min_train=12)
    scores = score_models(rows, series, models, min_train=12)
    assert select_model(scores).model == select_model(scores).model


def test_diebold_mariano_is_symmetric() -> None:
    rng = np.random.default_rng(7)
    a = rng.normal(0.0, 1.0, 40)
    b = rng.normal(0.0, 1.0, 40)
    stat_ab, p_ab = diebold_mariano(a, b, horizon=2)
    stat_ba, p_ba = diebold_mariano(b, a, horizon=2)
    assert math.isclose(stat_ab, -stat_ba, rel_tol=1e-12)
    assert math.isclose(p_ab, p_ba, rel_tol=1e-12)


def test_intervals_bracket_the_point_forecast() -> None:
    point = np.array([100.0, 110.0, 120.0])
    residuals = np.linspace(-0.3, 0.3, 21)
    bands = interval_from_errors(point, residuals)
    assert np.all(bands["lo50"] <= point)
    assert np.all(bands["hi50"] >= point)
    assert np.all(bands["lo95"] <= bands["lo50"])
    assert np.all(bands["hi95"] >= bands["hi50"])


def test_projection_ends_in_requested_year() -> None:
    series = _series([float(1000 + 20 * i) for i in range(20)])
    models = default_models()
    rows = rolling_origin(series, models, horizons=(1, 2), min_train=12)
    frame = project(series, models[1], rows, last_year=2040)
    assert int(frame["year"].iloc[0]) == 2020
    assert int(frame["year"].iloc[-1]) == 2040
    assert len(frame) == 21
    assert (frame["point"] >= 0).all()


def test_run_benchmark_writes_artefacts(tmp_path: Path) -> None:
    from forecast2040.models import run_benchmark

    frame = pd.DataFrame(
        {
            "period": [str(2000 + i) for i in range(30)],
            "series_a": [float(1000 + 25 * i) for i in range(30)],
        }
    )
    panel = tmp_path / "panel_annual.csv"
    frame.to_csv(panel, index=False)
    written = run_benchmark(panel, "series_a", tmp_path / "model", last_year=2035)
    assert all(path.exists() for path in written.values())
    register = pd.read_csv(written["register"])
    assert len(register) == 1
    assert register["series"].iloc[0] == "series_a"
    forecast = pd.read_csv(written["forecast"])
    assert int(forecast["year"].iloc[-1]) == 2035


def test_holt_tracks_a_linear_trend() -> None:
    history = np.arange(20, dtype=np.float64) * 10.0
    forecast = holt(history, 3)
    assert np.allclose(forecast, [200.0, 210.0, 220.0], atol=1e-6)


def test_combination_lies_between_members() -> None:
    history = 1000.0 * np.exp(0.02 * np.arange(20, dtype=np.float64))
    members = np.vstack([drift(history, 2), holt(history, 2), ridge_lags(history, 2)])
    combined = combination(history, 2)
    assert np.all(combined <= members.max(axis=0) + 1e-9)
    assert np.all(combined >= members.min(axis=0) - 1e-9)
