"""Checks added to P01 after the first round of internal review.

All four products use the loss differential in vehicles, because that is the
unit in which the horizon test is defined in the paper. The scaled version is
reported only through MASE, which comes from the archived metrics file.

Outputs, written to data/model/:

1. p01_variance.csv     the horizon test under three variance estimators
2. p01_power.csv        minimum detectable effect and achieved power per horizon
3. p01_romano_wolf.csv  stepdown max-t over the thirteen candidates, clustered by origin
4. p01_complexity.csv   free coefficients, tuned hyperparameters, features
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
BACK = ROOT / "data/model/backtest_full_destatis_pkw_neuzulassungen_jahre.csv"
OUT = ROOT / "data/model"

B = 20000
SEED = 20261124


def load() -> pd.DataFrame:
    return pd.read_csv(BACK)


def bartlett(d: np.ndarray, h: int) -> tuple[float, list[float]]:
    n = d.size
    mean = d.mean()
    var = float(np.mean((d - mean) ** 2))
    covs = []
    for k in range(1, min(h, n)):
        cov = float(np.mean((d[k:] - mean) * (d[:-k] - mean)))
        covs.append(cov)
        var += 2.0 * (1.0 - k / h) * cov
    return max(var, 0.0), covs


def hln(stat: float, n: int, h: int) -> float:
    return stat * np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)


def horizon_diff(back: pd.DataFrame, h: int) -> np.ndarray:
    wide = back[back["horizon"] == h].pivot_table(
        index="origin_year", columns="model", values="error"
    )
    return (wide["ridge_lags"].abs() - wide["naive"].abs()).to_numpy(float)


def variance_table(back: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for h in range(1, 6):
        d = horizon_diff(back, h)
        n = d.size
        mean = float(d.mean())
        var_iid = float(np.var(d, ddof=1))
        t_iid = mean / np.sqrt(var_iid / n)
        var_b, covs = bartlett(d, h)
        t_b = mean / np.sqrt(var_b / n)
        t_bh = hln(t_b, n, h)
        sample = d[rng.integers(0, n, size=(B, n))]
        stat = np.empty(B)
        for i, row in enumerate(sample):
            v, _ = bartlett(row, h)
            stat[i] = hln(row.mean() / np.sqrt(max(v, 1e-12) / n), n, h)
        rows.append(
            {
                "horizon": h,
                "mean_diff": mean,
                "t_iid": t_iid,
                "p_iid": 2 * stats.t.sf(abs(t_iid), n - 1),
                "dm_bartlett": t_b,
                "dm_hln": t_bh,
                "p_bartlett": 2 * stats.t.sf(abs(t_bh), n - 1),
                "p_bootstrap": float(np.mean(np.abs(stat) >= abs(t_bh))),
                "variance_ratio": var_b / var_iid,
                "gamma_1": covs[0] if covs else np.nan,
                "gamma_2": covs[1] if len(covs) > 1 else np.nan,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "p01_variance.csv", index=False, float_format="%.6f")
    return frame


def power(back: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for h in range(1, 6):
        wide = back[back["horizon"] == h].pivot_table(
            index="origin_year", columns="model", values="error"
        )
        d = (wide["ridge_lags"].abs() - wide["naive"].abs()).to_numpy(float)
        naive_mae = float(wide["naive"].abs().mean())
        n = d.size
        mean, sd = float(d.mean()), float(d.std(ddof=1))
        se = sd / np.sqrt(n)
        t_obs = mean / se
        t_crit = stats.t.ppf(0.975, n - 1)
        t_pow = stats.t.ppf(0.80, n - 1)
        mde = (t_crit + t_pow) * se
        achieved = float(
            stats.nct.sf(t_crit, n - 1, -abs(t_obs)) + stats.nct.cdf(-t_crit, n - 1, -abs(t_obs))
        )
        rows.append(
            {
                "horizon": h,
                "origins": n,
                "naive_mae": naive_mae,
                "mean_diff": mean,
                "observed_pct": 100 * abs(mean) / naive_mae,
                "mde_vehicles": mde,
                "mde_pct": 100 * mde / naive_mae,
                "power_at_observed": achieved,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "p01_power.csv", index=False, float_format="%.6f")
    return frame


def romano_wolf(back: pd.DataFrame) -> pd.DataFrame:
    # Mean absolute error per origin and model, then the differential against naive.
    # Averaging over the five horizons inside an origin keeps the origin as the
    # clustering unit, which is the unit that the rolling design actually replicates.
    back = back.assign(abs_error=back["error"].abs())
    frame = back.pivot_table(index="origin_year", columns="model", values="abs_error", aggfunc="mean")
    models = [c for c in frame.columns if c != "naive"]
    diff = frame[models].sub(frame["naive"], axis=0).to_numpy(float)
    n = diff.shape[0]
    mean = diff.mean(axis=0)
    se = diff.std(axis=0, ddof=1) / np.sqrt(n)
    t_obs = mean / se

    rng = np.random.default_rng(SEED)
    boot = diff[rng.integers(0, n, size=(B, n))].mean(axis=1)
    t_boot = np.abs((boot - mean) / se)

    order = np.argsort(-np.abs(t_obs))
    adjusted = np.empty(len(models))
    remaining = list(range(len(models)))
    for pos in order:
        crit = t_boot[:, remaining].max(axis=1)
        adjusted[pos] = float(np.mean(crit >= abs(t_obs[pos])))
        remaining.remove(int(pos))

    out = pd.DataFrame({"model": models, "t_cluster": t_obs, "p_stepdown": adjusted})
    out = out.sort_values("p_stepdown").reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    out.to_csv(OUT / "p01_romano_wolf.csv", index=False, float_format="%.6f")
    return out


COMPLEXITY = [
    ("naive", 0, 0, 0, "last value, no estimated quantity"),
    ("drift", 2, 0, 1, "intercept and slope on the time index"),
    ("loglinear", 2, 0, 1, "intercept and slope in logs"),
    ("ar1_growth", 2, 0, 1, "intercept and one autoregressive coefficient"),
    ("ar1_levels", 2, 0, 1, "intercept and one autoregressive coefficient"),
    ("holt", 2, 2, 1, "two states, alpha and beta chosen on a 9 by 5 grid"),
    ("holt_damped", 2, 3, 1, "two states, alpha, beta and phi on a 9 by 4 by 5 grid"),
    ("arima_111", 3, 0, 1, "three structural parameters plus the innovation variance"),
    ("combination", 0, 0, 3, "equal weights over drift, Holt and ridge, no estimated weight"),
    ("ridge_lags", 4, 0, 3, "intercept and three lag coefficients, penalty fixed at 1.0"),
    ("ridge_ml", 7, 0, 6, "intercept, three lags, two growth rates and a time index"),
    ("random_forest", 0, 3, 6, "400 trees, leaf size 2, at most 17 leaves per tree"),
    ("gradient_boosting", 0, 3, 6, "300 trees of depth 2, four leaves per tree"),
]


def complexity() -> pd.DataFrame:
    frame = pd.DataFrame(
        COMPLEXITY,
        columns=["model", "free_coefficients", "tuned_hyperparameters", "features", "note"],
    )
    frame["coefficients_per_15_obs"] = frame["free_coefficients"] / 15
    frame.to_csv(OUT / "p01_complexity.csv", index=False, float_format="%.4f")
    return frame


def main() -> None:
    back = load()
    print(variance_table(back).round(4).to_string(index=False))
    print()
    print(power(back).round(4).to_string(index=False))
    print()
    print(romano_wolf(back).round(4).to_string(index=False))
    print()
    print(complexity().iloc[:, :4].to_string(index=False))


if __name__ == "__main__":
    main()
