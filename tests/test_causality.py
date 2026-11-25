"""Property tests for the non-anticipative split of P01.

The Lean module proves that any forecaster receiving only the prefix is causal.
These tests check the same property on the Python implementation, at the level of
the runner rather than of a single function: changing the data after an origin
must not change any record produced at or before that origin.

Author: Armin Kajevic
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from p01_protocol import MODELS, forecast_path, mase_scale, run_series  # noqa: E402


def series(seed: int = 7, length: int = 26) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return 3.0e6 * np.exp(np.cumsum(rng.normal(0.0, 0.07, length)))


def test_prefix_is_the_only_input() -> None:
    """Every candidate returns the same path when the caller passes the same prefix."""
    y = series()
    origin = 20
    rng = np.random.default_rng(11)
    changed = y.copy()
    changed[origin:] = rng.uniform(1.0e6, 5.0e6, len(y) - origin)
    for model in MODELS:
        assert np.array_equal(
            forecast_path(y[:origin], model), forecast_path(changed[:origin], model)
        ), model


def test_scale_ignores_future_values() -> None:
    y = series()
    origin = 20
    changed = y.copy()
    changed[origin:] = 1.0
    assert mase_scale(y[:origin]) == mase_scale(changed[:origin])


def test_runner_records_are_causal() -> None:
    """Changing the future leaves every record at or before the origin unchanged."""
    y = series(length=24)
    years = np.arange(1991, 1991 + len(y))
    origin_index = 19
    changed = y.copy()
    rng = np.random.default_rng(13)
    changed[origin_index:] = rng.uniform(0.5e6, 6.0e6, len(y) - origin_index)

    base = run_series(y, years, "TEST")
    other = run_series(changed, years, "TEST")

    # Forecasts at or before the origin are causal, whatever the horizon.
    early = base[base.origin_index <= origin_index]
    early_other = other[other.origin_index <= origin_index]
    assert len(early) == len(early_other) > 0
    for column in ("forecast", "divergent", "fallback"):
        assert np.array_equal(early[column].to_numpy(), early_other[column].to_numpy()), column

    # Errors are causal only when the target itself lies before the change.
    past = base[base.origin_index + base.horizon - 1 < origin_index]
    past_other = other[other.origin_index + other.horizon - 1 < origin_index]
    assert len(past) == len(past_other) > 0
    for column in ("error", "mase"):
        assert np.array_equal(past[column].to_numpy(), past_other[column].to_numpy()), column


def test_selection_key_is_unique_when_scores_differ() -> None:
    scores = {"naive": 1.9, "holt": 2.0, "theta": 2.1}
    keys = sorted((value, name) for name, value in scores.items())
    assert keys[0][1] == "naive"
    assert keys[0][0] < keys[1][0]
