# Forecast 2040

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24516636.svg)](https://doi.org/10.5281/zenodo.24516636)

Pre-registered forecasting protocol and long-run ownership research on the German automotive industry.

This repository holds the code, the data and the results behind two papers by Armin Kajevic. The first fixes a forecasting protocol and applies it to German passenger car registrations. The second prices the capital cycle on 151 years of German data and asks who owns the plant when the cycle turns.

## Papers

**P01. Fixing the model before the backtest: a pre-registered protocol with a machine-checked split for long-horizon automotive demand.** The candidate set, the rolling-origin design, the loss, the selection rule and the projection are fixed before any result is seen. Thirteen models are compared on annual German passenger car registrations from 1991 to 2025 at fifteen origins and horizons of one to five years. Ridge regression on three lagged growth rates wins with an average MASE of 1.2839 against 1.5952 for the naive benchmark, a reduction of 19.5 percent. The paper reports the inference as it is, not as it would like it to be. The pre-specified horizon test rejects equal accuracy at four and five years, with p values of 0.0114 and 0.0094, a bootstrap that re-estimates the long-run variance does not reproduce the rejection, a variance clustered by origin gives p 0.175 at the pooled level, and a Bonferroni bound over thirteen candidates gives 0.148 at the strongest horizon. The point estimate is stable and the verdict is not, and the paper says so. The deterministic part of the split is written in Lean 4: nine theorems establish that no observation dated at or after an origin can enter the training set, that the expanding window is nested, and that selection is a function of the backtest output.

**P10. Who owns the plant and when they arrived: ownership layers and the capital cycle in German industry, 1870 to 2020.** Ownership is treated as a dated event rather than a structure. The paper builds a register of 63 ownership events between 1937 and 2026, prices the capital cycle on 151 years of German data, and reports both halves of the result. The annual change in bank credit to gross domestic product correlates with the real total equity return five years later at minus 0.303589 over 123 observations, with a slope of minus 1.020070 and a t statistic of minus 3.545150. The relation does not survive the removal of the war years, where the correlation falls to minus 0.095086, and it is absent after 1950, where the correlation is 0.000255 over 65 observations. The capital cycle is a pre-war phenomenon in the German data, and the period in which it disappears is the period in which families and states consolidated control.

## Repository layout

```
src/forecast2040/        Python package: models, backtest, metrics, data access
tests/                   Unit tests for models, parsers, configuration
lean_poc/                Lean 4 module with the split theorems
data/raw/                Raw series exactly as downloaded, never edited in place
data/historical/tidy/    German macrohistory extract and the drawdown record used by P10
data/model/              Backtest output, metrics, Diebold-Mariano matrix, P01 and P10 tables
papers/P01_full.md       Manuscript source, P01
papers/P10_full.md       Manuscript source, P10
papers/build/            Rendered manuscripts (PDF, DOCX)
tools/                   Scripts that build the figures, the tables and the PDFs
analysis/                Chapter level analysis scripts
figures/                 Figures used in the dissertation and in the papers
docs/OWNERSHIP.md        The ownership register used by P10
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

Every number in P10 is produced by one script, which writes the three output tables and the summary file:

```bash
python tools/p10_analysis.py
```

The two figures of P10 are rebuilt with:

```bash
python tools/figures_capital.py
python tools/fig_p10_ownership.py
```

The manuscripts are rebuilt from Markdown with:

```bash
python tools/render_pdf.py "$PWD/papers/P01_full.md" "$PWD/papers/build/P01_full.pdf"
python tools/render_pdf.py "$PWD/papers/P10_full.md" "$PWD/papers/build/P10_full.pdf"
```

The Lean module builds with Lean 4.36.0 and has no dependency on Mathlib:

```bash
cd lean_poc
lake build
```

## Data

The German registration series in P01 is Destatis GENESIS table 46131, downloaded on 24 November 2026. The Chinese series is Volkswagen Group deliveries as reported in the group annual reports. Both are public. The SHA256 of each file is recorded in the paper and in `data/manifest.csv`. No series is edited in place; every transformation is applied at run time.

P10 uses the German block of the JST Macrohistory Database release R6, stored as `data/historical/tidy/jst_germany.csv` with SHA256 9037f8602d88f5fcb1ee62526f50a3acda86f4412101500c51aaa9982575902a, and a drawdown record built from the same source, `data/historical/tidy/de_equity_drawdowns.csv` with SHA256 f55d2fc8b7fa1345a5e08d40ede12a419017fc5a4c3f2b5cd8fc662e073de9e8. The credit ratio is missing for 1870, for 1914 to 1926 and for 1944 to 1949, and the gaps are preserved rather than bridged, because bridging them would turn a five year change into a one year change. The ownership register is `docs/OWNERSHIP.md`.

## Results that are archived

- `data/model/metrics_full_destatis_pkw_neuzulassungen_jahre.csv`: thirteen models, MASE, RMSE, MAPE, bias, per-horizon MASE.
- `data/model/backtest_full_destatis_pkw_neuzulassungen_jahre.csv`: 975 forecast errors.
- `data/model/dm_matrix_destatis_pkw_neuzulassungen_jahre.csv`: pairwise Diebold-Mariano p values.
- `data/model/p01_power.csv`, `p01_variance.csv`, `p01_romano_wolf.csv`, `p01_complexity.csv`: the four tables added after review.
- `data/model/p10_lag_correlations.csv`: the correlation at horizons from minus five to plus five years.
- `data/model/p10_subsamples.csv`: the four subperiods and the full sample.
- `data/model/p10_exclusions.csv`: the variants without the war years, without 1923 and after 1950.
- `data/model/p10_summary.json`: every reported statistic in one file, including the power calculation.
- `data/model/capital_cycle_lags.csv` and `data/model/p10_concentration_ladder.csv`: the two figures.

## Citation

If you use the protocol, cite the paper and the archive. The metadata are in `CITATION.cff`. The archive is deposited at Zenodo under DOI 10.5281/zenodo.24516636, which resolves to https://doi.org/10.5281/zenodo.24516636 and covers every released version. The first release, v1.0.0, has its own version DOI, 10.5281/zenodo.24516637.

## Licence

Code is released under the MIT licence. Text, data and figures are released under CC BY 4.0. See `LICENSE`.
