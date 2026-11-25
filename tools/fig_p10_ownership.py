"""Figure for P10, the voting structure of Volkswagen AG at the end of 2025.

Left panel, the four blocks of voting rights and their shares. Right panel, the
same structure placed on a concentration ladder, so that the Herfindahl index
has a scale: a firm with one hundred equal holders, a firm with a single block
of twenty five percent and the remaining shares dispersed, and Volkswagen as
reported.

Input   docs/OWNERSHIP.md, voting rights notifications at 31 December 2025
Output  figures/fig21_vw_votes.png
        data/model/p10_concentration_ladder.csv
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "data" / "model"

NAVY = "#1f3b57"
RED = "#c8553d"
GREY = "#666666"
LIGHT = "#9aa7b1"

VOTES = {
    "Porsche SE": 53.3,
    "Lower Saxony": 20.0,
    "Qatar Holding": 17.0,
    "Free float": 9.7,
}


def hhi(shares):
    return float(sum(s * s for s in shares))


def ladder():
    equal = [1 / 100] * 100
    block = [0.25] + [(0.75 / 99)] * 99
    vw = [v / 100 for v in VOTES.values()]
    rows = [
        {"structure": "One hundred equal holders", "hhi": hhi(equal), "effective": 1 / hhi(equal)},
        {"structure": "One block of 25 percent", "hhi": hhi(block), "effective": 1 / hhi(block)},
        {"structure": "Volkswagen, 2025", "hhi": hhi(vw), "effective": 1 / hhi(vw)},
    ]
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9.5, "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.labelsize": 9.5, "xtick.labelsize": 9, "ytick.labelsize": 9})
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.4))

    ax = axes[0]
    names = list(VOTES.keys())[::-1]
    values = [VOTES[n] for n in names]
    palette = {"Porsche SE": NAVY, "Lower Saxony": RED, "Qatar Holding": GREY, "Free float": LIGHT}
    colours = [palette[n] for n in names]
    bars = ax.barh(names, values, color=colours, height=0.62)
    for bar, value in zip(bars, values):
        ax.text(value + 1.2, bar.get_y() + bar.get_height() / 2, f"{value:.1f}", va="center", fontsize=9, color="#222222")
    ax.set_xlim(0, 62)
    ax.set_xlabel("share of voting rights, percent")
    ax.set_title("Voting rights at Volkswagen AG, 31 December 2025", color="#111111")
    ax.grid(axis="x", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax = axes[1]
    frame = ladder()
    labels = frame["structure"].tolist()
    eff = frame["effective"].tolist()
    bars = ax.barh(labels[::-1], eff[::-1], color=[NAVY, RED, LIGHT], height=0.5)
    for bar, value in zip(bars, eff[::-1]):
        ax.text(value * 1.15, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va="center", fontsize=9, color="#222222")
    ax.set_xscale("log")
    ax.set_xlim(1, 200)
    ax.set_xlabel("effective number of owners, log scale")
    ax.set_title("What concentration means on a common scale", color="#111111")
    ax.grid(axis="x", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    fig.text(0.01, 0.015, "source: voting rights notifications at 31 December 2025, summarised in docs/OWNERSHIP.md", fontsize=8, color=GREY)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = FIG / "fig21_vw_votes.png"
    fig.savefig(target, dpi=200)
    plt.close(fig)
    frame.to_csv(OUT / "p10_concentration_ladder.csv", index=False)
    print(f"written {target}")
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
