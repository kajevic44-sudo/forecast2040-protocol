"""Render the dissertation Markdown to a print quality PDF.

Markdown is converted to HTML, mathematics is rendered by KaTeX in a headless
Chromium page, and the page is printed to A4 with running page numbers. The
script fails loudly if KaTeX reports an error, so a formula is never silently
printed as source code.

Usage  python3 tools/render_pdf.py [input.md] [output.pdf]
"""

from __future__ import annotations

import asyncio
import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
KATEX = ROOT / "tools" / "render" / "node_modules" / "katex" / "dist"

CSS = """
@page { size: A4; margin: 24mm 21mm 22mm 24mm; }
body { font-family: "DejaVu Serif", Georgia, serif; font-size: 11.5pt; line-height: 1.62;
       color: #1B1F22; text-align: justify; hyphens: manual; }
h1, h2, h3 { font-family: "DejaVu Sans", Helvetica, sans-serif; color: #1C2E3A; }
h1 { font-size: 20pt; line-height: 1.18; margin: 0 0 16pt 0; page-break-before: always;
     padding-bottom: 8pt; border-bottom: 0.6pt solid #D5DBDE; text-align: left;
     position: relative; }
h1::after { content: ""; display: block; width: 46pt; height: 2.4pt;
            background: #C3955E; margin-top: 8pt; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 13pt; margin: 18pt 0 6pt 0; page-break-after: avoid; text-align: left;
     letter-spacing: 0.2pt; }
h3 { font-size: 11pt; margin: 13pt 0 4pt 0; page-break-after: avoid; text-align: left;
     color: #35505E; }
p { margin: 0 0 6pt 0; orphans: 2; widows: 2; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 10pt 0 12pt 0;
        page-break-inside: auto; font-family: "DejaVu Sans", Helvetica, sans-serif; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th, td { border: none; border-bottom: 0.5pt solid #D5DBDE; padding: 4pt 5pt;
         vertical-align: top; text-align: left; }
th { background: #E7EDEF; color: #1C2E3A; font-weight: bold; font-size: 8.6pt;
     letter-spacing: 0.3pt; border-bottom: 0.9pt solid #1C2E3A; }
tbody tr:nth-child(even) td { background: #F6F8F8; }
img { max-width: 100%; max-height: 172mm; display: block; margin: 10pt auto; }
p:has(+ table) { page-break-after: avoid; break-after: avoid; }
figure { margin: 12pt 0; page-break-inside: avoid; }
figcaption, .caption { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 8.4pt;
                       color: #5F6E75; text-align: left; margin-top: 4pt; line-height: 1.4; }
em { color: #35505E; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.4pt; color: #2A3E48; }
pre { background: #F4F7F6; border-left: 2.2pt solid #C3955E; padding: 7pt 8pt;
      font-size: 8.1pt; white-space: pre-wrap; page-break-inside: avoid;
      font-family: "DejaVu Sans Mono", monospace; }
blockquote { margin: 8pt 16pt; padding-left: 8pt; border-left: 1.4pt solid #D5DBDE;
             font-style: italic; color: #35505E; }
.math-display { text-align: center; margin: 10pt 0; page-break-inside: avoid; }
.katex-display { margin: 0; }
.title-page { text-align: center; page-break-after: always; }
.title-page h1 { border: none; page-break-before: avoid; text-align: center; font-size: 25pt; }
.title-page h1::after { margin: 10pt auto 0 auto; }
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Dissertation</title>
<link rel="stylesheet" href="{katex}/katex.min.css">
<style>{css}</style>
</head><body>
{body}
<script src="{katex}/katex.min.js"></script>
<script src="{katex}/contrib/auto-render.min.js"></script>
<script>
try {{
  renderMathInElement(document.body, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "\\\\[", right: "\\\\]", display: true}},
      {{left: "\\\\(", right: "\\\\)", display: false}},
      {{left: "$", right: "$", display: false}}
    ],
    throwOnError: true,
    errorCallback: function (msg) {{ document.title = "KATEX ERROR " + msg; }}
  }});
  document.title = "RENDERED";
}} catch (e) {{ document.title = "KATEX ERROR " + e.message; }}
</script>
</body></html>
"""


def protect_math(text: str) -> tuple[str, list[str]]:
    """Replace display and inline math with placeholders Markdown cannot touch."""
    store: list[str] = []

    def clean(body: str) -> str:
        body = body.strip()
        for env in ("equation*", "equation"):
            body = body.replace("\\begin{%s}" % env, "").replace("\\end{%s}" % env, "")
        body = re.sub(r"\\label\{[^}]*\}", "", body)
        body = re.sub(r"\\tag\{([^}]*)\}", r"\\qquad (\\text{\1})", body)
        return body

    def keep_display(body: str) -> str:
        store.append(clean(body))
        return f"\n\nMATHBLOCK{len(store) - 1}ENDMATH\n\n"

    def keep_inline(match: re.Match[str]) -> str:
        store.append(match.group(1).strip())
        return f"MATHINLINE{len(store) - 1}ENDMATH"

    env = r"\\begin\{(equation\*?|align\*?|gather\*?)\}(.+?)\\end\{\1\}"
    text = re.sub(env, lambda m: keep_display(m.group(2)), text, flags=re.S)
    text = re.sub(r"\$\$(.+?)\$\$", lambda m: keep_display(m.group(1)), text, flags=re.S)
    text = re.sub(r"\\\[(.+?)\\\]", lambda m: keep_display(m.group(1)), text, flags=re.S)
    text = re.sub(r"\\\((.+?)\\\)", keep_inline, text, flags=re.S)
    text = re.sub(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)", keep_inline, text)
    return text, store


def restore_math(text: str, store: list[str]) -> str:
    def put_block(match: re.Match[str]) -> str:
        body = html.escape(store[int(match.group(1))], quote=False)
        return f'<div class="math-display">\\[{body}\\]</div>'

    def put_inline(match: re.Match[str]) -> str:
        body = html.escape(store[int(match.group(1))], quote=False)
        return f'<span class="math-inline">\\({body}\\)</span>'

    text = re.sub(r"<p>\s*MATHBLOCK(\d+)ENDMATH\s*</p>", put_block, text)
    text = re.sub(r"MATHBLOCK(\d+)ENDMATH", put_block, text)
    text = re.sub(r"MATHINLINE(\d+)ENDMATH", put_inline, text)
    return text


def build_html(source: Path) -> str:
    text = source.read_text()
    text, store = protect_math(text)
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"],
        output_format="html5",
    )
    body = restore_math(body, store)
    body = body.replace("<p>MATHBLOCK", "<p>MATHBLOCK")
    return TEMPLATE.format(katex=KATEX.as_uri(), css=CSS, body=body)


async def render(source: Path, target: Path) -> int:
    from playwright.async_api import async_playwright

    page_html = build_html(source)
    html_path = target.with_suffix(".html")
    html_path.write_text(page_html)
    errors: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(html_path.as_uri(), wait_until="load")
        await page.wait_for_timeout(1500)
        title = await page.title()
        if "KATEX ERROR" in title:
            errors.append(title)
        await page.pdf(
            path=str(target),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(
                '<div style="width:100%;font-size:8pt;color:#555;'
                'font-family:Georgia,serif;text-align:center;">'
                '<span class="pageNumber"></span></div>'
            ),
            margin={"top": "25mm", "bottom": "22mm", "left": "25mm", "right": "22mm"},
        )
        await browser.close()

    for message in errors:
        print("ERROR", message)
    return 1 if errors else 0


def main() -> int:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "DISSERTATION.md"
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "build" / "DISSERTATION.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    return asyncio.run(render(source, target))


if __name__ == "__main__":
    raise SystemExit(main())
