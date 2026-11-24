"""Eurostat dissemination API, JSON-stat 2.0.

The response is a multidimensional cube flattened into a dictionary keyed by a
row-major index. The decoder below turns any cube of up to five dimensions back
into a tidy frame, which keeps the fetcher independent of the dataset.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
import requests

from ..config import Settings, Source
from ..http import FetchError, get_json


def _labels(payload: Mapping[str, Any], dim: str) -> list[str]:
    """Return the category labels of one dimension, ordered by position."""
    category = payload["dimension"][dim]["category"]
    index = category.get("index")
    if isinstance(index, dict):
        ordered: list[str | None] = [None] * len(index)
        for name, position in index.items():
            ordered[int(position)] = str(name)
        return [name if name is not None else "" for name in ordered]
    if isinstance(index, list):
        return [str(name) for name in index]
    labels = category.get("label")
    if isinstance(labels, dict):
        return [str(labels[str(i)]) for i in range(len(labels))]
    raise ValueError(f"cannot read categories of dimension {dim!r}")


def _unravel(flat: int, sizes: Sequence[int]) -> list[int]:
    """Convert a row-major flat index into per-dimension positions."""
    positions: list[int] = []
    remainder = flat
    for size in reversed(sizes):
        positions.append(remainder % size)
        remainder //= size
    return list(reversed(positions))


def parse(payload: Mapping[str, Any]) -> pd.DataFrame:
    """Decode a JSON-stat 2.0 cube into a tidy frame with a value column."""
    try:
        dims = [str(d) for d in payload["id"]]
        sizes = [int(s) for s in payload["size"]]
        values = payload["value"]
    except (KeyError, TypeError) as exc:
        raise ValueError("not a JSON-stat cube") from exc
    if not isinstance(values, dict):
        raise ValueError("only dictionary-valued cubes are supported")

    labels = [_labels(payload, dim) for dim in dims]
    records: list[dict[str, Any]] = []
    for key, value in values.items():
        positions = _unravel(int(key), sizes)
        record: dict[str, Any] = {
            dim: labels[i][position]
            for i, (dim, position) in enumerate(zip(dims, positions, strict=True))
        }
        record["value"] = value
        records.append(record)

    frame = pd.DataFrame.from_records(records)
    if "time" in frame.columns:
        frame["date"] = _parse_time(frame["time"])
        frame = frame.sort_values("date").reset_index(drop=True)
    return frame


def _quarter_start(label: str) -> str | None:
    """Map a label such as 2026-Q3 to the first day of that quarter."""
    match = re.fullmatch(r"(\d{4})-Q([1-4])", label)
    if match is None:
        return None
    year, quarter = match.group(1), int(match.group(2))
    return f"{year}-{(quarter - 1) * 3 + 1:02d}-01"


def _parse_time(series: pd.Series) -> pd.Series:
    """Parse monthly, quarterly and annual Eurostat labels into timestamps."""
    text = series.astype(str)
    monthly = pd.to_datetime(text, format="%Y-%m", errors="coerce")
    quarterly = pd.to_datetime(text.map(_quarter_start), errors="coerce")
    annual = pd.to_datetime(text, format="%Y", errors="coerce")
    return monthly.fillna(quarterly).fillna(annual)


def fetch(settings: Settings, source: Source, session: requests.Session) -> pd.DataFrame:
    """Download one dataset with the filters declared in the registry."""
    query = source.params.get("query", {})
    if not isinstance(query, dict):
        raise FetchError(f"{source.id}: 'query' must be a mapping")
    params: dict[str, Any] = {"format": "JSON", "lang": "EN"}
    params.update({str(k): str(v) for k, v in query.items()})
    payload = get_json(session, source.url(), params=params, timeout=settings.timeout_s)
    frame = parse(payload)
    if frame.empty:
        raise FetchError(f"{source.id}: empty cube")
    return frame
