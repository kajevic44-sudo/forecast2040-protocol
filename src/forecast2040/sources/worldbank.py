"""World Bank Indicators API.

Response shape: [metadata, rows] where each row carries country, indicator,
date and value. The parser is pure so that it can be tested without a network.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from ..config import Settings, Source
from ..http import FetchError, get_json

COLUMNS = ("country", "iso3", "indicator", "year", "value")


def parse(payload: Any) -> pd.DataFrame:
    """Turn the World Bank JSON payload into a tidy frame."""
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("unexpected World Bank payload")
    rows = payload[1]
    if not isinstance(rows, list) or not rows:
        raise ValueError("World Bank returned no observations")

    records: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        records.append(
            {
                "country": row["country"]["value"],
                "iso3": row["countryiso3code"],
                "indicator": row["indicator"]["value"],
                "year": int(row["date"]),
                "value": row["value"],
            }
        )
    frame = pd.DataFrame.from_records(records, columns=list(COLUMNS))
    return frame.sort_values("year").reset_index(drop=True)


def fetch(settings: Settings, source: Source, session: requests.Session) -> pd.DataFrame:
    """Download one indicator for one country."""
    payload = get_json(
        session,
        source.url(),
        params={"format": "json", "per_page": "20000"},
        timeout=settings.timeout_s,
    )
    frame = parse(payload)
    if frame["value"].isna().all():
        raise FetchError(f"{source.id}: all observations are empty")
    return frame
