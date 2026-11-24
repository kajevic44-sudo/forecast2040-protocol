"""Proof of the footnote pipeline: Chicago notes at the bottom of the page.

WeasyPrint lays out the page and moves every element with `float: footnote` into
the footnote area of the page on which its call falls, which is what Chromium
cannot do. This script renders a short excerpt of chapter 5 with seven notes:
four full citations on first use and three short forms on later use, exactly the
pattern required by the Chicago notes and bibliography style.

Run with /usr/bin/python3 tools/footnote_sample.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
CITATIONS = ROOT / "data" / "citations.csv"
OUT = ROOT / "docs" / "FOOTNOTE_SAMPLE.pdf"

CSS = """
@page {
  size: A4;
  margin: 24mm 22mm 26mm 22mm;
  @bottom-center { content: counter(page); font-family: "Liberation Sans"; font-size: 9pt; color: #5F6E75; }
  @footnote { border-top: 0.5pt solid #C9D2D5; padding-top: 4pt; margin-top: 8pt; }
}
body { font-family: "Liberation Serif", Georgia, serif; font-size: 11.5pt; line-height: 1.6;
       color: #1B1F22; text-align: justify; hyphens: manual; }
h1 { font-family: "Liberation Sans"; font-size: 18pt; color: #10233F; margin: 0 0 10pt 0; }
h2 { font-family: "Liberation Sans"; font-size: 12.5pt; color: #10233F; margin: 14pt 0 6pt 0; }
p { margin: 0 0 6pt 0; }
.fn { float: footnote; font-size: 8.3pt; line-height: 1.35; text-align: left; }
::footnote-call { content: counter(footnote); vertical-align: super; font-size: 65%; color: #0E6B66; }
::footnote-marker { content: counter(footnote) ". "; color: #0E6B66; }
.note { color: #5F6E75; font-size: 9pt; }
"""


def load() -> dict[str, dict[str, str]]:
    with CITATIONS.open() as f:
        return {row["key"]: row for row in csv.DictReader(f)}


def full(row: dict[str, str]) -> str:
    author = row["author"]
    title = row["title"]
    container = row["container"]
    if container in ("GENESIS-Online", ""):
        return f'{author}, {title} (Destatis, {row["year"]}), accessed {row["accessed"]}.'
    vol = row["volume"]
    issue = row["issue"]
    year = row["year"]
    pages = row["pages"]
    if container == "Proceedings of the National Academy of Sciences":
        return f'{author}, "{title}," {container} {vol}, no. {issue} ({year}): {pages}.'
    return f'{author}, "{title}," {container} {vol}, no. {issue} ({year}): {pages}.'


def short(row: dict[str, str], page: str = "") -> str:
    base = row["short"]
    return f'{base}, {page}.' if page else f'{base}.'


def note(key: str, data: dict[str, dict[str, str]], page: str = "") -> str:
    row = data[key]
    body = full(row) if not page else short(row, page)
    return f'<span class="fn">{body}</span>'


def main() -> int:
    data = load()
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<h1>Notes at the bottom of the page</h1>
<p>This sample is the technical proof of the citation apparatus. It renders the same text twice: once with
full citations on first use and once with the short form that follows. The page is laid out by WeasyPrint,
which moves each note to the footnote area of the page where its call appears{note("teece2010", data)}.
The mechanism is the one the dissertation needs, because a note that sits at the end of the document cannot
be checked against the sentence that makes the claim.</p>

<p>The scaled error used throughout the forecast chapters is the mean absolute scaled error, defined so that
the naive forecast scores one in sample{note("hyndman2006", data)}. The comparison of two forecast sequences
uses the Diebold and Mariano statistic{note("diebold1995", data)}, and the small sample correction for
overlapping horizons is the one proposed by Harvey, Leybourne and Newbold{note("harvey1997", data)}.</p>

<h2>Later citations of the same sources</h2>
<p>The same three sources return in shorter form, as the style requires. The scaled error is invariant to the
unit of the series{note("hyndman2006", data, "680")}, the test is applied at each horizon separately
{note("diebold1995", data, "256")}, and the correction scales the statistic and refers it to a t distribution
{note("harvey1997", data, "283")}.</p>

<p>A pre-registered protocol removes the freedom to choose the rule after the result is known
{note("nosek2018", data)}. The failure mode that the protocol addresses is the garden of forking paths
{note("gelman2014", data)}. The German series is taken from the official register
{note("destatis2026", data)} and is never edited in place.</p>

<p class="note">This page is a sample, not a chapter. It exists to prove that the dissertation can carry
numbered notes at the foot of the page, with a full citation at first use and a short form afterwards,
before the apparatus is applied to all twenty chapters.</p>
</body></html>"""
    html = re.sub(r"\s+(<span class=\"fn\">)", r"\1", html)
    OUT.parent.mkdir(exist_ok=True)
    HTML(string=html).write_pdf(OUT)
    print("saved", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
