# Forecast 2040

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24516637.svg)](https://doi.org/10.5281/zenodo.24516637)

Pre-registered rolling-origin protocol for German passenger car registrations and long-horizon automotive demand.

This repository holds the code, the data and the results behind the paper *Fixing the model before the backtest: a pre-registered protocol with a machine-checked split for long-horizon automotive demand* by Armin Kajevic.

## What the protocol does

The candidate set, the rolling-origin design, the loss, the selection rule and the projection are fixed before any result is seen. Thirteen models are compared on annual German passenger car registrations from 1991 to 2025 at fifteen origins and horizons of one to five years. Ridge regression on three lagged growth rates wins with an average MASE of 1.2839 against 1.5952 for the naive benchmark, a reduction of 19.5 percent.

The paper reports the inference as it is, not as it would like it to be. The pre-specified horizon test rejects equal accuracy at four and five years, with p values of 0.0114 and 0.0094. A bootstrap that re-estimates the long-run variance does not reproduce the rejection, a variance clustered by origin gives p 0.175 at the pooled level, and a Bonferroni bound over thirteen candidates gives 0.148 at the strongest horizon. The point estimate is stable and the verdict is not, and the paper says so.

The deterministic part of the split is written in Lean 4. Nine theorems establish that no observation dated at or after an origin can enter the training set, that the expanding window is nested, and that selection is a function of the backtest output. The kernel certifies information separation, not estimation.

## Repository layout

```
src/forecast2040/        Python package: models, backtest, metrics, data access
tests/                   Unit tests for models, parsers, configuration
lean_poc/                Lean 4 module with the split theorems
data/raw/                Raw series exactly as downloaded, never edited in place
data/model/              Backtest output, metrics, Diebold-Mariano matrix, P01 tables
papers/P01_full.md       Manuscript source
papers/build/            Rendered manuscript (PDF, DOCX)
tools/                   Scripts that build the figures, the tables and the PDFs
analysis/                Chapter level analysis scripts
figures/                 Figures used in the dissertation
```

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
```

The backtest is rebuilt from the raw series with the package entry point:

```bash
python -m forecast2040.cli --help
```

The checks added in the second round of review, which produce the power table, the variance table, the Romano and Wolf stepdown and the capacity table, are in `tools/p01_reviewer_checks.py`:

```bash
python tools/p01_reviewer_checks.py
```

The manuscript is rebuilt from Markdown with:

```bash
python tools/render_pdf.py "$PWD/papers/P01_full.md" "$PWD/papers/build/P01_full.pdf"
```

The Lean module builds with Lean 4.36.0 and has no dependency on Mathlib:

```bash
cd lean_poc
lake build
```

## Data

The German series is Destatis GENESIS table 46131, downloaded on 24 November 2026. The Chinese series is Volkswagen Group deliveries as reported in the group annual reports. Both are public. The SHA256 of each file is recorded in the paper and in `data/manifest.csv`. No series is edited in place; every transformation is applied at run time.

## Results that are archived

- `data/model/metrics_full_destatis_pkw_neuzulassungen_jahre.csv`: thirteen models, MASE, RMSE, MAPE, bias, per-horizon MASE.
- `data/model/backtest_full_destatis_pkw_neuzulassungen_jahre.csv`: 975 forecast errors.
- `data/model/dm_matrix_destatis_pkw_neuzulassungen_jahre.csv`: pairwise Diebold-Mariano p values.
- `data/model/p01_power.csv`, `p01_variance.csv`, `p01_romano_wolf.csv`, `p01_complexity.csv`: the four tables added after review.

## Citation

If you use the protocol, cite the paper and the archive. The metadata are in `CITATION.cff`. Release v1.0.0 is deposited at Zenodo under DOI 10.5281/zenodo.24516637, which resolves to https://doi.org/10.5281/zenodo.24516637.

## Licence

Code is released under the MIT licence. Text, data and figures are released under CC BY 4.0. See `LICENSE`.
