"""Assemble the dissertation from the chapter files into one manuscript.

The chapters are written as separate Markdown files with LaTeX mathematics. This
script puts them in order, adds the front matter, the annexes that already exist
as files, and writes thesis/DISSERTATION.md. It also reports the word count, the
chapter table and any dash characters that must not appear.

Output  thesis/DISSERTATION.md
        thesis/build/report.txt
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "chapters"
PAPERS = ROOT / "papers"
OUT = ROOT / "DISSERTATION.md"
REPORT = ROOT / "build" / "report.txt"

ORDER = [
    "ch01_introduction.md",
    "ch02_literature.md",
    "ch03_systems.md",
    "ch04_data.md",
    "ch05_foundations.md",
    "ch06_models.md",
    "ch07_protocol.md",
    "ch08_machine_learning.md",
    "ch09_lean.md",
    "ch10_germany.md",
    "ch11_china.md",
    "ch12_ownership.md",
    "ch13_capital.md",
    "ch14_risk.md",
    "ch15_robustness.md",
    "ch16_strategy_vw.md",
    "ch17_strategy_industry.md",
    "ch18_limitations.md",
    "ch19_conclusion.md",
    "ch20_outlook.md",
]

PAPER_ORDER = [
    "P01_forecast_protocol.md",
    "P02_battery_lca_vintage.md",
    "P03_used_vehicles.md",
    "P04_china_certification.md",
    "P05_divestment_event_study.md",
    "P06_severance.md",
    "P07_pensions.md",
    "P08_crisis_consumption.md",
    "P09_migration.md",
    "P10_capital_ownership.md",
    "P11_autonomy_law.md",
    "P12_political_economy.md",
]

FRONT = """# Forecasting the German Automotive Industry and the Volkswagen Group to 2040

## A statistical, econometric and machine learning protocol, with a strategy assessment

Armin Kajevic

Doctoral dissertation, 2026

## Abstract

This dissertation asks what the German automotive industry and the Volkswagen
Group can expect by 2040, and what they should do about it. The answer is built
on a pre-registered forecasting protocol: thirteen candidate models, a rolling
origin backtest over the full history, a selection rule fixed before any result
is seen, and a split whose deterministic part is checked by the Lean 4 kernel.
German passenger car registrations from 1991 to 2025 select ridge regression on
lagged growth, with a mean absolute scaled error of 1.2839 against 1.5952 for
the naive benchmark and a Diebold and Mariano p value of 0.0051 at the pooled
level. The 2040 point forecast is 3,161,958.51 registrations, with an empirical
95 percent interval from 2,563,157.85 to 3,689,022.75. The same protocol applied
to Volkswagen Group deliveries in China from 1987 to 2025 produces no winner:
the best model has a scaled error of 7.7778 and a p value of 0.9615 against the
random walk. That null result is reported as a result, and it changes the
strategy: China is treated as three conditional paths of 1.33, 2.10 and 3.20
million vehicles in 2040 rather than as a point forecast. Ownership is modelled
as a constraint, because 90.3 percent of Volkswagen votes sit with three holders
and 9.7 percent with the free float. The contribution is a protocol that can be
audited, a published negative result, and a method for turning statistical
uncertainty into a strategy that a board can act on.

## The author

Armin Kajevic, born 20 October 1985 in Serbia. Vice President, Sincars Industry
Ltd. Vice President, L City GmbH, Munich. Founder, Ai-ministry.eu. Ingolstadt,
Germany.

# Contents

<!--TOC-->

<!--ENDTOC-->

"""


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip("\n")
    return text


def title_of(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled chapter"


def main() -> int:
    chunks: list[str] = [FRONT]
    report: list[str] = []
    total_words = 0

    for index, name in enumerate(ORDER, start=1):
        path = CHAPTERS / name
        if not path.exists():
            report.append(f"MISSING {name}")
            continue
        text = strip_front_matter(path.read_text())
        words = len(text.split())
        total_words += words
        report.append(f"{index:02d} {name:36s} {words:6d} words  {title_of(text)[:70]}")
        chunks.append(f"\n\n{text}\n")

    chunks.append("\n\n# Annex A. Glossary\n\n")
    chunks.append(
        "The glossary lists the terms that carry a technical meaning in this dissertation. "
        "Each entry gives the term, the definition used here, and the chapter where it is introduced. "
        "Terms are grouped by layer: data, statistics, ownership, regulation, and engineering.\n\n"
    )
    chunks.append(
        "| Term | Definition | Chapter |\n|---|---|---|\n"
        "| MASE | Mean absolute scaled error, the mean absolute forecast error divided by the in sample naive error | 5 |\n"
        "| Rolling origin | A backtest in which the estimation sample ends at an origin that moves forward one year at a time | 7 |\n"
        "| Diebold and Mariano | A test of equal predictive accuracy using the loss differential series | 5 |\n"
        "| Empirical interval | A forecast interval built from the quantiles of past backtest errors | 5 |\n"
        "| Register | The file that records every model run with its date and metrics | 7 |\n"
        "| Control layer | A holder or rule that can block a decision: family, state, fund, float, law | 12 |\n"
        "| Blocking minority | Twenty percent of votes, enough to block a control agreement in Germany | 12 |\n"
        "| Capital cycle | The relation between credit expansion and later equity returns | 13 |\n"
        "| Drawdown | The fall from a peak to a trough in the equity index | 13 |\n"
        "| Conditional path | A scenario computed under a stated rule, not a forecast | 11 |\n"
        "| Minimax capacity | The capacity that minimises the worst case loss across paths | 14 |\n"
        "| Certification wall | The private and public approval barrier that kept Chinese cars out of Europe | 11 |\n"
        "| Data vintage | The date at which an impact estimate was produced, which fixes its validity | 2 |\n"
    )

    chunks.append("\n\n# Annex B. Regulations and legal instruments\n\n")
    chunks.append(
        "The annex lists the instruments that the argument uses, with the chapter in which each appears. "
        "It is not a legal commentary. Where the dissertation relies on an instrument, the instrument is named "
        "in the text at first use.\n\n"
    )
    chunks.append(
        "| Instrument | What it does in the argument | Chapter |\n|---|---|---|\n"
        "| Regulation (EU) 2023/1542 | Battery passport, recycled content and due diligence duties | 2 |\n"
        "| Regulation (EU) 2018/858 | Type approval framework that carries the UN regulations | 11 |\n"
        "| UNECE Regulation No. 155 | Cybersecurity management system | 11 |\n"
        "| UNECE Regulation No. 156 | Software update management system | 11 |\n"
        "| Regulation (EU) 2024/2754 | Tariff instrument applied to battery electric vehicles | 11 |\n"
        "| German Securities Trading Act | Voting rights notifications that fix the ownership data | 12 |\n"
        "| Dismissal Protection Act | The statutory floor behind severance | 17 |\n"
    )

    chunks.append("\n\n# Annex C. The twelve papers\n\n")
    chunks.append(
        "The twelve papers are reproduced here as they were written, each with its own abstract and references. "
        "They are the publication layer of the dissertation and are cited in the main text by their number.\n\n"
    )
    for name in PAPER_ORDER:
        path = PAPERS / name
        if not path.exists():
            report.append(f"MISSING paper {name}")
            continue
        text = strip_front_matter(path.read_text())
        total_words += len(text.split())
        chunks.append(f"\n\n{text}\n")

    chunks.append("\n\n# Annex D. Model register and reproduction\n\n")
    chunks.append(
        "The register is the audit trail. It records the date of every run, the series, the number of origins, "
        "the selected model, the scaled error and the p value against naive. The file is "
        "data/model/model_register.csv. The commands that reproduce each table are listed in the repository "
        "readme. A reader who runs them obtains the same numbers, or finds the defect that prevents it.\n\n"
    )

    chunks.append("\n\n# Annex E. Interview protocol and anonymisation\n\n")
    chunks.append(
        "Nine interviews were conducted with managers and engineers from the German automotive and supplier "
        "base. Each case is identified only by a code, E01 to E09. The key that links codes to persons is held "
        "by the author and is not part of this document. Consent was oral in one case and written in the "
        "others, and the scope of each consent is recorded in the case file. No quotation in this dissertation "
        "identifies a person, a plant, or a date that would allow identification by triangulation. A "
        "participant may withdraw consent, and where a finding rests on a single case the withdrawal is "
        "reported in the text rather than hidden.\n\n"
    )

    text = "".join(chunks)
    OUT.write_text(text)

    bad = {
        "em dash": text.count("\u2014"),
        "en dash": text.count("\u2013"),
        "asterisk": text.count("*"),
    }
    report.append("")
    report.append(f"total words {total_words}")
    report.append(f"characters {len(text)}")
    report.append(f"pages at 350 words {total_words / 350:.1f}")
    for key, value in bad.items():
        report.append(f"{key} occurrences {value}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report) + "\n")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
