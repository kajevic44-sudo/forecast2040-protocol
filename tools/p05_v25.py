"""P05 version 2.5 extensions.

This script adds five analyses to the published version 2.4 event study:

1. A broad peer set of 23 European automotive manufacturers and suppliers,
   with the German peers taken from the panel used in the base specification
   and the other firms downloaded from Yahoo Finance.
2. Exact rank permutation p values for the peer gap, and a placebo in time
   for the peer gap over every three day window in 2025 and 2026.
3. A GARCH(1,1) volatility scaling of the event level statistics, with normal
   and Student t errors, next to rolling window scaling.
4. A cumulative average abnormal return path from ten days before to twenty
   days after the three primary events, with a simulation band under the null
   of no abnormal return.
5. A power curve and an event level forest plot.

The script is post hoc. It is labelled as such in the paper. The base
specification is checked against the published three event mean before any
extension is computed.

Input   data/model/p05_returns.csv
        data/raw/p05_peers_broad.csv, if present; otherwise downloaded
Output  data/raw/p05_peers_broad.csv and metadata
        data/model/p05_extras/peer_broad_cars.csv
        data/model/p05_extras/peer_broad_summary.csv
        data/model/p05_extras/peer_broad_placebo.csv
        data/model/p05_extras/garch.csv
        data/model/p05_extras/caar_path.csv
        data/model/p05_extras/power_curve.csv
        data/model/p05_extras/forest.csv
        data/model/p05_extras/v25_summary.json
        figures/fig26_p05_caar.png
        figures/fig27_p05_power.png
        figures/fig28_p05_peer_dist.png
        figures/fig29_p05_forest.png

Usage
    .venv/bin/python tools/p05_v25.py
    .venv/bin/python tools/p05_v25.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RETURNS = ROOT / "data" / "model" / "p05_returns.csv"
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "model" / "p05_extras"
FIG = ROOT / "figures"
PEERS_RAW = RAW / "p05_peers_broad.csv"
PEERS_META = RAW / "p05_peers_broad_metadata.json"

NAVY = "#1f3b57"
RED = "#c8553d"
GREY = "#666666"
GOLD = "#b08d3f"
GREEN = "#3f6b4f"
LIGHT = "#b9c4cf"

CONFIG = {
    "firm": "vw",
    "sector": "sector",
    "events": {
        "Italdesign": "2025-12-10",
        "Everllence": "2026-06-24",
        "IAV": "2026-08-11",
    },
    "est_anchor": "2025-12-10",
    "est_len": 250,
    "gap": 20,
    "seed": 20261125,
}

BASE_MEAN = -0.01595627349577246

# The 23 firm broad set. BMW and Mercedes-Benz are taken from the panel so
# that the German firms are measured on the same series as the base paper.
# The remaining 21 tickers are downloaded from Yahoo Finance.
BROAD_TICKERS = {
    "STLAP.PA": "Stellantis",
    "RNO.PA": "Renault",
    "RACE.MI": "Ferrari",
    "DTG.DE": "Daimler Truck",
    "IVG.MI": "Iveco",
    "VOLV-B.ST": "Volvo Group",
    "CON.DE": "Continental",
    "FRVIA.PA": "Forvia",
    "FR.PA": "Valeo",
    "ML.PA": "Michelin",
    "BRE.MI": "Brembo",
    "PIRC.MI": "Pirelli",
    "NOEJ.DE": "Norma Group",
    "ZIL2.DE": "ElringKlinger",
    "GRM.DE": "Grammer",
    "BDT.DE": "Bertrandt",
    "ED4.DE": "EDAG",
    "ATE.PA": "Alten",
    "OPM.PA": "OPmobility",
    "AML.L": "Aston Martin",
    "SGL.DE": "SGL Carbon",
}

GERMAN_PANEL = {"BMW.DE": "bmw", "MBG.DE": "mercedes"}
GERMAN3 = ["BMW.DE", "MBG.DE", "Porsche SE"]
OEM = ["BMW.DE", "MBG.DE", "STLAP.PA", "RNO.PA", "RACE.MI", "DTG.DE", "IVG.MI", "VOLV-B.ST", "AML.L"]
GERMAN2 = ["BMW.DE", "MBG.DE"]
ENGINEERING = ["BDT.DE", "ED4.DE", "ATE.PA"]
ALL_PEERS = list(GERMAN_PANEL) + list(BROAD_TICKERS)

DISPLAY = {
    "BMW.DE": "BMW",
    "MBG.DE": "Mercedes-Benz",
    "Porsche SE": "Porsche SE",
    **BROAD_TICKERS,
}

SETS = {
    "all": ("All European manufacturers and suppliers", ALL_PEERS),
    "oem": ("European OEMs", OEM),
    "german2": ("German OEMs", GERMAN2),
    "german3": ("German OEMs plus Porsche SE", GERMAN3),
    "engineering": ("Engineering services", ENGINEERING),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fit(y: np.ndarray, x: np.ndarray, i0: int, i1: int):
    """OLS of y on a constant and x over rows i0 through i1 inclusive."""
    design = np.column_stack([np.ones(i1 - i0 + 1), x[i0 : i1 + 1]])
    beta, *_ = np.linalg.lstsq(design, y[i0 : i1 + 1], rcond=None)
    residual = y[i0 : i1 + 1] - design @ beta
    sigma = float(np.sqrt(residual @ residual / (len(residual) - 2)))
    return beta, sigma, np.linalg.inv(design.T @ design)


def fit_masked(y: np.ndarray, x: np.ndarray, i0: int, i1: int) -> np.ndarray:
    """OLS on the rows with finite values, for peers with missing trading days."""
    ok = np.isfinite(y[i0 : i1 + 1]) & np.isfinite(x[i0 : i1 + 1])
    design = np.column_stack([np.ones(int(ok.sum())), x[i0 : i1 + 1][ok]])
    beta, *_ = np.linalg.lstsq(design, y[i0 : i1 + 1][ok], rcond=None)
    return beta


def locate(dates: pd.DatetimeIndex, value: str) -> int:
    return int(np.searchsorted(dates.values, np.datetime64(value)))


def estimation_window(dates: pd.DatetimeIndex, anchor: str, length: int, gap: int):
    first = locate(dates, anchor)
    end = first - gap
    return end - length + 1, end


def download_peers() -> pd.DataFrame:
    """Download adjusted closes for the broad peer set and cache them."""
    if PEERS_RAW.exists():
        return pd.read_csv(PEERS_RAW, parse_dates=["Date"]).set_index("Date").sort_index()
    import yfinance as yf

    tickers = list(BROAD_TICKERS)
    frame = yf.download(
        tickers,
        start="2016-11-24",
        end="2026-11-21",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    close = frame["Close"] if isinstance(frame.columns, pd.MultiIndex) else frame
    close = close.sort_index()
    close.index.name = "Date"
    close.to_csv(PEERS_RAW, float_format="%.6f")
    metadata = {
        "source": "Yahoo Finance via yfinance",
        "download_date": date.today().isoformat(),
        "start": "2016-11-24",
        "end": "2026-11-20",
        "tickers": BROAD_TICKERS,
        "rows": int(len(close)),
        "sha256_prices": sha256(PEERS_RAW),
        "note": "Adjusted closes. The raw file is not redistributed. The metadata records the exact download and its hash.",
    }
    PEERS_META.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return close


def build_returns(panel: pd.DataFrame, peers: pd.DataFrame) -> pd.DataFrame:
    """Log returns for Volkswagen, the sector and every peer on the panel dates."""
    dates = panel.index
    out = pd.DataFrame(index=dates)
    out["vw"] = panel["vw"]
    out["sector"] = panel["sector"]
    for ticker, column in GERMAN_PANEL.items():
        out[ticker] = panel[column]
    out["Porsche SE"] = panel["porsche_se"]
    peer_returns = np.log(peers).diff().reindex(dates)
    for ticker in BROAD_TICKERS:
        out[ticker] = peer_returns[ticker]
    return out


def event_cars(returns: pd.DataFrame, tickers: list[str], start: int, end: int) -> pd.DataFrame:
    """Three day CAR for each firm at each event, with the same market model."""
    sector = returns["sector"].to_numpy()
    rows = {}
    for ticker in tickers:
        y = returns[ticker].to_numpy()
        ok = np.isfinite(y[start : end + 1]) & np.isfinite(sector[start : end + 1])
        if ok.sum() < 200:
            continue
        beta = fit_masked(y, sector, start, end)
        values = []
        for value in CONFIG["events"].values():
            t = locate(returns.index, value)
            index = np.arange(t - 1, t + 2)
            if not np.isfinite(y[index]).all():
                values.append(np.nan)
                continue
            abnormal = y[index] - (beta[0] + beta[1] * sector[index])
            values.append(float(abnormal.sum()))
        rows[ticker] = values
    return pd.DataFrame(rows, index=list(CONFIG["events"])).T


def trimmed_mean(values: np.ndarray, proportion: float = 0.10) -> float:
    values = np.sort(values)
    cut = int(np.floor(proportion * len(values)))
    if cut == 0:
        return float(values.mean())
    return float(values[cut:-cut].mean())


def peer_summary(cars: pd.DataFrame) -> pd.DataFrame:
    """Summarise the Volkswagen gap for every event and peer set."""
    rows = []
    for event in CONFIG["events"]:
        vw = float(cars.loc["vw", event])
        for key, (label, members) in SETS.items():
            values = cars.loc[[m for m in members if m in cars.index], event].dropna().to_numpy()
            n = len(values)
            rank = int((values <= vw).sum()) + 1
            rows.append({
                "event": event,
                "set": key,
                "label": label,
                "n_peers": n,
                "peer_mean": float(values.mean()),
                "peer_median": float(np.median(values)),
                "peer_trimmed_mean": trimmed_mean(values),
                "peer_min": float(values.min()),
                "peer_max": float(values.max()),
                "vw_car": vw,
                "gap_mean": vw - float(values.mean()),
                "gap_median": vw - float(np.median(values)),
                "vw_rank": rank,
                "firms": n + 1,
                "p_one_sided": rank / (n + 1),
                "p_two_sided": min(1.0, 2 * min(rank, n + 1 - rank) / (n + 1)),
            })
    return pd.DataFrame(rows)


def leave_one_out(cars: pd.DataFrame) -> pd.DataFrame:
    """Range of the gap and the rank when one peer is removed at a time."""
    rows = []
    for event in CONFIG["events"]:
        vw = float(cars.loc["vw", event])
        for key, (label, members) in SETS.items():
            values = cars.loc[[m for m in members if m in cars.index], event].dropna()
            if len(values) < 3:
                continue
            gaps, ranks = [], []
            for member in values.index:
                remaining = values.drop(member).to_numpy()
                gaps.append(vw - float(remaining.mean()))
                ranks.append(int((remaining <= vw).sum()) + 1)
            rows.append({
                "event": event,
                "set": key,
                "n_peers": len(values),
                "gap_min": float(min(gaps)),
                "gap_max": float(max(gaps)),
                "rank_min": int(min(ranks)),
                "rank_max": int(max(ranks)),
            })
    return pd.DataFrame(rows)


def peer_placebo_time(returns: pd.DataFrame, cars: pd.DataFrame) -> pd.DataFrame:
    """The observed gap against every three day gap in 2025 and 2026."""
    sector = returns["sector"].to_numpy()
    start = locate(returns.index, "2025-01-02")
    end = locate(returns.index, "2026-11-20")
    betas = {}
    for ticker in ["vw"] + ALL_PEERS + ["Porsche SE"]:
        y = returns[ticker].to_numpy()
        beta = fit_masked(
            y,
            sector,
            *estimation_window(returns.index, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"]),
        )
        betas[ticker] = beta

    def car_at(ticker: str, t: int) -> float:
        y = returns[ticker].to_numpy()
        index = np.arange(t - 1, t + 2)
        if not np.isfinite(y[index]).all():
            return np.nan
        beta = betas[ticker]
        return float((y[index] - (beta[0] + beta[1] * sector[index])).sum())

    rows = []
    for event, value in CONFIG["events"].items():
        t = locate(returns.index, value)
        observed = float(cars.loc["vw", event])
        for key, (label, members) in SETS.items():
            usable = [m for m in members if m in betas]
            observed_peer = np.nanmean([car_at(m, t) for m in usable])
            observed_gap = observed - observed_peer
            gaps = []
            for j in range(start + 1, end):
                vw_car = car_at("vw", j)
                peer_cars = np.array([car_at(m, j) for m in usable])
                peer_cars = peer_cars[np.isfinite(peer_cars)]
                if np.isfinite(vw_car) and len(peer_cars) >= max(2, int(0.8 * len(usable))):
                    gaps.append(vw_car - float(peer_cars.mean()))
            gaps = np.array(gaps)
            rows.append({
                "event": event,
                "set": key,
                "label": label,
                "observed_gap": observed_gap,
                "windows": int(len(gaps)),
                "percentile": float((gaps <= observed_gap).mean() * 100),
                "p_one_sided": float((gaps <= observed_gap).mean()),
                "placebo_min": float(gaps.min()),
                "placebo_max": float(gaps.max()),
            })
    return pd.DataFrame(rows)


def garch_table(returns: pd.DataFrame) -> pd.DataFrame:
    """Event level z statistics under constant, rolling and GARCH volatility."""
    from arch import arch_model

    y = returns["vw"].to_numpy()
    sector = returns["sector"].to_numpy()
    start, end = estimation_window(returns.index, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    beta, sigma, _ = fit(y, sector.reshape(-1, 1), start, end)
    abnormal = y - (beta[0] + beta[1] * sector)

    models = {}
    models["patell"] = ("Constant variance", np.full(len(y), sigma))
    for window in (20, 60, 120, 250):
        models[f"rolling_{window}"] = (f"Rolling {window} days", None)

    for dist in ("normal", "t"):
        result = arch_model(
            y[start : end + 1] * 100,
            mean="Constant",
            vol="Garch",
            p=1,
            q=1,
            dist=dist,
            rescale=False,
        ).fit(disp="off")
        omega = result.params["omega"] / 10000
        alpha = result.params["alpha[1]"]
        beta_g = result.params["beta[1]"]
        mu = result.params["mu"] / 100
        variance = (result.conditional_volatility[-1] / 100) ** 2
        forecast = np.empty(len(y))
        forecast[:] = np.nan
        forecast[end] = variance
        for k in range(end + 1, len(y)):
            shock = y[k - 1] - mu
            forecast[k] = omega + alpha * shock * shock + beta_g * forecast[k - 1]
        models[f"garch_{dist}"] = (f"GARCH(1,1) {dist}", forecast)

    rows = []
    for event, value in CONFIG["events"].items():
        t = locate(returns.index, value)
        index = np.arange(t - 1, t + 2)
        car = float(abnormal[index].sum())
        for key, (label, series) in models.items():
            if key == "patell":
                sd = sigma
                z = car / (sd * np.sqrt(3))
            elif key.startswith("rolling"):
                window = int(key.split("_")[1])
                sd = float(np.std(abnormal[t - window - 1 : t - 1], ddof=1))
                z = car / (sd * np.sqrt(3))
            else:
                sd = float(np.sqrt(np.nanmean(series[index])))
                z = car / (sd * np.sqrt(3))
            rows.append({
                "event": event,
                "model": key,
                "label": label,
                "daily_sigma": sd,
                "car": car,
                "z": z,
                "p_two_sided": float(2 * stats.norm.sf(abs(z))),
            })
    return pd.DataFrame(rows)


def caar_path(returns: pd.DataFrame, draws: int = 10000) -> pd.DataFrame:
    """Average cumulative abnormal return and a simulation band under the null."""
    y = returns["vw"].to_numpy()
    sector = returns["sector"].to_numpy()
    start, end = estimation_window(returns.index, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    beta, sigma, _ = fit(y, sector.reshape(-1, 1), start, end)
    paths = []
    for value in CONFIG["events"].values():
        t = locate(returns.index, value)
        index = np.arange(t - 10, t + 21)
        abnormal = y[index] - (beta[0] + beta[1] * sector[index])
        paths.append(np.cumsum(abnormal))
    paths = np.array(paths)
    caar = paths.mean(axis=0)
    rng = np.random.default_rng(CONFIG["seed"])
    null = np.array([np.cumsum(rng.normal(0, sigma, (3, 31)), axis=1).mean(axis=0) for _ in range(draws)])
    lower = np.percentile(null, 2.5, axis=0)
    upper = np.percentile(null, 97.5, axis=0)
    return pd.DataFrame({
        "day": np.arange(-10, 21),
        "caar": caar,
        "lower_null": lower,
        "upper_null": upper,
    })


def power_curve(returns: pd.DataFrame) -> pd.DataFrame:
    """Power for a grid of event counts and true mean effects."""
    y = returns["vw"].to_numpy()
    sector = returns["sector"].to_numpy()
    start, end = estimation_window(returns.index, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    _, sigma, _ = fit(y, sector.reshape(-1, 1), start, end)
    per_event = sigma * np.sqrt(3)
    rows = []
    for effect in (0.016, 0.03, 0.06, 0.08):
        for n in range(3, 51):
            se = per_event / np.sqrt(n)
            ncp = effect / se
            critical = stats.t.ppf(0.975, n - 1)
            if ncp > 30:
                power = float(stats.norm.sf(critical - ncp))
            else:
                power = float(
                    stats.nct.sf(critical, n - 1, ncp)
                    + stats.nct.cdf(-critical, n - 1, ncp)
                )
                if not np.isfinite(power):
                    power = 1.0
            rows.append({"effect": effect, "n_events": n, "power": float(power)})
    return pd.DataFrame(rows)


def forest_table(returns: pd.DataFrame) -> pd.DataFrame:
    """Event CAR with constant variance and GARCH confidence intervals."""
    from arch import arch_model

    y = returns["vw"].to_numpy()
    sector = returns["sector"].to_numpy()
    start, end = estimation_window(returns.index, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    beta, sigma, _ = fit(y, sector.reshape(-1, 1), start, end)
    result = arch_model(
        y[start : end + 1] * 100,
        mean="Constant",
        vol="Garch",
        p=1,
        q=1,
        dist="t",
        rescale=False,
    ).fit(disp="off")
    omega = result.params["omega"] / 10000
    alpha = result.params["alpha[1]"]
    beta_g = result.params["beta[1]"]
    mu = result.params["mu"] / 100
    variance = (result.conditional_volatility[-1] / 100) ** 2
    forecast = np.empty(len(y))
    forecast[:] = np.nan
    forecast[end] = variance
    for k in range(end + 1, len(y)):
        shock = y[k - 1] - mu
        forecast[k] = omega + alpha * shock * shock + beta_g * forecast[k - 1]
    rows = []
    for event, value in CONFIG["events"].items():
        t = locate(returns.index, value)
        index = np.arange(t - 1, t + 2)
        abnormal = y[index] - (beta[0] + beta[1] * sector[index])
        car = float(abnormal.sum())
        se_patell = sigma * np.sqrt(3)
        se_garch = float(np.sqrt(np.nansum(forecast[index])))
        rows.append({
            "event": event,
            "car": car,
            "se_patell": se_patell,
            "lo_patell": car - 1.96 * se_patell,
            "hi_patell": car + 1.96 * se_patell,
            "se_garch": se_garch,
            "lo_garch": car - 1.96 * se_garch,
            "hi_garch": car + 1.96 * se_garch,
        })
    return pd.DataFrame(rows)


def plot_caar(path: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.fill_between(path.day, 100 * path.lower_null, 100 * path.upper_null, color=LIGHT, alpha=0.45, label="95 percent band under no effect")
    ax.plot(path.day, 100 * path.caar, color=NAVY, lw=2, label="average path")
    ax.axvline(0, color=GREY, lw=0.8, ls=":")
    ax.axhline(0, color=GREY, lw=0.8)
    ax.set_xlabel("trading days from the announcement")
    ax.set_ylabel("cumulative abnormal return, log points")
    ax.set_title("The average path is negative but inside the no-effect band")
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "fig26_p05_caar.png", dpi=200)
    plt.close(fig)


def plot_power(power: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    for effect, group in power.groupby("effect"):
        ax.plot(group.n_events, group.power, lw=1.8, label=f"true effect {100 * effect:.1f} log points")
    ax.axhline(0.8, color=GREY, lw=0.8, ls="--")
    ax.axvline(3, color=RED, lw=0.8, ls=":")
    ax.set_xlabel("number of events")
    ax.set_ylabel("power, five percent two sided level")
    ax.set_title("Three events detect only large effects")
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig27_p05_power.png", dpi=200)
    plt.close(fig)


def plot_peer_dist(cars: pd.DataFrame) -> None:
    values = cars.loc[[m for m in ALL_PEERS if m in cars.index], "Everllence"].dropna().sort_values()
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    colors = [NAVY if ticker in OEM else GREY for ticker in values.index]
    y = np.arange(len(values))
    ax.scatter(100 * values.values, y, c=colors, s=34, zorder=3)
    vw = 100 * float(cars.loc["vw", "Everllence"])
    ax.axvline(vw, color=RED, lw=1.4, ls="--", label="Volkswagen")
    ax.axvline(100 * values.mean(), color=GOLD, lw=1.0, ls=":", label="peer mean")
    ax.set_yticks(y)
    ax.set_yticklabels([DISPLAY.get(t, t) for t in values.index], fontsize=7)
    ax.set_xlabel("three day cumulative abnormal return at Everllence, log points")
    ax.set_title("Volkswagen is sixth of 24, not an outlier")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "fig28_p05_peer_dist.png", dpi=200)
    plt.close(fig)


def plot_forest(forest: pd.DataFrame) -> None:
    fig, (left, right) = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
    y = np.arange(len(forest))
    for ax, lo, hi, title in (
        (left, "lo_patell", "hi_patell", "constant variance"),
        (right, "lo_garch", "hi_garch", "GARCH(1,1) with t errors"),
    ):
        ax.hlines(y, 100 * forest[lo], 100 * forest[hi], color=NAVY, lw=2)
        ax.scatter(100 * forest.car, y, color=RED, zorder=3)
        ax.axvline(0, color=GREY, lw=0.8)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("CAR, log points")
    left.set_yticks(y)
    left.set_yticklabels(forest.event)
    left.invert_yaxis()
    fig.suptitle("Event level confidence intervals depend on the volatility model", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig29_p05_forest.png", dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(RETURNS, parse_dates=["date"]).set_index("date").sort_index()
    peers = download_peers()
    returns = build_returns(panel, peers)

    start, end = estimation_window(returns.index, CONFIG["est_anchor"], CONFIG["est_len"], CONFIG["gap"])
    cars = event_cars(returns, ["vw"] + ALL_PEERS + ["Porsche SE"], start, end)
    base_mean = float(cars.loc["vw", list(CONFIG["events"])].mean())
    print(f"base mean {base_mean:.10f}, published {BASE_MEAN:.10f}, difference {base_mean - BASE_MEAN:.2e}")
    if args.check:
        if abs(base_mean - BASE_MEAN) > 1e-9:
            raise SystemExit("base specification does not reproduce the published mean")
        print("base specification reproduces the published mean")
        return

    summary = peer_summary(cars)
    summary.to_csv(OUT / "peer_broad_summary.csv", index=False)
    cars.to_csv(OUT / "peer_broad_cars.csv")

    loo = leave_one_out(cars)
    loo.to_csv(OUT / "peer_broad_leave_one_out.csv", index=False)

    placebo = peer_placebo_time(returns, cars)
    placebo.to_csv(OUT / "peer_broad_placebo.csv", index=False)

    garch = garch_table(returns)
    garch.to_csv(OUT / "garch.csv", index=False)

    caar = caar_path(returns)
    caar.to_csv(OUT / "caar_path.csv", index=False)

    power = power_curve(returns)
    power.to_csv(OUT / "power_curve.csv", index=False)

    forest = forest_table(returns)
    forest.to_csv(OUT / "forest.csv", index=False)

    plot_caar(caar)
    plot_power(power)
    plot_peer_dist(cars)
    plot_forest(forest)

    key = {
        "base_mean_car": base_mean,
        "peer_summary": summary.round(6).to_dict(orient="records"),
        "leave_one_out": loo.round(6).to_dict(orient="records"),
        "peer_placebo": placebo.round(6).to_dict(orient="records"),
        "garch": garch.round(6).to_dict(orient="records"),
        "caar": {
            "day_1": float(caar.loc[caar.day == 1, "caar"].iloc[0]),
            "day_20": float(caar.loc[caar.day == 20, "caar"].iloc[0]),
            "minimum": float(caar.caar.min()),
            "minimum_day": int(caar.loc[caar.caar.idxmin(), "day"]),
        },
        "power": {
            "events_for_observed_effect": int(
                power[(power.effect == 0.016) & (power.power >= 0.8)].n_events.min()
            ),
            "power_at_three_for_six_log_points": float(
                power[(power.effect == 0.06) & (power.n_events == 3)].power.iloc[0]
            ),
        },
        "forest": forest.round(6).to_dict(orient="records"),
    }
    (OUT / "v25_summary.json").write_text(json.dumps(key, indent=2), encoding="utf-8")

    print("\nPeer summary, Everllence:")
    print(summary[summary.event == "Everllence"][["label", "n_peers", "peer_mean", "gap_mean", "vw_rank", "p_one_sided"]].round(4).to_string(index=False))
    print("\nGARCH, Everllence:")
    print(garch[garch.event == "Everllence"][["label", "daily_sigma", "z", "p_two_sided"]].round(4).to_string(index=False))
    print("\nPower:")
    print(key["power"])
    print(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
