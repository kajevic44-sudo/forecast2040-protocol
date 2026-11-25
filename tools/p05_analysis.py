"""P05, event study of the Volkswagen divestment programme.

The design was fixed in the working paper before any return was computed: log
daily total returns from the adjusted close, a market model estimated once on
the 250 trading days ending 20 trading days before the first event, and the
same parameters applied to every event. This script executes that design and
writes every number the paper reports.

Input   data/panel/panel_daily.csv, Volkswagen preference share and peers
        data/raw/p05_benchmarks.csv, DAX, STOXX Europe 600, STOXX Europe 600
        Automobiles and Parts (EXV5.DE), downloaded from Yahoo Finance on 25 November 2026
Output  data/model/p05_events.csv
        data/model/p05_tests.csv
        data/model/p05_robustness.csv
        data/model/p05_summary.json
        figures/fig22_p05_car_paths.png
        figures/fig23_p05_indexed.png
"""
from __future__ import annotations

import json
import math
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "model"
FIG = ROOT / "figures"
PANEL = ROOT / "data" / "panel" / "panel_daily.csv"
BENCH = RAW / "p05_benchmarks.csv"

NAVY = "#1f3b57"
RED = "#c8553d"
GREY = "#666666"
GOLD = "#b08d3f"

SYMBOLS = {"dax": "%5EGDAXI", "stoxx": "%5ESTOXX", "autos": "EXV5.DE"}

EVENTS = [
    {"id": "E1", "name": "Italdesign", "date": "2025-12-10", "type": "primary"},
    {"id": "E2", "name": "Everllence", "date": "2026-06-24", "type": "primary"},
    {"id": "E3", "name": "IAV", "date": "2026-08-11", "type": "press"},
    {"id": "E4", "name": "Programme", "date": "2026-09-01", "type": "guidance"},
]

PRIMARY_EVENTS = ["E1", "E2", "E3"]


def download_benchmarks() -> pd.DataFrame:
    """Download daily adjusted closes once and cache them with a date stamp."""
    if BENCH.exists():
        return pd.read_csv(BENCH, parse_dates=["date"])
    frames = []
    metadata: dict[str, dict[str, str]] = {}
    for name, symbol in SYMBOLS.items():
        url = (
            "https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{symbol}?period1=1451606400&period2=1798761600&interval=1d&events=div%2Csplits"
        )
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=60) as handle:
            payload = json.loads(handle.read().decode())
        result = payload["chart"]["result"][0]
        meta = result.get("meta", {})
        long_name = str(meta.get("longName", ""))
        if name == "autos" and "Automobiles" not in long_name and "Automobile" not in long_name:
            raise RuntimeError(
                f"the autos benchmark is {long_name!r}, not an automobiles and parts index"
            )
        close = result["indicators"]["adjclose"][0]["adjclose"]
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(result["timestamp"], unit="s").normalize(),
                name: close,
            }
        ).dropna()
        frames.append(frame.set_index("date"))
        metadata[name] = {"symbol": symbol, "long_name": long_name, "currency": meta.get("currency")}
    merged = pd.concat(frames, axis=1).sort_index()
    merged.index.name = "date"
    merged.to_csv(BENCH, float_format="%.6f")
    (RAW / "p05_benchmarks_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return merged.reset_index()


def load_prices() -> pd.DataFrame:
    panel = pd.read_csv(PANEL, parse_dates=["period"])
    prices = panel.dropna(subset=["yahoo_vow3"])[["period", "yahoo_vow3", "yahoo_pah3_de", "yahoo_bmw_de", "yahoo_mbg_de"]]
    prices = prices.rename(columns={"period": "date", "yahoo_vow3": "vw", "yahoo_pah3_de": "pah3", "yahoo_bmw_de": "bmw", "yahoo_mbg_de": "mbg"})
    bench = download_benchmarks()
    frame = prices.merge(bench, on="date", how="inner").sort_values("date").reset_index(drop=True)
    # Drop incomplete rows before differencing. Dropping after the diff would
    # remove a return while later returns still reference the dropped price,
    # and the cumulative sum would no longer equal the price ratio.
    columns = ["vw", "pah3", "bmw", "mbg", "dax", "stoxx", "autos"]
    frame = frame.dropna(subset=columns).reset_index(drop=True)
    return frame


def log_returns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame[["date"]].copy()
    for column in columns:
        out[column] = np.log(frame[column]).diff()
    return out.dropna().reset_index(drop=True)


def market_model(returns: pd.DataFrame, benchmark: str, event_date: pd.Timestamp, estimation: int = 250, gap: int = 20) -> dict:
    """Estimate alpha and beta on a window that ends before the event."""
    index = returns.index[returns["date"] == event_date]
    if len(index) == 0:
        raise ValueError(f"event date {event_date.date()} is not a trading day")
    end = int(index[0]) - gap
    start = end - estimation + 1
    window = returns.iloc[start : end + 1]
    y = window["vw"].to_numpy()
    x = window[benchmark].to_numpy()
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    alpha, beta = float(coefficients[0]), float(coefficients[1])
    residuals = y - design @ coefficients
    dof = len(y) - 2
    sigma = float(math.sqrt(float(residuals @ residuals) / dof))
    mean_x = float(x.mean())
    ss_x = float(((x - mean_x) ** 2).sum())
    return {
        "alpha": alpha,
        "beta": beta,
        "sigma": sigma,
        "mean_x": mean_x,
        "ss_x": ss_x,
        "estimation_days": len(y),
        "start": window["date"].iloc[0],
        "end": window["date"].iloc[-1],
    }


def abnormal_returns(returns: pd.DataFrame, model: dict, benchmark: str) -> pd.DataFrame:
    frame = returns.copy()
    frame["ar"] = frame["vw"] - model["alpha"] - model["beta"] * frame[benchmark]
    forecast_var = model["sigma"] ** 2 * (
        1.0
        + 1.0 / model["estimation_days"]
        + (frame[benchmark] - model["mean_x"]) ** 2 / model["ss_x"]
    )
    frame["sar"] = frame["ar"] / np.sqrt(forecast_var)
    return frame


def window_car(frame: pd.DataFrame, event_date: pd.Timestamp, low: int, high: int) -> dict:
    index = int(frame.index[frame["date"] == event_date][0])
    window = frame.iloc[index + low : index + high + 1]
    car = float(window["ar"].sum())
    csar = float(window["sar"].sum())
    days = len(window)
    return {"car": car, "csar": csar, "days": days, "start": window["date"].iloc[0], "end": window["date"].iloc[-1]}


def patell_z(rows: list[dict]) -> float:
    numerator = sum(row["csar"] for row in rows)
    denominator = math.sqrt(sum(row["days"] for row in rows))
    return numerator / denominator


def bmp_t(rows: list[dict]) -> float:
    scar = np.array([row["csar"] / math.sqrt(row["days"]) for row in rows])
    n = len(scar)
    return float(scar.mean() / (scar.std(ddof=1) / math.sqrt(n)))


def sign_test(values: list[float]) -> float:
    k = sum(1 for v in values if v > 0)
    n = len(values)
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def wilcoxon_exact(values: list[float]) -> float:
    n = len(values)
    ranks = pd.Series(np.abs(values)).rank().to_numpy()
    observed = sum(r for r, v in zip(ranks, values) if v > 0)
    outcomes = []
    for mask in range(2 ** n):
        total = sum(ranks[i] for i in range(n) if mask >> i & 1)
        outcomes.append(total)
    outcomes = np.array(outcomes, dtype=float)
    centre = ranks.sum() / 2
    return float((np.abs(outcomes - centre) >= abs(observed - centre)).mean())


def randomisation(returns: pd.DataFrame, model: dict, benchmark: str, observed: float, spacing: tuple[int, int], draws: int = 10000, seed: int = 20261125) -> dict:
    """Draw pseudo event sets with the same calendar spacing from 2017 to 2024."""
    rng = np.random.default_rng(seed)
    frame = abnormal_returns(returns, model, benchmark).reset_index(drop=True)
    dates = frame["date"]
    first_allowed = pd.Timestamp("2017-01-03")
    last_allowed = pd.Timestamp("2024-12-31") - timedelta(days=spacing[0] + spacing[1])
    candidates = dates[(dates >= first_allowed) & (dates <= last_allowed)].reset_index(drop=True)
    index_of = {d: i for i, d in enumerate(dates)}
    means = []
    for _ in range(draws):
        start = candidates.iloc[int(rng.integers(0, len(candidates)))]
        second = start + timedelta(days=spacing[0])
        third = second + timedelta(days=spacing[1])
        cars = []
        for target in (start, second, third):
            position = index_of.get(target)
            if position is None:
                cars = []
                break
            window = frame.iloc[max(0, position - 1) : position + 2]
            cars.append(float(window["ar"].sum()))
        if len(cars) == 3:
            means.append(float(np.mean(cars)))
    means = np.array(means)
    share_above = float((means >= observed).mean())
    share_below = float((means <= observed).mean())
    return {
        "draws": int(len(means)),
        "share_above": share_above,
        "share_below": share_below,
        "p_two_sided": float(min(1.0, 2 * min(share_above, share_below))),
        "mean_pseudo": float(means.mean()),
        "sd_pseudo": float(means.std(ddof=1)),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    prices = load_prices()
    returns = log_returns(prices, ["vw", "pah3", "bmw", "mbg", "dax", "stoxx", "autos"])
    # The extension analysis reads the same return series. Add the three
    # international peers on the same calendar without dropping any base row.
    panel = pd.read_csv(PANEL, parse_dates=["period"]).rename(columns={"period": "date"})
    peer_columns = {"yahoo_toyota": "toyota", "yahoo_byd": "byd", "yahoo_tsla": "tesla"}
    peers = panel[["date", *peer_columns]].rename(columns=peer_columns)
    peer_returns = peers.set_index("date").pipe(np.log).diff().reset_index()
    extras = returns.merge(peer_returns, on="date", how="left").rename(
        columns={"autos": "sector", "stoxx": "market", "mbg": "mercedes", "pah3": "porsche_se"}
    )
    extras.to_csv(OUT / "p05_returns.csv", index=False, float_format="%.10f")
    print(f"returns {returns['date'].min().date()} to {returns['date'].max().date()}, rows {len(returns)}")

    first = pd.Timestamp(EVENTS[0]["date"])
    model = market_model(returns, "autos", first)
    print("market model", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in model.items()})

    frame = abnormal_returns(returns, model, "autos")
    windows = {"(-1,+1)": (-1, 1), "(0,+1)": (0, 1), "(0,+5)": (0, 5), "(0,+20)": (0, 20), "(-5,+5)": (-5, 5)}

    rows = []
    for event in EVENTS:
        event_date = pd.Timestamp(event["date"])
        for label, (low, high) in windows.items():
            result = window_car(frame, event_date, low, high)
            rows.append(
                {
                    "event": event["id"],
                    "name": event["name"],
                    "date": event_date.date().isoformat(),
                    "type": event["type"],
                    "window": label,
                    **result,
                }
            )
    events = pd.DataFrame(rows)
    events.to_csv(OUT / "p05_events.csv", index=False)
    print(events[events["window"] == "(-1,+1)"].to_string(index=False))

    tests = []
    for label in windows:
        subset = events[(events["window"] == label) & (events["event"].isin(PRIMARY_EVENTS))]
        cars = subset["car"].tolist()
        tests.append(
            {
                "window": label,
                "events": len(subset),
                "mean_car": float(np.mean(cars)),
                "median_car": float(np.median(cars)),
                "patell_z": patell_z(subset.to_dict("records")),
                "bmp_t": bmp_t(subset.to_dict("records")),
                "sign_p": sign_test(cars),
                "wilcoxon_p": wilcoxon_exact(cars),
                "positive": int(sum(1 for c in cars if c > 0)),
            }
        )
    tests = pd.DataFrame(tests)
    tests.to_csv(OUT / "p05_tests.csv", index=False)
    print(tests.to_string(index=False))

    observed = float(tests.loc[tests["window"] == "(-1,+1)", "mean_car"].iloc[0])
    spacing = (
        (pd.Timestamp(EVENTS[1]["date"]) - pd.Timestamp(EVENTS[0]["date"])).days,
        (pd.Timestamp(EVENTS[2]["date"]) - pd.Timestamp(EVENTS[1]["date"])).days,
    )
    rand = randomisation(returns, model, "autos", observed, spacing)
    print("randomisation", rand, "spacing", spacing)

    robustness = []
    for benchmark in ("autos", "dax", "stoxx"):
        for estimation in (250, 120):
            fitted = market_model(returns, benchmark, first, estimation=estimation)
            ar = abnormal_returns(returns, fitted, benchmark)
            for label, (low, high) in (("(-1,+1)", (-1, 1)), ("(0,+1)", (0, 1)), ("(0,+5)", (0, 5))):
                subset = [window_car(ar, pd.Timestamp(e["date"]), low, high) for e in EVENTS if e["id"] in PRIMARY_EVENTS]
                robustness.append(
                    {
                        "benchmark": benchmark,
                        "estimation_days": estimation,
                        "window": label,
                        "mean_car": float(np.mean([s["car"] for s in subset])),
                        "patell_z": patell_z(subset),
                        "bmp_t": bmp_t(subset),
                        "beta": fitted["beta"],
                    }
                )
    robustness = pd.DataFrame(robustness)
    robustness.to_csv(OUT / "p05_robustness.csv", index=False)
    print(robustness.to_string(index=False))

    # Programme period, 9 December 2025 to the last observation.
    start = pd.Timestamp("2025-12-09")
    end = returns["date"].max()
    period = returns[(returns["date"] > start) & (returns["date"] <= end)]
    cumulative = {
        "vw": float(period["vw"].sum()),
        "autos": float(period["autos"].sum()),
        "dax": float(period["dax"].sum()),
        "stoxx": float(period["stoxx"].sum()),
        "days": int(len(period)),
        "start": start.date().isoformat(),
        "end": end.date().isoformat(),
    }
    print("programme period", cumulative)

    # Placebo, every three day window from 2017 to 2024 under the same model.
    placebo_frame = frame[(frame["date"] >= "2017-01-03") & (frame["date"] <= "2024-12-31")].reset_index(drop=True)
    placebo_cars = []
    for position in range(1, len(placebo_frame) - 1):
        placebo_cars.append(float(placebo_frame["ar"].iloc[position - 1 : position + 2].sum()))
    placebo_cars = np.array(placebo_cars)
    placebo = {
        "windows": int(len(placebo_cars)),
        "mean": float(placebo_cars.mean()),
        "sd": float(placebo_cars.std(ddof=1)),
        "share_at_or_below_observed": float((placebo_cars <= observed).mean()),
        "percentile_of_observed": float((placebo_cars <= observed).mean() * 100),
    }
    print("placebo", placebo)

    # Drift over the programme period, relative to the sector, with a t statistic.
    relative = period["vw"] - period["autos"]
    import statsmodels.api as sm

    nw = sm.OLS(relative.to_numpy(), np.ones(len(relative))).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    drift = {
        "mean_daily": float(relative.mean()),
        "sd_daily": float(relative.std(ddof=1)),
        "t": float(relative.mean() / (relative.std(ddof=1) / math.sqrt(len(relative)))),
        "t_newey_west": float(nw.tvalues[0]),
        "se_newey_west": float(nw.bse[0]),
        "days": int(len(relative)),
        "cumulative_relative": float(relative.sum()),
    }
    print("drift", drift)

    # Figure 1, cumulative abnormal returns around each event.
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    colours = {"E1": NAVY, "E2": RED, "E3": GOLD, "E4": GREY}
    for event in EVENTS:
        event_date = pd.Timestamp(event["date"])
        index = int(frame.index[frame["date"] == event_date][0])
        window = frame.iloc[index - 10 : index + 21]
        path = window["ar"].cumsum().to_numpy()
        ax.plot(range(-10, len(path) - 10), path * 100, label=f"{event['name']}, {event_date.date()}", color=colours[event["id"]], linewidth=1.8)
    ax.axvline(0, color=GREY, linewidth=0.8, linestyle=":")
    ax.axhline(0, color=GREY, linewidth=0.8)
    ax.set_xlabel("trading days from the announcement")
    ax.set_ylabel("cumulative abnormal return, percent")
    ax.set_title("Cumulative abnormal returns around four Volkswagen announcements")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig22_p05_car_paths.png", dpi=200)
    plt.close(fig)

    # Figure 2, the preference share against the sector, indexed to 100.
    base = pd.Timestamp("2025-01-02")
    subset = returns[returns["date"] >= base].copy()
    for column in ("vw", "autos", "dax"):
        subset[column] = 100 * np.exp(subset[column].cumsum())
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(subset["date"], subset["vw"], color=NAVY, linewidth=1.8, label="Volkswagen preference share")
    ax.plot(subset["date"], subset["autos"], color=RED, linewidth=1.4, label="STOXX Europe 600 Automobiles and Parts")
    ax.plot(subset["date"], subset["dax"], color=GREY, linewidth=1.2, label="DAX")
    for event in EVENTS:
        ax.axvline(pd.Timestamp(event["date"]), color="#cccccc", linewidth=0.8, linestyle="--")
    ax.set_ylabel("index, 2 January 2025 equals 100")
    ax.set_title("Volkswagen preference share against the sector and the market")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig23_p05_indexed.png", dpi=200)
    plt.close(fig)

    summary = {
        "sample": {"first": returns["date"].min().date().isoformat(), "last": returns["date"].max().date().isoformat(), "rows": len(returns)},
        "market_model": {k: (v.isoformat() if isinstance(v, pd.Timestamp) else v) for k, v in model.items()},
        "events": events.to_dict("records"),
        "tests": tests.to_dict("records"),
        "randomisation": rand,
        "spacing_days": spacing,
        "robustness": robustness.to_dict("records"),
        "programme_period": cumulative,
        "placebo": placebo,
        "drift": drift,
    }
    (OUT / "p05_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
