"""Robustness checks for P01, version 2.0.

Five checks that are fixed in the protocol before estimation:
A. crisis exclusion, origins 2008 and 2009 removed
B. leave-one-country-out ranking
C. alternative loss, symmetric absolute percentage error
D. rolling twenty-year training window instead of expanding
E. penalty sensitivity of the ridge model

Every check reuses the recorded forecasts where possible, so the numbers are
reproducible from data/model/p01_panel_results.csv without refitting. Checks D
and E refit the affected models and write their own record file.

Author: Armin Kajevic
"""
from __future__ import annotations

import os
import json

import numpy as np
import pandas as pd

from p01_protocol import (
    HORIZON,
    MODELS,
    _ar_features,
    forecast_path,
    load_panel,
    mase_scale,
)

RESULTS = "data/model/p01_panel_results.csv"
OUT_JSON = "data/model/p01_robustness.json"
OUT_CSV = "data/model/p01_robustness.csv"
OUT_ROLLING = "data/model/p01_rolling_results.csv"


def overall_from(frame: pd.DataFrame, loss: str = "mase") -> pd.DataFrame:
    """Country and horizon balanced mean of a cell-level loss."""
    usable = frame[frame.divergent == 0]
    per_country_horizon = usable.groupby(["model", "country", "horizon"])[loss].mean()
    per_country = per_country_horizon.groupby(["model", "country"]).mean()
    return per_country.groupby("model").mean().sort_values().reset_index()


def check_crisis(frame: pd.DataFrame) -> dict:
    kept = frame[~frame.origin_year.isin([2008, 2009])]
    table = overall_from(kept)
    return {
        "origins_removed": 2,
        "cells": int((kept.divergent == 0).sum()),
        "ranking": table.set_index("model").mase.round(4).to_dict(),
        "naive": round(float(table.set_index("model").loc["naive", "mase"]), 4),
        "best": table.iloc[0]["model"],
        "best_mase": round(float(table.iloc[0]["mase"]), 4),
        "naive_rank": int(table.reset_index().index[table.model == "naive"][0]) + 1,
    }


def check_leave_one_out(frame: pd.DataFrame) -> dict:
    countries = sorted(frame.country.unique())
    naive_first, records = 0, []
    for country in countries:
        table = overall_from(frame[frame.country != country])
        table = table.reset_index(drop=True)
        rank = int(table.index[table.model == "naive"][0]) + 1
        if rank == 1:
            naive_first += 1
        records.append(
            {
                "excluded": country,
                "best": table.iloc[0]["model"],
                "best_mase": round(float(table.iloc[0].mase), 4),
                "naive_rank": rank,
                "naive_mase": round(float(table.set_index("model").loc["naive", "mase"]), 4),
            }
        )
    return {
        "folds": len(countries),
        "naive_first": naive_first,
        "share": round(naive_first / len(countries), 4),
        "worst_naive_rank": max(r["naive_rank"] for r in records),
        "records": records,
    }


def check_smape(frame: pd.DataFrame) -> dict:
    usable = frame[frame.divergent == 0].copy()
    denominator = usable.actual.abs() + usable.forecast.abs()
    usable["smape"] = np.where(denominator > 0, 2 * usable.abs_error / denominator, np.nan)
    usable = usable.dropna(subset=["smape"])
    table = overall_from(usable, loss="smape")
    return {
        "cells": int(len(usable)),
        "ranking": table.set_index("model").smape.round(4).to_dict(),
        "best": table.iloc[0]["model"],
        "best_smape": round(float(table.iloc[0].smape), 4),
        "naive_smape": round(float(table.set_index("model").loc["naive", "smape"]), 4),
        "naive_rank": int(table.reset_index().index[table.model == "naive"][0]) + 1,
    }


def rolling_records(window: int = 20) -> pd.DataFrame:
    panel = load_panel()
    rows = []
    for geo, group in panel.groupby("geo"):
        group = group.sort_values("year")
        y = group.registrations.to_numpy(float)
        years = group.year.to_numpy()
        n = len(y)
        for origin in range(window, n - HORIZON + 1):
            train = y[origin - window:origin]
            scale = mase_scale(train)
            actual = y[origin:origin + HORIZON]
            ceiling = 10.0 * float(np.max(train))
            for model in MODELS:
                try:
                    path = forecast_path(train, model)
                except Exception:
                    path = forecast_path(train, "drift")
                divergent = int(np.any(path <= 0) or np.any(path > ceiling))
                for h in range(1, HORIZON + 1):
                    error = actual[h - 1] - path[h - 1]
                    rows.append(
                        {
                            "country": geo,
                            "origin_year": int(years[origin - 1]),
                            "horizon": h,
                            "model": model,
                            "forecast": float(path[h - 1]),
                            "actual": float(actual[h - 1]),
                            "abs_error": float(abs(error)),
                            "mase": float(abs(error) / scale),
                            "divergent": divergent,
                        }
                    )
    return pd.DataFrame(rows)


def check_rolling() -> dict:
    if os.path.exists(OUT_ROLLING):
        frame = pd.read_csv(OUT_ROLLING)
    else:
        frame = rolling_records()
        frame.to_csv(OUT_ROLLING, index=False)
    table = overall_from(frame)
    return {
        "window": 20,
        "cells": int((frame.divergent == 0).sum()),
        "ranking": table.set_index("model").mase.round(4).to_dict(),
        "best": table.iloc[0]["model"],
        "best_mase": round(float(table.iloc[0].mase), 4),
        "naive": round(float(table.set_index("model").loc["naive", "mase"]), 4),
        "naive_rank": int(table.reset_index().index[table.model == "naive"][0]) + 1,
    }


def check_penalty() -> dict:
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    panel = load_panel()
    rows = []
    for alpha in (0.1, 1.0, 10.0):
        for geo, group in panel.groupby("geo"):
            group = group.sort_values("year")
            y = group.registrations.to_numpy(float)
            years = group.year.to_numpy()
            n = len(y)
            for origin in range(15, n - HORIZON + 1):
                train = y[:origin]
                scale = mase_scale(train)
                dy = np.diff(train)
                X, target = _ar_features(dy)
                model = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=alpha))])
                model.fit(X, target)
                history = list(dy[-3:][::-1])
                level = y[-1]
                for h in range(1, HORIZON + 1):
                    step = float(model.predict(np.array(history).reshape(1, -1))[0])
                    level += step
                    history = [step] + history[:-1]
                    error = y[origin + h - 1] - level
                    rows.append(
                        {
                            "alpha": alpha,
                            "model": "ridge",
                            "country": geo,
                            "horizon": h,
                            "mase": abs(error) / scale,
                            "divergent": 0,
                            "origin_year": int(years[origin - 1]),
                        }
                    )
    frame = pd.DataFrame(rows)
    out = {}
    for alpha, group in frame.groupby("alpha"):
        table = overall_from(group)
        out[str(alpha)] = round(float(table.iloc[0]["mase"]), 4)
    return {"mase_by_alpha": out}


def main() -> None:
    frame = pd.read_csv(RESULTS)
    results = {}
    for name, check in (
        ("crisis", lambda: check_crisis(frame)),
        ("leave_one_out", lambda: check_leave_one_out(frame)),
        ("smape", lambda: check_smape(frame)),
        ("rolling", check_rolling),
        ("penalty", check_penalty),
    ):
        results[name] = check()
        with open(OUT_JSON, "w") as handle:
            json.dump(results, handle, indent=2)
        print("done", name, flush=True)
    rows = []
    for key in ("crisis", "smape", "rolling"):
        for model, value in results[key]["ranking"].items():
            rows.append({"check": key, "model": model, "mase": value})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    print(json.dumps({k: v for k, v in results.items() if k != "leave_one_out"}, indent=2))
    print("leave one out", {k: v for k, v in results["leave_one_out"].items() if k != "records"})


if __name__ == "__main__":
    main()
