"""Provenance manifest.

Every downloaded file is recorded with its hash, size, row count, source URL and
the UTC timestamp of the download. The manifest is the audit trail: any table in
the dissertation can be traced back to the exact bytes it was built from.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

FIELDS = (
    "fetched_at_utc",
    "source_id",
    "url",
    "path",
    "sha256",
    "size_bytes",
    "rows",
)


@dataclass(frozen=True, slots=True)
class Record:
    """One line of the manifest."""

    fetched_at_utc: str
    source_id: str
    url: str
    path: str
    sha256: str
    size_bytes: int
    rows: int


def utc_now() -> str:
    """ISO 8601 timestamp in UTC, seconds precision."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    """Hash a file without loading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_record(manifest_path: Path, record: Record) -> None:
    """Append one record, writing the header on first use."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not manifest_path.exists()
    with manifest_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(asdict(record))


def read_manifest(manifest_path: Path) -> list[Record]:
    """Read the manifest, returning an empty list when it does not exist."""
    if not manifest_path.exists():
        return []
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        return [
            Record(
                fetched_at_utc=row["fetched_at_utc"],
                source_id=row["source_id"],
                url=row["url"],
                path=row["path"],
                sha256=row["sha256"],
                size_bytes=int(row["size_bytes"]),
                rows=int(row["rows"]),
            )
            for row in csv.DictReader(handle)
        ]


def build_record(source_id: str, url: str, path: Path, rows: int) -> Record:
    """Assemble a record from a finished file."""
    return Record(
        fetched_at_utc=utc_now(),
        source_id=source_id,
        url=url,
        path=str(path),
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
        rows=rows,
    )
