"""Parser tests. Each payload is a small synthetic sample of the real shape."""

from __future__ import annotations

import pandas as pd
import pytest

from forecast2040.sources import eurostat, stooq, worldbank, yahoo


def test_worldbank_parse() -> None:
    payload = [
        {"page": 1},
        [
            {
                "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP"},
                "country": {"id": "DE", "value": "Germany"},
                "countryiso3code": "DEU",
                "date": "2025",
                "value": 4700000000000.0,
            },
            {
                "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP"},
                "country": {"id": "DE", "value": "Germany"},
                "countryiso3code": "DEU",
                "date": "2024",
                "value": 4600000000000.0,
            },
        ],
    ]
    frame = worldbank.parse(payload)
    assert list(frame.columns) == ["country", "iso3", "indicator", "year", "value"]
    assert frame["year"].tolist() == [2024, 2025]
    assert frame["value"].iloc[-1] == pytest.approx(4.7e12)


def test_worldbank_parse_rejects_empty() -> None:
    with pytest.raises(ValueError):
        worldbank.parse([{"page": 1}, []])


def test_eurostat_parse_monthly() -> None:
    payload = {
        "id": ["freq", "geo", "time"],
        "size": [1, 2, 2],
        "dimension": {
            "freq": {"category": {"index": {"M": 0}}},
            "geo": {"category": {"index": {"DE": 0, "FR": 1}}},
            "time": {"category": {"index": {"2026-01": 0, "2026-02": 1}}},
        },
        "value": {"0": 100.0, "1": 101.5, "2": 99.0, "3": 102.0},
    }
    frame = eurostat.parse(payload)
    assert len(frame) == 4
    assert set(frame["geo"]) == {"DE", "FR"}
    assert frame["date"].notna().all()
    de = frame[frame["geo"] == "DE"].sort_values("date")
    assert de["value"].tolist() == [100.0, 101.5]


def test_eurostat_parse_rejects_non_cube() -> None:
    with pytest.raises(ValueError):
        eurostat.parse({"error": "bad request"})


def test_stooq_parse() -> None:
    text = "Date,Open,High,Low,Close,Volume\n2026-11-20,90.1,91.0,89.5,90.8,1200000\n"
    frame = stooq.parse(text)
    assert len(frame) == 1
    assert frame["close"].iloc[0] == pytest.approx(90.8)
    assert isinstance(frame["date"].iloc[0], pd.Timestamp)


def test_stooq_parse_rejects_error_body() -> None:
    with pytest.raises(ValueError):
        stooq.parse("Brak danych")


def test_yahoo_parse() -> None:
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1763596800, 1763683200],
                    "indicators": {
                        "quote": [
                            {
                                "open": [90.0, 91.0],
                                "high": [91.0, 92.0],
                                "low": [89.0, 90.0],
                                "close": [90.5, 91.5],
                                "volume": [1000, 1100],
                            }
                        ],
                        "adjclose": [{"adjclose": [90.4, 91.4]}],
                    },
                }
            ]
        }
    }
    frame = yahoo.parse(payload)
    assert len(frame) == 2
    assert "adjclose" in frame.columns
    assert frame["close"].iloc[-1] == pytest.approx(91.5)


def test_yahoo_parse_rejects_error() -> None:
    with pytest.raises(ValueError):
        yahoo.parse({"chart": {"result": None, "error": {"code": "Not Found"}}})
