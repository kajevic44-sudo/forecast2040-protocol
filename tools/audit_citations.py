"""Check that the reference list and the in-text citations agree.

Two directions:
  uncited   a reference in the list that never appears in the body
  missing   an in-text author-year pair with no entry in the list

The match is deliberately generous: a reference counts as cited when its first
author surname and its year occur in the body within 120 characters of each
other. That catches "Klier and Rubenstein (2008)" and "(Klier and Rubenstein
2008)" but not a bare surname in a sentence about something else.
"""
from __future__ import annotations

import re
from pathlib import Path

P = Path("/home/ubuntu/battery_phd/thesis/papers/P01_full.md")
text = P.read_text()
body, refs = text.split("## References", 1)

entries = [e.strip() for e in refs.strip().split("\n\n") if e.strip()]


def key(entry: str) -> tuple[str, str] | None:
    year = re.search(r"\b(19|20)\d{2}[a-z]?\b", entry)
    if not year:
        return None
    surname = entry.split(",")[0].strip()
    return surname, year.group(0)


keys = [k for k in (key(e) for e in entries) if k]

uncited = []
for entry, (surname, year) in zip(entries, keys):
    hit = False
    for m in re.finditer(re.escape(surname), body):
        window = body[max(0, m.start() - 60) : m.start() + 160]
        if year in window:
            hit = True
            break
    if not hit:
        uncited.append((surname, year))

# in-text author-year pairs, restricted to capitalised names followed by a year
pattern = re.compile(r"([A-Z][A-Za-z\-]+)(?:,| and| et al\.)?[^().]{0,40}?\((19|20)(\d{2})\)")
listed = {(s, y) for s, y in keys}
missing = []
for m in re.finditer(r"\(([^()]{3,120}?(?:19|20)\d{2}[a-z]?)\)", body):
    inner = m.group(1)
    for part in inner.split(";"):
        part = part.strip()
        year = re.search(r"\b((?:19|20)\d{2})", part)
        if not year:
            continue
        name = re.match(r"([A-Z][A-Za-z\-]+)", part)
        if not name:
            continue
        if (name.group(1), year.group(1)) not in listed:
            missing.append((name.group(1), year.group(1)))

print(f"entries {len(entries)}  keys {len(keys)}")
print("\nUNCITED")
for s, y in uncited:
    print(" ", s, y)
print("\nMISSING (in text, not in list)")
seen = set()
for s, y in missing:
    if (s, y) in seen:
        continue
    seen.add((s, y))
    print(" ", s, y)
