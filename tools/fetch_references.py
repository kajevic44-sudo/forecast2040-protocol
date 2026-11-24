"""Fetch bibliographic metadata from Crossref so that no citation is invented.

Each entry is looked up by DOI. The script writes data/references.csv with the
fields the paper needs and prints any DOI that failed, so a failure is visible
instead of being replaced by a plausible guess.

Run with /usr/bin/python3 tools/fetch_references.py
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "references.csv"

DOIS = {
    "hyndman2006": "10.1016/j.ijforecast.2006.03.001",
    "diebold1995": "10.1080/07350015.1995.10524599",
    "harvey1997": "10.1016/S0169-2070(96)00719-4",
    "clark2007": "10.1016/j.jeconom.2006.05.023",
    "giacomini2006": "10.1111/j.1468-0262.2006.00685.x",
    "timmermann2006": "10.1016/S1574-0706(05)01004-9",
    "gneiting2014": "10.1146/annurev-statistics-062713-085831",
    "tashman2000": "10.1016/S0169-2070(00)00065-0",
    "bergmeir2012": "10.1016/j.ins.2011.12.028",
    "bergmeir2018": "10.1016/j.csda.2018.03.002",
    "cerqueira2020": "10.1007/s10618-020-00707-7",
    "makridakis2018": "10.1016/j.ijforecast.2019.04.014",
    "makridakis2000": "10.1016/S0169-2070(00)00057-1",
    "meese1983": "10.1016/0304-3932(83)90017-7",
    "stock1998": "10.1016/S0304-4076(97)00097-3",
    "breiman2001": "10.1023/A:1010933404324",
    "friedman2001": "10.1214/aos/1013203451",
    "hoerl1970": "10.1080/00401706.1970.10488634",
    "gardner1985": "10.1287/mnsc.31.10.1237",
    "nosek2018": "10.1073/pnas.1708274114",
    "simmons2011": "10.1177/0956797611417632",
    "gelman2014": "10.1511/2014.111.460",
    "munafo2017": "10.1038/s41562-016-0021",
    "peng2011": "10.1126/science.1213847",
    "baker2016": "10.1038/533452a",
    "christensen2018": "10.1126/science.aar5147",
    "demoura2021": "10.1007/978-3-030-79876-5_37",
    "mathlib2020": "10.1145/3372885.3373824",
    "sturgeon2008": "10.1093/jeg/lbn007",
    "teece2010": "10.1016/j.lrp.2009.07.003",
    "klein2008": "10.1016/j.ijforecast.2008.03.004",
    "hyndman2010": "10.1016/j.ijforecast.2009.10.006",
    "kolassa2011": "10.1016/j.ijforecast.2010.05.005",
    "fildes2011": "10.1016/j.ijforecast.2010.04.007",
    "goodwin2011": "10.1016/j.ijforecast.2010.04.009",
    "lawrence2000": "10.1016/S0169-2070(00)00066-2",
    "ord2007": "10.1016/j.ijforecast.2007.07.002",
}


def fetch(doi: str) -> dict | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    request = urllib.request.Request(url, headers={"User-Agent": "forecast2040/1.0 (mailto:armin@example.org)"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["message"]
    except Exception as exc:  # noqa: BLE001
        print("FAILED", doi, exc, file=sys.stderr)
        return None


def main() -> int:
    rows = []
    for key, doi in DOIS.items():
        msg = fetch(doi)
        if not msg:
            continue
        authors = []
        for a in msg.get("author", []):
            given = a.get("given", "")
            family = a.get("family", "")
            authors.append(f"{given} {family}".strip())
        year = ""
        for field in ("published-print", "published-online", "issued", "created"):
            parts = msg.get(field, {}).get("date-parts", [[None]])
            if parts and parts[0] and parts[0][0]:
                year = str(parts[0][0])
                break
        rows.append(
            {
                "key": key,
                "authors": "; ".join(authors),
                "title": (msg.get("title") or [""])[0],
                "container": (msg.get("container-title") or [""])[0],
                "volume": msg.get("volume", ""),
                "issue": msg.get("issue", ""),
                "year": year,
                "pages": msg.get("page", ""),
                "doi": doi,
                "publisher": msg.get("publisher", ""),
                "type": msg.get("type", ""),
            }
        )
        print("ok", key, year, len(authors))
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("saved", OUT, len(rows), "of", len(DOIS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
