Cover letter, P01

To the Editors  
Technological Forecasting and Social Change

Dear Editors,

I submit for your consideration the manuscript "The benchmark is hard to beat on this panel: a time-stamped protocol with a machine-checked split for long-horizon car demand". The manuscript fits the scope of Technological Forecasting and Social Change because it addresses forecasting governance, reproducibility and long-horizon decision support in a technology-intensive industry.

A long-horizon forecast is only as credible as the procedure that produced it, and that procedure is usually assembled after the results are known. The manuscript fixes the sample, thirteen candidate models, the tuning rules, the loss, the rolling origins, the tests and the interval construction before the panel is evaluated, and the protocol file carries an RFC 3161 timestamp from an independent authority. It then asks whether the winner of a single-market comparison survives when the same protocol is applied to seventeen European markets.

Three features may interest your readership. First, the result is negative and useful: the naive benchmark is first at every horizon, no candidate is significantly better after Holm correction, and the German winner of the earlier single-market version is 5.3 percent worse on the panel. Second, the inference is two-way clustered by country and year, and a Monte Carlo study with components estimated from the panel shows that the independent and one-way tests over-reject while the two-way test holds its size, at the cost of a low power that the paper reports openly. Third, the 2040 corridor is built by split conformal calibration and is four times wider than the 95 percent band of the single-market version, which changes the decision the corridor can support.

The formal part is deliberately narrow. A Lean 4 module proves that the forecast and the scale at an origin depend only on data up to that origin, that any forecaster receiving only the prefix is causal, and that the key order used to break ties has a unique minimum when scores differ. The paper states what the proof does not cover: the statistical tests and the Python implementation are not verified.

The manuscript is 43 pages, with eleven tables and five figures, and is self-contained: the literature review, the equations, the data appendix and the robustness section are all in the paper. Code, data and the Lean module are archived at Zenodo under the concept DOI 10.5281/zenodo.24516636, and the repository is public at github.com/kajevic44-sudo/forecast2040-protocol. To the best of my knowledge, the combination of a timestamped protocol, a multi-market rolling-origin evaluation and a machine-checked information split is unusual in the forecasting literature. The manuscript is not under review elsewhere, and I have no conflict of interest to declare.

I would be glad to respond to any question from the editorial team.

Yours sincerely,

Armin Kajevic  
Ingolstadt, Germany
