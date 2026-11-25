# Changelog
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
