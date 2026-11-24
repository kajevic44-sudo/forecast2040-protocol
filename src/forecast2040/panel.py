"""Panel assembly from the raw series.

The raw directory holds one tidy CSV per source, each with a ``time`` column and
a ``value`` column. This module turns that set into two wide panels, monthly and
annual, plus a codebook that records coverage and licence for every column, so
that the panel can be described in the data chapter without reading the code.

The panel is a derived artefact. It is rebuilt from ``data/raw`` and never edited
by hand, which keeps the provenance chain intact: registry, download, hash,
panel.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .config import Settings

MONTHLY = "monthly"
ANNUAL = "annual"
DAILY = "daily"

_ANNUAL = re.compile(r"^\d{4}$")
_MONTHLY = re.compile(r"^\d{4}-\d{2}$")
_DAILY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MISSING = frozenset({"", ".", "..", "na", "n/a", "nan", "null", "none"})

# The fetchers write different column names for the same two ideas. The panel
# reader normalises them here, in one place, instead of in every caller.
_TIME_COLUMNS = ("time", "year", "date", "timestamp")
_VALUE_COLUMNS = ("value", "close", "adjclose")

CODEBOOK_FIELDS = (
    "id",
    "label",
    "licence",
    "frequency",
    "first_period",
    "last_period",
    "span",
    "observations",
    "missing_share",
)


class PanelError(ValueError):
    """Raised when a raw file cannot be turned into a series."""


@dataclass(frozen=True, slots=True)
class Series:
    """One raw series, identified by its file stem."""

    id: str
    freq: str
    values: Mapping[str, float]

    def first_period(self) -> str:
        return min(self.values)

    def last_period(self) -> str:
        return max(self.values)


def infer_freq(period: str) -> str:
    """Return the frequency implied by a period label."""
    if _ANNUAL.match(period):
        return ANNUAL
    if _MONTHLY.match(period):
        return MONTHLY
    if _DAILY.match(period):
        return DAILY
    raise PanelError(f"unrecognised period {period!r}")


def parse_value(raw: str | None) -> float | None:
    """Return a float, or None for the several spellings of a missing value."""
    if raw is None:
        return None
    text = raw.strip()
    if text.lower() in _MISSING:
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise PanelError(f"value {raw!r} is not numeric") from exc


def read_series(path: Path) -> Series:
    """Read one tidy CSV into a series, dropping missing observations."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        time_column = next((name for name in _TIME_COLUMNS if name in fields), None)
        value_column = next((name for name in _VALUE_COLUMNS if name in fields), None)
        if time_column is None or value_column is None:
            raise PanelError(
                f"{path.name}: needs one of {_TIME_COLUMNS} and one of {_VALUE_COLUMNS}"
            )
        values: dict[str, float] = {}
        freq: str | None = None
        for row in reader:
            period = (row.get(time_column) or "").strip()
            if not period:
                continue
            if time_column == "timestamp" and len(period) >= 10:
                period = period[:10]
            row_freq = infer_freq(period)
            if freq is None:
                freq = row_freq
            elif freq != row_freq:
                raise PanelError(f"{path.name}: mixed frequencies at {period}")
            value = parse_value(row.get(value_column))
            if value is not None:
                values[period] = value
    if freq is None:
        raise PanelError(f"{path.name}: no observations")
    return Series(id=path.stem, freq=freq, values=values)


def load_raw(raw_dir: Path) -> tuple[Series, ...]:
    """Read every CSV in the raw directory, in a stable order."""
    if not raw_dir.is_dir():
        raise PanelError(f"raw directory not found: {raw_dir}")
    series = [read_series(path) for path in sorted(raw_dir.glob("*.csv"))]
    if not series:
        raise PanelError(f"no CSV files in {raw_dir}")
    return tuple(series)


def build_panel(
    series: Sequence[Series], freq: str
) -> tuple[list[str], dict[str, dict[str, float]]]:
    """Align the series of one frequency on a common, sorted period axis."""
    selected = [item for item in series if item.freq == freq]
    periods: set[str] = set()
    for item in selected:
        periods.update(item.values)
    columns = {item.id: dict(item.values) for item in selected}
    return sorted(periods), columns


def write_panel(
    path: Path, periods: Sequence[str], columns: Mapping[str, Mapping[str, float]]
) -> None:
    """Write a wide panel with one row per period and one column per series."""
    path.parent.mkdir(parents=True, exist_ok=True)
    names = sorted(columns)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["period", *names])
        for period in periods:
            row = [period]
            for name in names:
                value = columns[name].get(period)
                row.append("" if value is None else repr(value))
            writer.writerow(row)


def codebook_rows(
    series: Sequence[Series], labels: Mapping[str, str] | None = None
) -> list[dict[str, str]]:
    """Describe every series, including the share of missing periods."""
    known = labels or {}
    rows: list[dict[str, str]] = []
    for item in sorted(series, key=lambda entry: entry.id):
        first, last = item.first_period(), item.last_period()
        span = len(build_span(item.freq, first, last))
        observations = len(item.values)
        missing = 1.0 - observations / span if span else 0.0
        rows.append(
            {
                "id": item.id,
                "label": known.get(item.id, ""),
                "licence": "",
                "frequency": item.freq,
                "first_period": first,
                "last_period": last,
                "span": str(span),
                "observations": str(observations),
                "missing_share": f"{missing:.4f}",
            }
        )
    return rows


def build_span(freq: str, first: str, last: str) -> list[str]:
    """Return every period label between two boundaries, inclusive."""
    if freq == ANNUAL:
        return [str(year) for year in range(int(first), int(last) + 1)]
    if freq == DAILY:
        start = date.fromisoformat(first)
        end = date.fromisoformat(last)
        days: list[str] = []
        current = start
        while current <= end:
            days.append(current.isoformat())
            current += timedelta(days=1)
        return days
    start_year, start_month = (int(part) for part in first.split("-"))
    end_year, end_month = (int(part) for part in last.split("-"))
    span: list[str] = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        span.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return span


def write_codebook(path: Path, rows: Sequence[Mapping[str, str]]) -> None:
    """Write the codebook that accompanies the panels."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CODEBOOK_FIELDS))
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))


def write_panels(settings: Settings, out_dir: Path | None = None) -> list[Path]:
    """Build both panels and the codebook, returning the files written."""
    target = out_dir or settings.raw_dir.parent / "panel"
    series = load_raw(settings.raw_dir)
    labels = {source.id: source.label for source in settings.sources}
    licences = {source.id: source.licence for source in settings.sources}

    written: list[Path] = []
    layouts = (
        (MONTHLY, "panel_monthly.csv"),
        (ANNUAL, "panel_annual.csv"),
        (DAILY, "panel_daily.csv"),
    )
    for freq, name in layouts:
        if not any(item.freq == freq for item in series):
            continue
        periods, columns = build_panel(series, freq)
        path = target / name
        write_panel(path, periods, columns)
        written.append(path)

    rows = codebook_rows(series, labels)
    for row in rows:
        row["licence"] = licences.get(row["id"], "")
    path = target / "codebook.csv"
    write_codebook(path, rows)
    written.append(path)
    return written
