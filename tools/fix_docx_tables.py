"""Normalise table geometry and formatting in a pandoc DOCX build.

Pandoc writes pipe tables with equal width columns and relies on paragraph
styles such as ``Compact`` for the cells.  When the reference document does
not define those styles, some word processors collapse the table into a
single narrow column.  The template now defines them; this script then makes
the geometry explicit, guarantees that the longest word in each column fits
without breaking, bolds the header row and keeps the caption with its table.
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_child(parent, tag: str, **attributes: str):
    element = parent.find(qn(tag))
    if element is None:
        element = OxmlElement(tag)
        parent.append(element)
    for key, value in attributes.items():
        element.set(qn(f"w:{key}"), value)
    return element


def column_profile(table) -> tuple[list[int], list[int]]:
    longest_word = []
    total_text = []
    for column in table.columns:
        word = 0
        text = 0
        for cell in column.cells:
            for paragraph in cell.paragraphs:
                value = paragraph.text.strip()
                text += len(value)
                for token in value.split():
                    word = max(word, len(token))
        longest_word.append(word)
        total_text.append(text)
    return longest_word, total_text


def normalise(path: Path) -> None:
    document = Document(str(path))
    section = document.sections[0]
    text_width = (
        section.page_width.twips - section.left_margin.twips - section.right_margin.twips
    )

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text.startswith("Table ") and "." in text[:12]:
            paragraph.paragraph_format.keep_with_next = True
        if paragraph._p.findall(".//" + qn("w:drawing")):
            paragraph.paragraph_format.keep_with_next = True

    for table in document.tables:
        columns = len(table.columns)
        if columns == 0:
            continue
        font_points = 8.5 if columns <= 5 else (8.0 if columns <= 7 else 7.5)
        char_width = {8.5: 82, 8.0: 78, 7.5: 73}[font_points]

        longest_word, total_text = column_profile(table)
        required = [max(700, word * char_width + 150) for word in longest_word]
        if sum(required) > text_width:
            scale = text_width / sum(required)
            required = [int(value * scale) for value in required]
        spare = max(0, text_width - sum(required))
        text_total = max(1, sum(total_text))
        widths = [
            required[i] + int(spare * total_text[i] / text_total) for i in range(columns)
        ]
        widths[-1] += text_width - sum(widths)

        tbl = table._tbl
        tbl_pr = tbl.tblPr
        set_child(tbl_pr, "w:tblW", type="dxa", w=str(text_width))
        set_child(tbl_pr, "w:tblLayout", type="fixed")
        set_child(tbl_pr, "w:jc", val="center")
        margins = set_child(tbl_pr, "w:tblCellMar")
        for edge in ("left", "right"):
            set_child(margins, f"w:{edge}", type="dxa", w="60")

        grid = tbl.find(qn("w:tblGrid"))
        if grid is not None:
            for grid_col, width in zip(grid.findall(qn("w:gridCol")), widths):
                grid_col.set(qn("w:w"), str(width))

        for row_index, row in enumerate(table.rows):
            for cell, width in zip(row.cells, widths):
                tc_pr = cell._tc.get_or_add_tcPr()
                set_child(tc_pr, "w:tcW", type="dxa", w=str(width))
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(font_points)
                        if row_index == 0:
                            run.font.bold = True
    document.save(str(path))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: fix_docx_tables.py <file.docx>")
    normalise(Path(sys.argv[1]))
    print(f"normalised tables in {sys.argv[1]}")
