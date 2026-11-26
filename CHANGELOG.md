# Changelog

## v1.3.15, 27 November 2026

P05 version 2.5, reference list correction. The entries for Good (2005) and Gorton and Schmid (2000) are placed in alphabetical order, and the data availability statement no longer names a release tag, so it stays correct for every later version. No result, table, figure or data file changes.

## v1.3.14, 27 November 2026

P05 version 2.5. The peer comparison is rebuilt on 23 European manufacturers and suppliers instead of three German firms, with the exact rank p, a leave-one-out check and a placebo in time. The event level inference is re-estimated with rolling and GARCH(1,1) variance models. The paper adds a power curve, a cumulative average path with a null band and a forest plot, extends the specification curve with an indicator panel, and replaces the 10 log point Bayesian prior with priors of 1, 3 and 5 log points. The raw Yahoo price files are no longer redistributed; the metadata files record the tickers, dates and hashes, and the scripts re-download the raw files if they are absent. The manuscript is 55 pages.

## v1.3.13, 26 November 2026

- Corrected the event level Patell Z in P05. The statistics 1.78 and minus 4.09 are the standardised cumulative abnormal returns, not Patell Z. The event level Patell Z is the standardised cumulative abnormal return divided by the square root of the number of days in the window: 1.03 for Italdesign and minus 2.36 for Everllence. Section 5.2 now defines the event level statistic, and the executive summary, the confidence table, the key numbers table and section 6.2 report the corrected values. The Everllence event still rejects at five percent, with a two sided p value of about 0.018, so the conclusion is unchanged.
- Corrected the count of post hoc extensions from three to four in the abstract and added the Bayesian prior as the fourth question in the introduction to section 6.7.
- Added a peer placebo caveat after Table 8. Porsche SE is the controlling shareholder of Volkswagen AG and is not an independent peer. Excluding it widens the Everllence gap from 3.97 to 4.37 log points. With four firms the smallest possible one sided rank p value is 0.25, so the peer test is descriptive and is not a significance test.
- Softened the interpretation of the peer placebo. It narrows the explanation to firm level news but does not separate financing from governance.
- Added short citations for the 4 September restructuring agreement (Reuters 2026c), the January sale process (Bloomberg 2026a) and the event screen in Table 1.
- Left aligned the Data availability section in the PDF and in the DOCX.
- Rebuilt P05 as version 2.4: 46 pages and 47 references in the PDF, 52 pages in the DOCX rendering. The only numerical change is the event level Patell Z; every other estimate, test statistic, sample and conclusion is unchanged.
- Updated the P05 data availability statement to tag v1.3.13 and added the peer returns file `data/model/p05_extras/peer_cars.csv` to the list.
## v1.3.12, 26 November 2026
- Corrected ten statements in P05 that described differences between logarithmic returns as percentage points. The peer gaps are now reported in log points, the unit used by every table.
- Added the number of valid randomisation draws to section 5.3: 7,511 of the 10,000 draws fall on three trading days and enter the distribution.
- Rewrote section 6.7.3 to describe the five dimensions of the specification curve (benchmark, window, estimation length, event timing and event set) and the 128 resulting designs.
- Corrected the prior scale in appendix A13 to 3 log points, with the decimal equivalent 0.03 stated in parentheses.
- Added a sentence in section 5.2 explaining why the Kolari and Pynnönen (2010) adjustment does not apply to three events in one firm on different dates, and which tests address the remaining dependence.
- Rebuilt P05 as version 2.3: 46 pages and 47 references in the PDF, 51 pages in the DOCX rendering. No estimate, test statistic, sample or conclusion changed.
- Updated the P05 data availability statement to tag v1.3.12.
## v1.3.11, 26 November 2026
- Removed the hardcoded version 1.0.1 and publication date 2026-11-24 from `.zenodo.json`, which had overridden the release tag and date in every Zenodo archive since the first deposit. Zenodo now takes the version and the date from the GitHub release.
- Replaced the P01-specific archive title and description with a repository level title and description that cover the forecasting protocol, the P05 event study and the P10 ownership data.
- Updated the P05 data availability statement to tag v1.3.11 and rebuilt the PDF and DOCX. No result or number changed.
## v1.3.10, 26 November 2026
- Rewrote P05 as version 2.2, 46 pages and 47 references, and retitled it from engineering subsidiaries to engineering businesses because IAV is 50 percent owned and is not a subsidiary.
- Added a one page executive summary before the abstract, a confidence table, a key numbers table, a table of what would change the conclusion, a limitations table and a glossary.
- Corrected six facts. The 7.4 billion euros are expected proceeds to Volkswagen, derived from the 51 percent share and the expected debt, not an enterprise value; the implied 14.5 billion valuation and the market capitalisation arithmetic are removed. The Italdesign release was published after the Xetra close on 10 December 2025, so the first tradable day was 11 December. IAV is 50 percent owned by Volkswagen, Accenture is reported to acquire 70 percent, and IAV announced more than 2,000 job cuts on 6 August 2026. The Italdesign transaction closed on 7 September 2026, not 31 August. The 1 September event was a Reuters report citing Handelsblatt, not a company statement, and the 4 September supervisory board agreement explains the positive five day return. The sale process had been public since January 2026, so the Everllence announcement confirmed the buyer and the terms rather than revealing that a sale was possible.
- Added section 4.4, which documents each correction and keeps the corrected numbers as the only ones reported.
- Added section 6.7 with four post hoc extensions on the real data: the minimum detectable effect, 6.20 log points with three events at 80 percent power; the peer placebo, where the Everllence reaction is 3.97 log points worse than BMW, Mercedes-Benz and Porsche SE; the specification curve, where all 128 designs are negative but no three event design rejects on the BMP test; and the Bayesian posterior, where the probability of a negative mean is 0.70 to 0.82 and every 95 percent credible interval includes zero.
- Added `tools/p05_extras.py` with a check mode that reproduces the published three event mean of minus 1.596 log points before any extension is computed, and added the extension tables, the return series and figures 24 and 25.
- Converted every table to log points so that the tables and the text use one unit, and added the per event standard deviation in log points to the minimum detectable effect table.
- Fixed the PDF title metadata so that the file carries the paper title rather than a renderer placeholder, and improved the DOCX table builder so that header rows repeat, rows do not split and tables stay with their captions.
- Updated the data availability statement to tag v1.3.10 and the public README to the version 2.2 results.
## v1.3.9, 25 November 2026
- Corrected two event level statements in P05 so that they match the standardised statistics. The Italdesign three day reaction is now described as not significant at five percent, with a standardised cumulative abnormal return of 1.78 (the corresponding event level Patell Z is 1.03), rather than as indistinguishable from zero. The Everllence reaction is now described as rejecting the null on its own, with a standardised cumulative abnormal return of minus 4.09 (the corresponding event level Patell Z is minus 2.36), and the text states that a single event cannot separate the programme from other news in the window.
- Updated the data availability tag to v1.3.9 and rebuilt the P05 PDF and DOCX, 30 pages and 42 references.
## v1.3.8, 25 November 2026
- Corrected the P05 sector benchmark. The paper used EXV4.DE, which is the iShares STOXX Europe 600 Health Care UCITS ETF (DE), in place of EXV5.DE, the iShares STOXX Europe 600 Automobiles and Parts UCITS ETF (DE). The fund metadata is now stored with the price file and the analysis refuses a benchmark whose name does not contain Automobiles.
- Recomputed every P05 result. The sector beta is 0.965350, alpha 0.000498, residual standard deviation 0.010959 and R squared 0.631.
- Corrected event results: three day mean cumulative abnormal return minus 1.596 log points, Patell minus 1.452140, BMP minus 0.843318, one positive reaction of three; five day mean minus 4.607 log points, Patell minus 2.964906, BMP minus 1.321359, zero positive; twenty day mean minus 1.097 log points. The randomisation p value is 0.2045 and the placebo percentile 17.56.
- Corrected drift: Volkswagen minus 53.43 log points and minus 41.4 percent in simple terms, sector minus 24.47 and minus 21.7 percent, relative drift minus 28.96 log points with a t statistic of minus 1.62 and a Newey and West t of minus 1.64. The drift is not significant at five percent. BMW lost 45.1 percent, Mercedes-Benz 38.4 percent, BYD 36.4 percent and Tesla 22.3 percent over the same period, and Toyota gained 8.0 percent, so Volkswagen was not the worst performer.
- Rewrote the paper as a case study with a benchmark audit in section 4.2.1. The earlier conclusion, that the market delivered a large negative verdict on the programme, does not survive the correction.
- Rebuilt P05 as version 2.1: 30 pages and 42 references in the PDF, with the corrected figures and tables. Added the benchmark metadata file and updated the data availability statement to v1.3.8.
## v1.3.7, 25 November 2026
- Corrected P10's cross-reference to the companion forecasting paper: the old single-market interval from 2.56 to 3.69 million is replaced by the version 2.5 conformal corridor from 0.61 to 5.10 million around a point forecast of 2.86 million.
- Added the companion paper to the P10 reference list and updated the data availability tag to v1.3.7.
- Rebuilt the P10 PDF and DOCX, 28 pages and 41 references.
## v1.3.6, 25 November 2026
- Rewrote the P01 cover letter for version 2.5: the new title, the seventeen-country panel, thirteen candidate models, 216 origins and 13,610 errors, the timestamped protocol, the negative result, two-way clustering with the Monte Carlo study, the conformal 2040 corridor and the narrow Lean claim.
- Removed the single-market description, the nine theorems, the six tables, the missing figures and the Chinese control that no longer match the paper.
- Added the letter as Markdown and PDF in docs.
## v1.3.5, 25 November 2026
- Bumped the paper to version 2.5 and qualified the title with "on this panel", so the headline claim is explicitly a statement about the sample.
- Labelled the second Monte Carlo design, the common-sample ranking and the Germany-only conformal calibration as post hoc in Section 3.9 and where they are reported.
- Updated CITATION.cff to version 2.5.0.
- Rebuilt the manuscript, 43 pages.
## v1.3.4, 25 November 2026
- Removed the Kraftfahrt-Bundesamt FZ 28 reference, which pointed to electric powertrains while the paper uses the Destatis total registration series.
- Added the linear-scaling sensitivity for the 2040 band: the half-width would triple and the lower bound would fall below zero, which is a further argument for the square root rule.
- Stated that the Monte Carlo components are calibrated on the same panel, so the exercise validates the dependence structure rather than the level of the loss.
- Rebuilt the manuscript, 43 pages.
## v1.3.3, 25 November 2026
- Added a second Monte Carlo design with a country-origin effect estimated from the panel, 0.516 in standard deviation. The two-way test remains conservative at 3.7 percent; the independent and one-way tests remain far above nominal. Both designs are reported in Table 6 and in the abstract.
- Made the Holm statement symmetric: no candidate is significantly better than the benchmark, and three are significantly worse.
- Softened the conclusion from "the answer is no" to "no candidate is shown to beat it", and corrected the list of models that are significantly worse.
- Added the wild cluster bootstrap as a limitation and the differential test as the next step for the Lean link.
- Rebuilt the manuscript, 42 pages.
## v1.3.2, 25 November 2026
- Added a full Monte Carlo section with Table 6: size and power of the independent, one-way, two-way, bootstrap and HLN tests. The variance components are now estimated from the observed loss differentials rather than assumed, and every number in the abstract and in Section 5 was updated.
- Fixed a silent fallback in the first-version replication: damped Holt raised an exception in every call and was replaced by drift, which made the two rows of Table 5 identical. The damping parameter is now estimated, the fallback is recorded, and Table 5 was recomputed.
- Labelled the divergence rule and the ARIMA correction as post hoc in the abstract and in Section 3.9, and disclosed the different cell counts of the models.
- Added a common-sample ranking that drops every cell in which any model diverges: 11,960 errors, same order at the top.
- Corrected Section 6.4: only the random forest is significantly worse after Holm, not the linear trend, the log-linear trend or the six-feature ridge.
- Corrected the first-version interval from ninety to ninety-five percent, and made the comparison of corridor widths explicit about the nominal level.
- Added a Germany-only conformal calibration, the 2020 coverage check and the square root evidence from Table A1.
- Qualified the Lean claim: the module proves the key order and the fold, not the statistical selection, and the Python to Lean link is a specification rather than an extraction.
- Replaced the unsupported claim that single-market studies are common with a design statement, and reframed the Chinese series as a stress case rather than a held-out control.
- Rebuilt the manuscript, 42 pages.

## v1.3.1, 25 November 2026

- Added a generic causality theorem to the Lean module: any forecaster that receives only the prefix is causal, whatever its internal form. The module now has eighteen theorems.
- Added property tests that check the same invariance on the Python runner, and a hash lock with a verification script.
- Added a continuous integration workflow that builds both Lean modules, runs the tests and verifies the frozen inputs.
- Added a paragraph on foundation-model forecasters and the contamination audit they require to the limitations.
- Rebuilt the manuscript, 38 pages.

## v1.3.0, 25 November 2026

P01 version 2.0, the panel paper.

- The sample moves from one German series to a Eurostat panel of seventeen countries, 539 annual observations, 216 origins and 13,610 usable errors.
- The protocol is frozen and timestamped by an independent authority under RFC 3161, serial 0x0A90D1DF, and the token is archived with the protocol.
- The inference is two-way clustered by country and year, with a country-balanced loss, Holm correction and a model confidence set.
- The paper adds a Monte Carlo study of size and power, five robustness checks, split conformal intervals with a coverage table, and a 2040 corridor.
- The Lean module is rewritten: seventeen theorems cover the non-anticipative split, the invariance to appended data, the total order and the uniqueness of the selection.
- Five figures and nine tables replace the single-market exhibits.

## v1.2.0, 25 November 2026

P05, an event study of the Volkswagen divestment programme.

## v1.1.0, 25 November 2026

P10, ownership layers and the capital cycle in German industry, 1870 to 2020.

## v1.0.1, 24 November 2026

P01 version 1.0.1, the single-market paper, with the reference list and the declaration corrected.

## v1.0.0, 24 November 2026

First release: the protocol, the German series and the Lean module of P01 version 1.
