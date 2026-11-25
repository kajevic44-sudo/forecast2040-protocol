"""Monte Carlo study of the three tests used in P01.

The exercise asks which test keeps its nominal size when forecast errors are
clustered by country and overlap across horizons. Loss differentials are
generated with a country effect, an origin effect and a horizon effect. The
same differentials are then tested with an independent t test, with the
Harvey-Leybourne-Newbold correction at horizon five, and with a country
clustered statistic. Power is measured under a small negative mean.

Author: Armin Kajevic
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20261125
REPS = 4000
COUNTRIES = 17
ORIGINS = 14
HORIZONS = 5
SIGMA_COUNTRY = 0.30
SIGMA_ORIGIN = 0.50
SIGMA_CELL = 1.00


def one_replication(rng: np.random.Generator, mu: float) -> dict:
    country = rng.normal(0, SIGMA_COUNTRY, size=(COUNTRIES, 1, 1))
    origin = rng.normal(0, SIGMA_ORIGIN, size=(1, ORIGINS, 1))
    cell = rng.normal(0, SIGMA_CELL, size=(COUNTRIES, ORIGINS, HORIZONS))
    d = mu + country + origin + cell

    flat = d.reshape(-1)
    n = flat.size
    mean = flat.mean()
    se_iid = flat.std(ddof=1) / math.sqrt(n)
    t_iid = mean / se_iid
    p_iid = 2 * (1 - stats.t.cdf(abs(t_iid), df=n - 1))

    cluster_sums = (d - mean).sum(axis=(1, 2))
    g = COUNTRIES
    var_cluster = (g / (g - 1)) * float((cluster_sums ** 2).sum()) / n ** 2
    t_cluster = mean / math.sqrt(var_cluster)
    p_cluster = 2 * (1 - stats.t.cdf(abs(t_cluster), df=g - 1))

    time_sums = (d - mean).sum(axis=(0, 2))
    t_time = ORIGINS
    var_time = (t_time / (t_time - 1)) * float((time_sums ** 2).sum()) / n ** 2
    var_cell = float(((flat - mean) ** 2).sum()) / n ** 2 * (n / (n - 1))
    var_two = max(var_cluster + var_time - var_cell, 1e-12)
    t_two = mean / math.sqrt(var_two)
    p_two = 2 * (1 - stats.t.cdf(abs(t_two), df=min(g, t_time) - 1))

    # Country block bootstrap, the same resampling used for the model
    # confidence set.
    draws = rng.integers(0, COUNTRIES, size=(400, COUNTRIES))
    boot_means = d[draws].mean(axis=(1, 2, 3))
    share_low = float((boot_means <= 0).mean())
    share_high = float((boot_means >= 0).mean())
    p_boot = min(1.0, 2 * min(share_low, share_high))

    by_origin = d.mean(axis=(0, 2))
    t_len = by_origin.size
    m5 = by_origin.mean()
    gamma0 = np.sum((by_origin - m5) ** 2) / t_len
    var = gamma0
    for k in range(1, 5):
        var += 2 * np.sum((by_origin[k:] - m5) * (by_origin[:-k] - m5)) / t_len
    var /= t_len
    hln = math.sqrt((t_len + 1 - 2 * 5 + 5 * 4 / t_len) / t_len)
    t_hln = m5 / (math.sqrt(max(var, 1e-12)) * hln)
    p_hln = 2 * (1 - stats.t.cdf(abs(t_hln), df=t_len - 1))

    return {
        "p_iid": p_iid,
        "p_cluster": p_cluster,
        "p_twoway": p_two,
        "p_boot": p_boot,
        "p_hln5": p_hln,
        "mean": mean,
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    rows = []
    for label, mu in (("null", 0.0), ("alternative", -0.10)):
        results = [one_replication(rng, mu) for _ in range(REPS)]
        frame = pd.DataFrame(results)
        rows.append(
            {
                "scenario": label,
                "mu": mu,
                "reps": REPS,
                "size_iid": float((frame.p_iid < 0.05).mean()),
                "size_cluster": float((frame.p_cluster < 0.05).mean()),
                "size_twoway": float((frame.p_twoway < 0.05).mean()),
                "size_boot": float((frame.p_boot < 0.05).mean()),
                "size_hln5": float((frame.p_hln5 < 0.05).mean()),
                "mean_differential": float(frame["mean"].mean()),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv("data/model/p01_monte_carlo.csv", index=False)
    with open("data/model/p01_monte_carlo.json", "w") as handle:
        json.dump(table.to_dict(orient="records"), handle, indent=2)
    print(table.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
