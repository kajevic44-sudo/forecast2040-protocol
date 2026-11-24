"""Stooq daily price export.

The endpoint returns a CSV when the ticker is known and a short error line when
it is not, so the parser checks the header before reading.
"""

from __future__ import annotations

import io

import pandas as pd
import requests

from ..config import Settings, Source
from ..http import FetchError, get_text

EXPECTED = ("date", "open", "high", "low", "close", "volume")


def parse(text: str) -> pd.DataFrame:
    """Parse the CSV body into a frame with a parsed date column."""
    head = text.strip().splitlines()[0].lower() if text.strip() else ""
    if not head.startswith("date"):
        raise ValueError(f"unexpected Stooq response: {text[:80]!r}")
    frame = pd.read_csv(io.StringIO(text))
    frame.columns = [column.strip().lower() for column in frame.columns]
    missing = set(EXPECTED) - set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    return frame.sort_values("date").reset_index(drop=True)


def fetch(settings: Settings, source: Source, session: requests.Session) -> pd.DataFrame:
    """Download the full daily history for one ticker."""
    text = get_text(session, source.url(), timeout=settings.timeout_s)
    try:
        return parse(text)
    except ValueError as exc:
        raise FetchError(f"{source.id}: {exc}") from exc
