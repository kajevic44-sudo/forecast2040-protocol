"""Figure F16, risk exposure by control layer.

The scores are ordinal, from one to five, and they are the author's assessment
against six named channels. They are not measurements and the figure says so.
The point of the figure is to show that the same shock hits the four layers
differently, which is why the model carries ownership as a separate block.

Output  figures/fig16_risk_matrix.png
        data/model/risk_matrix.csv
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "data" / "model"

LAYERS = ["Family, Porsche SE", "State, Lower Saxony", "Sovereign fund, Qatar", "Free float, institutions"]
CHANNELS = [
    "plant closure veto",
    "capital dilution",
    "China joint venture",
    "technology shift",
    "labour agreements",
    "sanctions and politics",
]
SCORES = np.array(
    [
        [5, 4, 3, 4, 5, 2],
        [4, 3, 3, 3, 4, 3],
        [2, 2, 4, 2, 2, 5],
        [3, 5, 4, 5, 2, 4],
    ]
)


def main() -> int:
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titlesize": 11, "axes.titleweight": "bold"})
    frame = pd.DataFrame(SCORES, index=LAYERS, columns=CHANNELS)
    fig, axis = plt.subplots(figsize=(10, 4.2))
    image = axis.imshow(SCORES, cmap="YlOrRd", vmin=1, vmax=5, aspect="auto")
    axis.set_xticks(range(len(CHANNELS)))
    axis.set_xticklabels(CHANNELS, rotation=25, ha="right", fontsize=8)
    axis.set_yticks(range(len(LAYERS)))
    axis.set_yticklabels(LAYERS, fontsize=8.5)
    for row in range(len(LAYERS)):
        for column in range(len(CHANNELS)):
            value = int(SCORES[row, column])
            axis.text(column, row, str(value), ha="center", va="center", fontsize=10, color="#222222")
    axis.set_title("Exposure of each control layer to six channels, ordinal score one to five")
    bar = fig.colorbar(image, ax=axis, ticks=[1, 2, 3, 4, 5], fraction=0.025, pad=0.02)
    bar.set_label("exposure", fontsize=8)
    axis.text(
        0.0,
        -0.34,
        "author assessment, not a measurement, criteria defined in the ownership chapter",
        transform=axis.transAxes,
        fontsize=7.5,
        color="#666666",
    )
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "fig16_risk_matrix.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    frame.to_csv(OUT / "risk_matrix.csv")
    print(f"wrote {FIG / 'fig16_risk_matrix.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
