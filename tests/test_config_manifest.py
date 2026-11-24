"""Tests for the registry and the provenance manifest. No network access."""

from __future__ import annotations

from pathlib import Path

import pytest

from forecast2040.config import ConfigError, load_settings
from forecast2040.manifest import Record, append_record, read_manifest, sha256_file


def test_registry_loads_and_ids_are_unique() -> None:
    settings = load_settings()
    ids = [source.id for source in settings.sources]
    assert ids, "registry must not be empty"
    assert len(ids) == len(set(ids))
    kinds = {"worldbank", "eurostat", "stooq", "yahoo", "csv"}
    assert all(source.kind in kinds for source in settings.sources)


def test_url_is_rendered_from_params() -> None:
    settings = load_settings()
    source = settings.source("worldbank_deu_gdp")
    assert source.url().endswith("/country/DEU/indicator/NY.GDP.MKTP.CD")


def test_unknown_source_raises() -> None:
    settings = load_settings()
    with pytest.raises(ConfigError):
        settings.source("does_not_exist")


def test_manifest_roundtrip(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    data = tmp_path / "x.csv"
    data.write_text("a,b\n1,2\n", encoding="utf-8")

    record = Record(
        fetched_at_utc="2026-11-23T12:00:00+00:00",
        source_id="demo",
        url="https://example.org/x.csv",
        path=str(data),
        sha256=sha256_file(data),
        size_bytes=data.stat().st_size,
        rows=1,
    )
    append_record(manifest, record)
    append_record(manifest, record)

    rows = read_manifest(manifest)
    assert len(rows) == 2
    assert rows[0].sha256 == record.sha256
    assert rows[0].rows == 1


def test_hash_changes_with_content(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("one", encoding="utf-8")
    second.write_text("two", encoding="utf-8")
    assert sha256_file(first) != sha256_file(second)
