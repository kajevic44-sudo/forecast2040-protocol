"""Dispatch table between the registry and the fetchers.

A fetch is complete only when two things exist: the CSV in data/raw and the
manifest row that describes it. If the file is written but the manifest row is
not, the run is considered failed, because provenance would be broken.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import pandas as pd
import requests

from ..config import Settings, Source
from ..http import FetchError, build_session
from ..manifest import append_record, build_record
from . import csv_direct, eurostat, stooq, worldbank, yahoo

Fetcher = Callable[[Settings, Source, requests.Session], pd.DataFrame]

FETCHERS: dict[str, Fetcher] = {
    "worldbank": worldbank.fetch,
    "eurostat": eurostat.fetch,
    "stooq": stooq.fetch,
    "yahoo": yahoo.fetch,
    "csv": csv_direct.fetch,
}


def fetch_source(
    settings: Settings,
    source: Source,
    session: requests.Session | None = None,
) -> Path:
    """Download one source, write it to data/raw and record provenance."""
    if source.kind not in FETCHERS:
        raise FetchError(f"{source.id}: no fetcher for kind {source.kind!r}")

    own_session = session is None
    active = session or build_session(settings)
    try:
        frame = FETCHERS[source.kind](settings, source, active)
    finally:
        if own_session:
            active.close()

    if frame.empty:
        raise FetchError(f"{source.id}: no rows returned")

    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    target = settings.raw_dir / f"{source.id}.csv"
    frame.to_csv(target, index=False)
    append_record(
        settings.manifest_path,
        build_record(source.id, source.url(), target, len(frame)),
    )
    return target


def fetch_many(
    settings: Settings,
    sources: Sequence[Source],
) -> list[tuple[Source, Path | None, str | None]]:
    """Fetch several sources, collecting failures instead of stopping.

    Returns one tuple per source: the source, the written path when it worked,
    and the error message when it did not.
    """
    results: list[tuple[Source, Path | None, str | None]] = []
    session = build_session(settings)
    try:
        for source in sources:
            try:
                path = fetch_source(settings, source, session)
            except (FetchError, ValueError) as exc:
                results.append((source, None, str(exc)))
            else:
                results.append((source, path, None))
    finally:
        session.close()
    return results
