"""Figure F15, three scenario paths for Volkswagen Group deliveries in China.

The scenarios are not model forecasts and are not presented as such. They are
conditional paths built from the observed series, with the rule for each path
written in the caption and in the output CSV, so that a reader can recompute
them from the same data.

Path A  continuation of the log-linear decline estimated on 2019 to 2025.
Path B  decline that halves every five years towards a floor of 2.0 million.
Path C  stabilisation to 2028, then growth at half the 2010 to 2015 rate.

Input   data/raw/vw_group_china_deliveries.csv
Output  figures/fig15_scenario_fan.png
        data/model/china_scenarios.csv
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "vw_group_china_deliveries.csv"
FIG = ROOT / "figures"
OUT = ROOT / "data" / "model"

NAVY = "#1f3b57"
RED = "#c8553d"
GREEN = "#588157"
GREY = "#666666"
FLOOR = 2_000_000.0


def slope(frame: pd.DataFrame, first: int, last: int) -> float:
    part = frame[(frame["year"] >= first) & (frame["year"] <= last)]
    years = part["year"].to_numpy(dtype=float)
    values = np.log(part["value"].to_numpy(dtype=float))
    return float(np.polyfit(years, values, 1)[0])


def build(frame: pd.DataFrame) -> pd.DataFrame:
    start_year = int(frame["year"].max())
    start_value = float(frame.loc[frame["year"] == start_year, "value"].iloc[0])
    decline = slope(frame, 2019, start_year)
    recovery = 0.5 * slope(frame, 2010, 2015)
    rows = []
    for offset in range(1, 15):
        year = start_year + offset
        path_a = start_value * np.exp(decline * offset)
        gap = start_value - FLOOR
        path_b = FLOOR + gap * 0.5 ** (offset / 5.0)
        if offset <= 2:
            path_c = start_value
        else:
            path_c = min(start_value * np.exp(recovery * (offset - 2)), 3_200_000.0)
        for name, value in (("A continuation", path_a), ("B halving to floor", path_b), ("C stabilisation", path_c)):
            rows.append({"year": year, "path": name, "value": round(value)})
    table = pd.DataFrame(rows)
    table.attrs["decline"] = decline
    table.attrs["recovery"] = recovery
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
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
        }
    )


def main() -> int:
    style()
    frame = pd.read_csv(SRC)
    table = build(frame)
    decline = table.attrs["decline"]
    recovery = table.attrs["recovery"]

    fig, axis = plt.subplots(figsize=(10.5, 5.4))
    axis.plot(frame["year"], frame["value"] / 1e6, color="#222222", linewidth=1.8, label="observed deliveries")
    colours = {"A continuation": RED, "B halving to floor": NAVY, "C stabilisation": GREEN}
    for name, group in table.groupby("path", sort=True):
        axis.plot(group["year"], group["value"] / 1e6, color=colours[str(name)], linewidth=1.6, linestyle="--", label=str(name))
        axis.annotate(
            f"{group['value'].iloc[-1] / 1e6:.2f}",
            xy=(group["year"].iloc[-1], group["value"].iloc[-1] / 1e6),
            xytext=(4, 0),
            textcoords="offset points",
            fontsize=8,
            color=colours[str(name)],
            va="center",
        )
    axis.axhline(FLOOR / 1e6, color=GREY, linewidth=0.8, linestyle=":")
    axis.text(1988, FLOOR / 1e6 + 0.05, "floor 2.0 million", fontsize=7.5, color=GREY)
    axis.set_xlim(1987, 2043)
    axis.set_ylabel("million vehicles per year")
    axis.set_xlabel("year")
    axis.set_title("Volkswagen Group in China, three conditional paths to 2040")
    axis.legend(fontsize=8, frameon=False, loc="upper left")
    axis.text(
        0.0,
        -0.18,
        f"path A uses the 2019 to 2025 log slope {decline:.3f} per year, path C uses {recovery:.3f} per year from 2028",
        transform=axis.transAxes,
        fontsize=7.5,
        color=GREY,
    )
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "fig15_scenario_fan.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    table.to_csv(OUT / "china_scenarios.csv", index=False)
    print(f"wrote {FIG / 'fig15_scenario_fan.png'}")
    print(f"decline {decline:.4f}, recovery {recovery:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
