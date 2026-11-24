"""Download KBA FZ 28 yearly files and extract the monthly drive type series.

Sheet FZ 28.2 holds new registrations by month with three columns of interest:
total, all electric drives (battery plus plug-in hybrid), and battery electric
only. The two electric columns are kept apart, because merging them overstates
the battery share by roughly a quarter.

Usage:
    python tools/kba_fz28.py 2021 2026
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import openpyxl
import requests

BASE = "https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ28"
SHEET = "FZ 28.2"
MONTHS = {
    "Januar": 1,
    "Februar": 2,
    "Marz": 3,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}
DATA = Path(__file__).resolve().parents[1] / "data" / "raw"
HEADERS = {"User-Agent": "Mozilla/5.0 (research)"}


def fetch(year: int, month: int) -> bytes | None:
    url = f"{BASE}/fz28_{year}_{month:02d}.xlsx?__blob=publicationFile"
    response = requests.get(url, headers=HEADERS, timeout=60)
    if response.status_code != 200 or len(response.content) < 10000:
        return None
    if not response.content.startswith(b"PK"):
        return None
    return response.content


def parse(payload: bytes, year: int) -> list[tuple[str, int, int, int]]:
    """Read FZ 28.2, tracking the year marker that precedes each month block."""
    workbook = openpyxl.load_workbook(io.BytesIO(payload), read_only=True, data_only=True)
    if SHEET not in workbook.sheetnames:
        return []
    rows: list[tuple[str, int, int, int]] = []
    current = year
    for row in workbook[SHEET].iter_rows(max_col=8, values_only=True):
        if not row or len(row) < 7:
            continue
        label = str(row[1]).strip() if row[1] is not None else ""
        if label.startswith("Jahr "):
            digits = "".join(ch for ch in label[5:9] if ch.isdigit())
            if len(digits) == 4:
                current = int(digits)
            continue
        month = MONTHS.get(label)
        if month is None:
            continue
        try:
            total = int(float(row[2]))
            electric = int(float(row[5]))
            bev = int(float(row[7])) if row[7] is not None else 0
        except (TypeError, ValueError):
            continue
        rows.append((f"{current}-{month:02d}", total, electric, bev))
    return rows


def main(argv: list[str]) -> int:
    first = int(argv[1]) if len(argv) > 1 else 2021
    last = int(argv[2]) if len(argv) > 2 else 2026
    collected: dict[str, tuple[int, int, int]] = {}
    for year in range(first, last + 1):
        payload = None
        for month in (12, 11, 10):
            payload = fetch(year, month)
            if payload is not None:
                break
        if payload is None:
            print(f"{year}: no file")
            continue
        try:
            rows = parse(payload, year)
        except Exception as exc:
            print(f"{year}: unreadable ({type(exc).__name__})")
            continue
        for period, total, electric, bev in rows:
            collected[period] = (total, electric, bev)
        print(f"{year}: {len(rows)} months")

    DATA.mkdir(parents=True, exist_ok=True)
    full = DATA / "kba_fz28_months.csv"
    with full.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["period", "total", "electric_drives", "bev"])
        for period in sorted(collected):
            writer.writerow([period, *collected[period]])

    for column, name in ((1, "kba_electric_drives"), (2, "kba_bev")):
        path = DATA / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["time", "value"])
            for period in sorted(collected):
                writer.writerow([period, collected[period][column]])

    print(f"written {len(collected)} months to {full}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
