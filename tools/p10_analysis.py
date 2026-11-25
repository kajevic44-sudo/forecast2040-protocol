"""Analysis for P10, ownership layers and the capital cycle.

Every number that appears in the manuscript is produced here and written to
data/model/. The script is deliberately explicit: it prints what it computes,
it writes the tables, and it fails loudly if a series is missing.

Run with the project virtual environment:
    thesis/.venv/bin/python tools/p10_analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "historical" / "tidy" / "jst_germany.csv"
OUT = ROOT / "data" / "model"
OUT.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(20261124)
WAR_YEARS = set(range(1914, 1925)) | set(range(1939, 1949))


def load() -> pd.DataFrame:
    d = pd.read_csv(DATA)
    # Keep every row. Dropping missing credit ratios before differencing would
    # bridge the gaps and turn a five year change into a one year change, which
    # is the mistake this comment exists to prevent.
    d = d[["year", "eq_tr", "debtgdp"]].sort_values("year").reset_index(drop=True)
    d["dcredit"] = d["debtgdp"].diff()
    return d


def lag_table(d: pd.DataFrame) -> pd.DataFrame:
    """Correlation of the credit change with the real return k years ahead."""
    rows = []
    for k in range(-5, 6):
        x = d["dcredit"]
        y = d["eq_tr"].shift(-k)
        m = x.notna() & y.notna()
        n = int(m.sum())
        r = float(np.corrcoef(x[m], y[m])[0, 1])
        rows.append(
            {
                "horizon": k,
                "correlation": round(r, 6),
                "observations": n,
                "band_2se": round(2 / np.sqrt(n), 6),
            }
        )
    return pd.DataFrame(rows)


def hac_regression(y: np.ndarray, x: np.ndarray, lags: int) -> dict:
    """OLS with Newey and West standard errors, computed directly."""
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    xtx_inv = np.linalg.inv(X.T @ X)
    # Newey and West with Bartlett weights
    S = (X * resid[:, None]).T @ (X * resid[:, None])
    for lag in range(1, lags + 1):
        w = 1 - lag / (lags + 1)
        gamma = (X[lag:] * resid[lag:, None]).T @ (X[:-lag] * resid[:-lag, None])
        S += w * (gamma + gamma.T)
    cov = xtx_inv @ S @ xtx_inv
    se = np.sqrt(np.diag(cov))
    t = beta / se
    ss_tot = float(((y - y.mean()) ** 2).sum())
    ss_res = float((resid ** 2).sum())
    return {
        "slope": float(beta[1]),
        "intercept": float(beta[0]),
        "se_slope": float(se[1]),
        "t_slope": float(t[1]),
        "p_slope": float(2 * (1 - stats.norm.cdf(abs(t[1])))),
        "r2": 1 - ss_res / ss_tot,
        "n": n,
        "lags": lags,
    }


def block_bootstrap(d: pd.DataFrame, k: int = 5, block: int = 10, reps: int = 5000) -> dict:
    """Moving block bootstrap for the correlation at horizon k."""
    x = d["dcredit"].to_numpy()
    y = d["eq_tr"].shift(-k).to_numpy()
    m = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[m], y[m]
    n = len(x)
    point = float(np.corrcoef(x, y)[0, 1])
    draws = np.empty(reps)
    n_blocks = int(np.ceil(n / block))
    for i in range(reps):
        starts = RNG.integers(0, n - block + 1, n_blocks)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        draws[i] = np.corrcoef(x[idx], y[idx])[0, 1]
    return {
        "point": point,
        "ci_low": float(np.percentile(draws, 2.5)),
        "ci_high": float(np.percentile(draws, 97.5)),
        "share_below_zero": float((draws < 0).mean()),
        "reps": reps,
        "block": block,
    }


def subsamples(d: pd.DataFrame) -> pd.DataFrame:
    windows = {
        "1870 to 1913": (1870, 1913),
        "1914 to 1948": (1914, 1948),
        "1949 to 1990": (1949, 1990),
        "1991 to 2020": (1991, 2020),
        "1870 to 2020": (1870, 2020),
    }
    rows = []
    for label, (a, b) in windows.items():
        s = d[(d["year"] >= a) & (d["year"] <= b)]
        x = s["dcredit"]
        y = s["eq_tr"].shift(-5)
        m = x.notna() & y.notna()
        n = int(m.sum())
        r = float(np.corrcoef(x[m], y[m])[0, 1]) if n > 3 else np.nan
        beta = np.nan
        if n > 3:
            beta = float(np.polyfit(x[m], y[m], 1)[0])
        rows.append({"window": label, "n": n, "correlation": round(r, 6), "slope": round(beta, 6)})
    return pd.DataFrame(rows)


def exclusions(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base = d.copy()
    variants = {
        "all years": base,
        "without 1923": base[base["year"] != 1923],
        "without war years": base[~base["year"].isin(WAR_YEARS)],
        "without 1923 and war years": base[(base["year"] != 1923) & (~base["year"].isin(WAR_YEARS))],
        "after 1950": base[base["year"] >= 1950],
    }
    for label, s in variants.items():
        x = s["dcredit"]
        y = s["eq_tr"].shift(-5)
        m = x.notna() & y.notna()
        n = int(m.sum())
        r = float(np.corrcoef(x[m], y[m])[0, 1])
        rho, p = stats.spearmanr(x[m], y[m])
        reg = hac_regression(y[m].to_numpy(), x[m].to_numpy(), lags=5)
        rows.append(
            {
                "variant": label,
                "n": n,
                "pearson": round(r, 6),
                "spearman": round(float(rho), 6),
                "spearman_p": round(float(p), 6),
                "hac_slope": round(reg["slope"], 6),
                "hac_t": round(reg["t_slope"], 6),
                "hac_p": round(reg["p_slope"], 6),
                "r2": round(reg["r2"], 6),
            }
        )
    return pd.DataFrame(rows)


def reverse_test(d: pd.DataFrame) -> dict:
    """Does the five year return predict later credit growth?"""
    x = d["eq_tr"]
    y = d["dcredit"].shift(-5)
    m = x.notna() & y.notna()
    reg = hac_regression(y[m].to_numpy(), x[m].to_numpy(), lags=5)
    reg["correlation"] = float(np.corrcoef(x[m], y[m])[0, 1])
    return reg


def cumulative_test(d: pd.DataFrame, horizon: int = 5) -> dict:
    """The five year cumulative real return instead of the single year return."""
    growth = (1 + d["eq_tr"]).rolling(horizon).apply(np.prod, raw=True).shift(-horizon) - 1
    pair = pd.concat([d["dcredit"], growth], axis=1).dropna()
    x, y = pair.iloc[:, 0].to_numpy(), pair.iloc[:, 1].to_numpy()
    reg = hac_regression(y, x, lags=horizon)
    reg["correlation"] = float(np.corrcoef(x, y)[0, 1])
    return reg


def log_credit_test(d: pd.DataFrame, horizon: int = 5) -> dict:
    """Log growth of the credit ratio as the regressor."""
    lc = np.log(d["debtgdp"]).diff()
    pair = pd.concat([lc, d["eq_tr"].shift(-horizon)], axis=1).dropna()
    x, y = pair.iloc[:, 0].to_numpy(), pair.iloc[:, 1].to_numpy()
    reg = hac_regression(y, x, lags=horizon)
    reg["correlation"] = float(np.corrcoef(x, y)[0, 1])
    return reg


def rolling_correlation(d: pd.DataFrame, window: int = 40) -> dict:
    x = d["dcredit"]
    y = d["eq_tr"].shift(-5)
    s = pd.DataFrame({"x": x, "y": y}).dropna()
    r = s["x"].rolling(window).corr(s["y"]).dropna()
    return {
        "window": window,
        "first_year": int(s.index[min(window - 1, len(s) - 1)] + d["year"].iloc[0]),
        "min": float(r.min()),
        "max": float(r.max()),
        "median": float(r.median()),
        "share_negative": float((r < 0).mean()),
        "n_windows": int(len(r)),
    }


def drawdown_stats() -> dict:
    dd = pd.read_csv(ROOT / "data" / "historical" / "tidy" / "de_equity_drawdowns.csv")
    depth = dd.iloc[:, 2].to_numpy(dtype=float)
    years = dd.iloc[:, 3].to_numpy(dtype=float)
    rho, p = stats.spearmanr(depth, years)
    pear, ppear = stats.pearsonr(depth, years)
    return {
        "episodes": int(len(dd)),
        "depth_duration_spearman": float(rho),
        "p_value": float(p),
        "depth_duration_pearson": float(pear),
        "pearson_p": float(ppear),
        "deepest": float(depth.min()),
        "median_recovery": float(np.median(years)),
        "max_recovery": float(years.max()),
    }


def ownership_concentration() -> dict:
    """Herfindahl index of voting rights at Volkswagen, 31 December 2025."""
    votes = {"Porsche SE": 53.3, "Lower Saxony": 20.0, "Qatar Holding": 17.0, "free float": 9.7}
    shares = np.array(list(votes.values())) / 100
    hhi = float((shares ** 2).sum())
    top3 = float(sum(sorted(shares)[-3:]))
    return {"hhi": hhi, "top3": top3, "effective_number": 1 / hhi, "votes": votes}


def power_block(n_pairs: int, overlap: int, observed: float) -> dict:
    """Effective sample size and power for the overlapping five year windows."""
    import math
    from scipy.stats import norm

    n_eff = n_pairs / overlap
    se = 1.0 / math.sqrt(n_eff - 3)
    mde = math.tanh((norm.ppf(0.975) + norm.ppf(0.80)) * se)

    def power(r: float, s: float) -> float:
        zr = math.atanh(r)
        lo = norm.ppf(0.025) * s
        hi = norm.ppf(0.975) * s
        return float(norm.cdf((lo - zr) / s) + 1.0 - norm.cdf((hi - zr) / s))

    grid = {f"{r:.1f}": power(r, se) for r in (-0.2, -0.3, -0.4, -0.5, -0.6, -0.7)}
    return {
        "pairs": n_pairs,
        "overlap": overlap,
        "effective_n": n_eff,
        "fisher_se": se,
        "mde_80": mde,
        "observed": observed,
        "power_observed": power(observed, se),
        "power_if_independent": power(observed, 1.0 / math.sqrt(n_pairs - 3)),
        "power_grid": grid,
    }


def main() -> None:
    d = load()
    print(f"years {int(d['year'].min())} to {int(d['year'].max())}, rows {len(d)}")

    pw = power_block(123, 5, -0.303589)
    print("\npower and effective sample size")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in pw.items()}, indent=2))

    lags = lag_table(d)
    lags.to_csv(OUT / "p10_lag_correlations.csv", index=False)
    print("\nlag correlations")
    print(lags.to_string(index=False))

    pair5 = pd.concat([d["dcredit"], d["eq_tr"].shift(-5)], axis=1).dropna()
    reg5 = hac_regression(pair5.iloc[:, 1].to_numpy(), pair5.iloc[:, 0].to_numpy(), lags=5)
    reg5["correlation"] = float(pair5.iloc[:, 0].corr(pair5.iloc[:, 1]))
    print("\nHAC regression, horizon 5")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in reg5.items()}, indent=2))

    boot = block_bootstrap(d)
    print("\nblock bootstrap")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in boot.items()}, indent=2))

    subs = subsamples(d)
    subs.to_csv(OUT / "p10_subsamples.csv", index=False)
    print("\nsubsamples")
    print(subs.to_string(index=False))

    exc = exclusions(d)
    exc.to_csv(OUT / "p10_exclusions.csv", index=False)
    print("\nexclusions")
    print(exc.to_string(index=False))

    rev = reverse_test(d)
    print("\nreverse test")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in rev.items()}, indent=2))

    cum = cumulative_test(d)
    print("\ncumulative five year return")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in cum.items()}, indent=2))

    logc = log_credit_test(d)
    print("\nlog credit growth")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in logc.items()}, indent=2))

    roll = rolling_correlation(d)
    print("\nrolling correlation")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in roll.items()}, indent=2))

    dd = drawdown_stats()
    print("\ndrawdowns")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in dd.items()}, indent=2))

    own = ownership_concentration()
    print("\nownership")
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in own.items()}, indent=2))

    summary = {
        "lag_table": lags.to_dict(orient="records"),
        "regression_h5": reg5,
        "power": pw,
        "bootstrap_h5": boot,
        "reverse": rev,
        "cumulative": cum,
        "log_credit": logc,
        "rolling": roll,
        "drawdowns": dd,
        "ownership": own,
    }
    (OUT / "p10_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
