# Forecast 2040

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24516636.svg)](https://doi.org/10.5281/zenodo.24516636)

Pre-registered forecasting protocol and long-run ownership research on the German automotive industry.

This repository holds the code, the data and the results behind three papers by Armin Kajevic. The first fixes a forecasting protocol and applies it to German passenger car registrations. The second prices the capital cycle on 151 years of German data and asks who owns the plant when the cycle turns. The third measures how the market priced the Volkswagen divestment programme of 2025 and 2026.

## Papers

**P01. The benchmark is hard to beat on this panel: a time-stamped protocol with a machine-checked split for long-horizon car demand.** The candidate set, the rolling-origin design, the loss, the selection rule and the projection are fixed before any result is seen, and the protocol file carries an RFC 3161 timestamp from an independent authority. Thirteen models are compared on a panel of seventeen European markets from 1991 to 2024, with 539 annual observations, 216 origins and 13,610 usable forecast errors. The naive benchmark is first at every horizon, with a mean absolute scaled error of 1.913 against 1.969 for damped Holt and 2.028 for the theta method, and no candidate beats it after Holm correction. The first version of the study, run on Germany alone, had reported a 19.5 percent gain for a flexible model over the same benchmark; re-estimated with the same model set, the German winner gains 18.5 percent, and on the panel that model is 5.3 percent worse than the benchmark. The rank correlation between the two evaluations is 0.41. The paper reports the inference as it is: a two-way clustered Diebold-Mariano test by country and year, a model confidence set that contains all thirteen candidates, and a Monte Carlo study in which the independent test rejects a true null in 64 percent of samples, one-way clustering in 16 percent, and two-way clustering between 3.7 and 4.7 percent, depending on whether a country-origin effect is present. Split conformal intervals cover at least their nominal level at every horizon, and the 2040 projection is 2.86 million registrations with a 90 percent band from 0.61 to 5.10 million, four times wider than the 95 percent band the single-market version reported. The discrete part of the protocol is written in Lean 4: eighteen theorems establish that the forecast and the scale at an origin depend only on data up to that origin, that any forecaster receiving only the prefix is causal, that appending future data leaves the values unchanged, and and that the lexicographic key order is a total order whose fold returns a unique minimum when scores differ.

**P10. Who owns the plant and when they arrived: ownership layers and the capital cycle in German industry, 1870 to 2020.** Ownership is treated as a dated event rather than a structure. The paper builds a register of 63 ownership events between 1937 and 2026, prices the capital cycle on 151 years of German data, and reports both halves of the result. The annual change in bank credit to gross domestic product correlates with the real total equity return five years later at minus 0.303589 over 123 observations, with a slope of minus 1.020070 and a t statistic of minus 3.545150. The relation does not survive the removal of the war years, where the correlation falls to minus 0.095086, and it is absent after 1950, where the correlation is 0.000255 over 65 observations. The capital cycle is a pre-war phenomenon in the German data, and the period in which it disappears is the period in which families and states consolidated control.

**P05. Pricing the sale of engineering businesses: an event study of the Volkswagen divestment programme, 2025 to 2026.** The paper measures the returns around four disclosures: the sale of a majority of Italdesign to UST, an exclusive arrangement to sell 51 percent of Everllence to Bain Capital with expected proceeds of about 7.4 billion euros, the agreement to transfer 70 percent of IAV to Accenture, and the Reuters report of 1 September 2026 that Volkswagen expected to sell 8.5 million vehicles and planned further divestments. The design was fixed before any return was computed. The three primary events produce a mean cumulative abnormal return over the three day window of minus 1.60 log points, with a Patell statistic of minus 1.45, a Boehmer-Musumeci-Poulsen t of minus 0.84 and one positive reaction out of three. At the event level the Patell Z is 1.03 for Italdesign and minus 2.36 for Everllence, so only the Everllence announcement rejects on its own under the pre-specified test. Over the five days after the event the mean is minus 4.61 log points, the Patell statistic is minus 2.96 and the BMP t is minus 1.32. The randomisation test gives a two sided p value of 0.205 and the placebo places the observed mean at the 17.6th percentile. Between 9 December 2025 and 20 November 2026 the preference share lost 41.4 percent while the sector lost 21.7 percent, a relative drift of minus 28.96 log points with a t statistic of minus 1.62, which is not significant at five percent and is smaller than the losses of BMW and Mercedes-Benz in simple terms. Six post hoc extensions bound the inference. The minimum detectable effect with three events is 6.20 log points at 80 percent power, four times the observed mean, and the power curve shows that about 14 events would be needed to detect the observed effect. A peer comparison with 23 European manufacturers and suppliers places the Everllence reaction of minus 4.49 log points 3.53 log points below the peer mean, but Volkswagen ranks sixth of 24 and the exact rank p is 0.25; among nine European vehicle makers it ranks third of 10, and it is the most negative only among the German firms. The same gap lies at the 6.3rd percentile of 462 three day windows in 2025 and 2026, which is suggestive but not significant at five percent. A specification curve of 128 designs produces a negative mean in every case, but no three event design rejects on the BMP test. A Bayesian posterior with priors of 1, 3 and 5 log points places the probability of a negative mean between 0.70 and 0.81 and includes zero in every 95 percent credible interval. A GARCH(1,1) model raises the daily volatility at Everllence from 1.10 to 1.88 log points and lowers the event level z from minus 2.36 to minus 1.38, so the one rejection in the sample is not robust to time varying volatility. Section 4.4 documents six corrections: the benchmark audit that replaced the health care fund EXV4.DE with the automobiles fund EXV5.DE and moved the beta from 0.292 to 0.965, the Everllence proceeds that are not an enterprise value, the Italdesign release after the Xetra close, the IAV ownership and job cuts, the Italdesign closing on 7 September, and the 1 September press report whose five day window contains the 4 September restructuring agreement. The paper is a case study, not a rejection.

## Repository layout

```
src/forecast2040/        Python package: models, backtest, metrics, data access
tests/                   Unit tests for models, parsers, configuration
lean_poc/                Lean 4 module with the split theorems of P01 version 1
lean_p01/                Lean 4 module of P01 version 2: causality and selection
protocol/                Frozen protocol of P01 version 2 and its RFC 3161 token
data/raw/                Raw series exactly as downloaded, never edited in place
data/historical/tidy/    German macrohistory extract and the drawdown record used by P10
data/model/              Backtest output, metrics, Diebold-Mariano matrix, P01 and P10 tables
papers/P01_full.md       Manuscript source, P01
papers/P10_full.md       Manuscript source, P10
papers/P05_full.md       Manuscript source, P05
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
The panel version of P01 is reproduced from the Eurostat extract in four steps, in this order:
```bash
python tools/p01_panel_data.py      # download, hash and tidy the panel
python tools/p01_protocol.py        # thirteen models on 216 origins
python tools/p01_inference.py       # clustered tests, confidence set, conformal band
python tools/p01_robustness.py      # crisis, window, loss, leave-one-out, penalty
python tools/p01_monte_carlo.py     # size and power of the five tests
python tools/p01_figures.py         # the five figures of the paper
```
The property tests and the frozen-input check run on every push, and can be run locally:
```bash
pytest -q tests
python tools/verify_hashes.py
```
The timestamp of the protocol is verified with one command:
```bash
openssl ts -verify -data protocol/p01_protocol.yaml -in protocol/p01_protocol.tsr \
  -CAfile protocol/tsa_cacert.pem -untrusted protocol/tsa.crt
```

Every number in P10 is produced by one script, which writes the three output tables and the summary file:

```bash
python tools/p10_analysis.py
```

Every number in P05 is produced by three scripts. The first downloads the three benchmark series once, writes the event tables, the return series and the two event figures. The second reproduces the minimum detectable effect, the three firm peer set, the specification curve and the Bayesian posterior. The third downloads the 23 firm peer set once, and reproduces the five peer sets, the leave-one-out table, the placebo in time, the GARCH and rolling volatility table, the cumulative average path, the power curve and the forest plot. Both extension scripts check that the base specification matches the published mean before they compute any extension:

```bash
python tools/p05_analysis.py
python tools/p05_extras.py
python tools/p05_v25.py
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
python tools/render_pdf.py "$PWD/papers/P05_full.md" "$PWD/papers/build/P05_full.pdf"
```

The Lean module builds with Lean 4.36.0 and has no dependency on Mathlib:

```bash
cd lean_poc
lake build
```

## Data

The panel in P01 version 2 is Eurostat dataset road_eqr_carmot, downloaded on 24 November 2026, with raw SHA256 27c1edcd49c013e2babdfc6e8798f212bbd65f316281a3ddf06ec86acfe7e91a. The sample rule keeps countries with at least twenty-five consecutive annual observations ending in 2024 inside 1991 to 2024, which gives seventeen countries and 539 observations. The German registration series in the single-market version is Destatis GENESIS table 46131, downloaded on 24 November 2026. The Chinese series is Volkswagen Group deliveries as reported in the group annual reports. Both are public. The SHA256 of each file is recorded in the paper and in `data/manifest.csv`. No series is edited in place; every transformation is applied at run time.

P10 uses the German block of the JST Macrohistory Database release R6, stored as `data/historical/tidy/jst_germany.csv` with SHA256 9037f8602d88f5fcb1ee62526f50a3acda86f4412101500c51aaa9982575902a, and a drawdown record built from the same source, `data/historical/tidy/de_equity_drawdowns.csv` with SHA256 f55d2fc8b7fa1345a5e08d40ede12a419017fc5a4c3f2b5cd8fc662e073de9e8. The credit ratio is missing for 1870, for 1914 to 1926 and for 1944 to 1949, and the gaps are preserved rather than bridged, because bridging them would turn a five year change into a one year change. The ownership register is `docs/OWNERSHIP.md`. P05 uses the daily panel in `data/panel/panel_daily.csv`, three benchmark series downloaded from Yahoo Finance on 25 November 2026, and 23 European peers downloaded on 26 November 2026. The raw Yahoo price files are not redistributed, because the provider's terms do not permit redistribution. The metadata files `data/raw/p05_benchmarks_metadata.json` and `data/raw/p05_peers_broad_metadata.json` record the tickers, the download dates, the row counts and the SHA256 of each raw file, and the scripts re-download the raw files if they are absent.

## Results that are archived

- `data/model/metrics_full_destatis_pkw_neuzulassungen_jahre.csv`: thirteen models, MASE, RMSE, MAPE, bias, per-horizon MASE.
- `data/model/backtest_full_destatis_pkw_neuzulassungen_jahre.csv`: 975 forecast errors.
- `data/model/dm_matrix_destatis_pkw_neuzulassungen_jahre.csv`: pairwise Diebold-Mariano p values.
- `data/model/p01_power.csv`, `p01_variance.csv`, `p01_romano_wolf.csv`, `p01_complexity.csv`: the four tables added after review of version 1.
- `data/model/p01_panel_results.csv`: 13,610 cell-level forecast errors of the panel version.
- `data/model/p01_panel_overall.csv`, `p01_panel_macro.csv`: the ranking and its horizon profile.
- `data/model/p01_dm_table.csv`: country-balanced loss differentials, two-way clustered standard errors and Holm p values.
- `data/model/p01_horizon_dm.csv`, `p01_gw.csv`: horizon tests and the Giacomini-White test.
- `data/model/p01_conformal.csv`, `p01_forecast_2040.csv`: coverage by horizon and the projection.
- `data/model/p01_country_gain.csv`: the map of gains and losses by country.
- `data/model/p01_v1_comparison.csv`: the first-version model set re-estimated on Germany and on the panel.
- `data/model/p01_monte_carlo.csv`, `p01_robustness.json`: size and power, and the five robustness checks.
- `data/model/p10_lag_correlations.csv`: the correlation at horizons from minus five to plus five years.
- `data/model/p10_subsamples.csv`: the four subperiods and the full sample.
- `data/model/p10_exclusions.csv`: the variants without the war years, without 1923 and after 1950.
- `data/model/p10_summary.json`: every reported statistic in one file, including the power calculation.
- `data/model/capital_cycle_lags.csv` and `data/model/p10_concentration_ladder.csv`: the two P10 figures.
- `data/model/p05_events.csv`, `p05_tests.csv`, `p05_robustness.csv`: the event study tables of P05.
- `data/model/p05_summary.json`: every P05 statistic in one file.
- `data/model/p05_extras/peer_broad_summary.csv`: the five peer sets at each event, with the gap, rank and exact rank p.
- `data/model/p05_extras/peer_broad_leave_one_out.csv`: the all peer gap and rank when each firm is removed.
- `data/model/p05_extras/peer_broad_placebo.csv`: the peer gap distribution in time.
- `data/model/p05_extras/garch.csv`: event level z under Patell, rolling and GARCH variance models.
- `data/model/p05_extras/caar_path.csv`: the cumulative average path and its null band.
- `data/model/p05_extras/power_curve.csv`: power for 3 to 50 events and four effect sizes.
- `data/model/p05_extras/forest.csv`: event level confidence intervals under constant variance and GARCH.
- `data/model/p05_extras/v25_summary.json`: every v2.5 statistic in one file.

## Citation

If you use the protocol, cite the paper and the archive. The metadata are in `CITATION.cff`. The archive is deposited at Zenodo under DOI 10.5281/zenodo.24516636, which resolves to https://doi.org/10.5281/zenodo.24516636 and covers every released version. The single-market version, v1.0.1, has its own version DOI, 10.5281/zenodo.24516796. The panel version, v2.0.0, corresponds to release v1.3.0 of this repository; its version DOI is assigned when the release is deposited at Zenodo, and the concept DOI above resolves to the latest deposit once it is published.

## Licence

Code is released under the MIT licence. Text, data and figures are released under CC BY 4.0. See `LICENSE`.
