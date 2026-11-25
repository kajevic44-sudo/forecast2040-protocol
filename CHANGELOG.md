# Changelog

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
