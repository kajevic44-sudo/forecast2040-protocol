"""Figure F13, the capital cycle test on German long run data.

The question is whether credit expansion predicts later equity returns, which
is the mechanism the dissertation attributes to the large owners. The test is
deliberately simple and reproducible: annual change in credit to GDP against
the real total equity return k years later, for k from minus five to plus
five. A negative correlation at positive k is the capital cycle signature.

Input   data/historical/tidy/jst_germany.csv, JST Macrohistory Database R6.
Output  figures/fig13_capital_cycle.png
        data/model/capital_cycle_lags.csv
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "historical" / "tidy" / "jst_germany.csv"
FIG = ROOT / "figures"
OUT = ROOT / "data" / "model"

NAVY = "#1f3b57"
RED = "#c8553d"
GREY = "#666666"


def load() -> pd.DataFrame:
    frame = pd.read_csv(SRC, usecols=["year", "eq_tr", "debtgdp"])
    frame = frame.sort_values("year").reset_index(drop=True)
    frame["credit_change"] = frame["debtgdp"].diff()
    frame["equity_return"] = frame["eq_tr"]
    return frame


def lag_table(frame: pd.DataFrame, lags: range) -> pd.DataFrame:
    rows = []
    for lag in lags:
        forward = frame["equity_return"].shift(-lag)
        pair = pd.concat([frame["credit_change"], forward], axis=1).dropna()
        pair.columns = ["credit_change", "forward_return"]
        correlation = float(pair["credit_change"].corr(pair["forward_return"]))
        rows.append({"lag_years": lag, "correlation": correlation, "observations": len(pair)})
    table = pd.DataFrame(rows)
    table["band"] = 2.0 / np.sqrt(table["observations"])
    return table


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.color": "#e5e5e5",
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
        }
    )


def main() -> int:
    style()
    frame = load()
    table = lag_table(frame, range(-5, 6))

    fig, (left, right) = plt.subplots(2, 1, figsize=(7.4, 8.4))

    colours = [RED if value < 0 else NAVY for value in table["correlation"]]
    left.bar(table["lag_years"], table["correlation"], color=colours, width=0.7)
    left.axhline(0, color=GREY, linewidth=0.8)
    left.axhline(float(table["band"].iloc[0]), color=GREY, linewidth=0.8, linestyle=":")
    left.axhline(-float(table["band"].iloc[0]), color=GREY, linewidth=0.8, linestyle=":")
    left.set_xlabel("years between credit change and equity return")
    left.set_ylabel("correlation")
    left.set_ylim(-0.34, 0.22)
    left.set_title("Credit growth and later equity returns\nGermany, 1870 to 2020")
    left.set_xticks(list(table["lag_years"]))
    left.text(
        0.02,
        0.04,
        "dotted lines: two standard error band, red bars are negative",
        transform=left.transAxes,
        fontsize=8.5,
        color=GREY,
    )
    for lag, value in zip(table["lag_years"], table["correlation"], strict=True):
        left.annotate(
            f"{value:.2f}",
            xy=(lag, value),
            xytext=(0, 4 if value >= 0 else -12),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color="#222222",
        )

    horizon = 5
    scatter = pd.concat([frame["credit_change"], frame["equity_return"].shift(-horizon)], axis=1).dropna()
    scatter.columns = ["credit_change", "forward_return"]
    right.scatter(scatter["credit_change"], scatter["forward_return"], s=18, color=NAVY, alpha=0.65, edgecolor="none")
    slope, intercept = np.polyfit(scatter["credit_change"], scatter["forward_return"], 1)
    grid = np.linspace(scatter["credit_change"].min(), scatter["credit_change"].max(), 50)
    right.plot(grid, intercept + slope * grid, color=RED, linewidth=1.6)
    fitted = intercept + slope * scatter["credit_change"]
    r_squared = 1 - float(((scatter["forward_return"] - fitted) ** 2).sum()) / float(
        ((scatter["forward_return"] - scatter["forward_return"].mean()) ** 2).sum()
    )
    right.set_xlabel("change in the credit to GDP ratio")
    right.set_ylabel("real equity return, next five years")
    right.set_title("The five year relation")
    right.text(
        0.03,
        0.05,
        f"slope {slope:.3f}, R squared {r_squared:.3f}, n {len(scatter)}",
        transform=right.transAxes,
        fontsize=8.5,
        color=GREY,
    )

    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "fig13_capital_cycle.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    table.to_csv(OUT / "capital_cycle_lags.csv", index=False)
    print(f"wrote {FIG / 'fig13_capital_cycle.png'}")
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
