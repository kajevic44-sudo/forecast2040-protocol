"""Tests for the panel builder."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from forecast2040.config import Settings
from forecast2040.panel import (
    ANNUAL,
    DAILY,
    MONTHLY,
    PanelError,
    Series,
    build_panel,
    build_span,
    codebook_rows,
    infer_freq,
    load_raw,
    parse_value,
    read_series,
    write_panels,
)


def _write(path: Path, header: list[str], rows: list[list[str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    return path


def _settings(raw_dir: Path) -> Settings:
    return Settings(
        raw_dir=raw_dir,
        manifest_path=raw_dir.parent / "manifest.csv",
        user_agent="test",
        timeout_s=1,
        max_retries=1,
        backoff_s=0.0,
        sources=(),
    )


def test_infer_freq_recognises_both_shapes() -> None:
    assert infer_freq("2024") == ANNUAL
    assert infer_freq("2024-07") == MONTHLY


def test_infer_freq_rejects_quarters() -> None:
    with pytest.raises(PanelError):
        infer_freq("2024-Q1")


@pytest.mark.parametrize("raw", ["", " ", "..", "NA", "null", None])
def test_parse_value_treats_missing_markers_as_none(raw: str | None) -> None:
    assert parse_value(raw) is None


def test_parse_value_reads_numbers_and_negatives() -> None:
    assert parse_value("12.5") == 12.5
    assert parse_value("-3") == -3.0


def test_parse_value_rejects_text() -> None:
    with pytest.raises(PanelError):
        parse_value("high")


def test_read_series_drops_missing_and_keeps_order(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "worldbank_deu_gdp.csv",
        ["time", "value"],
        [["2020", "100"], ["2021", ""], ["2022", "120"]],
    )
    series = read_series(path)
    assert series.id == "worldbank_deu_gdp"
    assert series.freq == ANNUAL
    assert series.values == {"2020": 100.0, "2022": 120.0}


def test_read_series_rejects_mixed_frequencies(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "broken.csv",
        ["time", "value"],
        [["2020", "1"], ["2020-01", "2"]],
    )
    with pytest.raises(PanelError):
        read_series(path)


def test_read_series_requires_time_and_value(tmp_path: Path) -> None:
    path = _write(tmp_path / "other.csv", ["period", "amount"], [["2020", "1"]])
    with pytest.raises(PanelError):
        read_series(path)


def test_build_panel_aligns_on_the_union_of_periods() -> None:
    series = (
        Series(id="a", freq=ANNUAL, values={"2020": 1.0, "2021": 2.0}),
        Series(id="b", freq=ANNUAL, values={"2021": 3.0, "2022": 4.0}),
        Series(id="m", freq=MONTHLY, values={"2020-01": 9.0}),
    )
    periods, columns = build_panel(series, ANNUAL)
    assert periods == ["2020", "2021", "2022"]
    assert set(columns) == {"a", "b"}
    assert columns["a"]["2021"] == 2.0
    assert "2022" not in columns["a"]


def test_build_span_counts_gaps_across_a_year_boundary() -> None:
    assert build_span(MONTHLY, "2020-11", "2021-02") == [
        "2020-11",
        "2020-12",
        "2021-01",
        "2021-02",
    ]
    assert build_span(ANNUAL, "2019", "2021") == ["2019", "2020", "2021"]


def test_read_series_accepts_the_worldbank_year_column(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "worldbank_deu_gdp.csv",
        ["country", "iso3", "indicator", "year", "value"],
        [["Germany", "DEU", "GDP", "2020", "3887.0"]],
    )
    series = read_series(path)
    assert series.values == {"2020": 3887.0}
    assert series.freq == ANNUAL


def test_read_series_accepts_the_yahoo_timestamp_and_close(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "yahoo_vow3.csv",
        ["timestamp", "open", "close", "volume"],
        [["2026-11-20 08:00:00+00:00", "90", "91.5", "1000"]],
    )
    series = read_series(path)
    assert series.values == {"2026-11-20": 91.5}
    assert series.freq == DAILY


def test_build_span_counts_days_inclusively() -> None:
    assert build_span(DAILY, "2026-11-20", "2026-11-23") == [
        "2026-11-20",
        "2026-11-21",
        "2026-11-22",
        "2026-11-23",
    ]


def test_codebook_reports_missing_share() -> None:
    series = (Series(id="a", freq=ANNUAL, values={"2020": 1.0, "2022": 2.0}),)
    row = codebook_rows(series)[0]
    assert row["span"] == "3"
    assert row["observations"] == "2"
    assert row["missing_share"] == "0.3333"


def test_load_raw_is_stable_and_rejects_empty_directory(tmp_path: Path) -> None:
    _write(tmp_path / "b.csv", ["time", "value"], [["2020", "1"]])
    _write(tmp_path / "a.csv", ["time", "value"], [["2020", "2"]])
    assert [item.id for item in load_raw(tmp_path)] == ["a", "b"]
    with pytest.raises(PanelError):
        load_raw(tmp_path / "missing")


def test_write_panels_produces_two_panels_and_a_codebook(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write(raw / "annual.csv", ["time", "value"], [["2020", "1"], ["2021", "2"]])
    _write(raw / "monthly.csv", ["time", "value"], [["2020-01", "5"]])
    written = write_panels(_settings(raw), out_dir=tmp_path / "panel")
    assert [path.name for path in written] == [
        "panel_monthly.csv",
        "panel_annual.csv",
        "codebook.csv",
    ]
    with (tmp_path / "panel" / "panel_annual.csv").open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["period", "annual"]
    assert rows[1] == ["2020", "1.0"]
    with (tmp_path / "panel" / "codebook.csv").open(encoding="utf-8") as handle:
        codebook = list(csv.DictReader(handle))
    assert {row["id"] for row in codebook} == {"annual", "monthly"}
