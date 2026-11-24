"""Insert a table of contents with real page numbers into the manuscript.

The manuscript carries two markers, <!--TOC--> and <!--ENDTOC-->. The script
renders the PDF, finds the page on which each level one heading appears, writes
the entries between the markers, and renders again. It repeats until the page
numbers stop moving, which normally takes two passes because the contents block
occupies a fixed number of pages.

Usage  python3 tools/build_toc.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "DISSERTATION.md"
PDF = ROOT / "build" / "DISSERTATION.pdf"
RENDER = ROOT / "tools" / "render_pdf.py"
TOC = re.compile(r"<!--TOC-->.*?<!--ENDTOC-->", re.S)


def headings(text: str) -> list[str]:
    return [line[2:].strip() for line in text.splitlines() if line.startswith("# ")]


def page_text(page: int) -> str:
    out = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), str(PDF), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    return re.sub(r"\s+", " ", out.stdout)


def find_pages(titles: list[str], total: int) -> dict[str, int]:
    pages = [page_text(p) for p in range(1, total + 1)]
    toc_start = next((i for i, t in enumerate(pages, start=1) if t.startswith("Contents")), 0)
    first_chapter = next((i for i, t in enumerate(pages, start=1) if t.startswith("Chapter 1.")), total + 1)
    found: dict[str, int] = {}
    for title in titles:
        needle = re.sub(r"\s+", " ", title)[:45]
        for index, text in enumerate(pages, start=1):
            if toc_start <= index < first_chapter and not title.startswith("Contents"):
                continue
            if text.startswith(needle):
                found[title] = index
                break
    return found


def build_block(titles: list[str], pages: dict[str, int]) -> str:
    lines = ["<!--TOC-->", ""]
    skip = {"Contents", "Forecasting the German Automotive Industry and the Volkswagen Group to 2040"}
    for title in [t for t in titles if t not in skip]:
        page = pages.get(title)
        label = title if len(title) <= 78 else title[:75].rstrip() + "..."
        if page is None:
            lines.append(f"{label}  ")
        else:
            lines.append(f"{label} .... {page}  ")
    lines.append("")
    lines.append("<!--ENDTOC-->")
    return "\n".join(lines)


def main() -> int:
    text = MD.read_text()
    titles = headings(text)
    previous: dict[str, int] = {}

    for attempt in range(1, 5):
        subprocess.run([sys.executable, str(RENDER)], check=True, capture_output=True)
        total = int(
            re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout).group(1)
        )
        pages = find_pages(titles, total)
        missing = [t for t in titles if t not in pages]
        print(f"pass {attempt}: {total} pages, {len(pages)} of {len(titles)} headings found")
        if missing:
            for title in missing:
                print("  not found:", title[:70])
        if pages == previous:
            print("stable")
            break
        text = TOC.sub(lambda _: build_block(titles, pages), MD.read_text(), count=1)
        MD.write_text(text)
        previous = pages

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
