"""Fetch a table from an endpoint that returns CSV without a key.

Many statistical offices publish a stable CSV address that needs no
registration. This fetcher keeps those sources inside the same provenance
pipeline as the API sources, so a direct download is recorded exactly like a
keyed one. Separator detection is explicit because European files frequently
use a semicolon.
"""

from __future__ import annotations

import io

import pandas as pd
import requests

from ..config import Settings, Source
from ..http import FetchError

SEPARATORS: tuple[str, ...] = (",", ";", "\t")


def fetch(settings: Settings, source: Source, session: requests.Session) -> pd.DataFrame:
    response = session.get(source.url(), timeout=90)
    if response.status_code != 200:
        raise FetchError(f"{source.id}: HTTP {response.status_code}")
    text = response.text.strip()
    if not text:
        raise FetchError(f"{source.id}: empty response")
    if text[0] == "<":
        raise FetchError(f"{source.id}: response is HTML, not a table")
    last_error: Exception | None = None
    for separator in SEPARATORS:
        try:
            frame = pd.read_csv(io.StringIO(text), sep=separator, engine="python")
        except Exception as exc:
            last_error = exc
            continue
        if frame.shape[1] > 1 and len(frame) > 1:
            if frame.shape[1] == 2:
                frame.columns = ["time", "value"]
            return frame
    raise FetchError(f"{source.id}: no tabular content, last error {last_error}")
