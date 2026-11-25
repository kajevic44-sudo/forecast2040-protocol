"""Acquire the annual panel of new passenger car registrations used in P01.

Source: Eurostat dataset road_eqr_carmot, new passenger cars by type of motor
energy and engine size, annual, total motor energy and total engine size.
The raw JSON-stat response is cached unchanged, hashed, and parsed into a tidy
country-year table. Aggregates (EU27, euro area, EFTA and similar) are dropped
because they are sums of the country series and would double count.

Run from the thesis directory:

    python3 tools/p01_panel_data.py
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

API = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "road_eqr_carmot?format=JSON&lang=EN"
)
RAW = Path("data/raw/eurostat_road_eqr_carmot.json")
OUT = Path("data/panel/p01_registrations_panel.csv")
COVERAGE = Path("data/panel/p01_panel_coverage.csv")
META = Path("data/panel/p01_panel_meta.json")

AGGREGATES = {
    "EU27_2020", "EU28", "EU25", "EU15", "EA20", "EA19", "EA18", "EA17",
    "EA16", "EA15", "EEA", "EFTA", "EU_EFTA", "EUR", "XK",
}


def download() -> bytes:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists():
        return RAW.read_bytes()
    with urllib.request.urlopen(API, timeout=120) as response:
        payload = response.read()
    RAW.write_bytes(payload)
    return payload


def parse(payload: bytes) -> pd.DataFrame:
    data = json.loads(payload)
    dims = data["dimension"]
    order = data["id"]
    sizes = data["size"]
    values = data["value"]

    def labels(name: str) -> dict[str, str]:
        return dims[name]["category"]["label"]

    geo_labels = labels("geo")
    time_labels = labels("time")
    mot_labels = labels("mot_nrg")
    engine_labels = labels("engine")

    # Linear index over the dimension order declared in the file.
    strides = []
    acc = 1
    for size in reversed(sizes):
        strides.append(acc)
        acc *= size
    strides = list(reversed(strides))
    position = {name: i for i, name in enumerate(order)}

    rows = []
    for key, value in values.items():
        idx = int(key)
        coords = {}
        remainder = idx
        for name, size, stride in zip(order, sizes, strides):
            coords[name] = remainder // stride
            remainder %= stride
        geo = list(geo_labels)[coords["geo"]]
        year = int(list(time_labels)[coords["time"]])
        mot = list(mot_labels)[coords["mot_nrg"]]
        engine = list(engine_labels)[coords["engine"]]
        if mot != "TOTAL" or engine != "TOTAL":
            continue
        if geo in AGGREGATES:
            continue
        rows.append(
            {
                "geo": geo,
                "country": geo_labels[geo],
                "year": year,
                "registrations": float(value),
            }
        )
    frame = pd.DataFrame(rows).sort_values(["geo", "year"]).reset_index(drop=True)
    return frame


def main() -> None:
    payload = download()
    frame = parse(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False)

    coverage = (
        frame.groupby(["geo", "country"])
        .agg(first_year=("year", "min"), last_year=("year", "max"), years=("year", "size"))
        .reset_index()
        .sort_values(["first_year", "geo"])
    )
    coverage.to_csv(COVERAGE, index=False)

    digest = hashlib.sha256(payload).hexdigest()
    meta = {
        "dataset": "road_eqr_carmot",
        "title": "New passenger cars by type of motor energy and engine size",
        "publisher": "Eurostat",
        "endpoint": API,
        "retrieved": date.today().isoformat(),
        "sha256_raw": digest,
        "rows": int(len(frame)),
        "countries": int(frame["geo"].nunique()),
        "first_year": int(frame["year"].min()),
        "last_year": int(frame["year"].max()),
        "note": "Total motor energy, total engine size, aggregates removed.",
    }
    META.write_text(json.dumps(meta, indent=2) + "\n")

    print(f"rows {len(frame)}, countries {frame['geo'].nunique()}, years {frame['year'].min()} to {frame['year'].max()}")
    print(f"sha256 {digest}")
    print(coverage.to_string(index=False))


if __name__ == "__main__":
    main()
