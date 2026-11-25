"""Inference for P01: clustered Diebold-Mariano, Holm, MCS, conformal intervals.

Inputs are produced by tools/p01_protocol.py. The script writes
data/model/p01_inference.json, data/model/p01_dm_table.csv,
data/model/p01_conformal.csv and data/model/p01_forecast_2040.csv.

Author: Armin Kajevic
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20261125
ALPHA = 0.05
LEVELS = (0.80, 0.90, 0.95)
BOOT = 10000


def cells(records: pd.DataFrame) -> pd.DataFrame:
    records = records[records.divergent == 0]
    return records


def cluster_dm(frame: pd.DataFrame, model: str, benchmark: str = "naive") -> dict:
    a = frame[frame.model == model].set_index(["country", "origin_year", "horizon"]).mase
    b = frame[frame.model == benchmark].set_index(["country", "origin_year", "horizon"]).mase
    d = (a - b).dropna()
    n = len(d)
    groups = d.index.get_level_values("country")
    # Country-balanced weights: each country contributes one unit, so a
    # country with a long history does not dominate the mean. This is the
    # aggregation fixed in the protocol and reported in Table 3.
    counts = d.groupby(groups).transform("size")
    weight = 1.0 / counts
    total = float(weight.sum())
    countries = int(d.index.get_level_values("country").nunique())
    scale = total / countries
    dbar = float((weight * d).sum() / total)
    resid = weight * (d - dbar) * scale
    cluster_sums = resid.groupby(groups).sum()
    g = cluster_sums.size
    denom = (total * scale) ** 2
    var_country = (g / (g - 1)) * float((cluster_sums ** 2).sum()) / denom
    times = d.index.get_level_values("origin_year")
    time_sums = resid.groupby(times).sum()
    t_count = time_sums.size
    var_time = (t_count / (t_count - 1)) * float((time_sums ** 2).sum()) / denom
    var_cell = float((resid ** 2).sum()) / denom * (n / (n - 1))
    var = max(var_country + var_time - var_cell, 1e-12)
    se = math.sqrt(var)
    t = dbar / se
    df = min(g, t_count) - 1
    p = 2 * (1 - stats.t.cdf(abs(t), df=df))
    crit = stats.t.ppf(0.975, df=df)
    se_one = math.sqrt(var_country)
    se_iid = math.sqrt(float((weight ** 2 * (d - dbar) ** 2).sum())) / total
    return {
        "model": model,
        "mean_differential": dbar,
        "se_cluster": se,
        "t": t,
        "p": p,
        "p_oneway": 2 * (1 - stats.t.cdf(abs(dbar / se_one), df=g - 1)),
        "p_iid": 2 * (1 - stats.t.cdf(abs(dbar / se_iid), df=n - 1)),
        "ci_low": dbar - crit * se,
        "ci_high": dbar + crit * se,
        "cells": n,
        "clusters": int(g),
        "periods": int(t_count),
        "df": int(df),
    }


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        value = min(1.0, (m - i) * p)
        running = max(running, value)
        adjusted[name] = running
    return adjusted


def horizon_dm(frame: pd.DataFrame, model: str, benchmark: str = "naive") -> pd.DataFrame:
    a = frame[frame.model == model].set_index(["country", "origin_year", "horizon"]).mase
    b = frame[frame.model == benchmark].set_index(["country", "origin_year", "horizon"]).mase
    d = (a - b).dropna().reset_index()
    rows = []
    for h, block in d.groupby("horizon"):
        series = (
            block.groupby(["origin_year", "country"])
            .mase.mean()
            .groupby("origin_year")
            .mean()
            .sort_index()
        )
        x = series.to_numpy()
        t_len = len(x)
        mean = x.mean()
        gamma0 = np.sum((x - mean) ** 2) / t_len
        var = gamma0
        for k in range(1, h):
            gamma = np.sum((x[k:] - mean) * (x[:-k] - mean)) / t_len
            var += 2 * gamma
        var /= t_len
        hln = math.sqrt((t_len + 1 - 2 * h + h * (h - 1) / t_len) / t_len)
        se = math.sqrt(max(var, 1e-12)) * hln
        stat = mean / se
        rows.append(
            {
                "model": model,
                "horizon": int(h),
                "mean": mean,
                "t": stat,
                "p": 2 * (1 - stats.t.cdf(abs(stat), df=t_len - 1)),
                "origins": t_len,
            }
        )
    return pd.DataFrame(rows)


def giacomini_white(frame: pd.DataFrame, model: str, benchmark: str = "naive") -> pd.DataFrame:
    import statsmodels.api as sm

    a = frame[frame.model == model].set_index(["country", "origin_year", "horizon"]).mase
    b = frame[frame.model == benchmark].set_index(["country", "origin_year", "horizon"]).mase
    d = (a - b).dropna().reset_index()
    rows = []
    for h, block in d.groupby("horizon"):
        series = (
            block.groupby(["origin_year", "country"])
            .mase.mean()
            .groupby("origin_year")
            .mean()
            .sort_index()
        )
        if len(series) < 8:
            continue
        y = series.to_numpy()[1:]
        x = np.column_stack([np.ones(len(y)), series.to_numpy()[:-1]])
        model_fit = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": max(1, h)})
        rows.append(
            {
                "model": model,
                "horizon": int(h),
                "lag_coef": float(model_fit.params[1]),
                "t": float(model_fit.tvalues[1]),
                "p": float(model_fit.pvalues[1]),
            }
        )
    return pd.DataFrame(rows)


def model_confidence_set(frame: pd.DataFrame, alpha: float = 0.10, boot: int = BOOT) -> dict:
    # One observation per country, the mean loss across its origins. This is
    # the same equal country weighting used everywhere else in the paper.
    loss = frame.groupby(["country", "model"]).mase.mean().unstack().dropna()
    models = list(loss.columns)
    matrix = loss.to_numpy()
    rng = np.random.default_rng(SEED)
    countries = len(loss)
    draws = rng.integers(0, countries, size=(boot, countries))
    boot_means = matrix[draws].mean(axis=1)
    se = boot_means.std(axis=0, ddof=1)
    mean = matrix.mean(axis=0)

    remaining = models.copy()
    eliminated, pvalues = [], {}
    while len(remaining) > 1:
        cols = [models.index(m) for m in remaining]
        obs = mean[cols]
        obs_range = float(((obs - obs.min()) / se[cols]).max())
        block = boot_means[:, cols]
        studentised = (block - block.min(axis=1, keepdims=True)) / se[cols]
        ranges = studentised.max(axis=1)
        p = float((ranges >= obs_range).mean())
        for m in remaining:
            pvalues[m] = max(pvalues.get(m, 0.0), p)
        if p >= alpha:
            break
        worst = remaining[int(np.argmax(obs))]
        eliminated.append(worst)
        remaining.remove(worst)
    for m in remaining:
        pvalues[m] = max(pvalues.get(m, 0.0), alpha)
    return {
        "mcs": remaining,
        "eliminated": eliminated,
        "pvalues": pvalues,
        "bootstrap": boot,
    }


def conformal(frame: pd.DataFrame, model: str) -> tuple[pd.DataFrame, dict]:
    block = frame[frame.model == model].copy()
    # The scale is constant within a country and origin, so it can be
    # recovered from any model on that cell.
    scale = frame.drop_duplicates(["country", "origin_year"])[
        ["country", "origin_year", "abs_error", "mase"]
    ].copy()
    scale["scale"] = scale.abs_error / scale.mase
    scale = scale[["country", "origin_year", "scale"]]
    block = block.merge(scale, on=["country", "origin_year"], how="left")
    block["score"] = block.abs_error / block.scale

    rows = []
    for h, part in block.groupby("horizon"):
        cal, ev = [], []
        for country, series in part.groupby("country"):
            origins = sorted(series.origin_year.unique())
            cut = max(1, int(round(0.6 * len(origins))))
            cal.append(series[series.origin_year.isin(origins[:cut])])
            ev.append(series[series.origin_year.isin(origins[cut:])])
        cal = pd.concat(cal)
        ev = pd.concat(ev)
        for level in LEVELS:
            n = len(cal)
            rank = min(1.0, math.ceil((n + 1) * level) / n)
            q = float(np.quantile(cal.score.to_numpy(), rank, method="higher"))
            coverage = float((ev.score <= q).mean())
            rows.append(
                {
                    "horizon": int(h),
                    "level": level,
                    "quantile": q,
                    "coverage": coverage,
                    "calibration_n": n,
                    "evaluation_n": len(ev),
                    "mean_width_scaled": 2 * q,
                }
            )
    table = pd.DataFrame(rows)
    q5 = float(table[(table.horizon == 5) & (table.level == 0.90)]["quantile"].iloc[0])
    return table, {"q5_90": float(q5)}


def forecast_2040(german: pd.Series, q5: float) -> pd.DataFrame:
    y = german.to_numpy(float)
    last_year = int(german.index.max())
    last_value = float(y[-1])
    scale = float(np.mean(np.abs(np.diff(y))))
    rows = []
    for h in range(1, 16):
        width90 = q5 * math.sqrt(h / 5) * scale
        rows.append(
            {
                "year": last_year + h,
                "point": last_value,
                "lower_90": last_value - width90,
                "upper_90": last_value + width90,
                "width_90": 2 * width90,
                "note": "flat benchmark, conformal width scaled by sqrt(h/5)",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    records = pd.read_csv("data/model/p01_panel_results.csv")
    frame = cells(records)
    summary = {}

    naive_balanced = (
        frame[frame.model == "naive"]
        .groupby(["country", "horizon"])
        .mase.mean()
        .groupby("country")
        .mean()
        .mean()
    )
    summary["naive_mean_mase"] = float(naive_balanced)

    dm_rows = [cluster_dm(frame, m) for m in sorted(frame.model.unique()) if m != "naive"]
    dm = pd.DataFrame(dm_rows)
    dm["p_holm"] = dm.model.map(holm(dict(zip(dm.model, dm.p))))
    dm = dm.sort_values("mean_differential")
    dm.to_csv("data/model/p01_dm_table.csv", index=False)
    summary["dm"] = dm.to_dict(orient="records")

    horizon_rows = []
    for m in ["holt_damped", "theta", "ridge_lags"]:
        horizon_rows.append(horizon_dm(frame, m))
    horizon = pd.concat(horizon_rows, ignore_index=True)
    horizon.to_csv("data/model/p01_horizon_dm.csv", index=False)

    gw_rows = []
    for m in ["holt_damped", "theta", "ridge_lags"]:
        gw_rows.append(giacomini_white(frame, m))
    gw = pd.concat(gw_rows, ignore_index=True)
    gw.to_csv("data/model/p01_gw.csv", index=False)

    mcs = model_confidence_set(frame)
    summary["mcs"] = mcs

    best = (
        frame.groupby(["model", "country", "horizon"])
        .mase.mean()
        .groupby(["model", "country"])
        .mean()
        .groupby("model")
        .mean()
        .idxmin()
    )
    summary["best_model"] = best
    conf, extra = conformal(frame, best)
    conf.to_csv("data/model/p01_conformal.csv", index=False)
    summary["conformal"] = conf.to_dict(orient="records")

    german = pd.read_csv("data/raw/destatis_pkw_neuzulassungen_jahre.csv").sort_values("time")
    german = german[(german.time >= 1991) & (german.time <= 2025)].set_index("time").value
    projection = forecast_2040(german, extra["q5_90"])
    projection.to_csv("data/model/p01_forecast_2040.csv", index=False)
    summary["forecast_2040"] = projection.to_dict(orient="records")

    summary["counts"] = {
        "countries": int(frame.country.nunique()),
        "origins": int(frame[["country", "origin_year"]].drop_duplicates().shape[0]),
        "cells": int(len(frame)),
    }
    with open("data/model/p01_inference.json", "w") as handle:
        json.dump(summary, handle, indent=2)

    print(dm.round(4).to_string(index=False))
    print(f"\nMCS {mcs['mcs']}")
    print(conf.round(4).to_string(index=False))
    print(f"\nbest model {best}")
    print(projection.round(0).to_string(index=False))


if __name__ == "__main__":
    main()
