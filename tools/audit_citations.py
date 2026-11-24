"""Check that the reference list and the in-text citations agree.

Two directions:
  uncited   a reference in the list that never appears in the body
  missing   an in-text author-year pair with no entry in the list

The match is deliberately generous. A reference counts as cited when one of its
author forms and its year occur in the body within 200 characters of each other,
which catches "Klier and Rubenstein (2008)" and "(Klier and Rubenstein 2008)"
without counting a bare surname in an unrelated sentence.

Corporate authors are the hard case: the list carries the full name, the body
carries the acronym. The ALIASES table below states, in one place, which forms
belong to the same source, so the check is explicit rather than guessed.
"""
from __future__ import annotations

import re
from pathlib import Path

P = Path("/home/ubuntu/battery_phd/thesis/papers/P01_full.md")
text = P.read_text()
body, refs = text.split("## References", 1)

entries = [e.strip() for e in refs.strip().split("\n\n") if e.strip()]

ALIASES = {
    "China Association of Automobile Manufacturers": ["China Association of Automobile Manufacturers", "CAAM"],
    "European Automobile Manufacturers Association": ["European Automobile Manufacturers Association", "ACEA"],
    "International Energy Agency": ["International Energy Agency", "IEA"],
    "Kraftfahrt-Bundesamt": ["Kraftfahrt-Bundesamt", "KBA"],
    "Statistisches Bundesamt (Destatis)": ["Statistisches Bundesamt", "Destatis"],
    "Volkswagen AG": ["Volkswagen AG", "Volkswagen", "VW"],
}

STOPWORDS = {
    "The", "A", "An", "In", "On", "At", "By", "For", "From", "With", "Since",
    "After", "Before", "Between", "During", "This", "These", "Those", "Its",
    "Because", "Figure", "Table", "Section", "Appendix", "Note", "Source",
}


def split_entry(entry: str) -> tuple[str, str] | None:
    """Return the author string and the year of a reference entry."""
    year = re.search(r"\b(19|20)\d{2}[a-z]?\b", entry)
    if not year:
        return None
    author = entry[: year.start()].strip().rstrip(".").strip()
    return author, year.group(0)


def author_forms(author: str) -> list[str]:
    """All forms under which a source may be cited in the body."""
    forms = {author}
    if author in ALIASES:
        forms.update(ALIASES[author])
    m = re.search(r"\(([^)]+)\)", author)
    if m:
        forms.add(m.group(1).strip())
        forms.add(author[: m.start()].strip())
    if "," in author:
        forms.add(author.split(",")[0].strip())
    for suffix in (" AG", " GmbH", " Inc", " Ltd", " PLC"):
        if author.endswith(suffix):
            forms.add(author[: -len(suffix)])
    return sorted(f for f in forms if f)


pairs: list[tuple[str, str, list[str]]] = []
for entry in entries:
    parsed = split_entry(entry)
    if parsed is None:
        continue
    author, year = parsed
    pairs.append((author, year, author_forms(author)))

uncited: list[tuple[str, str]] = []
for author, year, forms in pairs:
    hit = False
    for form in forms:
        for m in re.finditer(re.escape(form), body):
            window = body[max(0, m.start() - 80) : m.start() + 200]
            if year in window:
                hit = True
                break
        if hit:
            break
    if not hit:
        uncited.append((author, year))

listed_forms = {form for _, _, forms in pairs for form in forms}
listed_years = {year for _, year, _ in pairs}

missing: list[tuple[str, str]] = []
for m in re.finditer(r"\(([^()]{3,160}?(?:19|20)\d{2}[a-z]?)\)", body):
    for part in m.group(1).split(";"):
        part = part.strip()
        year = re.search(r"\b((?:19|20)\d{2})", part)
        if not year:
            continue
        name = re.match(r"([A-Z][A-Za-z\u00C0-\u024F\-]+)", part)
        if not name:
            continue
        token = name.group(1)
        if token in STOPWORDS:
            continue
        if year.group(1) not in listed_years:
            missing.append((token, year.group(1)))
            continue
        if not any(token in form or form in token for form in listed_forms):
            missing.append((token, year.group(1)))

print(f"entries {len(entries)}  parsed {len(pairs)}")
print("\nUNCITED")
for author, year in uncited:
    print(" ", author, year)
if not uncited:
    print("  none")
print("\nMISSING (in text, not in list)")
seen: set[tuple[str, str]] = set()
for token, year in missing:
    if (token, year) in seen:
        continue
    seen.add((token, year))
    print(" ", token, year)
if not missing:
    print("  none")
