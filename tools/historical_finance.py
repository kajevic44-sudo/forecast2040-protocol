"""Convert the long-run financial datasets into tidy annual series.

Three public sources feed this script:

* Jordà, Schularick and Taylor, Macrohistory Database R6, 18 countries from
  1870, annual, equity total returns and crisis dates included.
* Shiller, online data set, United States from 1871, monthly prices, dividends,
  earnings, CPI and the cyclically adjusted price earnings ratio.
* Kenneth French, Fama-French research factors, United States from 1926,
  monthly market excess return, size and value factors, risk free rate.

The output is deliberately small and rectangular: one row per country and
year, one row per year for the single country series. Provenance for every
downloaded file is written next to the data, because a long-run series without
its download date cannot be reproduced.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HIST = ROOT / "data" / "historical"
OUT = ROOT / "data" / "historical" / "tidy"

SOURCES: dict[str, str] = {
    "JSTdatasetR6.xlsx": (
        "https://www.macrohistory.net/app/download/9834512569/JSTdatasetR6.xlsx"
    ),
    "shiller_ie_data.xls": "http://www.econ.yale.edu/~shiller/data/ie_data.xls",
    "ff_factors.zip": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Research_Data_Factors_CSV.zip"
    ),
}

JST_COLUMNS: tuple[str, ...] = (
    "year",
    "country",
    "iso",
    "eq_tr",
    "eq_capgain",
    "eq_dp",
    "eq_div_rtn",
    "crisisJST",
    "debtgdp",
    "stir",
    "ltrate",
    "rgdpmad",
    "pop",
    "cpi",
    "unemp",
    "hpnom",
    "tloans",
    "lev",
    "capital_tr",
    "risky_tr",
    "safe_tr",
    "housing_tr",
    "bond_tr",
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_provenance() -> pd.DataFrame:
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for name, url in SOURCES.items():
        path = HIST / name
        if not path.exists():
            continue
        rows.append(
            {
                "file": name,
                "url": url,
                "bytes": path.stat().st_size,
                "sha256": sha256_of(path),
                "downloaded_utc": stamp,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(HIST / "historical_manifest.csv", index=False)
    return frame


def convert_jst() -> pd.DataFrame:
    raw = pd.read_excel(HIST / "JSTdatasetR6.xlsx", sheet_name=0)
    missing = [c for c in JST_COLUMNS if c not in raw.columns]
    if missing:
        raise SystemExit(f"JST file is missing columns: {missing}")
    frame = raw[list(JST_COLUMNS)].copy()
    frame["year"] = frame["year"].astype(int)
    frame = frame.sort_values(["country", "year"]).reset_index(drop=True)
    frame.to_csv(OUT / "jst_panel.csv", index=False)
    germany = frame[frame["iso"] == "DEU"].reset_index(drop=True)
    germany.to_csv(OUT / "jst_germany.csv", index=False)
    return frame


def _shiller_frame() -> pd.DataFrame:
    raw = pd.read_excel(HIST / "shiller_ie_data.xls", sheet_name="Data", header=None)
    header_row = None
    for index in range(raw.shape[0]):
        first = str(raw.iloc[index, 0]).strip()
        if first.lower() == "date":
            header_row = index
            break
    if header_row is None:
        raise SystemExit("Shiller sheet has no Date header row")
    frame = raw.iloc[header_row + 1 :].copy()
    frame.columns = [str(c).strip() for c in raw.iloc[header_row]]
    if "PE10" not in frame.columns and "CAPE" in frame.columns:
        frame = frame.rename(columns={"CAPE": "PE10"})
    frame = frame.rename(columns={"Date": "date_raw"})
    frame = frame[frame["date_raw"].notna()]
    frame["year"] = frame["date_raw"].astype(float).floordiv(1).astype(int)
    for column in ("P", "D", "E", "CPI", "PE10", "GS10"):
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame[frame["year"] >= 1871]
    return frame


def convert_shiller() -> pd.DataFrame:
    frame = _shiller_frame()
    annual = (
        frame.groupby("year", as_index=False)
        .agg(
            price_nominal=("P", "mean"),
            dividend_nominal=("D", "mean"),
            earnings_nominal=("E", "mean"),
            cpi=("CPI", "mean"),
            cape=("PE10", "mean"),
        )
        .sort_values("year")
    )
    annual["price_real"] = annual["price_nominal"] / annual["cpi"]
    annual["dividend_real"] = annual["dividend_nominal"] / annual["cpi"]
    annual["return_real"] = (
        (annual["price_real"] + annual["dividend_real"]) / annual["price_real"].shift(1) - 1.0
    )
    annual = annual[annual["year"] <= 2025].reset_index(drop=True)
    annual.round(4).to_csv(OUT / "shiller_annual.csv", index=False)
    return annual


def convert_french() -> pd.DataFrame:
    archive = zipfile.ZipFile(io.BytesIO((HIST / "ff_factors.zip").read_bytes()))
    name = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
    text = archive.read(name).decode("latin-1")
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().startswith(","))
    body: list[str] = []
    for line in lines[start:]:
        token = line.split(",")[0].strip()
        if len(token) == 6 and token.isdigit():
            body.append(line)
        elif body:
            break
    frame = pd.read_csv(io.StringIO("\n".join(body)), header=None)
    frame.columns = ["yyyymm", "mkt_rf", "smb", "hml", "rf"]
    for column in ("mkt_rf", "smb", "hml", "rf"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce") / 100.0
    frame["year"] = (frame["yyyymm"] // 100).astype(int)
    annual = frame.groupby("year", as_index=False).agg(
        market_excess=("mkt_rf", lambda s: float((1.0 + s).prod() - 1.0)),
        smb=("smb", lambda s: float((1.0 + s).prod() - 1.0)),
        hml=("hml", lambda s: float((1.0 + s).prod() - 1.0)),
        risk_free=("rf", lambda s: float((1.0 + s).prod() - 1.0)),
        months=("rf", "size"),
    )
    annual = annual[annual["months"] == 12].drop(columns=["months"]).reset_index(drop=True)
    annual.round(4).to_csv(OUT / "ff_factors_annual.csv", index=False)
    return annual


def german_crisis_years(jst: pd.DataFrame) -> list[int]:
    germany = jst[(jst["iso"] == "DEU") & (jst["crisisJST"] == 1)]
    return sorted(int(y) for y in germany["year"].tolist())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = write_provenance()
    jst = convert_jst()
    shiller = convert_shiller()
    french = convert_french()
    crises = german_crisis_years(jst)
    print(f"jst rows {len(jst):5d}  countries {jst['iso'].nunique():2d}  "
          f"years {jst['year'].min()} to {jst['year'].max()}")
    print(f"shiller rows {len(shiller):4d}  years {shiller['year'].min()} to "
          f"{shiller['year'].max()}")
    print(f"french rows {len(french):4d}  years {french['year'].min()} to "
          f"{french['year'].max()}")
    print(f"german crisis years {len(crises)}: {crises}")
    print(f"provenance rows {len(manifest)} written to {HIST / 'historical_manifest.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
