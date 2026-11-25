# Pricing the sale of engineering businesses: an event study of the Volkswagen divestment programme, 2025 to 2026

Armin Kajevic

Ingolstadt, Germany

ORCID 0009-0004-1241-8313

Version 2.2, 26 November 2026

## Executive summary

### The market did not deliver a verdict on the divestment programme

Between December 2025 and September 2026 Volkswagen sold a majority of Italdesign, agreed to sell 51 percent of Everllence and to transfer 70 percent of IAV to Accenture, and was reported to be planning further divestments. The question for a board is not whether the sales are strategically sensible. It is whether the market priced them as value creation, as a financing necessity, or as a signal that the group is selling assets it cannot manage.

The answer is negative but small, and the paper is explicit about what it can and cannot see. Across the three primary events, the average three day abnormal return is minus 1.60 log points, or about minus 1.6 percent. The Patell statistic is minus 1.45 and the BMP t is minus 0.84, so the estimate is not statistically distinguishable from zero. The five day average is minus 4.61 log points, with a Patell statistic of minus 2.96 and a BMP t of minus 1.32; one test rejects, the other does not. A randomisation test gives a two sided p value of 0.205, and the observed mean sits at the 17.6th percentile of all three day windows between 2017 and 2024.

The most important number in the paper is not the estimate. It is the minimum detectable effect. With three events and a residual standard deviation of 1.10 log points a day, the design can detect a three day mean reaction of 6.20 log points at 80 percent power. The observed reaction is one quarter of that. A failure to reject is therefore not evidence that the market approved. It is evidence that the sample cannot see a reaction of the size that the programme would plausibly produce.

The Everllence disposal is the cleanest disclosure, and it carries the interpretation. The group announced an exclusive arrangement to sell 51 percent to Bain Capital, with expected proceeds of about 7.4 billion euros, a book value of 3.4 billion euros, revenue of 4.9 billion euros and about 16,000 employees. The preference share fell 4.49 log points over three days, and the event level Patell statistic is minus 4.09, so this announcement rejects the null on its own. The peer placebo sharpens the point: BMW, Mercedes-Benz and Porsche SE moved by minus 0.53 log points on average over the same window, so the Volkswagen reaction is about 4.0 percentage points worse than its closest peers. The reaction is specific to the seller, not to the sector.

The annual record is weaker than the announcement effects. Between 9 December 2025 and 20 November 2026 the preference share lost 41.4 percent, the sector lost 21.7 percent, and the relative drift is minus 28.96 log points with a t statistic of minus 1.62. The drift is not significant, and it is not unusual: BMW lost 45.1 percent and Mercedes-Benz 38.4 percent over the same period. The programme year was a bad year for the German car industry, not a unique verdict on Volkswagen.

What does this mean for a decision? First, do not read the absence of a significant reaction as approval. The design cannot detect a reaction below 6.2 log points, and the point estimate is negative. Second, the Everllence reaction is the one robust signal: it is large relative to peers and rejects on its own. If the group sells another business of similar size, the market will likely price the proceeds and the retained stake, not the strategic narrative. Third, communicate the use of proceeds. The paper cannot separate financing from governance, but the negative sign is consistent with a market that expects the cash to be retained for an uncertain transition. A clear commitment on debt reduction, buybacks or investment would change the signal that the next sale sends.

### Confidence in the findings

| Finding | Confidence | Why |
|:--|:--|:--|
| The three day mean reaction is negative | Moderate | The point estimate is negative in every specification, but it is not significant |
| The five day mean reaction is negative | Weak | The Patell test rejects, the BMP and exact tests do not |
| The Everllence reaction is specific to Volkswagen | Moderate | Event level Patell minus 4.09; peer gap minus 3.97 percentage points |
| The drift is negative but not significant | Weak | t statistic minus 1.62; BMW and Mercedes also fell |
| The market approved the programme | Not supported | No specification produces a positive significant mean |
| The benchmark correction changes the conclusion | Strong | Beta moves from 0.292 to 0.965 and the drift from minus 64.45 to minus 28.96 |

### Key numbers

| Item | Value | Unit | Note |
|:--|--:|:--|:--|
| Three day mean CAR, three primary events | -1.60 | log points | About minus 1.58 percent in simple terms |
| Patell statistic | -1.45 | statistic | Two sided p 0.146 under the normal approximation |
| BMP t | -0.84 | statistic | Two sided p 0.488 with two degrees of freedom |
| Five day mean CAR | -4.61 | log points | Patell minus 2.96, BMP minus 1.32 |
| Randomisation p, two sided | 0.205 | probability | 7,511 pseudo event sets |
| Placebo percentile | 17.6 | percentile | 2,004 three day windows |
| Minimum detectable effect, three events | 6.20 | log points | 80 percent power, five percent level |
| Everllence three day CAR | -4.49 | log points | Event level Patell minus 4.09 |
| Peer mean at Everllence | -0.53 | log points | BMW, Mercedes-Benz and Porsche SE |
| Relative drift | -28.96 | log points | t minus 1.62, Newey and West minus 1.64 |
| Sector beta | 0.965 | coefficient | R squared 0.631 |

### What would change the conclusion

The conclusion would become stronger if a fourth disposal of similar size produced a three day reaction below minus 6.2 log points, because the mean would then become detectable. It would weaken if the next sale produced a positive reaction after the group announced a concrete use of proceeds, such as debt reduction or a buyback. It would become sector-wide rather than firm-specific if the peer placebo at the next event showed a similar negative reaction for BMW, Mercedes-Benz and Porsche SE. It would be overturned if a corrected benchmark or a longer estimation window produced a positive and significant mean across the three events.

### Limitations at a glance

| Limitation | Consequence for the conclusion | What would change it |
|:--|:--|:--|
| Three events in one firm | The effective number of independent observations is one; exact tests cannot reject below 0.25 | Add earlier disposals and a matched control group |
| Event dates | The IAV and programme events are press reports; Italdesign was released after the close | Timestamped releases and intraday data |
| Confounders | IAV job cuts, the Everllence clearance and the 4 September restructuring agreement | Narrower windows and event specific controls |
| Benchmark | An exchange traded fund rather than the index | Constituent level index data |
| Instrument | The preference share carries no vote | Ordinary share data, if liquid enough |
| Drift | Earnings, tariffs, China and works council news | A causal design with a synthetic control |

### Glossary

CAR. Cumulative abnormal return, the sum of daily returns that the market model does not explain.

Patell Z. A standardised test that assumes the events are independent.

BMP t. A cross-sectional test that allows the variance to change at the event.

MDE. The smallest true effect that the design can detect with 80 percent power at a five percent significance level.

Randomisation p. The share of pseudo event sets whose mean is at least as extreme as the observed mean.

Placebo percentile. The rank of the observed mean among all windows in a period without the event.

Specification curve. The distribution of estimates across all reasonable combinations of design choices.

Bayesian posterior. The probability distribution of the effect after combining the data with a prior.

Log point. A change in the natural logarithm of price; one log point is about one percent for small changes.

## Abstract

Between December 2025 and September 2026 the Volkswagen Group announced the sale of a majority of Italdesign to UST, an exclusive arrangement to sell 51 percent of Everllence to Bain Capital with expected proceeds of about 7.4 billion euros, the agreement to transfer 70 percent of IAV to Accenture, and a reported plan for further divestments. This paper measures the returns around those disclosures with a design fixed before any return was computed: logarithmic daily total returns, a market model estimated once on the 250 trading days ending 20 trading days before the first event, the STOXX Europe 600 Automobiles and Parts as the primary benchmark, and Patell, Boehmer-Musumeci-Poulsen, exact sign and rank tests, a randomisation test on the observed calendar spacing and a placebo distribution. The three primary announcements produce a mean cumulative abnormal return over the three day window of minus 1.60 log points, with a Patell statistic of minus 1.45, a Boehmer-Musumeci-Poulsen t of minus 0.84 and one positive reaction out of three. Over the five days after the event the mean is minus 4.61 log points, the Patell statistic is minus 2.96 and the BMP t is minus 1.32. The randomisation test gives a two sided p value of 0.205, and the observed mean lies at the 17.6th percentile of all three day windows between 2017 and 2024. Three post hoc extensions bound the inference. The minimum detectable effect with three events is 6.20 log points at 80 percent power, four times the observed mean. A peer placebo shows that the Everllence reaction of minus 4.49 log points was 3.97 percentage points worse than BMW, Mercedes-Benz and Porsche SE, so it is specific to the seller. A specification curve of 128 designs produces a negative mean in every case, but no three event design rejects on the BMP test. A Bayesian posterior with three priors places the probability of a negative mean between 0.70 and 0.82 and includes zero in every 95 percent credible interval. The annual record is also weaker than it first appears: between 9 December 2025 and 20 November 2026 the preference share lost 41.4 percent in simple terms, the sector lost 21.7 percent, and the relative drift is minus 28.96 log points with a t statistic of minus 1.62. The drift is not significant at five percent and is not unusual relative to peers: BMW lost 45.1 percent, Mercedes-Benz 38.4 percent and BYD 36.4 percent over the same period. A benchmark audit shows that an earlier version of the paper used a health care exchange traded fund in place of the automobile sector fund; the correction moves the beta from 0.292 to 0.965 and the drift from minus 64.45 to minus 28.96 log points. The earlier conclusion does not survive. The paper's contribution is a transparent case study of what a small event set can and cannot identify, and a benchmark audit checklist for event studies.

Keywords: event study, divestiture, portfolio restructuring, engineering services, Volkswagen, ownership concentration, minimum detectable effect, specification curve, benchmark validation, reproducibility

JEL codes: G14, G34, L62, C11

## 1 Introduction

The Volkswagen Group has spent two years converting engineering capacity into cash and software. In December 2025 Audi agreed to sell a majority of Italdesign Giugiaro to the American design and engineering firm UST. In June 2026 the group entered an exclusive arrangement to sell 51 percent of Everllence, the former MAN Energy Solutions, to Bain Capital, with expected proceeds of about 7.4 billion euros. In August 2026 it was reported that 70 percent of IAV, an engineering company in which Volkswagen holds 50 percent, would pass to Accenture. On 1 September 2026 Reuters reported, citing Handelsblatt, that the group expected to sell 8.5 million vehicles in 2026 and planned further asset divestments. The pattern is a substitution rather than a retreat: the group sells styling and engineering, which it has in surplus, and buys software, which it lacks.

Whether that substitution creates value is a question the share price answers every day, and the four disclosures are occasions on which the answer can be read. This paper reads it with a design that was fixed in advance. The estimation window, the benchmark, the event windows, the abnormal return definition, the standardisation and the test statistics are all specified before any return is computed. The paper therefore does two things at once: it reports what the market did, and it demonstrates a discipline in which the reporting rule cannot be chosen after the result is known.

The result is weaker than the programme's scale suggests. On the event dates the reaction is negative but imprecise. The three primary events produce a mean cumulative abnormal return of minus 1.60 log points over the three day window, with a Patell statistic of minus 1.45 and a BMP t of minus 0.84. Over the five days after the event the mean is minus 4.61 log points, the Patell statistic is minus 2.96 and the BMP t is minus 1.32. The exact sign test cannot reject, because only one of the three reactions is positive and three observations cannot produce a two sided p value below 0.25 by any sign or rank route. A randomisation test with 7,511 pseudo event sets gives a two sided p value of 0.205, and a placebo places the observed mean at the 17.6th percentile. The three day effect is not statistically distinguishable from the ordinary variation of the stock. The five day window is stronger on the Patell criterion and weaker on the BMP, and the paper reports both rather than choosing the one that rejects.

The paper then asks what the design could have seen. The minimum detectable effect with three events is 6.20 log points at 80 percent power, four times the observed mean. That number changes the interpretation of the failure to reject: the sample is blind to an effect of the size that the programme would plausibly produce. A peer placebo shows that the Everllence reaction was 3.97 percentage points worse than BMW, Mercedes-Benz and Porsche SE, so it is specific to the seller rather than to the sector. A specification curve of 128 designs produces a negative mean in every case, but no three event design rejects on the BMP test. A Bayesian posterior with three priors places the probability of a negative mean between 0.70 and 0.82 and includes zero in every 95 percent credible interval. The conclusion is therefore narrower than the first version's: the sign is robust, the magnitude is small, and the one firm specific signal is the Everllence sale.

The drift is also weaker than it first appears. Between 9 December 2025 and 20 November 2026 the preference share lost 41.4 percent in simple terms, the sector lost 21.7 percent, and the relative drift is minus 28.96 log points with a t statistic of minus 1.62 and a Newey and West t of minus 1.64. The drift is not significant at five percent. It is also not specific to Volkswagen: BMW lost 45.1 percent, Mercedes-Benz 38.4 percent, BYD 36.4 percent and Tesla 22.3 percent over the same period, while Toyota gained 8.0 percent. The equal weighted peer average lost 29.0 percent, and Volkswagen's gap against that average is minus 19.2 log points. The programme year was a bad year for the German car industry, not a unique verdict on Volkswagen.

The correction that produces these numbers is part of the paper. An earlier version used EXV4.DE as the automobile sector benchmark. EXV4.DE is the iShares STOXX Europe 600 Health Care UCITS ETF (DE), not the Automobiles and Parts fund; the correct ticker is EXV5.DE. The old series had a correlation of 1.0000 with EXV4.DE and 0.4229 with EXV5.DE, and its metadata named health care. The error produced a beta of 0.292 against the sector instead of 0.965, and a drift of minus 64.45 log points instead of minus 28.96. The earlier version's conclusion, that the market delivered a large negative verdict on the programme, does not survive the correction. The paper reports the weaker result and describes the audit that found the error, because a benchmark that is not what it claims to be is a failure mode that event studies rarely check.

Five further corrections separate this version from the first. The 7.4 billion euros is expected proceeds to Volkswagen, derived from the 51 percent share and the expected debt, not an enterprise value; the implied enterprise value of 14.5 billion and the market capitalisation arithmetic that followed from it are removed. The Italdesign release was published after the Xetra close on 10 December 2025, so the first tradable day was 11 December. IAV is 50 percent owned by Volkswagen, not a subsidiary, and it announced more than 2,000 job cuts on 6 August 2026. The Italdesign transaction closed on 7 September 2026, not 31 August, and the 1 September event was a press report rather than a company statement; the 4 September restructuring agreement, not the report, explains the positive five day return around that date. Section 4.4 documents each correction.

The paper makes three contributions. The first is empirical: it prices a divestment programme that has no disclosed transaction prices, using the only public signal that exists, which is the return on the liquid instrument, and it shows that the programme's announcement effects are negative but statistically weak. The second is methodological: it shows what a small, clustered event set can and cannot identify, and it reports the arithmetic of the limit rather than a p value that the sample cannot support. The third is a benchmark audit: it documents how a wrong sector series reverses the conclusion, and it proposes a simple checklist that would have caught the error before any return was computed.

The rest of the paper is organised as follows. Section 2 reviews the event study method, the divestiture evidence and the German ownership literature, and states the gap. Section 3 describes the programme and the four events. Section 4 describes the data, the benchmark and the audit. Section 5 sets out the design, the estimators and the decision rules. Section 6 reports the results, the robustness checks and the placebo. Section 7 interprets them against the three competing explanations. Section 8 states the limitations and section 9 concludes.

## 2 Literature

### 2.1 The event study and its small sample problem

The event study rests on the assumption that prices impound public information quickly and unbiasedly. Fama, Fisher, Jensen and Roll (1969) introduced the residual approach for stock splits, and MacKinlay (1997) formalised the market model, the estimation window and the cumulative abnormal return that almost every subsequent paper uses. Brown and Warner (1985) show that the standard procedures are well specified with daily data when the event does not change the variance of the residual, and that the simple market model is hard to beat. Fama (1998) reviews the long-run evidence and warns that abnormal return estimates are sensitive to the benchmark and to the method, a warning that applies with more force to the drift in section 6.6 than to the three day windows. Lyon, Barber and Tsai (1999) show that long-run tests depend on the reference portfolio and on the standardisation, which is why the drift is reported against the sector, the broad index, the DAX and an equal weighted peer group rather than against a single benchmark.

The qualifications matter more for this paper than the baseline. Boehmer, Musumeci and Poulsen (1991) show that event induced variance inflates the test statistic and propose a standardisation that uses the cross section of event windows. Kolari and Pynnönen (2010) show that cross sectional correlation, which arises when events cluster in calendar time or in an industry, inflates the Patell statistic even after the Boehmer correction, and they propose an adjustment based on the average pairwise correlation of the abnormal returns. Ahern (2009) shows that sample selection, meaning the choice of which events enter, can generate spurious significance in small samples. Kothari and Warner (2007) survey the econometrics and conclude that the tests are reliable in samples of hundreds and unreliable in samples of ten.

The literature that uses three events is thin, and for good reason. With three observations the cross sectional statistic has two degrees of freedom and a two sided five percent critical value of 4.303. The exact sign test attains a two sided p value of 0.25 when all three reactions have the same sign, and the exact Wilcoxon test attains 0.25 as well. No design can extract a conventional rejection from three events unless the effect is enormous relative to the residual variance. This paper does not pretend otherwise. It reports the estimates, the standardised statistics, the exact tests, the randomisation distribution and the placebo, and it treats the absence of a rejection as information about the design rather than about the world.

### 2.2 What divestitures do to the seller's price

The sell-off record is consistent in sign and modest in size. Alexander, Benson and Kampmeyer (1984) find positive announcement returns for voluntary sell-offs. Hite, Owers and Rogers (1987) report average abnormal returns of 1.66 percent for sellers and 0.83 percent for buyers in a sample of asset sales. John and Ofek (1995) tie the gain to increased focus: the sellers that divest unrelated segments gain more, and the gain is larger when the proceeds are used to reduce debt or to invest in the remaining business. Lang, Poulsen and Stulz (1995) show that asset sales that raise financing for the seller gain less than sales that restructure the portfolio, and that the market discounts proceeds that are retained for an uncertain use.

Comment and Jarrell (1995) show that the stock market rewarded focus increasing changes in the 1980s, which is the historical basis for the refocusing prior. The refocusing interpretation rests on a diversification discount. Lang and Stulz (1994) and Berger and Ofek (1995) document that diversified firms trade at a discount to a portfolio of pure play comparables, and Desai and Jain (1999) and Dittmar and Shivdasani (2003) show that separations which increase focus create value. The mechanism is that a focused firm allocates capital better and is monitored more effectively, which is the argument that Jensen (1986) makes about free cash flow and that Jensen (1993) applies to the conglomerate.

Andrade, Mitchell and Stafford (2001) summarise the merger evidence and show that the announcement returns to bidders are close to zero on average and negative for the largest deals. Mulherin and Boone (2000) compare acquisitions and divestitures in the same sample and find that the wealth effects of divestitures are larger and more uniformly positive than those of acquisitions, which is the benchmark against which the Volkswagen programme should be read. The merger literature supplies the counterweight. Moeller, Schlingemann and Stulz (2004) show that acquirers of large targets lose value, Fuller, Netter and Stegemoller (2002) show that the loss is concentrated in public targets, and Betton, Eckbo and Thorburn (2008) show that the announcement return to the bidder depends on the competition for the target and on the method of payment. Eckbo and Thorburn (2008) survey the evidence and conclude that the average announcement effect of a divestiture is positive but small, and that the cross section is explained by the use of proceeds and by the relatedness of the divested unit.

Volkswagen is not a conglomerate selling an unrelated division. It is selling a capability on which its own development depends, to buyers that intend to sell it back to the industry as a service. Italdesign grew revenue by more than 15 percent a year from 2022 to 2025, employed about 1,300 people across ten sites and had developed more than 300 production models (Audi AG 2025; AutoNext 2026). IAV is an engineering company in which Volkswagen holds 50 percent; it employs several thousand engineers and works on powertrain, electronics and software for the group and for third parties (Reuters 2026d). A sale of that kind is closer to a sale and leaseback of a capability than to the disposal of a diversification mistake, and the refocusing premium may therefore be smaller or absent.

### 2.3 Ownership, liquidity and the instrument

German ownership adds a measurement problem that the event study literature rarely faces. Blockholders hold most of the votes (Franks and Mayer 2001; Gorton and Schmid 2000), and at Volkswagen the ordinary shares carry the votes while the preference shares carry the dividend. At 31 December 2025 Porsche Automobil Holding held 53.3 percent of the votes, the State of Lower Saxony 20.0 percent and Qatar Holding 17.0 percent, leaving a free float of 9.7 percent (Volkswagen AG 2026). Three holders controlled 90.3 percent of the votes.

The liquid instrument is the preference share. It carries no vote, so its price measures what minority capital expects from the use of proceeds rather than what a control buyer would pay for the asset or for the firm. The ordinary share is illiquid and its price is not informative at a daily frequency. The design therefore uses the preference share, and the interpretation is limited to a minority's valuation. La Porta, Lopez-de-Silanes and Shleifer (1999) and Faccio and Lang (2002) show that this structure is the European norm rather than a German exception, and Dyck and Zingales (2004) show that the private benefits of control are priced in exactly this kind of structure. Shleifer and Vishny (1997) provide the framework in which the controlling holder's horizon differs from the minority's, which is the link between this paper and the ownership literature.

### 2.4 The gap

Three gaps follow. The first is empirical: there is no event study of the current Volkswagen divestment programme, because the programme is recent and because two of the four events have no disclosed price. The second is methodological: the divestiture literature reports averages over hundreds of events and says nothing about what can be learned from four events in one firm inside nine months. The third is interpretive: the refocusing hypothesis predicts a positive reaction to the sale of a non core unit, and the financing hypothesis predicts a negative reaction to a sale whose proceeds are retained, and the two have not been confronted in a case where the divested unit is a profitable capability rather than a diversification mistake.

This paper fills the three gaps with a pre-specified design, a small sample, and an explicit statement of what the sample cannot support. Its contribution is not a new test statistic. It is the combination of a dated, reproducible event study with an honest account of the inference that four events can bear, applied to a programme that is still running and that will be judged by history.

## 3 The programme and the four events

### 3.1 What was sold

Italdesign Giugiaro is the styling house that Audi acquired in 2010 and that drew, among others, the first Volkswagen Golf and the Alfa Romeo Brera. Audi announced on 10 December 2025 that UST, an American engineering and design firm, would acquire a majority stake, that Lamborghini would retain a minority, and that the price would not be disclosed (Audi AG 2025). The release was published after the Xetra close, so the first trading day on which the information could be traded was 11 December 2025. The transaction completed on 7 September 2026 (UST 2026).

Everllence is the former MAN Energy Solutions, the large engine and marine propulsion business that Volkswagen put under the Everllence name in 2024. On 24 June 2026 the group announced an exclusive arrangement with Bain Capital for the sale of 51 percent, retaining 49 percent in the medium term. The release states that the leveraged buy-out generates expected proceeds of about 7.4 billion euros for Volkswagen, derived from the 51 percent share and the expected debt, and that the book value of Everllence was about 3.4 billion euros at 31 May 2026. It also reports revenue of 4.9 billion euros and about 16,000 employees (Volkswagen Group 2026; Reuters 2026a). The European Commission cleared the transaction in case M.12527 on 12 August 2026 (European Commission 2026). The sale process had been public since January 2026, and Bloomberg reported next-round bidders in April, so the announcement confirmed the buyer and the terms rather than revealing that a sale was possible (Bloomberg 2026a).

IAV is an engineering company in which Volkswagen holds 50 percent, with several thousand engineers working on powertrain, electronics and software. On 6 August 2026 IAV announced that it would reduce its German workforce from more than 5,000 to 2,970 by the end of 2027 (IAV 2026). On 11 August 2026 Automotive News Europe reported that Accenture would acquire 70 percent, with Volkswagen retaining 30 percent (Automotive News Europe 2026). Neither company had confirmed the report at the time of writing, and no price was disclosed.

The fourth event is neither a transaction nor a company statement. On 1 September 2026 Reuters reported, citing Handelsblatt, that Volkswagen expected to sell 8.5 million vehicles in 2026 and planned asset divestments (Reuters 2026b). The report was published at 17:09 Central European Time, 21 minutes before the Xetra close. Three days later, late on 3 September, the supervisory board agreed a restructuring package that added 50,000 job cuts, bringing the total to 100,000, and the shares rose 5.9 percent on 4 September (Reuters 2026c). The programme event is therefore a press report about the plan, not a formal guidance release, and its five day window contains the positive 4 September agreement.

### 3.2 Why the four events are not four independent observations

The four announcements share a common factor, which is the group's restructuring news, and they are separated by 196, 48 and 21 calendar days. A reader who treats them as four independent draws overstates the information in the sample. The paper therefore reports the event level estimates and the cross sectional statistics, and it adds two designs that respect the dependence: a randomisation test that draws pseudo event sets with the same spacing from 2017 to 2024, and a placebo that compares the observed mean with every three day window in the same period.

The events also overlap with other news. The IAV report of 11 August 2026 falls one day before the European Commission cleared the Everllence sale, so the window around the IAV report contains the clearance of a much larger disposal. IAV had announced job cuts on 6 August, five days before the report. The programme report of 1 September 2026 was followed by the supervisory board's restructuring agreement on 4 September, which is inside the five day window. The Italdesign closing on 7 September falls after the programme report and outside its three day window; the first version wrongly treated it as a confounder. None of these overlaps can be removed by choosing a different window, because the news is inside every window that contains the event. The paper reports the event level estimates with the confounders named, and it uses the peer placebo to separate the firm from the sector.

### 3.3 What the programme is not

The programme is not a liquidation. The group sold minority and majority stakes, retained industrial minorities in two cases, and reinvested part of the proceeds in software through the Rivian venture. It is also not a refocusing in the sense of the 1980s literature, because the units that were sold are related to the core: styling, powertrain engineering and large engines are capabilities that the remaining car business uses. The paper therefore treats the programme as a portfolio substitution, and it asks whether the market priced it as a creation of value, as a financing necessity, or as a signal about management's commitment to a strategy that the market doubts.

## 4 Data

### 4.1 Prices

The analysis uses daily adjusted closing prices for the Volkswagen preference share, Porsche Automobil Holding, BMW, Mercedes-Benz Group, the DAX, the STOXX Europe 600 and the STOXX Europe 600 Automobiles and Parts. The equity series for Volkswagen and its peers come from the project panel, which records the adjusted close for each trading day from 24 November 2016 to 20 November 2026, 2,505 return observations after the first difference. The three benchmark series were downloaded from Yahoo Finance on 25 November 2026 and are stored in `data/raw/p05_benchmarks.csv` with SHA256 0174ad7dcb5dd55438a444b803ad17875f80d90f5f8e29dcb9b25efebd1662f9 and the fund metadata in `data/raw/p05_benchmarks_metadata.json` with SHA256 1fa299bf30ea41ac6b7b57f13a81a18a43adbded4aea168cfd121622c8e06eec. The panel file has SHA256 9bc7f8c3cbf5a94e8ed1985b884d6db4a28538f72c6deebb39a9163c60f86caa.

Adjusted closes are used because the preference share pays a dividend and because the ordinary and preference shares have different dividend rights. The adjustment removes the dividend drop from the return, which matters in April of each year and would otherwise contaminate any window that contains the annual general meeting.

The choice of the preference share is not a convenience. The ordinary share carries the votes and is held by three blocks that control 90.3 percent of the votes, so its daily price reflects the valuation of a small free float in a stock that is not the marginal instrument. The preference share is the liquid security, it is the one that index funds hold, and it is the one whose price responds to news about the use of proceeds.

### 4.2 Benchmarks

The primary benchmark is the STOXX Europe 600 Automobiles and Parts, because the confounders of 2025 and 2026 are industry wide: the Chinese price war, the European electric vehicle mandate, the tariff regime and the margin compression that all European manufacturers reported. A market model against a broad index would attribute the sector shock to the firm. The DAX and the STOXX Europe 600 are used as robustness benchmarks, and the results are reported for all three.

The sector benchmark is an exchange traded fund that tracks the index, not the index itself, because the index level is not freely available at a daily frequency for the full window. The fund is the iShares STOXX Europe 600 Automobiles and Parts UCITS ETF (DE), ticker EXV5.DE. It replicates the index and its tracking error is small relative to the daily variance of Volkswagen, but the paper reports the DAX and the broad index results so that a reader can see whether the choice matters.

#### 4.2.1 A benchmark audit

The first version of this paper used EXV4.DE for the sector. The ticker was wrong: EXV4.DE is the iShares STOXX Europe 600 Health Care UCITS ETF (DE). The error was found by checking the fund's metadata and by correlating the series with the two candidate funds. The old series had a correlation of 1.0000 with EXV4.DE and 0.4229 with EXV5.DE. The metadata for EXV4.DE names health care; the metadata for EXV5.DE names automobiles and parts.

The consequences were large. Against the health care fund, Volkswagen had a beta of 0.292 and a residual standard deviation of 1.77 percent a day; against the automobile fund, the beta is 0.965 and the residual standard deviation is 1.10 percent a day. The health care fund rose while the automobile stocks fell, so the old drift of minus 64.45 log points was partly the difference between two sectors, not a verdict on Volkswagen. The corrected drift is minus 28.96 log points.

The audit is simple and should be standard. It has three steps. First, record the fund's name, ticker, currency and provider at the time of download, and store the metadata with the price file. Second, correlate the candidate series with the returns of the firms that the benchmark is supposed to represent; a sector fund should comove with its constituents, and a health care fund should not. Third, check the sign and the size of the beta against the sector. A beta of 0.29 for a car manufacturer against an automobile index is possible but unusual; a beta of 0.29 against a health care index is a warning. The paper reports the audit so that the correction is reproducible and so that the reader can see which results changed.

### 4.3 Event dates and disclosure

Table 1 lists the four events, their dates, the type of disclosure and the confounders.

Table 1. The event set.

| Event | Date | Disclosure | Status at the time of writing | Confounder in the window |
|:--|:--|:--|:--|:--|
| Italdesign | 10 December 2025, after close | Primary, Audi media release, price undisclosed | Closed 7 September 2026 | None identified; first tradable day 11 December 2025 |
| Everllence | 24 June 2026 | Primary, group release, exclusive arrangement | Cleared 12 August 2026 | Sale process reported since January 2026 |
| IAV | 11 August 2026 | Press report, no company confirmation | Reported, not signed | IAV job cuts on 6 August 2026; Everllence clearance on 12 August 2026 |
| Programme | 1 September 2026, 17:09 CET | Press report, Reuters citing Handelsblatt, no company confirmation | Ongoing | Restructuring agreement on 4 September 2026 |

The dates differ in quality. The Italdesign and Everllence releases are primary and time stamped by the issuer. The IAV and programme events are press reports, and neither company had confirmed them, so the information may have been impounded before the report and the true date is unobserved. The programme report is a plan rather than a transaction, and its content is a sales forecast and an intention rather than a number.

The paper keeps the fourth event out of the primary tests and reports it separately. The reason is that the programme report is not a disposal, and including it in a cross section of disposals would mix two kinds of news. The event level results for all four are reported in Table 3 so that a reader can see what the inclusion would do.

### 4.4 What we checked and corrected

Six corrections separate this version from the first. Each is documented because the correction, not the original number, is the reproducible object.

The benchmark. The first version used EXV4.DE, a health care exchange traded fund, in place of EXV5.DE, the automobiles and parts fund. The beta moved from 0.965 to 0.292 and the drift from minus 28.96 to minus 64.45 log points. The corrected numbers are the only ones reported here. Section 4.2.1 describes the audit.

The Everllence value. The first version described 7.4 billion euros as an enterprise value and inferred a value of 14.5 billion for the whole business. The release says the 7.4 billion is expected proceeds to Volkswagen, derived from the 51 percent share and the expected debt. It also reports a book value of 3.4 billion euros at 31 May 2026. The inference is removed, and the paper uses the 7.4 billion only to rank the disposal by size.

The Italdesign date. The release was published after the Xetra close on 10 December 2025. The first tradable day was 11 December. The main table keeps the announcement date, because that is the pre-specified convention, and the three day window includes 11 December. The specification curve reports the first tradable alignment; the mean moves from minus 1.60 to minus 1.65 log points and the conclusion does not change.

The IAV description. IAV is 50 percent owned by Volkswagen, not a subsidiary. Accenture is reported to acquire 70 percent, with Volkswagen retaining 30 percent. IAV announced on 6 August 2026 that it would reduce its German workforce from more than 5,000 to 2,970 by the end of 2027. The job cuts are outside the three day window but inside the information set that the market used to price the 11 August report.

The Italdesign closing. The transaction closed on 7 September 2026, not 31 August. The first version treated the closing as a confounder for the 1 September programme report. It is not: the closing occurred after the report and outside the three day window. The correction removes a confounder that did not exist.

The programme event. The 1 September event was not a company statement. It was a Reuters report, citing Handelsblatt, that Volkswagen expected to sell 8.5 million vehicles in 2026 and planned asset divestments. The report was published at 17:09 Central European Time, 21 minutes before the Xetra close. The 4 September supervisory board agreement, which added 50,000 job cuts and brought the total to 100,000, is inside the five day window and is a positive confounder. The paper therefore reads the programme's three day return as the reaction to the report and does not read its five day return as a reaction to the report alone.

## 5 Method

### 5.1 Returns and the market model

Daily logarithmic total returns are computed from the adjusted close:

$$R_t = \ln\left(\frac{A_t}{A_{t-1}}\right)$$

where $A_t$ is the adjusted close on trading day $t$. The event date is the announcement date, which is the convention fixed before any return was computed. When a release is published after the close of Xetra at 17:30 Central European Time, the first tradable day is the next trading day, and the three day window from one day before to one day after the announcement contains that day. The Italdesign release is the only event in the sample with this feature. The main table keeps the announcement date so that the event set is the one that was fixed in advance, and the specification curve reports the first tradable alignment as a separate design.

The market model is estimated once, on the 250 trading days ending 20 trading days before the first event:

$$R_t = \alpha + \beta R_{mt} + \varepsilon_t$$

where $R_{mt}$ is the return on the benchmark. The estimation window runs from 11 November 2024 to 12 November 2025, which ends 20 trading days before 10 December 2025 and therefore excludes the run up to the first announcement. The same parameters are applied to every event. Estimating a separate window for each event would be preferable in a large sample, but the windows of the later events would contain the earlier announcements, and a window that ends before the first announcement is the only one that is clean for all four.

The abnormal return is the residual:

$$AR_t = R_t - \hat{\alpha} - \hat{\beta} R_{mt}$$

and the cumulative abnormal return over a window from $t_1$ to $t_2$ is:

$$CAR(t_1,t_2) = \sum_{t=t_1}^{t_2} AR_t$$

### 5.2 Standardisation and test statistics

The forecast standard error of the abnormal return follows Patell (1976):

$$S_t = s\sqrt{1 + \frac{1}{L} + \frac{(R_{mt} - \bar{R}_m)^2}{\sum_{\tau=1}^{L}(R_{m\tau} - \bar{R}_m)^2}}$$

where $s$ is the residual standard deviation from the estimation window and $L$ is the number of estimation days. The standardised abnormal return is $SAR_t = AR_t / S_t$, the standardised cumulative abnormal return over a window of $T_i$ days is $CSAR_i = \sum_t SAR_t$, and the Patell statistic for $N$ events is:

$$Z_{Patell} = \frac{\sum_{i=1}^{N} CSAR_i}{\sqrt{\sum_{i=1}^{N} T_i}}$$

The Boehmer, Musumeci and Poulsen (1991) statistic standardises again by the window length and uses the cross section:

$$SCAR_i = \frac{CSAR_i}{\sqrt{T_i}}, \qquad t_{BMP} = \frac{\overline{SCAR}}{s_{SCAR}/\sqrt{N}}$$

which is distributed as a t with $N-1$ degrees of freedom. With three events the two sided five percent critical value is 4.303.

Two exact tests are reported because the parametric ones assume a distribution that three observations cannot verify. The sign test counts the number of positive cumulative abnormal returns and uses the binomial distribution with $p = 1/2$. The Wilcoxon signed rank test ranks the absolute values and enumerates all $2^N$ sign assignments, which is exact for $N = 3$. Both tests attain a two sided p value of 0.25 when all three observations have the same sign, which is the smallest p value that three events can produce.

### 5.3 Randomisation and placebo

The randomisation test asks whether the observed mean cumulative return is unusual relative to the calendar. It draws 10,000 pseudo event sets from the trading days between 3 January 2017 and 31 December 2024, each set containing three dates with the same spacing as the observed events, 196 and 48 calendar days. For each set the mean three day cumulative abnormal return is computed with the same market model parameters, and the observed mean is ranked in the resulting distribution. The two sided p value is twice the smaller tail. The seed is fixed at 20261125.

The placebo is simpler and does not impose the spacing. It computes the three day cumulative abnormal return for every trading day between 2017 and 2024 and reports the share of windows that are at or below the observed mean. The placebo answers the question that a reader will ask: how often does this stock move by this much over three days for no announced reason.

### 5.4 The drift

The event study measures four days. The programme lasted a year, and the paper therefore reports the cumulative return of the preference share against the sector over the period from 9 December 2025 to 20 November 2026. The relative return is the difference of the logarithmic returns, its daily mean is tested with a t statistic that uses the sample standard deviation over 237 trading days and with a Newey and West (1987) heteroskedasticity and autocorrelation consistent variance with five lags, and the result is reported as descriptive rather than causal, because the period contains earnings releases, guidance changes, works council negotiations and the Chinese price war.

### 5.5 Hypotheses and decision rules

The design tests four hypotheses, each with a decision rule fixed before the returns were computed.

H1, refocusing. If the disposals increase focus, the mean cumulative abnormal return is positive and largest at the first announcement, which is the one that reveals the programme. The rule is that H1 is supported if the mean three day return is positive and the Patell statistic exceeds 1.96.

H2, financing. If the disposals raise cash that the market expects to be retained for an uncertain transition, the mean cumulative abnormal return is non-positive, and the reaction is more negative for the larger disposals. The rule is that H2 is supported if the mean is negative and the five day Patell statistic is below minus 1.96.

H3, signalling. If the announcements are information about management's commitment to the portfolio logic, the reactions diminish as the programme becomes expected. The rule is that H3 is supported if the absolute reaction at the first event exceeds the absolute reaction at the third.

H4, drift. If the market revalues the firm over the programme rather than at the announcements, the relative return over the period is negative and larger in absolute value than the sum of the announcement effects. The rule is descriptive: H4 is supported if the relative drift is negative and its t statistic exceeds 1.96 in absolute value.

The rules are stated in advance so that the paper cannot choose the test after seeing the result. Where a rule is not met, the paper says so and reports the estimate as uninformative rather than as evidence of no effect.

## 6 Results

### 6.1 The market model

Table 2 reports the market model estimated on the 250 trading days from 11 November 2024 to 12 November 2025.

Table 2. Market model estimates, Volkswagen preference share, 250 trading days to 12 November 2025.

| Benchmark | Alpha | Beta | Residual standard deviation, daily | Estimation days |
|:--|--:|--:|--:|--:|
| STOXX Europe 600 Automobiles and Parts | 0.0498 | 0.965350 | 1.0959 | 250 |
| DAX | -0.0190 | 0.865015 | 1.5247 | 250 |
| STOXX Europe 600 | 0.0088 | 0.958154 | 1.5886 | 250 |

Note: alpha and the residual standard deviation are in log points per day; beta is unitless.

The beta against the sector is 0.965350, which is normal for a car manufacturer and is close to the beta against the DAX, 0.865015, and the beta against the broad European index, 0.958154. The preference share moves with the sector almost one for one, and the residual standard deviation of 1.10 log points a day is smaller than the 1.77 log points that the wrong benchmark produced. The R squared of the sector model is 0.631. A beta near one means that the sector benchmark absorbs most of the common variation and leaves the firm specific news in the residual, which is what an event study wants. The earlier version's low beta of 0.292 was an artifact of the health care fund, and it is the clearest signal that the benchmark was wrong.

### 6.2 The event windows

Table 3 reports the cumulative abnormal returns for the four events and the five windows.

Table 3. Cumulative abnormal returns by event and window, log points.

| Event | Date | (-1,+1) | (0,+1) | (0,+5) | (0,+20) | (-5,+5) |
|:--|:--|--:|--:|--:|--:|--:|
| Italdesign | 10 December 2025 | 1.96 | 0.94 | -0.51 | -1.30 | 1.48 |
| Everllence | 24 June 2026 | -4.49 | -3.33 | -11.55 | -8.84 | -19.31 |
| IAV | 11 August 2026 | -2.26 | -1.55 | -1.77 | 6.85 | -2.33 |
| Programme | 1 September 2026 | -2.80 | -2.73 | 6.63 | -2.20 | 8.87 |

Note: values are log points.

The pattern is not uniform, and the heterogeneity is informative. Italdesign, the smallest disposal and the one with the least disclosure, produced a positive three day return of 1.96 log points, which is not significant at five percent (Patell 1.78) and which turns negative over the twenty days after the announcement, minus 1.30 log points. Everllence, the largest disposal and the only one with a disclosed proceeds figure, produced the largest negative reaction, minus 4.49 log points over three days and minus 11.55 log points over the five days after the announcement. IAV, reported rather than confirmed, produced minus 2.26 log points over three days. The programme report produced minus 2.80 log points over three days. Its positive 6.63 log points over the five days after the report is not a reaction to the report: it is the 4 September supervisory board agreement, which added 50,000 job cuts and sent the shares up 5.9 percent on the day. The three day window is the clean measure of the report, and the five day window is not.

The Everllence reaction deserves a comment because it is the cleanest disclosure in the sample. The announcement was a primary release, the proceeds were disclosed at about 7.4 billion euros, the buyer was a financial sponsor rather than a strategic buyer, and the window contains no other group release. The market marked the stock down by 4.49 log points over three days, which is about 4.39 percent in simple terms, on a transaction that was supposed to simplify the portfolio and raise cash. A refocusing story would have predicted the opposite sign, and the sign is therefore evidence against it. The event level Patell statistic is minus 4.09, so this announcement rejects the null on its own; what the sample cannot do is attribute the reaction to the programme rather than to other news in the window, and the cross section of three events does not reject. The sale process had been public since January, so the reaction measures the update on the buyer and the terms, not the surprise that a sale was possible. The peer placebo in section 6.7.2 shows that the reaction was specific to Volkswagen: BMW, Mercedes-Benz and Porsche SE fell by 0.53 log points on average over the same window, 3.97 percentage points less than Volkswagen.

### 6.3 Cross sectional tests

Table 4 reports the tests across the three primary events, excluding the programme report.

Table 4. Cross sectional tests of the three primary events.

| Window | Events | Mean CAR | Median CAR | Patell Z | BMP t | Sign p | Wilcoxon p | Positive |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| (-1,+1) | 3 | -1.60 | -2.26 | -1.452140 | -0.843318 | 1.00 | 0.50 | 1 |
| (0,+1) | 3 | -1.31 | -1.55 | -1.463848 | -1.059007 | 1.00 | 0.50 | 1 |
| (0,+5) | 3 | -4.61 | -1.77 | -2.964906 | -1.321359 | 0.25 | 0.25 | 0 |
| (0,+20) | 3 | -1.10 | -1.30 | -0.378229 | -0.242900 | 1.00 | 0.75 | 1 |
| (-5,+5) | 3 | -6.72 | -2.33 | -3.193084 | -1.051820 | 1.00 | 0.50 | 1 |

Note: mean and median cumulative abnormal returns are in log points; the test statistics are unitless.

The three day mean is minus 1.60 log points, which is minus 1.58 percent in simple terms. The Patell statistic is minus 1.452140, which corresponds to a two sided p value of 0.146 against the normal approximation, and the BMP t is minus 0.843318, which corresponds to a two sided p value of 0.488 with two degrees of freedom. Neither rejects. The two statistics agree in sign but not in precision; the Patell is closer to the threshold because it treats the three events as independent draws, while the BMP reflects the dispersion of the three reactions, which is large because the first is positive and the other two are negative.

The five day window is stronger on the Patell criterion. The mean is minus 4.61 log points, the Patell statistic is minus 2.964906 and the BMP t is minus 1.321359. The Patell is below the five percent threshold, the BMP is not, and the exact sign and Wilcoxon tests attain their smallest possible p value of 0.25 with zero positive reactions out of three. A reader who wants a single sentence should say that the five day evidence is suggestive but not conclusive: one standardised statistic rejects, the other does not, and the exact tests cannot reject below 0.25 whatever the data say.

The twenty day window is not significant: mean minus 1.10 log points, Patell minus 0.378229, BMP minus 0.242900. The IAV reaction reverses, with plus 6.85 log points over twenty days, and the mean falls.

The cross section excludes the programme report, so the 4 September restructuring agreement does not enter the five day mean. The five day mean of minus 4.61 log points is therefore a clean average of the three primary events, and the positive programme return does not offset it. The event level programme result in Table 3 is reported for completeness, not as an input to the cross section.

### 6.4 Randomisation and placebo

The randomisation test draws 7,511 pseudo event sets with the observed spacing from 2017 to 2024. The pseudo mean has a mean of minus 0.27 log points and a standard deviation of 1.14 log points. The observed mean of minus 1.60 log points lies below 89.8 percent of the pseudo distribution, so the one sided p value is 0.102 and the two sided p value is 0.205. The announcement effect is in the tail of the calendar distribution, but it is not far enough into the tail to reject at five percent.

The placebo is less demanding and gives a similar answer. Across 2,004 three day windows between 2017 and 2024, the mean cumulative abnormal return is minus 0.25 log points and the standard deviation is 1.89 log points. The observed mean of minus 1.60 log points lies at the 17.56th percentile, which means that a three day decline of that size or larger occurred in about one window in six during a period in which no divestment programme was announced.

The two tests say the same thing in different ways. The negative reaction is not a routine move for this stock, but it is not so unusual that a sample of three can distinguish it from routine variation. The paper reports both and does not choose the one that rejects.

### 6.5 Robustness

Table 5 reports the mean three day and five day returns for three benchmarks and two estimation windows.

Table 5. Robustness of the mean cumulative abnormal return to the benchmark and the estimation window.

| Benchmark | Estimation days | (-1,+1) | Patell Z | BMP t | (0,+5) | Patell Z | BMP t |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Sector | 250 | -1.60 | -1.452140 | -0.843318 | -4.61 | -2.964906 | -1.321359 |
| Sector | 120 | -1.61 | -1.369907 | -0.854497 | -4.59 | -2.753003 | -1.327413 |
| DAX | 250 | -2.76 | -1.806414 | -1.938692 | -4.95 | -2.287990 | -1.572246 |
| DAX | 120 | -2.85 | -1.785996 | -2.035295 | -5.09 | -2.252331 | -1.606565 |
| STOXX 600 | 250 | -2.88 | -1.806202 | -1.682087 | -5.33 | -2.367965 | -1.712361 |
| STOXX 600 | 120 | -2.78 | -1.785949 | -1.679471 | -4.93 | -2.241222 | -1.486782 |

Note: mean cumulative abnormal returns are in log points; the test statistics are unitless.

The sign and the order of magnitude survive every combination. The three day mean ranges from minus 1.60 to minus 2.88 log points, and the five day mean ranges from minus 4.59 to minus 5.33 log points. The five day Patell statistic is below minus 2.2 in every specification, and the BMP statistic is between minus 1.32 and minus 1.71. The sector beta is 0.965 with 250 estimation days and 0.926 with 120, which is stable; the broad index beta moves from 0.958 to 1.432 when the window is shortened, which reflects the composition of the 2024 to 2025 period rather than a change in the firm. The robustness table does not rescue the three day result: no specification brings the BMP statistic near the five percent threshold, and the Patell statistic is below 1.96 in absolute value in every three day specification.

### 6.6 The drift and the peer comparison

Figure 1 plots the cumulative abnormal returns around each event and Figure 2 plots the preference share against the sector and the market from 2 January 2025.

![Cumulative abnormal returns around the four announcements](../figures/fig22_p05_car_paths.png)

Figure 1. Cumulative abnormal returns around the four announcements, trading days minus ten to plus twenty, log points.

![Volkswagen against the sector and the market](../figures/fig23_p05_indexed.png)

Figure 2. The Volkswagen preference share against the STOXX Europe 600 Automobiles and Parts and the DAX, indexed to 100 on 2 January 2025, with the four announcement dates marked.

The drift is negative but smaller than the announcement effects alone would suggest. Between 9 December 2025 and 20 November 2026 the preference share returned minus 53.43 log points, which is minus 41.4 percent in simple terms. Over the same 237 trading days the sector returned minus 24.47 log points, which is minus 21.7 percent, the broad European index plus 7.96 log points and the DAX plus 2.61 log points. The relative return against the sector is minus 28.96 log points, with a daily mean of minus 0.122 log points, a daily standard deviation of 1.16 log points, a t statistic of minus 1.62 and a Newey and West t of minus 1.64. The drift is not significant at five percent.

The peer comparison puts the number in context. Table 6 reports the cumulative log return of Volkswagen and five peers over the same period, in log points.

Table 6. Cumulative returns over the programme period, 9 December 2025 to 20 November 2026.

| Company | Cumulative return, log points | Simple return, percent |
|:--|--:|--:|
| Volkswagen preference share | -53.43 | -41.4 |
| BMW | -60.01 | -45.1 |
| Mercedes-Benz Group | -48.46 | -38.4 |
| Toyota | 7.72 | 8.0 |
| BYD | -45.22 | -36.4 |
| Tesla | -25.25 | -22.3 |
| Equal weighted peers | -34.25 | -29.0 |
| STOXX Europe 600 Automobiles and Parts | -24.47 | -21.7 |

BMW lost more than Volkswagen, Mercedes-Benz lost slightly less, and BYD lost less. The equal weighted peer average lost 29.0 percent, and Volkswagen's gap against that average is minus 19.2 log points. Volkswagen is not the worst performer in the group, and its gap against the sector is smaller than BMW's. The programme year was a bad year for the German car industry, not a unique verdict on Volkswagen.

The twelve month relative return against the sector is also not exceptional for this stock. Across 1,975 overlapping twelve month windows between 2017 and 2026, the programme window ranks 650th, at the 32.9th percentile. The worst window, in October 2023, was minus 53.3 log points, nearly twice the programme window. The drift is negative, but it is not the worst year in the sample and it is not statistically distinguishable from zero.

### 6.7 Post hoc extensions

Three questions remained after the first version. How large an effect could the design detect? Did the peers react in the same way? And how sensitive is the conclusion to the choices that the design fixed? The analyses below answer those questions. They are post hoc: they were not part of the pre-specified design, and they are labelled as such. Each base specification reproduces the published three event mean of minus 1.60 log points before any extension is computed.

#### 6.7.1 Minimum detectable effect

The residual standard deviation of the sector model is 1.10 log points a day, so a three day cumulative abnormal return has a standard deviation of about 1.90 log points per event. With three events the standard error of the mean is 1.10 log points, and the two sided five percent critical value with two degrees of freedom is 4.303. At 80 percent power the minimum detectable effect is 6.20 log points. Table 7 reports it for five windows and three sample sizes. With three events the design can detect a reaction of about 6.2 log points, which is larger than every three day reaction in the sample; the observed mean is one quarter of it. The correct reading of the failure to reject is not that the market approved, but that the design cannot see an effect of the size that the programme would plausibly produce.

Table 7. Minimum detectable effect for the mean cumulative abnormal return, 80 percent power and five percent two sided level. Values are log points; the per event standard deviation is the daily residual standard deviation of 1.0959 log points multiplied by the square root of the window length, and the three event column uses the noncentral t distribution with two degrees of freedom.

| Window | Days | Per event standard deviation | Three events | Ten events | Fifty events |
|:--|--:|--:|--:|--:|--:|
| (-1,+1) | 3 | 1.90 | 6.20 | 1.89 | 0.77 |
| (0,+1) | 2 | 1.55 | 5.06 | 1.54 | 0.63 |
| (0,+5) | 6 | 2.68 | 8.76 | 2.67 | 1.08 |
| (0,+20) | 21 | 5.02 | 16.39 | 5.00 | 2.03 |
| (-5,+5) | 11 | 3.63 | 11.86 | 3.62 | 1.47 |

#### 6.7.2 Peer placebo

The same event dates can be applied to firms that did not sell a business. If BMW, Mercedes-Benz and Porsche SE fell by the same amount, the reaction is a sector shock rather than a verdict on Volkswagen. Table 8 reports the three day cumulative abnormal return of Volkswagen and the three German peers around each announcement. At Italdesign, Volkswagen rose 1.96 log points, the peers rose 0.54 log points on average, and Volkswagen was the highest of the four. At Everllence, Volkswagen fell 4.49 log points, the peers fell 0.53 log points, and Volkswagen was the lowest of the four; the gap is 3.97 percentage points. At IAV, Volkswagen fell 2.26 log points, the peers fell 1.05 log points, and the gap is 1.21 percentage points. The Everllence reaction is therefore specific to the seller. The IAV reaction is partly sector wide. The Italdesign reaction is positive and specific, but small. The peer placebo does not prove that the market priced the disposal rather than other Volkswagen news, but it removes the simplest alternative, which is that the whole sector moved.

Table 8. Peer placebo, three day cumulative abnormal returns around the three disposal announcements.

| Event | Volkswagen | Peer mean | Peer minimum | Peer maximum | Volkswagen minus peers | Volkswagen rank |
|:--|--:|--:|--:|--:|--:|--:|
| Italdesign | 1.96 | 0.54 | -0.49 | 1.46 | 1.42 | 4 of 4 |
| Everllence | -4.49 | -0.53 | -1.34 | 0.72 | -3.97 | 1 of 4 |
| IAV | -2.26 | -1.05 | -2.48 | 0.23 | -1.21 | 2 of 4 |

Note: values are log points. The peers are BMW, Mercedes-Benz Group and Porsche Automobil Holding. Each peer is estimated on the same 250 day window with the sector benchmark. A rank of 1 means the lowest return of the four firms; a rank of 4 means the highest.

#### 6.7.3 Specification curve

The design fixed four choices: the benchmark, the event window, the estimation length and the treatment of the IAV event. A reader can reasonably ask whether the conclusion depends on them. Figure 3 reports the mean cumulative abnormal return for all 128 combinations, including the announcement date and the first tradable date for Italdesign. Every specification produces a negative mean. The 64 three event specifications range from minus 10.25 to minus 1.12 log points; the narrower (-1,+1) three event specifications range from minus 2.88 to minus 1.52. The 64 specifications that drop the IAV event contain two events and are also negative. The base specification is not an outlier. No three event specification produces a BMP t below minus 4.303, the five percent critical value with two degrees of freedom. The sign is robust; the significance is not. That is the same conclusion as the main table, but it is now a statement about the whole design space rather than about one column.

![Specification curve for the mean cumulative abnormal return](../figures/fig24_p05_spec_curve.png)

Figure 3. Specification curve for the mean cumulative abnormal return. Each point is one of 128 combinations of benchmark, window, estimation length, event timing and event set. The top panel reports the mean cumulative abnormal return in log points; the bottom panel reports the Patell and BMP statistics. The base specification is circled.

#### 6.7.4 Bayesian posterior

The p value answers a question that a board does not ask. A board wants the probability that the reaction is negative, given the data and a reasonable prior. Table 9 reports a random effects posterior for the mean cumulative abnormal return with three priors. The likelihood is weak, so the prior matters. With a prior standard deviation of 1 log point, the posterior mean is minus 0.44 log points and the 95 percent credible interval runs from minus 2.11 to plus 1.32. With a prior of 10 log points, the posterior mean is minus 1.54 and the interval runs from minus 5.48 to plus 2.43. The probability that the mean is negative ranges from 0.70 to 0.82. The Bayesian answer is therefore the same as the frequentist one: the sign is more likely negative than positive, but the data do not exclude zero.

Table 9. Bayesian posterior for the mean three day cumulative abnormal return, prior sensitivity.

| Prior standard deviation | Posterior mean | Posterior standard deviation | 95 percent interval | Probability mean is negative |
|:--|--:|--:|:--|--:|
| 1 log point | -0.44 | 0.87 | -2.11 to 1.32 | 0.698 |
| 3 log points | -1.18 | 1.57 | -4.19 to 2.10 | 0.793 |
| 10 log points | -1.54 | 1.95 | -5.48 to 2.43 | 0.818 |

Note: values are log points. The model is a random effects specification with event level standard deviations of 1.8981 log points, a half normal prior on the between event standard deviation with scale 3 log points, and 60,000 draws from the posterior.

![Bayesian posterior for the mean cumulative abnormal return](../figures/fig25_p05_bayes.png)

Figure 4. Bayesian posterior mean and 95 percent credible interval for the mean three day cumulative abnormal return under three priors. The interval includes zero under every prior.

#### 6.7.5 What the extensions change

The extensions do not change the sign or the policy conclusion. They change the confidence with which the paper can state it. The minimum detectable effect shows that the design is blind to effects below 6.2 log points, so the failure to reject is not evidence of approval. The peer placebo shows that the Everllence reaction is specific to Volkswagen, which strengthens the financing interpretation. The specification curve shows that the sign is stable across 128 designs, which weakens the worry that the result is a forking path artifact. The Bayesian posterior shows that the probability of a negative mean is 0.70 to 0.82, which is informative but not decisive. The conclusion is therefore narrower than the first version's: the market reaction to the disposals is negative, small and imprecise, and the one robust signal is the Everllence sale.

### 6.8 The hypotheses

H1, refocusing, is not supported. The mean three day return is negative, not positive, and the Patell statistic is minus 1.45 rather than above 1.96. The first announcement produced plus 1.96 log points, and the two largest disposals produced negative reactions. The sign is consistent with the refocusing hypothesis failing, but the estimate is too imprecise to reject it.

H2, financing, is supported on the pre-specified Patell criterion but not on the BMP. The mean five day return is negative, minus 4.61 log points, and the five day Patell statistic is minus 2.96, which is below minus 1.96. The BMP t is minus 1.32, and the exact tests cannot reject. The reaction is more negative for the larger disposal: Everllence, with expected proceeds of about 7.4 billion euros, produced minus 4.49 log points over three days, while Italdesign, with no disclosed value, produced plus 1.96. The peer placebo in section 6.7.2 shows that the Everllence reaction was 3.97 percentage points worse than the German peers, so the evidence is not merely a sector wide repricing. The evidence is consistent with financing, but it is not strong enough to separate financing from governance.

H3, signalling, is not supported. The rule required the absolute reaction at the first event to exceed the absolute reaction at the third, and the data give 1.96 against 2.26. The reactions grew rather than diminished, which is the opposite of what a learning market would produce if the programme were expected after the first announcement.

H4, drift, is not supported. The relative return over the programme period is minus 28.96 log points with a t statistic of minus 1.62 and a Newey and West t of minus 1.64, which is below 1.96 in absolute value. The drift is 3.8 times the sum of the four three day event effects, and those windows account for about 26 percent of it, but the estimate is too imprecise to reject the null of no revaluation.

## 7 Interpretation

### 7.1 Three explanations and what the price says

The refocusing explanation predicts a positive reaction to the sale of a unit that is not part of the core. The data do not support it: the mean three day return is negative, and the first announcement, which revealed the programme, was positive but small. The units that were sold are part of the core, so the refocusing premium should be small or absent, and the data are consistent with that prediction. But the estimate is too imprecise to distinguish a small negative effect from zero.

The financing explanation predicts a negative reaction when the proceeds are retained for an uncertain use. The data are consistent with it: the mean is negative, the largest disposal produced the largest negative reaction, and the group did not announce a distribution, a buyback or a debt reduction with the disposals. But the evidence is weak: the three day BMP is not significant, the exact tests cannot reject, and the five day result depends on the Patell statistic. The paper cannot claim that financing is confirmed.

The signalling explanation predicts diminishing reactions as the programme becomes expected. The data reject it: the reactions grew from 1.96 at the first event to 2.26 at the third, and the programme report produced minus 2.80. The growth is consistent with each announcement being a negative surprise about the scale of the programme, but three observations cannot distinguish a learning market from a sequence of unrelated shocks.

A fourth explanation is governance. The preference share carries no vote, and the holders who set the strategy are the family holding, the state and the sovereign fund. A minority holder who disagrees with the programme cannot change it and can only sell. The negative reaction is therefore the price at which the minority accepts the programme, and it is consistent with the literature on the private benefits of control (Dyck and Zingales 2004; Shleifer and Vishny 1997). The paper cannot separate this channel from the financing channel with three events, and it says so.

### 7.2 What the price identifies

The absence of a disclosed price for two of the three events changes what the estimate identifies. With no consideration, the market cannot compute the gain or loss on the sale, so the return measures the update to the credibility of the programme rather than the net present value of the transaction. For Everllence the proceeds were disclosed, but the figure is not a price for 51 percent and not an enterprise value: the release derives it from the 51 percent share and the expected debt, and it reports a book value of 3.4 billion euros for the whole business. The paper therefore does not infer the value of the whole business or the gain on the sale from the 7.4 billion. It uses the figure only to rank the disposal by size, and it reads the 4.49 log point decline as the market's update on the terms of the sale, not as a valuation of Everllence.

### 7.3 Ownership and the minority price

The preference share carries no vote, and the holders who set the strategy are the family holding, the state and the sovereign fund. A minority holder who disagrees with the programme cannot change it and can only sell. The negative reaction is therefore the price at which the minority accepts the programme, and it is consistent with the literature on the private benefits of control (Dyck and Zingales 2004; Shleifer and Vishny 1997). The paper cannot separate this channel from the financing channel with three events, and it says so. The ownership angle is an interpretation, not a test.

## 8 Limitations

The sample has three primary events in one firm and one year, and the effective number of independent observations is one. The parametric tests assume independence that the events do not have, and the exact tests cannot reject at a level below 0.25 whatever the data say. The paper reports the estimates and the limits, and it does not claim a rejection that the design cannot deliver. The minimum detectable effect makes the limit concrete: with three events the design can detect a three day mean reaction of 6.20 log points at 80 percent power. The observed mean of minus 1.60 is inside the blind spot, so the failure to reject is not evidence that the market approved.

The benchmark correction is itself a limitation. The first version used a health care fund, and the corrected results are weaker. The audit in section 4.2.1 documents the error, but a reader should treat the corrected numbers as the only valid ones and should not use the earlier version.

The event dates are not all primary. The IAV event is a press report, and the true date of the information may be earlier. The programme event is a press report rather than a company statement, and its content is a sales forecast and an intention rather than a number. The Italdesign release was published after the Xetra close, so the first tradable day was 11 December 2025. The Everllence date is a primary release, but the transaction was an exclusive arrangement rather than a signed sale, so the market may have revised its probability later, when the European Commission cleared the deal on 12 August 2026. The sale process had been public since January 2026, so the announcement confirmed the buyer and the terms rather than revealing that a sale was possible.

The benchmark is an exchange traded fund rather than the index, and its tracking error is small but not zero. The beta against the sector is 0.965, which is normal, but the model is still sensitive to the estimation window and to the composition of the sector index. The robustness table shows that the sign survives, but the precision does not.

The instrument is the preference share, which carries no vote. The measured reaction is a minority reaction, and it may understate or overstate the reaction of the ordinary shares, which are illiquid and held by three blocks. The paper cannot observe the ordinary share price at a daily frequency in a way that is informative.

The peer placebo and the Bayesian posterior have their own limits. The placebo uses three German firms, and it cannot rule out a European sector shock that hit Volkswagen more because of its exposure to China or to electric vehicles. The Bayesian posterior depends on the prior, and the paper reports three priors rather than one. Neither extension turns three events into a sample.

The drift is confounded. The period contains earnings releases, the 4 September restructuring agreement, the works council negotiations, the Chinese price war and the European tariff regime. The paper reports the drift as a description and does not attribute it to the programme. A reader who wants a causal estimate needs a counterfactual, and the peer comparison in Table 6 is a description, not a causal design.

Finally, the data are adjusted closes from a commercial provider, and the adjustment methodology is not public in detail. The paper records the SHA256 of every file so that a reader can reproduce the numbers from the same input, and it does not claim that the input is the only possible measure of the return.

## 9 Conclusion

This paper has measured the returns around four disclosures in the Volkswagen divestment programme with a design fixed before any return was computed. The three primary events produced a mean cumulative abnormal return of minus 1.60 log points over the three day window, with a Patell statistic of minus 1.45, a BMP t of minus 0.84 and one positive reaction out of three. Over the five days after the event the mean was minus 4.61 log points, the Patell statistic was minus 2.96 and the BMP t was minus 1.32. The randomisation test gave a two sided p value of 0.205 and the placebo placed the observed mean at the 17.6th percentile of three day windows between 2017 and 2024. The three day effect is negative but not statistically distinguishable from zero; the five day effect is stronger on the Patell criterion and weaker on the BMP.

The extensions bound the inference. The minimum detectable effect with three events is 6.20 log points at 80 percent power, four times the observed mean, so the design cannot see a reaction of the size that the programme would plausibly produce. The peer placebo shows that the Everllence reaction of minus 4.49 log points was 3.97 percentage points worse than BMW, Mercedes-Benz and Porsche SE, so it is specific to the seller. The specification curve produces a negative mean in all 128 designs, but no design rejects on the BMP test. The Bayesian posterior places the probability of a negative mean between 0.70 and 0.82 and includes zero in every 95 percent credible interval. The sign is robust; the magnitude is small; the significance is absent.

The annual record is also weaker than it first appears. Between 9 December 2025 and 20 November 2026 the preference share lost 41.4 percent in simple terms, the sector lost 21.7 percent, and the relative drift was minus 28.96 log points with a t statistic of minus 1.62. The drift is not significant at five percent, and it is not unusual relative to peers: BMW lost 45.1 percent, Mercedes-Benz 38.4 percent and BYD 36.4 percent over the same period. The programme year was a bad year for the German car industry, not a unique verdict on Volkswagen.

The interpretation that fits the evidence is financing rather than refocusing, but the evidence is weak. The units that were sold were part of the core capability, the proceeds were retained for a software transition that the market doubts, and the largest disposal with a disclosed proceeds figure produced the largest negative reaction. The refocusing hypothesis predicted the opposite sign, and the signalling hypothesis predicted diminishing reactions that did not occur. None of these patterns is estimated with enough precision to separate the channels. The 4 September restructuring agreement is a useful counterpoint: the market rewarded the broader restructuring with a 5.9 percent gain, so the negative reactions to the disposals are not a generic discount on restructuring. They are specific to the sale of the engineering and engine businesses.

The contribution is not a rejection. It is a transparent estimate with a wide interval, a statement of what four events can and cannot identify, a benchmark audit checklist that shows how a wrong sector series can reverse the conclusion, and a demonstration that a pre-specified design can be executed on a programme that is still running. The next step is to extend the event set backwards to earlier group disposals and to add a matched portfolio of engineering services firms as a control. Neither would turn four events into a sample, but together they would turn a case study into a comparison.

## Data availability

The equity series are the adjusted closes in `data/panel/panel_daily.csv`, SHA256 9bc7f8c3cbf5a94e8ed1985b884d6db4a28538f72c6deebb39a9163c60f86caa, which covers 24 November 2016 to 20 November 2026. The benchmark series were downloaded from Yahoo Finance on 25 November 2026 and are stored in `data/raw/p05_benchmarks.csv`, SHA256 0174ad7dcb5dd55438a444b803ad17875f80d90f5f8e29dcb9b25efebd1662f9, with the fund metadata in `data/raw/p05_benchmarks_metadata.json`, SHA256 1fa299bf30ea41ac6b7b57f13a81a18a43adbded4aea168cfd121622c8e06eec. The return series used by every extension is `data/model/p05_returns.csv`, SHA256 142efd527ce50a0e8cdd2a3038604d1707e713bd3a89636d1d63085946e5b13c. The event level results are `data/model/p05_events.csv`, SHA256 ca443cf72797737f26b9aaead7d82c4f34b6fa2b50fadb982aee58ef6568401d, the tests are `data/model/p05_tests.csv`, SHA256 4142d8bba535ba79bdcc32810c6ecc8372a6d5ba8f25cb7afb01c7c005c8636d, the robustness table is `data/model/p05_robustness.csv`, SHA256 7030281a2a19c822307afb3856006ef86da25e43be613fa602a24ced507bc1f9, and the summary is `data/model/p05_summary.json`, SHA256 d608e671ff105a9b0b526ea8d6dda1f0f990e7c1becfb729115abfbb09ef2d29. The extensions are `data/model/p05_extras/mde.csv`, SHA256 69202f4ad411f2067bcd234b81a5eb91d3cf04879dd80501d3ee2d091c4c1ad3, `data/model/p05_extras/peer_placebo.csv`, SHA256 fcbcf657c1dc8f77497044cc4611cf51cce60b9e2b6b5920547fcd2bd58a22ff, `data/model/p05_extras/spec_curve.csv`, SHA256 7cf5b7f3d5c7bc1ed05c26ea2bc6fe414002db6bd5e2b66664446b4c24bbb58b, and `data/model/p05_extras/bayes.csv`, SHA256 f12ea674880a0eb1f27c9d2614dfc080df2523da9de8517e55752402b1d39b85. The project is archived at Zenodo under the concept DOI 10.5281/zenodo.24516636, which resolves to the latest published version of the archive. The release that contains this paper is tagged v1.3.11 in the public repository, and the repository holds the code, the data and the results under the licence recorded in the archive.

## Code availability

The analysis has two scripts. `tools/p05_analysis.py` downloads the benchmarks once, reproduces the event study, the tests, the robustness table, the summary file, the return series and the two event figures. `tools/p05_extras.py` reproduces the minimum detectable effect, the peer placebo, the specification curve and the Bayesian posterior, and it checks that the base specification matches the published mean before it computes any extension. Both run on Python 3.12 with numpy, pandas, scipy and matplotlib. The repository is public at github.com/kajevic44-sudo/forecast2040-protocol. The commands are:

```
.venv/bin/python tools/p05_analysis.py
.venv/bin/python tools/p05_extras.py
```

## Appendix A. Reproduction

A1. Load `data/panel/panel_daily.csv`, keep the rows with a Volkswagen price, and merge the benchmark file on the date. The result is 2,506 price observations and 2,505 return observations from 24 November 2016 to 20 November 2026.

A2. Compute logarithmic returns as the first difference of the log adjusted close for the preference share, Porsche Automobil Holding, BMW, Mercedes-Benz, the DAX, the STOXX Europe 600 and the STOXX Europe 600 Automobiles and Parts.

A3. Estimate the market model on the 250 trading days ending 20 trading days before 10 December 2025, which is the window from 11 November 2024 to 12 November 2025, and keep alpha, beta, the residual standard deviation and the moments of the benchmark.

A4. Compute the abnormal return for every trading day as the residual from the fitted model, and the standardised abnormal return with the Patell forecast standard error.

A5. Sum the abnormal returns and the standardised abnormal returns over the five windows, and report the event level table.

A6. Compute the Patell statistic, the BMP t statistic, the exact sign test and the exact Wilcoxon test over the three primary events for each window.

A7. Draw 10,000 pseudo event sets with the observed spacing, 196 and 48 calendar days, from the trading days between 3 January 2017 and 31 December 2024, using the seed 20261125. Of the 10,000 draws, 7,511 satisfy the requirement that all three dates are trading days; the two sided p value is computed on those. Compute the placebo over every three day window in the same period.

A8. Re-estimate the model for the DAX and the STOXX Europe 600 and for a 120 day window, and report the robustness table. Compute the drift as the difference between the cumulative log return of the preference share and the benchmark over the period from 9 December 2025 to 20 November 2026.

A9. Before any estimation, verify the benchmark. Read the fund's name, ticker, currency and provider from the metadata, correlate the candidate series with the returns of the firms it is supposed to represent, and check the sign and the size of the beta. The audit that found the EXV4.DE error is described in section 4.2.1.

A10. For the minimum detectable effect, take the residual standard deviation of 1.0959 log points from the sector model, multiply it by the square root of the window length to obtain the per event standard deviation, divide by the square root of the number of events, and solve for the noncentral t with N minus one degrees of freedom at 80 percent power and a five percent two sided level. The three event, three day value is 6.20 log points.

A11. For the peer placebo, estimate the same market model for BMW, Mercedes-Benz and Porsche SE on the same 250 day window, compute the three day cumulative abnormal return for each firm at the same announcement dates, and compare Volkswagen with the peer mean, minimum, maximum and rank. The Everllence gap is minus 3.97 percentage points.

A12. For the specification curve, combine four benchmarks (sector, DAX, STOXX Europe 600, sector plus market), four windows, two estimation lengths, two event timings and two event sets (with and without IAV). That gives 128 specifications. Report the mean, the Patell statistic and the BMP statistic for each. All 128 means are negative; none has a BMP t below minus 4.303.

A13. For the Bayesian posterior, model the three event cumulative abnormal returns as normal with event level standard deviations of 1.8981 log points and a common mean, place a normal prior on the mean with standard deviations of 1, 3 and 10 log points and a half normal prior on the between event standard deviation with scale 0.03, integrate the between event standard deviation on a grid, and draw 60,000 values from the posterior. Report the mean, the standard deviation, the 95 percent credible interval and the probability that the mean is negative for each prior.

## Declaration of generative AI and AI-assisted technologies in the writing process

During the preparation of this manuscript, the author used AI-assisted tools for language editing, for improving English phrasing and linguistic clarity, and for limited technical assistance in reviewing and supporting the preparation of the analytical code. These tools supported the efficiency of the research workflow and did not replace the author's independent scientific work. The research objectives, the methodology, the analytical framework, the interpretation of the data and the scientific conclusions were determined and critically reviewed by the author. The author independently evaluated the analytical outputs, verified every reported result against the underlying data, and takes full responsibility for the accuracy, originality and integrity of the manuscript and its findings.

## References

Ahern, Kenneth R. 2009. "Sample Selection and Event Study Estimation." Journal of Empirical Finance 16 (3): 466-482.

Alexander, Gordon J., P. George Benson, and Joan M. Kampmeyer. 1984. "Investigating the Valuation Effects of Announcements of Voluntary Corporate Selloffs." Journal of Finance 39 (2): 503-517.

Andrade, Gregor, Mark Mitchell, and Erik Stafford. 2001. "New Evidence and Perspectives on Mergers." Journal of Economic Perspectives 15 (2): 103-120.

Audi AG. 2025. "Audi Group Forms Strategic Partnership: UST Acquires Majority Stake in Italdesign." Media release, Ingolstadt, Moncalieri and Aliso Viejo, 10 December 2025. Accessed 24 November 2026.

Automotive News Europe. 2026. "VW Plans to Sell Majority Stake in Engineering Unit IAV to Accenture." 11 August 2026. Accessed 24 November 2026.

AutoNext. 2026. "Audi Has Sold Italdesign, the House That Drew the Golf, to UST." 31 August 2026. Accessed 24 November 2026.

Berger, Philip G., and Eli Ofek. 1995. "Diversification's Effect on Firm Value." Journal of Financial Economics 37 (1): 39-65.

Betton, Sandra, B. Espen Eckbo, and Karin S. Thorburn. 2008. "Corporate Takeovers." In Handbook of Corporate Finance: Empirical Corporate Finance, Volume 2, edited by B. Espen Eckbo, 291-430. Amsterdam: Elsevier.

Bloomberg. 2026a. "Volkswagen Selects Next-Round Bidders for Everllence, Bloomberg News Reports." 22 April 2026. Accessed 25 November 2026.

Boehmer, Ekkehart, Jim Musumeci, and Annette B. Poulsen. 1991. "Event-Study Methodology under Conditions of Event-Induced Variance." Journal of Financial Economics 30 (2): 253-272.

Brown, Stephen J., and Jerold B. Warner. 1985. "Using Daily Stock Returns: The Case of Event Studies." Journal of Financial Economics 14 (1): 3-31.

Comment, Robert, and Gregg A. Jarrell. 1995. "Corporate Focus and Stock Returns." Journal of Financial Economics 37 (1): 67-87.

Desai, Hemang, and Prem C. Jain. 1999. "Firm Performance and Focus: Long-Run Stock Market Performance Following Spinoffs." Journal of Financial Economics 54 (1): 75-101.

Dittmar, Amy, and Anil Shivdasani. 2003. "Divestitures and Divisional Investment Policies." Journal of Finance 58 (6): 2711-2744.

Dyck, Alexander, and Luigi Zingales. 2004. "Private Benefits of Control: An International Comparison." Journal of Finance 59 (2): 537-600.

Eckbo, B. Espen, and Karin S. Thorburn. 2008. "Corporate Restructuring: Breakups and LBOs." In Handbook of Corporate Finance: Empirical Corporate Finance, Volume 2, edited by B. Espen Eckbo, 431-495. Amsterdam: Elsevier.

European Commission. 2026. "Case M.12527, Bain Capital / Volkswagen / Everllence." Competition case register, decision of 12 August 2026. Accessed 24 November 2026.

Faccio, Mara, and Larry H. P. Lang. 2002. "The Ultimate Ownership of Western European Corporations." Journal of Financial Economics 65 (3): 365-395.

Fama, Eugene F. 1998. "Market Efficiency, Long-Term Returns, and Behavioral Finance." Journal of Financial Economics 49 (3): 283-306.

Fama, Eugene F., Lawrence Fisher, Michael C. Jensen, and Richard Roll. 1969. "The Adjustment of Stock Prices to New Information." International Economic Review 10 (1): 1-21.

Franks, Julian, and Colin Mayer. 2001. "Ownership and Control of German Corporations." Review of Financial Studies 14 (4): 943-977.

Fuller, Kathleen, Jeffry Netter, and Mike Stegemoller. 2002. "What Do Returns to Acquiring Firms Tell Us? Evidence from Firms That Make Many Acquisitions." Journal of Finance 57 (4): 1763-1793.

Gorton, Gary, and Frank A. Schmid. 2000. "Universal Banking and the Performance of German Firms." Journal of Financial Economics 58 (1-2): 29-80.

Hite, Gailen L., James E. Owers, and Ronald C. Rogers. 1987. "The Market for Interfirm Asset Sales: Partial Sell-Offs and Total Liquidations." Journal of Financial Economics 18 (2): 229-252.

IAV. 2026. "IAV Is Realigning Itself." Press release, 6 August 2026. Accessed 25 November 2026.

Jensen, Michael C. 1986. "Agency Costs of Free Cash Flow, Corporate Finance, and Takeovers." American Economic Review 76 (2): 323-329.

Jensen, Michael C. 1993. "The Modern Industrial Revolution, Exit, and the Failure of Internal Control Systems." Journal of Finance 48 (3): 831-880.

John, Kose, and Eli Ofek. 1995. "Asset Sales and Increase in Focus." Journal of Financial Economics 37 (1): 105-126.

Kolari, James W., and Seppo Pynnönen. 2010. "Event Study Testing with Cross-Sectional Correlation of Abnormal Returns." Review of Financial Studies 23 (11): 3996-4025.

Kothari, S. P., and Jerold B. Warner. 2007. "Econometrics of Event Studies." In Handbook of Corporate Finance: Empirical Corporate Finance, Volume 1, edited by B. Espen Eckbo, 3-36. Amsterdam: Elsevier.

La Porta, Rafael, Florencio Lopez-de-Silanes, and Andrei Shleifer. 1999. "Corporate Ownership Around the World." Journal of Finance 54 (2): 471-517.

Lang, Larry, Annette Poulsen, and René Stulz. 1995. "Asset Sales, Firm Performance, and the Agency Costs of Managerial Discretion." Journal of Financial Economics 37 (1): 3-37.

Lang, Larry H. P., and René M. Stulz. 1994. "Tobin's q, Corporate Diversification, and Firm Performance." Journal of Political Economy 102 (6): 1248-1280.

Lyon, John D., Brad M. Barber, and Chih-Ling Tsai. 1999. "Improved Methods for Tests of Long-Run Abnormal Stock Returns." Journal of Finance 54 (1): 165-201.

MacKinlay, A. Craig. 1997. "Event Studies in Economics and Finance." Journal of Economic Literature 35 (1): 13-39.

Moeller, Sara B., Frederik P. Schlingemann, and René M. Stulz. 2004. "Firm Size and the Gains from Acquisitions." Journal of Financial Economics 73 (2): 201-228.

Mulherin, J. Harold, and Audra L. Boone. 2000. "Comparing Acquisitions and Divestitures." Journal of Corporate Finance 6 (2): 117-139.

Newey, Whitney K., and Kenneth D. West. 1987. "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix." Econometrica 55 (3): 703-708.

Patell, James M. 1976. "Corporate Forecasts of Earnings per Share and Stock Price Behavior: Empirical Tests." Journal of Accounting Research 14 (2): 246-276.

Reuters. 2026a. "Volkswagen to Sell 51 Percent Stake in Everllence to Bain Capital for About 7.4 Billion Euros." 24 June 2026. Accessed 24 November 2026.

Reuters. 2026b. "Volkswagen Expects 2026 Sales of 8.5 Million Vehicles, Plans Asset Divestments, Report Says." 1 September 2026. Accessed 25 November 2026.

Reuters. 2026c. "Volkswagen Shares Jump in Early Trade Following Turnaround Agreement." 4 September 2026. Accessed 25 November 2026.

Reuters. 2026d. "Workers Protest at VW-backed IAV Berlin Against Plans to Cut 1,400 Jobs." 12 May 2026. Accessed 25 November 2026.

Shleifer, Andrei, and Robert W. Vishny. 1997. "A Survey of Corporate Governance." Journal of Finance 52 (2): 737-783.

UST. 2026. "UST Completes Majority Stake Acquisition of Italdesign from Audi." Press release, 7 September 2026. Accessed 25 November 2026.

Volkswagen AG. 2026. Annual Report 2025, Shareholder Structure. Wolfsburg: Volkswagen AG. Accessed 24 November 2026.

Volkswagen Group. 2026. "Key Step Towards Streamlining Investment Portfolio: Volkswagen Group Enters into Exclusive Arrangement with Bain Capital for Sale of Majority Stake in Everllence." Press release, 24 June 2026. Accessed 24 November 2026.
