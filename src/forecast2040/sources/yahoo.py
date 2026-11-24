"""Yahoo Finance chart endpoint.

Used only for listed share prices, where Yahoo is the cheapest reproducible
source. The adjusted close is kept when present, because splits and dividends
matter for any return calculation.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from ..config import Settings, Source
from ..http import FetchError, get_json

QUOTE_FIELDS = ("open", "high", "low", "close", "volume")


def parse(payload: Any) -> pd.DataFrame:
    """Turn the chart JSON into a tidy frame indexed by UTC timestamp."""
    try:
        result = payload["chart"]["result"][0]
        stamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("unexpected Yahoo chart payload") from exc

    frame = pd.DataFrame({"timestamp": pd.to_datetime(stamps, unit="s", utc=True)})
    for field in QUOTE_FIELDS:
        frame[field] = quote.get(field)
    adjusted = result["indicators"].get("adjclose")
    if adjusted:
        frame["adjclose"] = adjusted[0].get("adjclose")
    return frame.sort_values("timestamp").reset_index(drop=True)


def fetch(settings: Settings, source: Source, session: requests.Session) -> pd.DataFrame:
    """Download the price history declared in the registry."""
    params = {
        "range": str(source.params.get("range", "10y")),
        "interval": str(source.params.get("interval", "1d")),
        "events": "div,splits",
    }
    payload = get_json(session, source.url(), params=params, timeout=settings.timeout_s)
    try:
        frame = parse(payload)
    except ValueError as exc:
        raise FetchError(f"{source.id}: {exc}") from exc
    if frame.empty:
        raise FetchError(f"{source.id}: empty price history")
    return frame
