"""P05 extensions: minimum detectable effect, peer placebo, specification curve
and a Bayesian posterior for the mean cumulative abnormal return.

These are post hoc analyses. They were specified after the event study in
P05 version 2.1 was estimated, and the paper labels them as such. The base
specification is checked against the published three-event mean before any
extension is reported.

Input   data/model/p05_returns.csv, written by tools/p05_analysis.py
Output  data/model/p05_extras/*.csv
        data/model/p05_extras/summary.json
        figures/fig24_p05_spec_curve.png
        figures/fig25_p05_bayes.png

Usage
    .venv/bin/python tools/p05_extras.py
    .venv/bin/python tools/p05_extras.py --check
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RETURNS = ROOT / "data" / "model" / "p05_returns.csv"
OUT = ROOT / "data" / "model" / "p05_extras"
FIG = ROOT / "figures"

NAVY = "#1f3b57"
RED = "#c8553d"
GREY = "#666666"
GOLD = "#b08d3f"

CONFIG = {
    "firm": "vw",
    "sector": "sector",
    "dax": "dax",
    "market": "market",
    "peers": ["bmw", "mercedes", "porsche_se"],
    "events": {
        "Italdesign": "2025-12-10",
        "Everllence": "2026-06-24",
        "IAV": "2026-08-11",
    },
    # The Italdesign release was published after the Xetra close. The first
    # tradable day is therefore 11 December 2025. The other two releases were
    # published during the trading day.
    "after_close": {"Italdesign": True, "Everllence": False, "IAV": False},
    "est_anchor": "2025-12-10",
    "est_len": 250,
    "gap": 20,
    "seed": 20261125,
}

BASE_MEAN = -0.01595627349577246


def fit(y: np.ndarray, x: np.ndarray, i0: int, i1: int):
    """OLS of y on a constant and x over rows i0 through i1 inclusive."""
    design = np.column_stack([np.ones(i1 - i0 + 1), x[i0 : i1 + 1]])
    beta, *_ = np.linalg.lstsq(design, y[i0 : i1 + 1], rcond=None)
    residual = y[i0 : i1 + 1] - design @ beta
    sigma = float(np.sqrt(residual @ residual / (len(residual) - 2)))
    return beta, sigma, np.linalg.inv(design.T @ design)


def car_scar(y, x, beta, sigma, xtx_inv, t0: int, t1: int):
    """CAR and Patell-standardised CAR over trading days t0 through t1."""
    index = np.arange(t0, t1 + 1)
    design = np.column_stack([np.ones(len(index)), x[index]])
    abnormal = y[index] - design @ beta
    forecast = sigma * np.sqrt(
        1.0 + np.einsum("ij,jk,ik->i", design, xtx_inv, design)
    )
    return float(abnormal.sum()), float((abnormal / forecast).sum() / np.sqrt(len(index)))


def event_stats(cars: np.ndarray, scars: np.ndarray) -> dict:
    n = len(cars)
    patell = float(scars.sum() / np.sqrt(n))
    bmp = float(scars.mean() / (scars.std(ddof=1) / np.sqrt(n))) if n > 2 else float("nan")
    return {
        "mean_car": float(cars.mean()),
        "median_car": float(np.median(cars)),
        "patell_z": patell,
        "bmp_t": bmp,
        "positive": int((cars > 0).sum()),
        "n_events": n,
    }


def locate(dates: pd.DatetimeIndex, value: str, after_close: bool = False, shift: int = 0) -> int:
    """First trading day on or after value, optionally moved to the next day."""
    index = int(np.searchsorted(dates.values, np.datetime64(value)))
    return index + (1 if after_close else 0) + shift


def estimation_window(dates: pd.DatetimeIndex, anchor: str, length: int, gap: int):
    first = int(np.searchsorted(dates.values, np.datetime64(anchor)))
    end = first - gap
    start = end - length + 1
    return start, end


def base_cars(returns: pd.DataFrame):
    """The published three-event specification, with announcement dates."""
    dates = returns.index
    start, end = estimation_window(dates, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    y = returns[CONFIG["firm"]].to_numpy()
    x = returns[[CONFIG["sector"]]].to_numpy()
    beta, sigma, xtx_inv = fit(y, x, start, end)
    cars, scars = [], []
    for name, value in CONFIG["events"].items():
        t = locate(dates, value, after_close=False)
        c, s = car_scar(y, x, beta, sigma, xtx_inv, t - 1, t + 1)
        cars.append(c)
        scars.append(s)
    return np.array(cars), np.array(scars), beta, sigma


def mde_table(sigma: float, windows=((-1, 1), (0, 1), (0, 5), (0, 20), (-5, 5)),
              n_events=(3, 5, 10, 20, 50), alpha: float = 0.05, power: float = 0.80) -> pd.DataFrame:
    """Minimum detectable effect for the mean CAR across independent events.

    The per-event CAR standard deviation is sigma times the square root of the
    window length. The known-variance row uses the normal critical value; the
    t row uses a noncentral t with n minus one degrees of freedom, which is the
    relevant case with three events.
    """
    rows = []
    for low, high in windows:
        length = high - low + 1
        per_event = sigma * np.sqrt(length)
        for n in n_events:
            standard_error = per_event / np.sqrt(n)
            mde_normal = (stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)) * standard_error
            if n > 2:
                critical = stats.t.ppf(1 - alpha / 2, n - 1)
                lo, hi = 0.0, 30.0
                for _ in range(100):
                    mid = (lo + hi) / 2
                    p = stats.nct.sf(critical, n - 1, mid) + stats.nct.cdf(-critical, n - 1, mid)
                    lo, hi = (mid, hi) if p < power else (lo, mid)
                mde_t = mid * standard_error
            else:
                mde_t = float("nan")
            rows.append({
                "window": f"({low},{high})",
                "days": length,
                "n_events": n,
                "per_event_sd": per_event,
                "mde_normal": mde_normal,
                "mde_t": mde_t,
                "mde_t_pct": 100 * mde_t,
            })
    return pd.DataFrame(rows)


def peer_placebo(returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the same event dates to the German peers."""
    dates = returns.index
    start, end = estimation_window(dates, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    x = returns[[CONFIG["sector"]]].to_numpy()
    rows = {}
    for firm in [CONFIG["firm"], *CONFIG["peers"]]:
        y = returns[firm].to_numpy()
        beta, sigma, xtx_inv = fit(y, x, start, end)
        values = []
        for name, value in CONFIG["events"].items():
            # The placebo uses the same announcement dates as Table 4. The
            # first-tradable alignment is a separate dimension in the curve.
            t = locate(dates, value, after_close=False)
            c, _ = car_scar(y, x, beta, sigma, xtx_inv, t - 1, t + 1)
            values.append(c)
        rows[firm] = values
    cars = pd.DataFrame(rows, index=list(CONFIG["events"])).T
    peers = cars.loc[CONFIG["peers"]]
    summary = pd.DataFrame({
        "firm_car": cars.loc[CONFIG["firm"]],
        "peer_mean_car": peers.mean(),
        "peer_min_car": peers.min(),
        "peer_max_car": peers.max(),
        "firm_minus_peers": cars.loc[CONFIG["firm"]] - peers.mean(),
        "firm_rank_among_four": [
            int((cars[name] <= cars.loc[CONFIG["firm"], name]).sum()) for name in cars.columns
        ],
    })
    return cars, summary


def spec_curve(returns: pd.DataFrame) -> pd.DataFrame:
    """All combinations of benchmark, window, estimation length, timing and event set."""
    dates = returns.index
    y = returns[CONFIG["firm"]].to_numpy()
    benchmarks = {
        "sector": [CONFIG["sector"]],
        "dax": [CONFIG["dax"]],
        "market": [CONFIG["market"]],
        "sector+market": [CONFIG["sector"], CONFIG["market"]],
    }
    windows = [(-1, 1), (0, 1), (0, 5), (-5, 5)]
    lengths = [250, 120]
    timings = ["announcement", "first_tradable"]
    drops = [None, "IAV"]
    rows = []
    for (benchmark, columns), window, length, timing, drop in itertools.product(
        benchmarks.items(), windows, lengths, timings, drops
    ):
        start, end = estimation_window(dates, CONFIG["est_anchor"], length, CONFIG["gap"])
        x = returns[columns].to_numpy()
        beta, sigma, xtx_inv = fit(y, x, start, end)
        cars, scars = [], []
        for name, value in CONFIG["events"].items():
            if name == drop:
                continue
            t = locate(dates, value, CONFIG["after_close"][name] and timing == "first_tradable")
            c, s = car_scar(y, x, beta, sigma, xtx_inv, t + window[0], t + window[1])
            cars.append(c)
            scars.append(s)
        stats_row = event_stats(np.array(cars), np.array(scars))
        rows.append({
            "benchmark": benchmark,
            "window": f"({window[0]},{window[1]})",
            "est_len": length,
            "timing": timing,
            "dropped": drop or "-",
            **stats_row,
        })
    curve = pd.DataFrame(rows)
    curve["base"] = (
        (curve.benchmark == "sector")
        & (curve.window == "(-1,1)")
        & (curve.est_len == 250)
        & (curve.timing == "announcement")
        & (curve.dropped == "-")
    )
    return curve.sort_values("mean_car").reset_index(drop=True)


def bayes_mean(cars: np.ndarray, sds: np.ndarray, prior_sd: float,
               tau_scale: float = 0.03, grid: int = 500) -> dict:
    """Random-effects posterior for the mean CAR, integrated over tau."""
    y = np.asarray(cars, float)
    variance = np.asarray(sds, float) ** 2
    taus = np.linspace(1e-6, 6 * tau_scale, grid)
    weights = np.empty(grid)
    means = np.empty(grid)
    sds = np.empty(grid)
    for j, tau in enumerate(taus):
        total = variance + tau ** 2
        precision = 1 / prior_sd ** 2 + (1 / total).sum()
        means[j] = (y / total).sum() / precision
        sds[j] = precision ** -0.5
        covariance = np.diag(total) + prior_sd ** 2 * np.ones((len(y), len(y)))
        sign, logdet = np.linalg.slogdet(covariance)
        loglik = -0.5 * (logdet + y @ np.linalg.solve(covariance, y))
        weights[j] = loglik + stats.halfnorm.logpdf(tau, scale=tau_scale)
    weights = np.exp(weights - weights.max())
    weights /= weights.sum()
    rng = np.random.default_rng(CONFIG["seed"])
    draws_index = rng.choice(grid, 60000, p=weights)
    draws = rng.normal(means[draws_index], sds[draws_index])
    return {
        "prior_sd": prior_sd,
        "post_mean": float(draws.mean()),
        "post_sd": float(draws.std()),
        "ci95_lo": float(np.percentile(draws, 2.5)),
        "ci95_hi": float(np.percentile(draws, 97.5)),
        "p_negative": float((draws < 0).mean()),
        "draws": draws,
    }


def plot_curve(curve: pd.DataFrame, path: Path) -> None:
    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [3, 2]}
    )
    x = np.arange(len(curve))
    colors = np.where(curve.timing == "announcement", NAVY, RED)
    top.scatter(x, 100 * curve.mean_car, s=14, c=colors, alpha=0.8)
    top.axhline(0, color=GREY, lw=0.8)
    base = curve.index[curve.base]
    if len(base):
        top.scatter(base, 100 * curve.mean_car.iloc[base], s=90, facecolors="none",
                    edgecolors=GOLD, linewidths=1.8, label="base specification")
        top.legend(frameon=False, loc="upper left")
    top.set_ylabel("mean CAR, log points")
    top.set_title("Specification curve: sign is stable, significance is not")
    bottom.scatter(x, curve.patell_z, s=14, c=colors, alpha=0.8, label="Patell z")
    bottom.scatter(x, curve.bmp_t, s=14, c=colors, alpha=0.5, marker="x", label="BMP t")
    bottom.axhline(0, color=GREY, lw=0.8)
    bottom.axhline(-1.96, color=GREY, lw=0.8, ls="--")
    bottom.axhline(-4.303, color=GREY, lw=0.8, ls=":")
    bottom.set_ylabel("test statistic")
    bottom.set_xlabel("specifications, sorted by mean CAR")
    bottom.legend(frameon=False, loc="lower left", ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_bayes(table: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, row in table.iterrows():
        ax.plot([100 * row.ci95_lo, 100 * row.ci95_hi], [i, i], color=NAVY, lw=2)
        ax.scatter(100 * row.post_mean, i, color=RED, zorder=3)
    ax.axvline(0, color=GREY, lw=0.8)
    ax.set_yticks(range(len(table)))
    ax.set_yticklabels([f"prior sd {100 * p:.0f} log points" for p in table.prior_sd])
    ax.set_xlabel("mean cumulative abnormal return, log points, with 95 percent credible interval")
    ax.set_title("Bayesian posterior is wide under every prior")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    returns = pd.read_csv(RETURNS, parse_dates=["date"]).set_index("date").sort_index()

    cars, scars, beta, sigma = base_cars(returns)
    base_mean = float(cars.mean())
    print(f"base mean {base_mean:.10f}, published {BASE_MEAN:.10f}, difference {base_mean - BASE_MEAN:.2e}")
    if args.check:
        if abs(base_mean - BASE_MEAN) > 1e-9:
            raise SystemExit("base specification does not reproduce the published mean")
        print("base specification reproduces the published mean")
        return

    mde = mde_table(sigma)
    mde.to_csv(OUT / "mde.csv", index=False)

    peer_cars, peer_summary = peer_placebo(returns)
    peer_cars.to_csv(OUT / "peer_cars.csv")
    peer_summary.to_csv(OUT / "peer_placebo.csv")

    curve = spec_curve(returns)
    curve.drop(columns=["base"]).to_csv(OUT / "spec_curve.csv", index=False)
    plot_curve(curve, FIG / "fig24_p05_spec_curve.png")

    sd_event = sigma * np.sqrt(3)
    bayes_rows = []
    for prior in (0.01, 0.03, 0.10):
        result = bayes_mean(cars, np.full(len(cars), sd_event), prior)
        result.pop("draws")
        bayes_rows.append(result)
    bayes = pd.DataFrame(bayes_rows)
    bayes.to_csv(OUT / "bayes.csv", index=False)
    plot_bayes(bayes, FIG / "fig25_p05_bayes.png")

    summary = {
        "base_mean_car": base_mean,
        "base_patell_z": float(scars.sum() / np.sqrt(len(scars))),
        "base_bmp_t": float(scars.mean() / (scars.std(ddof=1) / np.sqrt(len(scars)))),
        "residual_sd_daily": sigma,
        "mde_three_events_three_day": float(
            mde[(mde.window == "(-1,1)") & (mde.n_events == 3)].mde_t.iloc[0]
        ),
        "specifications": int(len(curve)),
        "share_negative": float((curve.mean_car < 0).mean()),
        "share_significant_negative_bmp": float(
            ((curve.bmp_t < -4.303) & (curve.n_events == 3)).mean()
        ),
        "curve_min": float(curve.mean_car.min()),
        "curve_max": float(curve.mean_car.max()),
        "peer_placebo": peer_summary.round(6).to_dict(orient="index"),
        "bayes": bayes.round(6).to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nMDE, three-day window:")
    print(mde[(mde.window == "(-1,1)")][["n_events", "mde_t", "mde_t_pct"]].round(4).to_string(index=False))
    print("\nPeer placebo:")
    print(peer_summary.round(4).to_string())
    print("\nSpecification curve:")
    print(f"specifications {len(curve)}, share negative {(curve.mean_car < 0).mean():.3f}, "
          f"range {curve.mean_car.min():.4f} to {curve.mean_car.max():.4f}")
    print("\nBayesian posterior:")
    print(bayes.round(4).to_string(index=False))
    print(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
