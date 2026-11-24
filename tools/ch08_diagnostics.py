"""Numbers quoted in chapter 8, computed from the registered pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from forecast2040.ml import design_matrix, feature_importance, learning_curve, ml_models

ROOT = "/home/ubuntu/battery_phd/thesis"
PANEL = f"{ROOT}/data/panel/panel_annual.csv"

SERIES = {
    "vw_group_china_deliveries": 1987,
    "destatis_pkw_neuzulassungen_jahre": 1991,
}


def load(column: str) -> np.ndarray:
    frame = pd.read_csv(PANEL)
    subset = frame[["period", column]].dropna()
    return np.asarray(subset[column].to_numpy(), dtype=np.float64)


for column, first_year in SERIES.items():
    values = load(column)
    X, y = design_matrix(values)
    print("=" * 70)
    print(column, "n", values.size, "rows", X.shape[0], "features", X.shape[1])

    scaler = StandardScaler().fit(X)
    Z = scaler.transform(X)
    Zc = Z - Z.mean(axis=0)
    sv = np.linalg.svd(Zc, compute_uv=False)
    print("singular values", np.round(sv, 3))
    print("condition number", round(float(sv.max() / sv.min()), 2))
    lam = 1.0
    df = float(np.sum(sv**2 / (sv**2 + lam)))
    print("effective df at alpha=1:", round(df, 3), "plus intercept ->", round(df + 1, 3))
    for a in (0.01, 0.1, 1.0, 10.0, 100.0):
        print("  alpha", a, "df", round(float(np.sum(sv**2 / (sv**2 + a))), 3))

    pipe = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=1.0))]).fit(X, y)
    coef = pipe.named_steps["ridge"].coef_
    print("ridge coef (scaled):", np.round(coef, 3))
    print("ridge intercept:", round(float(pipe.named_steps["ridge"].intercept_), 1))

    # correlation between tree predictions, the rho of the proposition
    forest = RandomForestRegressor(n_estimators=400, random_state=42, min_samples_leaf=2)
    forest.fit(X, y)
    preds = np.column_stack([t.predict(X) for t in forest.estimators_])
    corr = np.corrcoef(preds.T)
    iu = np.triu_indices_from(corr, k=1)
    print("mean tree correlation rho:", round(float(corr[iu].mean()), 4))
    print("min/max tree corr:", round(float(corr[iu].min()), 4), round(float(corr[iu].max()), 4))
    var_single = float(np.mean(np.var(preds, axis=0, ddof=1)))
    var_avg = float(np.var(preds.mean(axis=1), ddof=1))
    print("mean single tree variance:", round(var_single, 1))
    print("variance of average:", round(var_avg, 1))
    print("ratio observed:", round(var_avg / var_single, 4))
    rho = float(corr[iu].mean())
    B = preds.shape[1]
    print("ratio predicted by proposition:", round(rho + (1 - rho) / B, 4))
    print("effective number of independent trees:", round(1 / (rho + (1 - rho) / B), 1))

    print("importance:")
    for row in feature_importance(values):
        print("   ", row.feature, round(row.importance, 4))

    curve = learning_curve(
        pd.Series(values, index=[str(first_year + i) for i in range(values.size)]),
        ml_models()[1],
        horizons=(1,),
    )
    g = curve.groupby("train_size")["abs_error"].mean()
    print("learning curve first/last:", round(float(g.iloc[0]), 1), round(float(g.iloc[-1]), 1))
    print("learning curve min:", round(float(g.min()), 1), "at", int(g.idxmin()))
    print("learning curve at 12, 20, 30:", [round(float(g.loc[s]), 1) for s in (12, 20, 30) if s in g.index])
