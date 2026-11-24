"""Build the dissertation Word template with proper styles.

The uploaded template is structurally complete but visually plain and uses
dashes in its placeholders. This script produces a cleaner document: a ruled
title page, real Word fields for the table of contents and the lists, named
styles for body, headings, captions, source lines and footnotes, page numbers
in the footer, and a sample chapter that shows every element in use.

Output  thesis/template/Dissertation_Template_Armin_Kajevic.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = Path(__file__).resolve().parent.parent / "template" / "Dissertation_Template_Armin_Kajevic.docx"

NAVY = RGBColor(0x1F, 0x3B, 0x57)
GREY = RGBColor(0x59, 0x59, 0x59)


def set_font(style, name: str, size: float, bold: bool = False, italic: bool = False, colour: RGBColor | None = None) -> None:
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    if colour is not None:
        style.font.color.rgb = colour
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for key in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(key), name)


def field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Right click and choose Update Field"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(separate)
    run._r.append(placeholder)
    run._r.append(end)


def rule(paragraph, size: int = 6, colour: str = "1F3B57") -> None:
    ppr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), colour)
    borders.append(bottom)
    ppr.append(borders)


def page_number_footer(section) -> None:
    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    field(paragraph, "PAGE")
    for run in paragraph.runs:
        run.font.name = "Georgia"
        run.font.size = Pt(9)
        run.font.color.rgb = GREY


def build() -> Path:
    document = Document()

    styles = document.styles
    set_font(styles["Normal"], "Georgia", 11)
    normal = styles["Normal"].paragraph_format
    normal.line_spacing = 1.5
    normal.space_after = Pt(6)
    normal.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    set_font(styles["Heading 1"], "Georgia", 16, bold=True, colour=NAVY)
    h1 = styles["Heading 1"].paragraph_format
    h1.space_before = Pt(18)
    h1.space_after = Pt(12)
    h1.page_break_before = True
    h1.keep_with_next = True

    set_font(styles["Heading 2"], "Georgia", 13, bold=True, colour=NAVY)
    styles["Heading 2"].paragraph_format.space_before = Pt(14)
    styles["Heading 2"].paragraph_format.space_after = Pt(6)
    styles["Heading 2"].paragraph_format.keep_with_next = True

    set_font(styles["Heading 3"], "Georgia", 11.5, bold=True, italic=True, colour=NAVY)
    styles["Heading 3"].paragraph_format.space_before = Pt(10)
    styles["Heading 3"].paragraph_format.space_after = Pt(4)

    caption = styles.add_style("Caption Custom", 1)
    caption.base_style = styles["Normal"]
    set_font(caption, "Georgia", 9, italic=True)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    caption.paragraph_format.space_before = Pt(6)
    caption.paragraph_format.space_after = Pt(2)

    source = styles.add_style("Source Line", 1)
    source.base_style = styles["Normal"]
    set_font(source, "Georgia", 8.5, italic=True, colour=GREY)
    source.paragraph_format.space_after = Pt(10)

    footnote = styles.add_style("Footnote Text Custom", 1)
    footnote.base_style = styles["Normal"]
    set_font(footnote, "Georgia", 9)
    footnote.paragraph_format.line_spacing = 1.0
    footnote.paragraph_format.space_after = Pt(2)

    section = document.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(3.0)
    section.left_margin = Cm(3.2)
    section.right_margin = Cm(2.8)
    section.different_first_page_header_footer = True
    page_number_footer(section)

    # title page
    for _ in range(3):
        document.add_paragraph()
    university = document.add_paragraph()
    university.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = university.add_run("UNIVERSITY NAME")
    run.font.name = "Georgia"
    run.font.size = Pt(11)
    run.font.color.rgb = GREY
    run.font.small_caps = True
    rule(university, size=4, colour="BFBFBF")

    document.add_paragraph()
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Forecasting the German Automotive Industry\nand the Volkswagen Group to 2040")
    run.font.name = "Georgia"
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = NAVY

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("A statistical, econometric and machine learning protocol,\nwith a strategy assessment")
    run.font.name = "Georgia"
    run.font.size = Pt(12)
    run.font.italic = True
    run.font.color.rgb = GREY

    for _ in range(4):
        document.add_paragraph()
    line = document.add_paragraph()
    line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = line.add_run("Doctoral dissertation")
    run.font.name = "Georgia"
    run.font.size = Pt(11)
    run.font.small_caps = True
    rule(line, size=4, colour="BFBFBF")

    for _ in range(2):
        document.add_paragraph()
    author = document.add_paragraph()
    author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = author.add_run("Armin Kajevic")
    run.font.name = "Georgia"
    run.font.size = Pt(13)

    year = document.add_paragraph()
    year.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = year.add_run("2026")
    run.font.name = "Georgia"
    run.font.size = Pt(11)
    run.font.color.rgb = GREY

    # about the author, city and country only, the street stays in the submission form
    document.add_heading("The author", level=1)
    author_block = [
        "Armin Kajevic, born 20 October 1985 in Serbia.",
        "Vice President, Sincars Industry Ltd.",
        "Vice President, L City GmbH, Munich.",
        "Founder, Ai-ministry.eu.",
        "Ingolstadt, Germany.",
    ]
    for line_text in author_block:
        document.add_paragraph(line_text)

    # front matter
    document.add_heading("Declaration of Originality", level=1)
    document.add_paragraph(
        "I declare that this dissertation is my own work, that it has not been submitted for any other degree, "
        "and that every source used is acknowledged in the text and in the reference list."
    )
    document.add_paragraph("Candidate: Armin Kajevic")
    document.add_paragraph("Signature: ______________________________")
    document.add_paragraph("Date: ___________________________________")

    document.add_heading("Abstract", level=1)
    document.add_paragraph(
        "The abstract states the problem, the data, the method, the principal result and the contribution "
        "in one paragraph of no more than three hundred words."
    )
    keywords = document.add_paragraph()
    run = keywords.add_run("Keywords: ")
    run.font.bold = True
    keywords.add_run("forecasting, rolling origin, model selection, ownership, automotive industry")

    document.add_heading("Table of Contents", level=1)
    toc = document.add_paragraph()
    field(toc, 'TOC \\o "1-3" \\h \\z \\u')

    document.add_heading("List of Figures", level=1)
    field(document.add_paragraph(), 'TOC \\h \\z \\c "Figure"')

    document.add_heading("List of Tables", level=1)
    field(document.add_paragraph(), 'TOC \\h \\z \\c "Table"')

    document.add_heading("List of Abbreviations", level=1)
    table = document.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    for row, (short, long) in enumerate(
        (("BEV", "battery electric vehicle"), ("MASE", "mean absolute scaled error"), ("DM", "Diebold and Mariano"))
    ):
        table.cell(row, 0).text = short
        table.cell(row, 1).text = long

    # sample chapter
    document.add_heading("1 Introduction", level=1)
    document.add_heading("1.1 The question", level=2)
    document.add_paragraph(
        "The chapter opens with one paragraph that states what it settles. Citations use the Harvard form in the "
        "text, for example (Diebold and Mariano 1995), and the full entry sits in the reference list."
    )
    document.add_paragraph(
        "A footnote carries what does not belong in the sentence, such as an archive mark or a download date."
    ).add_run().font.superscript = True

    document.add_heading("1.2 A table with its source", level=2)
    caption_paragraph = document.add_paragraph("Table 1.1. Selected model and its error by horizon", style="Caption Custom")
    caption_paragraph.runs[0].font.bold = True
    table = document.add_table(rows=3, cols=3)
    table.style = "Light Grid Accent 1"
    for column, head in enumerate(("Model", "MASE", "p value")):
        table.cell(0, column).text = head
    for row, values in enumerate((("ridge_lags", "1.2839", "0.0051"), ("naive", "1.5952", "reference")), start=1):
        for column, value in enumerate(values):
            table.cell(row, column).text = value
    document.add_paragraph("Author calculation from the model register, 24 November 2026.", style="Source Line")

    document.add_heading("1.3 An equation", level=2)
    equation = document.add_paragraph()
    equation.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = equation.add_run("MASE = mean(|e_t|) / mean(|e_t naive|)")
    run.font.name = "Cambria Math"
    run.font.italic = True

    document.add_heading("References", level=1)
    document.add_paragraph("Diebold, F.X. and Mariano, R.S. (1995) Comparing predictive accuracy. Journal of Business and Economic Statistics, 13(3), pp. 253 to 263.")
    document.add_paragraph("Hyndman, R.J. and Athanasopoulos, G. (2021) Forecasting: principles and practice. 3rd ed. Melbourne: OTexts.")

    # main matter with arabic numbering
    new_section = document.add_section(WD_SECTION.NEW_PAGE)
    new_section.footer.is_linked_to_previous = False
    page_number_footer(new_section)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUT)
    return OUT


if __name__ == "__main__":
    print(f"wrote {build()}")
