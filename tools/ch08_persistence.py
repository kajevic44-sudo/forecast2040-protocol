"""Local persistence of the fitted one step maps used in the recursive forecast."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from forecast2040.ml import _features, design_matrix

PANEL = "/home/ubuntu/battery_phd/thesis/data/panel/panel_annual.csv"
LAGS = 3

SERIES = {
    "vw_group_china_deliveries": 1987,
    "destatis_pkw_neuzulassungen_jahre": 1991,
}


def load(column: str) -> np.ndarray:
    frame = pd.read_csv(PANEL)
    return np.asarray(frame[["period", column]].dropna()[column].to_numpy(), dtype=np.float64)


for column, first in SERIES.items():
    values = load(column)
    X, y = design_matrix(values)
    models = {
        "ridge_ml": Pipeline([("s", StandardScaler()), ("r", Ridge(alpha=1.0))]),
        "forest": RandomForestRegressor(n_estimators=400, random_state=42, min_samples_leaf=2),
        "boost": GradientBoostingRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=2, random_state=42
        ),
    }
    print("=" * 70)
    print(column, "n", values.size, "mean level", round(float(values.mean()), 1))
    base = _features(values, LAGS, values.size)
    for name, model in models.items():
        model.fit(X, y)
        row = base.reshape(1, -1).copy()
        f0 = float(np.asarray(model.predict(row)).ravel()[0])
        step = 1e-4 * float(values.mean())
        grads = []
        for j in range(LAGS):
            pert = row.copy()
            pert[0, j] += step
            f1 = float(np.asarray(model.predict(pert)).ravel()[0])
            grads.append((f1 - f0) / step)
        print(
            f"  {name:9s} f0 {f0:12.1f}  grads {np.round(grads, 3)}  persistence {sum(grads):.3f}"
        )
