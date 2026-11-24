# Fixing the model before the backtest: a pre-registered protocol with a machine-checked split for long-horizon automotive demand

Armin Kajevic

Ingolstadt, Germany

## Abstract

Forecast comparisons in applied economics are often assembled after the results are known. The candidate set grows when a model fails, the loss changes when a ranking is inconvenient, and the boundary between training and test data is defended by code review rather than by proof. This paper sets out a protocol in which the candidate set, the rolling-origin design, the loss, the selection rule and the projection are fixed before any result is seen, and in which the deterministic part of the split is checked by the Lean 4 kernel. Thirteen models are evaluated on annual German passenger car registrations from 1991 to 2025 at fifteen origins and horizons of one to five years. Ridge regression on lagged growth wins with a mean absolute scaled error of 1.2839 against 1.5952 for the naive benchmark, a reduction of 19.5 percent. The pre-specified horizon test rejects equal accuracy at four and five years, with p values of 0.011 and 0.009, while a bootstrap of the same statistic, a variance clustered by origin and a Bonferroni bound over thirteen candidates do not, and the paper reports that disagreement instead of resolving it in its own favour. The 2040 point forecast is 3,161,958.51 registrations, with an empirical 95 percent interval from 2,563,157.85 to 3,689,022.75. On a second series, Volkswagen Group deliveries in China from 1987 to 2025, no model beats the random walk, and the protocol reports that null unchanged. The contribution is a protocol that can be audited, a published negative result, and a method for turning statistical uncertainty into a number a board can act on.

Keywords: forecast evaluation, rolling origin, pre-registration, MASE, Diebold and Mariano, Lean 4, automotive demand

JEL codes: C52, C53, C18, L62

## 1 Introduction

A forecast is a claim about a future that cannot be observed. A forecast comparison is a claim about which of several such claims is better, and it is made on a sample that is small, overlapping and chosen by the analyst. The second claim is the fragile one. It is fragile because the analyst who compares models has usually seen the results before deciding which comparison to report, because the candidate set is usually enlarged after a failure, and because the boundary between the data used to fit and the data used to judge is usually enforced by a line of code that no reader can check.

This paper takes the fragility seriously and removes the freedom that produces it. The candidate set, the rolling-origin scheme, the loss, the scale, the selection rule and the projection are fixed in a protocol before the first result is computed. The protocol is written down, dated and stored with the code. The deterministic part of the split, which is the part that decides whether an observation belongs to training or to evaluation, is written in Lean 4 and checked by the kernel, so that the claim that no future observation enters a forecast is a theorem rather than a promise. The statistical part, which is the estimation and the projection, remains in Python and is not formalised.

The empirical setting is the German passenger car market. Annual registrations from 1991 to 2025 give 35 observations, a series that moves between 2,567,103 and 3,807,175 vehicles, that contains the reunification boom, the 2009 scrappage programme and the 2020 collapse, and that is the single number a manufacturer, a supplier and a ministry all watch. Thirteen candidates are compared: two benchmarks, six econometric models, four machine learning models and one equal-weight combination. The comparison runs at fifteen rolling origins, from 2006 to 2020, at horizons of one to five years, which gives 75 forecast errors per model.

Three results organise the paper. First, the winner is ridge regression on three lagged growth rates, with a mean absolute scaled error of 1.2839 against 1.5952 for the naive benchmark, a reduction of 19.5 percent. Second, the gain is not uniform across horizons: the corrected Diebold and Mariano test separates the long horizons, where the corrected statistic is minus 2.911 at four years and minus 3.009 at five, from the short horizons, where it is indistinguishable from zero. Third, the same protocol applied to a second series produces a null: on Volkswagen Group deliveries in China, no candidate beats the random walk, the best scaled error is 7.7778, and the p value against naive is 0.9615. The null is reported as a result, not as a failure, because a protocol that can only produce wins is not a protocol.

The paper makes four contributions. It specifies a forecast comparison that is fixed in advance and therefore immune to the garden of forking paths described by Gelman and Loken (2014) and to the selection effects reviewed by Simmons, Nelson and Simonsohn (2011). It proves the split property in a proof assistant, which turns a code review question into a formal one, following the reproducibility agenda of Peng (2011) and Munafò et al. (2017). It reports a negative result on a second series with the same protocol, which is rare in a literature that publishes wins. And it converts the backtest errors into an empirical interval, so that the output of the exercise is a corridor rather than a point, which is the form in which a planning department can use it.

The rest of the paper is organised as follows. Section 2 reviews the literature on forecast evaluation, testing, multiplicity and reproducibility, and states the gap. Section 3 states the hypotheses and the pre-specified decision rules. Section 4 describes the two series and the transformations. Section 5 sets out the protocol, the formal definitions and the Lean module. Section 6 reports the results. Section 7 reports the robustness checks. Section 8 discusses what the design cannot establish. Section 9 concludes. The data, the code and the Lean module are listed in the availability statements at the end.

## 2 Literature review

### 2.1 Evaluation on a rolling origin

The evaluation of forecasting models has a long record of out-of-sample failures, of which the Meese and Rogoff (1983) result on exchange rate models is the classic case, and the practice is surveyed by Armstrong (2001) and Hyndman and Athanasopoulos (2021). The standard alternative to a single train-test split is the rolling-origin design, in which the model is estimated on data up to an origin, forecasts are made for horizons one to h, the origin moves forward, and the errors are collected. Tashman (2000) sets out the design and its pitfalls, including the choice of window, the treatment of the first origins and the temptation to report only the last split. Bergmeir and Benítez (2012) show that cross-validation is not automatically valid for time series, because the dependence structure that makes a series predictable also makes a random fold leak information. Bergmeir, Hyndman and Koo (2018) give conditions under which cross-validation remains valid for autoregressive models, and Cerqueira, Torgo and Mozetič (2020) compare performance estimation methods across a large set of series and find that the choice of method changes the ranking. The protocol in this paper follows Tashman in fixing the origins and the horizons, and it follows the later literature in reporting every origin rather than a selected one.

The number of origins is a design choice with a statistical cost. Fifteen origins give fifteen errors per horizon, which is enough to rank models but not enough to estimate a tail. The paper therefore reports the ranking, the per horizon tests and the interval, and it treats the interval as the object with the widest uncertainty, which is the opposite of the usual practice of reporting the point and mentioning the interval.

### 2.2 Loss, scale and the choice of the object

A comparison needs a loss, and the loss determines what the comparison means. The absolute loss is consistent for the conditional median and the squared loss for the conditional mean, as set out in the probabilistic forecasting literature surveyed by Gneiting and Katzfuss (2014). A series that is bounded below and skewed in crisis years does not have a symmetric predictive distribution, so the two losses rank models differently. The protocol fixes the absolute loss for selection and reserves the squared loss for a reported root mean squared error and for the first tie-break.

The scale is the second choice. The mean absolute scaled error of Hyndman and Koehler (2006) divides each absolute error by the in-sample mean absolute error of the naive forecast computed at the same origin. The scale is recomputed at every origin, which means that the benchmark does not score exactly one, a property that is often treated as a defect and is in fact the point: the metric compares each model to the naive forecast on the same information set, not to an abstract unit. The paper states this property and uses it, rather than assuming that the naive score is one.

### 2.3 Testing equal accuracy

Forecasting is also a task in which expertise is unevenly distributed, and Tetlock (2005) shows that confident judgment is a weak guide to distant outcomes, which is a reason to prefer a rule to a view. The comparison of two forecast sequences is a test of equal expected loss. Diebold and Mariano (1995) give the statistic and the variance estimator, and Harvey, Leybourne and Newbold (1997) correct the small-sample behaviour and the overlap. Clark and West (2007) address the nested case, in which the larger model contains the smaller one and the null lies on the boundary of the parameter space. Giacomini and White (2006) reframe the test as a conditional one, which is the right object when the question is whether a model is better in the regime that is being forecast rather than on average.

The protocol uses the Diebold and Mariano statistic with the Harvey, Leybourne and Newbold correction at each horizon, because forecasts h steps ahead overlap by h minus one target years and the overlap inflates the effective sample. The pooled statistic that stacks all horizons is reported for reconciliation with the metrics file and is explicitly marked as not valid as a test. This distinction is the difference between a number that is arithmetically correct and a number that answers a question.

### 2.4 Multiplicity, forking paths and pre-registration

A selection rule that examines thirteen candidates and reports the best one is a search. The p value of the winner is the p value of one comparison computed after thirteen were examined, and the probability that the best of thirteen noise models looks good is not the nominal level. Simmons, Nelson and Simonsohn (2011) show how ordinary degrees of freedom in analysis produce false positives, and Gelman and Loken (2014) generalise the point to the garden of forking paths, in which no single decision is dishonest and the path is still selected after the data are seen. Nosek et al. (2018) argue that pre-registration is the remedy, and Christensen and Miguel (2018) set out what transparency means for economics in particular.

The protocol is a pre-registration of a forecast comparison. It fixes the candidate set, the origins, the horizons, the loss, the scale, the tie-breaks, the selection functional and the projection, and it records a timestamp. It differs from a clinical trial registration in that the data are public and the exercise can be repeated by anyone, which is why the code and the Lean module are part of the contribution rather than an appendix.

### 2.5 Reproducibility and formal verification

Reproducibility is usually treated as a property of code and data. Peng (2011) sets out the standard, Baker (2016) documents how far practice is from it, and Munafò et al. (2017) propose a manifesto that includes registration and reporting. Formal verification goes further: it proves a property of the algorithm rather than testing an implementation. De Moura and Ullrich (2021) describe Lean 4, and the mathlib community (2020) describes the library that makes formal mathematics practical. The module used here is deliberately small, nine theorems and no Mathlib, because the property that matters is local: the training set at an origin contains no index at or after the origin, and the expanding window is nested.

The choice of Lean rather than a test suite is a statement about what kind of error is being ruled out. A test can show that a function returned the right list on the cases that were tried. A proof shows that no input produces a leak. The cost is that only the deterministic skeleton is proved, and the paper says so.

### 2.6 Combinations, machine learning and the benchmark

The forecasting literature has a long record of simple benchmarks beating complex models. Makridakis et al. (2000) report the M3 competition and Makridakis, Spiliotis and Assimakopoulos (2020) report M4, where combinations and relatively simple statistical methods remain hard to beat. Timmermann (2006) explains why combination works, and the equal-weight combination is included here as a candidate rather than as a default. The machine learning candidates are ridge regression (Hoerl and Kennard 1970), random forests (Breiman 2001) and gradient boosting (Friedman 2001), with a damped trend as the econometric alternative to a pure random walk (Gardner and McKenzie 1985). The point of including them is not to claim that machine learning wins. It is to put them in the same pre-registered comparison, so that a win or a loss is a result rather than a preference.

### 2.7 Automotive demand and the case for a corridor

The automotive literature supplies the object rather than the method. Sturgeon, Van Biesebroeck and Gereffi (2008) describe the industry as a global value chain in which assembly is the visible end of a long sequence of suppliers, and Klier and Rubenstein (2008) document how much of a vehicle is made by firms whose names are not on it. Demand forecasting at the manufacturer level is therefore a forecast of a chain, not of a brand. The official series used here are the German registrations from Destatis (2026), the German electric drive series from KBA (2025), the European registration data from ACEA (2025), and the Chinese deliveries reported by Volkswagen (2025) and by the China Association of Automobile Manufacturers (2025). The International Energy Agency (2025) provides the technology context. None of these sources provides a forecast, which is why the protocol is needed.

### 2.8 The gap

The literature contains the pieces: rolling-origin evaluation, scaled losses, corrected tests, multiplicity corrections, pre-registration and formal methods. It does not contain a forecast comparison that fixes all of them in advance, proves the split, reports a negative result on a second series and converts the errors into an interval in the same paper. That combination is the contribution, and it is a contribution of method rather than of a number. The number is the test of the method.

## 3 Hypotheses and pre-specified decision rules

The protocol is stated as three hypotheses and three decision rules, all fixed before the backtest.

H1. A model selected by the protocol has a lower expected absolute scaled loss than the naive benchmark on the German series, at the pooled level and at the longest horizon.

H2. The gain is horizon-specific: it is larger at horizons four and five than at horizons one to three, because the short horizon is dominated by the current level and the long horizon by the growth rate.

H3. The same protocol applied to a second series with a different data generating process produces no winner, and the null is reported unchanged.

The decision rules are equally explicit. A candidate wins if it has the lowest average MASE across the five horizons. Ties are broken by the lower root mean squared error, then by the alphabetically earlier name. The winner is reported with the Diebold and Mariano statistic at each horizon, with the Harvey, Leybourne and Newbold correction, and with a Bonferroni bound over the thirteen candidates. A hypothesis is supported only if the sign is as stated and the corrected test clears the threshold that the protocol fixed; otherwise it is reported as not supported, including when the point estimate is favourable.

The rules are stated in the present tense because they were fixed before the results. The timestamp of the protocol file and the hash of the metrics file are recorded in the repository, so the order can be checked. The repository does not carry a third-party timestamp from before the analysis, and the claim to pre-registration rests on the dated protocol file, the run manifest and the hashes rather than on an external registry. A reader who requires an external timestamp should treat the protocol as documented rather than as registered, and the paper prefers that reading to an overclaim.

## 4 Data

### 4.1 The German series

The primary series is the annual number of passenger car registrations in Germany from 1991 to 2025, 35 observations, taken from the Destatis GENESIS table 46131 and downloaded on 24 November 2026 (Destatis 2026). The series is held in `data/raw/destatis_pkw_neuzulassungen_jahre.csv` and is never edited in place. It runs from 2,567,103 in its lowest year to 3,807,175 in 2009, the year of the scrappage programme, and it contains three events that dominate any comparison: the reunification boom of the early 1990s, the 2009 programme, which pulled forward demand and produced a 23 percent rise against 2008, and the 2020 collapse. The 2008 to 2010 sequence, 3,090,040 then 3,807,175 then 2,916,260, is the reason the absolute loss is used for selection. A squared loss lets those two transitions dominate the ranking of thirteen models, and the ranking then measures the crisis rather than the typical year.

Annual data are used for three reasons. The question is a fifteen-year projection, and monthly seasonality is irrelevant at that horizon. The annual series is the one that is revised consistently and published without breaks. And the origins and horizons of the protocol have to be defined in the same unit as the projection, which is a year. The cost is 35 observations, and the paper is explicit that 35 observations cannot identify a complex model. That is why the candidate set contains models with three parameters at most and why the machine learning candidates are regularised.

### 4.2 The Chinese series

The second series is Volkswagen Group deliveries in China from 1987 to 2025, 38 usable observations, with 2023 missing because the group changed its reporting that year. The series is held in `data/raw/vw_group_china_deliveries.csv`. It is included for a reason that is methodological rather than substantive, and the choice was made before the comparison was run. Volkswagen Group deliveries in China are the largest single market exposure of the firm that the German series describes, the series is published by the group itself in its annual report, and it runs long enough to supply twenty-one origins rather than fifteen. It also has a different data generating process, a different break structure and a different reporting authority. A series chosen because it is easy to forecast would prove nothing; a series chosen because it is the same firm in a different institutional setting is a specification check with a substantive reading, and the null it produces is informative about the method rather than about the analyst. If the protocol produces a winner on the German series and a null on the Chinese series, the difference cannot be attributed to the protocol, because the protocol is the same. That is the logic of a specification check, and it is the logic that makes the null informative.

### 4.3 Transformations and the unit root question

Two transformations are used. The growth rate is the annual change divided by the previous level, and the log difference is the change in the natural logarithm. Both remove the level and both are used in at least one candidate. The protocol does not gate the candidate set on a unit root test. A pre-test would introduce a first-stage selection that is not in the protocol, and the power of the test with 35 observations is low. Instead, both level and growth specifications enter the candidate set, and the rolling-origin comparison decides. This is a deliberate departure from the common practice of testing, then modelling, then reporting only the model that the test selected.

### 4.4 The scale

The scale at origin $m$ is the in-sample mean absolute error of the naive forecast on the window that ends at $m$,

$$
q_m = \frac{1}{T_m - 1} \sum_{t=2}^{T_m} \left| y_t - y_{t-1} \right|, \tag{1}
$$

where $T_m$ is the number of observations available at origin $m$. The scale is recomputed at every origin, so a model that is evaluated in a volatile window is not punished for the volatility of a different window. The consequence is that the naive benchmark does not score exactly one, and the paper reports the benchmark score rather than assuming it.

## 5 Protocol

### 5.1 Objects and the non-anticipative condition

Let $y_t$ be the series observed at annual dates $t = 1, \dots, T$. A forecast produced at origin $m$ for horizon $h$ is written $\hat{y}_{m+h \mid m}$, where $m$ is the last year whose data are used. The information set is $\mathcal{F}_m$, the sigma algebra generated by $y_1, \dots, y_m$. A forecaster is a measurable map $f_h$ from that information set to the real line,

$$
\hat{y}_{m+h \mid m} = f_h(y_1, \dots, y_m), \qquad h \geq 1. \tag{2}
$$

Definition 1. A forecaster is non-anticipative if (2) holds, that is, if the forecast is a function of the information set alone and not of any observation dated after the origin.

Every result in the paper is conditional on Definition 1. The rolling-origin procedure satisfies it by construction, and the Lean module proves the property for the index sets that the procedure uses.

### 5.2 Loss and scaled loss

The error of a forecast is the realised value minus the forecast,

$$
e_{m+h \mid m} = y_{m+h} - \hat{y}_{m+h \mid m}. \tag{3}
$$

The absolute loss is $L_1(e) = |e|$ and the squared loss is $L_2(e) = e^2$. Selection uses the absolute loss, because the absolute loss is consistent for the conditional median and the median is the object a planning department needs: the typical year, not the average of a distribution with a long right tail. The squared loss is reported as a root mean squared error in vehicles and used only as the first tie-break.

At horizon $h$, with $N_h$ origins, the scaled loss is

$$
\mathrm{MASE}_h = \frac{1}{N_h} \sum_{m \in \mathcal{M}_h} \frac{\left| e_{m+h \mid m} \right|}{q_m}, \tag{4}
$$

and the aggregate that the selection rule uses is the unweighted mean over the five horizons,

$$
\mathrm{MASE} = \frac{1}{H} \sum_{h=1}^{H} \mathrm{MASE}_h, \qquad H = 5. \tag{5}
$$

The unweighted mean is a choice. It gives the five-year horizon the same weight as the one-year horizon, which is the right choice when the object of interest is the long projection and the wrong choice when the object is next year's plan. The paper states the choice so that a reader who disagrees can recompute the ranking with weights, and section 7 reports what happens when the loss changes.

### 5.3 The selection functional

A selection rule is a function of the backtest output. Let $C$ be the candidate set, with $|C| = 13$, and let $\bar{M}(c)$, $R(c)$ and $\nu(c)$ be the average MASE, the root mean squared error and the name of candidate $c$. The score is the triple

$$
s(c) = \left( \bar{M}(c), R(c), \nu(c) \right) \in \mathbb{R} \times \mathbb{R} \times \Sigma^{*}, \tag{6}
$$

ordered lexicographically, and the selection functional is

$$
S(C) = \arg\min_{c \in C} s(c). \tag{7}
$$

The order is total on a finite set, so the minimum exists and is unique. The rule is fixed in advance, which is what separates it from a rule chosen after the table is seen. The Lean theorem `selectBest_det` states that identical inputs give identical outputs, which is the formal content of that sentence.

### 5.4 The candidate set

The thirteen candidates are fixed before the backtest and are listed in Table 1. The set is deliberately unbalanced: it contains two benchmarks, six econometric models, four machine learning models and one combination. The purpose is not to give every family an equal chance but to make the comparison informative about the families that a manufacturer would actually consider. Table 2 counts what each candidate is allowed to fit, because a ranking that hides the capacity of the entrants is a ranking that invites the wrong objection.

Table 1. The thirteen candidates, fixed before the backtest.

| Candidate | Family | Specification |
|:--|:--|:--|
| naive | benchmark | last observed level |
| drift | benchmark | last level plus average historical change |
| loglinear | econometric | linear trend on the logarithm of the level |
| ar1_levels | econometric | first order autoregression on the level, rolling window, slope clipped to 0 to 0.98 |
| ar1_growth | econometric | first order autoregression on the growth rate |
| holt | econometric | Holt linear trend, additive |
| holt_damped | econometric | Holt with a damped trend |
| arima_111 | econometric | ARIMA(1,1,1) without drift |
| ridge_lags | machine learning | ridge on three lagged growth rates, penalty fixed at 1.0 |
| ridge_ml | machine learning | ridge on three lags, two growth rates and a time index, penalty fixed at 1.0 |
| random_forest | machine learning | random forest on six features, 400 trees, minimum leaf 2 |
| gradient_boosting | machine learning | gradient boosting on six features, 300 trees of depth 2, learning rate 0.05 |
| combination | ensemble | equal weights on drift, holt and ridge_lags |

Table 2. Capacity of the thirteen candidates, counted from the code that ran the backtest.

| Candidate | Free coefficients | Tuned hyperparameters | Inputs |
|:--|--:|--:|--:|
| naive | 0 | 0 | 0 |
| drift | 2 | 0 | 1 |
| loglinear | 2 | 0 | 1 |
| ar1_growth | 2 | 0 | 1 |
| ar1_levels | 2 | 0 | 1 |
| holt | 2 | 2 | 1 |
| holt_damped | 2 | 3 | 1 |
| arima_111 | 3 | 0 | 1 |
| combination | 0 | 0 | 3 |
| ridge_lags | 4 | 0 | 3 |
| ridge_ml | 7 | 0 | 6 |
| random_forest | 0 | 3 | 6 |
| gradient_boosting | 0 | 3 | 6 |

The winner sits in the middle of the table, with four coefficients against two for the autoregression that finishes second, and the two candidates with the largest capacity, the forest and the boosting machine, finish third and tenth. A forest has no coefficient that can be counted, but with a minimum leaf of two and a training window that starts at fifteen observations it can grow at most seventeen leaves per tree, and the boosting machine grows four leaves in each of three hundred trees. The comparison is therefore not like for like in capacity, and the paper does not claim that it is. What the table establishes is that the winner is not the most flexible entrant and that the ranking is not a story about capacity.

Two constraints apply to every candidate. No candidate may use an observation dated at or after the origin, and no hyperparameter may be selected on the evaluation sample. The constants are fixed in the code before the backtest: the ridge penalty at 1.0, the forest at 400 trees with a minimum leaf of 2, the boosting machine at 300 trees of depth 2. None of them is tuned on the evaluation sample, because none of them is tuned at all. The Holt and damped Holt models are the exception, and their two and three smoothing constants are chosen by a grid search inside each training window, which is the only split that respects the arrow of time.

### 5.5 Origins, horizons and windows

The origins run from 2006 to 2020, fifteen origins. At origin $m$ the training window starts in 1991 and ends at $m$, so the window expands. The minimum training length is fifteen observations, which is reached at the first origin. Each model is asked for horizons one to five, so each model produces $15 \times 5 = 75$ errors and each horizon has fifteen errors. The evaluation targets therefore run from 2007 to 2025, nineteen distinct years, which is the source of the overlap that the test has to correct. Two index conventions meet at this point and the paper states both. In the data, years are numbered from one and the window at origin $m$ contains observations 1 to $m$, the origin year included, because the origin year is observed before the forecast is made. In the Lean module, indices start at zero, so the same window is the set of indices strictly below the origin index, which is what `trainIdx_lt` states. The theorem and the code say the same thing in different numbering, and the translation is one line of arithmetic.

The evaluation ends at the 2020 origin, whose last target is 2025. The projection uses a separate origin, 2025, which is not part of the evaluation: the model is refitted on the full sample and iterated to 2040 at horizons one to fifteen. The projection is not evaluated, because the future is not available; it is reported with an interval built from the backtest errors, and the interval is the object that carries the uncertainty.

### 5.6 Tests

The comparison of two sequences uses the loss differential

$$
d_{m,h} = \left| e^{(A)}_{m,h} \right| - \left| e^{(0)}_{m,h} \right|, \tag{8}
$$

with $A$ the candidate and $0$ the naive benchmark. The long run variance uses a Bartlett kernel truncated at $h-1$ lags, because forecasts $h$ steps ahead overlap by $h-1$ target years,

$$
\hat{V}_h = \hat{\gamma}_0 + 2 \sum_{k=1}^{h-1} \left(1 - \frac{k}{h}\right) \hat{\gamma}_k, \qquad
\mathrm{DM}_h = \frac{\bar{d}_h}{\sqrt{\hat{V}_h / N_h}}. \tag{9}
$$

With fifteen origins the normal reference is too generous, so the Harvey, Leybourne and Newbold correction scales the statistic and refers it to a $t$ distribution with $N_h - 1$ degrees of freedom,

$$
\mathrm{DM}^{\mathrm{HLN}}_h = \mathrm{DM}_h \sqrt{\frac{N_h + 1 - 2h + h(h-1)/N_h}{N_h}}. \tag{10}
$$

The pooled statistic that stacks the 75 errors is reported in the metrics file and is not used as a test. The reason is stated in section 2.3: the 75 errors are not 75 independent observations, and a variance truncated at zero lags understates the dependence.

### 5.7 The interval

The interval is empirical. The relative error of the selected model is computed at every origin and horizon, the quantiles at 2.5 and 97.5 percent are taken from the pooled distribution, and the bounds are applied to the point projection. The lower bound is clipped at zero, because registrations cannot be negative. The interval is therefore a statement about the errors that the model actually made, not a statement derived from a Gaussian assumption that the errors do not satisfy.

### 5.8 The Lean module

The deterministic skeleton of the split is written in Lean 4.36.0 without Mathlib. The module defines the training index set at an origin, the expanding window and the fixed length window, and it proves nine theorems. Four carry the property that matters: every index in the training set is strictly below the origin (`trainIdx_lt`), the origin is never in the training set (`origin_not_in_train`), the expanding window is nested (`trainIdx_mono`), and a fixed length window ending before the origin never reaches it (`rollIdx_lt`). Selection is a fold over the candidate list (`selectBest`), and `selectBest_det` states that it is a function. The module compiles in seconds and has no dependencies. It does not formalise estimation, asymptotics, the projection or the interval, and the paper does not claim that it does. The distinction matters for how the rest of the paper should be read. The kernel certifies that no observation dated at or after the origin can enter the training set and that the selection is a deterministic function of the backtest output. It says nothing about whether the loss is the right loss, whether the test has the right size, or whether the projection is accurate. A reader who wants a proof of the forecast will not find one in the module, and the paper does not offer one.

### 5.9 Pseudocode

The procedure is short enough to state in full.

```
protocol(y, candidates, origins, horizons, loss, scale):
    for m in origins:
        train = y[1 .. m]                      # proved: no index >= m
        for h in horizons:
            for c in candidates:
                theta = fit(c, train)          # hyperparameters inside train only
                yhat[c, m, h] = predict(c, theta, h)
                e[c, m, h] = y[m + h] - yhat[c, m, h]
    for c in candidates:
        score[c] = (mean_h mean_m |e[c]| / scale(train_m), rmse(c), name(c))
    winner = argmin_lex(score)
    report(winner, dm_by_horizon(winner, naive), interval(winner))
```

The pseudocode is the protocol in operational form. The comment on the first line is the theorem, not a hope.

## 6 Results

### 6.1 The ranking

Table 3 reports the thirteen candidates in the order fixed by the selection functional. Ridge regression on three lagged growth rates is first with an average MASE of 1.2839, a root mean squared error of 335,728.61 vehicles and a bias of minus 125,280.19. The naive benchmark is sixth with 1.5952, and the gap is 0.3113 scaled units, or 19.5 percent of the benchmark. The autoregression on levels is second at 1.4315, which is consistent with the persistence of the series: a short rolling window with a clipped slope is a disciplined way to use the level. The random forest is third at 1.4829, ahead of the equal-weight combination at 1.5544 and ridge on lags with time features at 1.5558, and gradient boosting is tenth at 1.6559, which is the familiar result that boosted trees need more data than 35 annual observations.

Table 3. Backtest results, German registrations, fifteen origins and five horizons.

| Rank | Candidate | Family | MASE | RMSE | Bias |
|--:|:--|:--|--:|--:|--:|
| 1 | ridge_lags | machine learning | 1.2839 | 335,728.61 | -125,280.19 |
| 2 | ar1_levels | econometric | 1.4315 | 362,808.50 | -164,271.41 |
| 3 | random_forest | machine learning | 1.4829 | 386,614.64 | -154,135.10 |
| 4 | combination | ensemble | 1.5544 | 430,812.04 | -94,694.75 |
| 5 | ridge_ml | machine learning | 1.5558 | 408,552.58 | -184,112.17 |
| 6 | naive | benchmark | 1.5952 | 451,926.96 | -119,880.25 |
| 7 | holt_damped | econometric | 1.5989 | 444,472.01 | -114,556.10 |
| 8 | arima_111 | econometric | 1.6078 | 443,993.50 | -76,389.92 |
| 9 | loglinear | econometric | 1.6338 | 410,688.66 | -237,333.96 |
| 10 | gradient_boosting | machine learning | 1.6559 | 439,249.86 | -159,726.12 |
| 11 | drift | benchmark | 1.6734 | 472,196.48 | -82,018.72 |
| 12 | ar1_growth | econometric | 1.9174 | 576,204.74 | -150,518.36 |
| 13 | holt | econometric | 1.9288 | 548,451.72 | -76,785.33 |

Two features of the table matter for interpretation. The spread between the first and the last candidate is 0.6449 scaled units, which is large relative to the differences among the top five, and it says that the choice of family matters more than the choice of hyperparameter within a family. The bias is negative for every candidate, which means that every model underpredicts on average over the evaluation period, and the smallest bias belongs to arima_111 at minus 76,389.92, not to the winner. A model can win on absolute error and still carry a bias, and the paper reports both.

### 6.2 The horizon profile

The average MASE hides the horizon. Table 4 reports the winner against the benchmark at each horizon, with the loss differential in vehicles, the Diebold and Mariano statistic, the Harvey, Leybourne and Newbold correction, the p value from the corrected statistic, and a bootstrap p value computed by resampling the fifteen origins and re-estimating the long-run variance in every resample.

Table 4. Ridge on lagged growth against naive, by horizon, Germany.

| Horizon | MASE, ridge | MASE, naive | Gain, vehicles | DM | DM corrected | p value | Bootstrap p |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | 1.1333 | 1.2397 | -20,859 | -0.402 | -0.388 | 0.7037 | 0.7244 |
| 2 | 1.2900 | 1.5258 | -50,628 | -1.033 | -0.929 | 0.3685 | 0.5200 |
| 3 | 1.3639 | 1.5784 | -48,663 | -1.029 | -0.857 | 0.4061 | 0.5102 |
| 4 | 1.3186 | 1.7769 | -104,632 | -3.800 | -2.911 | 0.0114 | 0.2196 |
| 5 | 1.3135 | 1.8550 | -127,569 | -4.303 | -3.009 | 0.0094 | 0.3232 |

The profile is the finding. The point estimate is better at every horizon, and the gain grows from 20,859 vehicles at one year, 7.6 percent of the naive error, to 127,569 vehicles at five years, 29.9 percent. The pre-specified statistic rejects equal accuracy at four years, minus 2.911 with a p value of 0.011, and at five years, minus 3.009 with 0.009. It does not reject at one to three years, where the statistic is below one in absolute value.

The bootstrap column is the reason the paper does not stop there. When the fifteen origins are resampled and the long-run variance is estimated again in each resample, the same statistic produces p values of 0.220 at four years and 0.323 at five. The asymptotic p value treats the estimated variance as known. With fifteen observations and three autocovariances the variance is itself a random quantity with a wide distribution, and the bootstrap says so. The pre-specified test is reported because the protocol fixed it, the bootstrap is reported because the protocol is supposed to be auditable, and the two disagree.

The direction of the overlap correction explains part of the disagreement. The usual warning is that ignoring overlap understates the variance and overstates significance, which assumes positively autocorrelated differentials. Here the estimated autocovariances are negative: at four years the first two are minus 14.8 billion and minus 11.8 billion, so the corrected variance is about a quarter of the zero-lag variance and the statistic rises from minus 1.874 to minus 3.800 before the small sample factor shrinks it to minus 2.911. The differential alternates with the cycle, with a large favourable value at the 2009 origin and a large unfavourable one at 2020, and alternation is negative autocorrelation. A variance estimated from three such autocovariances is a fragile object, and the bootstrap is the check that makes the fragility visible.

### 6.3 The projection and the interval

The selected model is projected from the 2025 origin to 2040. The point forecast is 3,161,958.51 registrations. The empirical 95 percent interval runs from 2,563,157.85 to 3,689,022.75, a width of 1,125,864.90 vehicles, about 36 percent of the point. The interval is asymmetric in proportional terms: the lower bound is 18.9 percent below the point and the upper bound is 16.7 percent above it, because the distribution of relative errors has a longer right tail than left.

The interval is the object the paper recommends for planning. A point forecast invites a decision at the point, and a decision at the point is a decision at the 50th percentile of a distribution whose 5th percentile is 700,000 vehicles lower. A corridor invites a decision that is robust to the range, which is the form in which capacity, sourcing and workforce plans are actually made.

### 6.4 The Chinese null

The same protocol is applied to Volkswagen Group deliveries in China. No candidate beats the random walk. The best scaled error in the set is 7.7778, the corrected test against naive gives a p value of 0.9615, and the autoregression on levels comes closest to the benchmark without beating it. The scale is large because the Chinese series moves by millions of vehicles between adjacent years, and a scaled error of 7.7778 is a statement about the scale of the breaks, not about the quality of the code.

The result is reported unchanged. It is the specification check that the protocol needs: a method that produces a winner on one series and a null on another, with the same rule and the same code, is a method that is measuring something about the series rather than something about the analyst. The null also has a substantive reading, which is that the Chinese series behaves like a random walk over the evaluation period, and a random walk is a level model with a unit root. Chapter 11 of the dissertation treats the Chinese path as a set of conditional scenarios rather than as a forecast, and the paper does not repeat that argument.

## 7 Robustness

### 7.1 Leave one origin out

The check deletes each origin in turn, recomputes the average MASE on the remaining fourteen, and records the rank of the winner. Ridge on lagged growth is first in fifteen of fifteen deletions. The ratio to naive ranges from 0.7415, when 2020 is deleted, to 0.8816, when 2009 is deleted, so the reduction lies between 11.84 and 25.85 percent. The smallest margin over the runner-up is 0.1062, which occurs when 2009 is removed, and the largest is 0.1599. The deletion changes the size of the gain and not its sign.

The 2009 case is the expected extreme. That origin is the most favourable for the model at four years, with a contribution of minus 522,931 vehicles, so removing it shrinks the apparent gain. The 2020 case is the other extreme: the 2024 level, 2,817,331, was close to the 2020 level, 2,917,678, so the flat forecast was nearly right and the model's advantage narrowed. Neither deletion moves the winner.

### 7.2 Alternative losses

Five alternative criteria are computed on the same errors: mean absolute error, root mean squared error, median absolute error, mean absolute percentage error and a trimmed mean that removes the three largest absolute errors per model. The winner is first under all five, with a ratio to naive between 0.7429 and 0.8634. The Spearman correlation between the MASE ranking and the alternative rankings is 0.995 for mean absolute error, 1.000 for percentage error, 0.995 for the trimmed mean, 0.857 for the root mean squared error and 0.516 for the median absolute error. The top is stable and the middle is not, which is the correct reading: the identity of the winner does not depend on the loss, and the ordering of the candidates below the top does.

### 7.3 Multiplicity

Thirteen candidates and five horizons are sixty comparisons against the benchmark, and a nominal five percent threshold is not a family-wise five percent. Three corrections are reported, because they answer three different questions.

The pre-registered family is the thirteen candidates at the pooled level. The archived pooled statistic gives a p value of 0.0051, and a Bonferroni bound multiplies it by thirteen to 0.0663, which does not clear five percent. The Šidák adjustment gives 0.0643 and Holm gives 0.0663. The pooled statistic itself is examined in section 7.5 and is not the test this paper defends.

The family that the paper does defend is the five horizon tests. A Bonferroni bound over thirteen candidates applied to the strongest horizon gives 0.0114 times thirteen, 0.148 at four years, and 0.0094 times thirteen, 0.122 at five years. Neither clears five percent.

The third correction is a stepdown max-t over the thirteen candidates with the variance clustered by origin, which is the bootstrap procedure of Romano and Wolf (2005). It gives an adjusted p value of 0.420 for the winner. The only candidate that separates from the benchmark under this correction is Holt, at plus 3.181 with an adjusted p value of 0.009, and the separation is in the wrong direction: Holt is significantly worse. The design can detect a large deterioration and cannot detect a moderate improvement, which is the definition of low power and is quantified in section 7.4.

The bound over thirteen independent tests is conservative because the candidates are correlated. The mean off-diagonal correlation of the twelve pooled loss differentials is 0.237, and the eigenvalues of their correlation matrix fall from 6.093 to 0.009, so most of the twelve dimensions are one or two common factors. The effective number of tests is 3.07, which gives a family-wise error of 0.035 for the horizon test at five years and 0.031 at four. The truth lies between 0.031 and 0.148, and the paper reports the range rather than choosing the flattering end.

### 7.4 What fifteen origins can detect

A test that does not reject is informative only if it could have rejected. Table 5 reports the minimum detectable effect at 80 percent power for each horizon, computed from the observed standard deviation of the loss differential, and the power that the design actually had at the effect that was observed.

Table 5. What fifteen origins can detect, German series.

| Horizon | Naive MAE | Observed gain | Percent | MDE | Percent | Power |
|--:|--:|--:|--:|--:|--:|--:|
| 1 | 274,365 | 20,859 | 7.6 | 161,901 | 59.0 | 0.07 |
| 2 | 340,054 | 50,628 | 14.9 | 172,323 | 50.7 | 0.13 |
| 3 | 355,414 | 48,663 | 13.7 | 193,254 | 54.4 | 0.11 |
| 4 | 403,400 | 104,632 | 25.9 | 168,181 | 41.7 | 0.42 |
| 5 | 426,485 | 127,569 | 29.9 | 164,885 | 38.7 | 0.58 |

The table is the honest answer to the sample size objection. With fifteen origins the design can detect a gain of about 162,000 to 193,000 vehicles, which is 39 to 59 percent of the naive error. The observed gain is 21,000 to 128,000 vehicles, 8 to 30 percent. The power at the observed effect runs from 0.07 at one year to 0.58 at five. A null result at one to three years therefore says very little: a gain of 40 percent would have been needed to reject, and no plausible model delivers 40 percent against a random walk on this series. The rejection at five years is at the edge of detectability, which is why the bootstrap in Table 4 matters.

The same arithmetic explains the multiplicity result. The only candidate that separates from the benchmark under the clustered stepdown is Holt, and it separates because its deterioration is larger than the improvement of the winner. Low power is not symmetric: it hides small gains and reveals large losses.

### 7.5 The pooled statistic and the variance

The pooled statistic in the metrics file is minus 2.802 with a p value of 0.0051. It is computed on the 75 stacked errors with the long-run variance truncated at zero lags, because the scoring function calls the test with the default horizon of one. That construction treats five overlapping errors per origin as independent draws and ignores the correlation between adjacent origins. It is the number the pre-registered protocol produced, and it is not a valid test at the pooled level.

Four replacements are reported in Table 6. The first treats the fifteen horizon differentials as independent and refers the mean to a t distribution with fourteen degrees of freedom; it is the most conservative of the asymptotic versions and gives p 0.082 at four years and 0.035 at five. The second is the pre-specified Bartlett and Harvey, Leybourne and Newbold statistic, with p 0.011 and 0.009. The third resamples origins and re-estimates the variance, with p 0.220 and 0.323. The fourth clusters the five horizons within each origin and tests the pooled mean across fifteen origins: the mean differential is minus 70,470 vehicles, the statistic is minus 1.427 and the p value is 0.175. That is the correct pooled test for this design, and it does not reject.

Table 6. The same comparison under four variance estimators, German series.

| Horizon | t, independent | p | DM corrected | p | Bootstrap p | Variance ratio |
|--:|--:|--:|--:|--:|--:|--:|
| 1 | -0.388 | 0.7037 | -0.388 | 0.7037 | 0.7244 | 0.93 |
| 2 | -0.885 | 0.3910 | -0.929 | 0.3685 | 0.5200 | 0.73 |
| 3 | -0.759 | 0.4606 | -0.857 | 0.4061 | 0.5102 | 0.54 |
| 4 | -1.874 | 0.0819 | -2.911 | 0.0114 | 0.2196 | 0.24 |
| 5 | -2.331 | 0.0352 | -3.009 | 0.0094 | 0.3232 | 0.29 |

A moving block bootstrap with blocks of two adjacent origins, which preserves the dependence between neighbouring origins, gives p 0.385 at four years and 0.488 at five. The weaker the dependence assumption, the weaker the evidence, and the range runs from 0.009 to 0.488. The columns do not agree, and the disagreement is the result. A paper that reported only the third column would claim significance at four and five years. A paper that reported only the first or the fourth would claim none. The honest statement is that the point estimate is stable and the inference is not: the winner is better at every horizon by a margin that grows with the horizon, and whether that margin is distinguishable from zero depends on an assumption about the variance that fifteen observations cannot settle.

### 7.6 What the checks do not cover

The deletion holds the forecasts fixed, so it measures the influence of a year on the average, not the uncertainty of a model estimated without it. A refitted deletion would be the correct version and is not run, because the archived backtest stores forecasts and not fitted objects. The alternative losses use the same errors, so they test the criterion and not the data. The multiplicity correction assumes that the candidate set is the family, and a reader who believes that other models should have been included is testing a different family. These limits are stated because a robustness section that claims to cover everything covers nothing. The power calculation has a limit of its own: it takes the observed standard deviation as the population value, and that standard deviation is estimated from fifteen observations. A wider true dispersion would lower the power further, a narrower one would raise it, and the table should be read as an order of magnitude rather than as a calibrated statement.

## 8 Discussion

The result that matters is not that ridge regression wins. It is that a rule fixed in advance, applied to a short annual series, produces a winner whose advantage is concentrated at the horizon the projection uses, a benchmark that is not beaten on a second series, and an interval that is wide enough to change a decision. A paper that reported only the first of those would be a paper about a model. The four together are a paper about a method.

Three limitations bound the claim. The sample is 35 annual observations from one country, and the evaluation period contains three structural breaks, so the winner is the best model for a period that includes the breaks rather than the best model for any period. The comparison is univariate, and a multivariate model with leading indicators could beat every candidate in the set; the protocol does not claim otherwise, it claims that within the set the ranking is fixed and reproducible. The interval is pooled across horizons, calibrated on five-step errors and applied to a fifteen-step projection, which makes it too narrow at the long end. The dissertation reports a horizon-specific calibration as an extension and treats the interval in this paper as a lower bound on the uncertainty.

A fourth limitation is the one this section has been circling. The sample supports a point estimate and not a verdict. The protocol was designed for a series that grows by one observation a year, and fifteen origins is what thirty-five years of annual data can supply at a five-year horizon. The remedy is not a different test on the same fifteen numbers; it is more origins, a quarterly series, or a panel of markets that share the protocol. The paper reports the effect size, the interval and the range of p values so that a reader who has those data can rerun the rule and see whether the conclusion travels.

The external validity of the Chinese null is similarly bounded. The series is one firm's deliveries in one market, and the null says that the series behaves like a random walk over the evaluation window, not that Chinese demand is unpredictable in principle. A different window, a different firm or a different frequency could produce a different result, and the protocol would report it.

## 9 Conclusion

The paper fixes a forecast comparison before the results are known, proves the split in Lean 4, and reports what the comparison produces on two series. On German passenger car registrations, ridge regression on three lagged growth rates beats the naive benchmark by 19.5 percent in average scaled error, the advantage is concentrated at horizons four and five, and the projection to 2040 is 3,161,958.51 vehicles with a 95 percent interval from 2,563,157.85 to 3,689,022.75. On Volkswagen Group deliveries in China, no candidate beats the random walk, and the null is published unchanged.

The statistical verdict is narrower than the point estimate. The pre-specified test rejects at four and five years, the bootstrap and the family-wise corrections do not, and the paper leaves the question open rather than closing it in its own favour. What it does close is the accounting: the candidate set, the split, the loss and the rule are fixed, the split is proved, and every number in the tables can be recomputed from the archived files.

The contribution is the protocol, not the number. A reader who disagrees with the candidate set can add a model and rerun the rule. A reader who disagrees with the loss can recompute the ranking, and section 7 reports what happens. A reader who doubts the split can read the Lean module, which is nine theorems and no dependencies. That is the standard the paper sets for itself, and it is the standard against which the other eleven papers in the programme are written.

## Data availability

The German series is Destatis GENESIS table 46131, downloaded on 24 November 2026 and stored in `thesis/data/raw/destatis_pkw_neuzulassungen_jahre.csv`, SHA256 47f9609c55769afd926c356501161afa8bcdee61b073567955826e9cd1235c37. The Chinese series is stored in `thesis/data/raw/vw_group_china_deliveries.csv`. The backtest output, the metrics file and the Diebold and Mariano matrix are in `thesis/data/model/`; the metrics file used in Table 3 has SHA256 3e408618afedf7357dab24573527e955250a98d76b6aad5c8c96c26ab6457362. All series are public and none is edited in place.

## Code availability

The protocol, the thirteen candidates, the rolling-origin loop and the interval are implemented in Python in `thesis/analysis/`. The Lean 4 module is `lean_poc/Protocol.lean`, with a checking harness in `lean_poc/Check.lean`, built with Lean 4.36.0 and no Mathlib. The repository is prepared for publication at github.com/kajevic44-sudo/forecast2040-protocol, with one commit per unit and a README that reproduces Tables 2 and 3 with one command.

## References

Andersen, Torben G., Dobrislav Dobrev, and Ernst Schaumburg. 2012. "Jump-robust volatility estimation using nearest neighbor truncation." *Journal of Econometrics* 169 (1): 75-93. https://doi.org/10.1016/j.jeconom.2012.01.011

Armstrong, J. Scott. 2001. *Principles of Forecasting: A Handbook for Researchers and Practitioners*. Boston: Kluwer Academic Publishers.

Baker, Monya. 2016. "1,500 scientists lift the lid on reproducibility." *Nature* 533 (7604): 452-454. https://doi.org/10.1038/533452a

Bergmeir, Christoph, and José M. Benítez. 2012. "On the use of cross-validation for time series predictor evaluation." *Information Sciences* 191: 192-213. https://doi.org/10.1016/j.ins.2011.12.028

Bergmeir, Christoph, Rob J. Hyndman, and Bonsoo Koo. 2018. "A note on the validity of cross-validation for evaluating autoregressive time series prediction." *Computational Statistics & Data Analysis* 120: 70-83. https://doi.org/10.1016/j.csda.2017.11.003

Breiman, Leo. 2001. "Random Forests." *Machine Learning* 45 (1): 5-32. https://doi.org/10.1023/A:1010933404324

Cerqueira, Vitor, Luis Torgo, and Igor Mozetič. 2020. "Evaluating time series forecasting models: an empirical study on performance estimation methods." *Machine Learning* 109 (11): 1997-2028. https://doi.org/10.1007/s10994-020-05910-7

China Association of Automobile Manufacturers. 2025. *Annual Production and Sales Data*. Accessed 24 November 2026. http://www.caam.org.cn.

Christensen, Garret, and Edward Miguel. 2018. "Transparency, Reproducibility, and the Credibility of Economics Research." *Journal of Economic Literature* 56 (3): 920-980. https://doi.org/10.1257/jel.20171350

Clark, Todd E., and Kenneth D. West. 2007. "Approximately normal tests for equal predictive accuracy in nested models." *Journal of Econometrics* 138 (1): 291-311. https://doi.org/10.1016/j.jeconom.2006.05.023

Community, The mathlib. 2020. "The lean mathematical library." *Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs*: 367-381. https://doi.org/10.1145/3372885.3373824

Diebold, Francis X., and Roberto S. Mariano. 1995. "Comparing Predictive Accuracy." *Journal of Business & Economic Statistics* 13 (3): 253-263. https://doi.org/10.1080/07350015.1995.10524599

Efron, Bradley, and Robert J. Tibshirani. 1993. *An Introduction to the Bootstrap*. New York: Chapman and Hall.

European Automobile Manufacturers Association. 2025. *Motor Vehicle Registrations in the EU by Country and Vehicle Type*. Accessed 24 November 2026. https://www.acea.auto.

Friedman, Jerome H.. 2001. "Greedy function approximation: A gradient boosting machine." *The Annals of Statistics* 29 (5): 1189-1232. https://doi.org/10.1214/aos/1013203451

Gardner, Everette S., and Ed. Mckenzie. 1985. "Forecasting Trends in Time Series." *Management Science* 31 (10): 1237-1246. https://doi.org/10.1287/mnsc.31.10.1237

Gelman, Andrew, and Eric Loken. 2014. "The Statistical Crisis in Science." *American Scientist* 102 (6): 460. https://doi.org/10.1511/2014.111.460

Giacomini, Raffaella, and Halbert White. 2006. "Tests of Conditional Predictive Ability." *Econometrica* 74 (6): 1545-1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Gneiting, Tilmann, and Matthias Katzfuss. 2014. "Probabilistic Forecasting." *Annual Review of Statistics and Its Application* 1 (1): 125-151. https://doi.org/10.1146/annurev-statistics-062713-085831

Harvey, Andrew C., Stephen J. Leybourne, and Paul Newbold. 1997. "Testing the Equality of Prediction Mean Squared Errors." *International Journal of Forecasting* 13 (2): 281-291. https://doi.org/10.1016/S0169-2070(96)00719-4

Hoerl, Arthur E., and Robert W. Kennard. 1970. "Ridge Regression: Biased Estimation for Nonorthogonal Problems." *Technometrics* 12 (1): 55-67. https://doi.org/10.1080/00401706.1970.10488634

Hyndman, Rob J., and Anne B. Koehler. 2006. "Another look at measures of forecast accuracy." *International Journal of Forecasting* 22 (4): 679-688. https://doi.org/10.1016/j.ijforecast.2006.03.001

Hyndman, Rob J., and George Athanasopoulos. 2021. *Forecasting: Principles and Practice*. 3rd ed. Melbourne: OTexts.

International Energy Agency. 2025. *Global EV Outlook 2025*. Paris: IEA. https://www.iea.org/reports/global-ev-outlook-2025.

Klier, Thomas H., and James Rubenstein. 2008. *Who Really Made Your Car? Restructuring and Geographic Change in the Auto Industry*. Kalamazoo: W.E. Upjohn Institute.

Kraftfahrt-Bundesamt. 2025. *Fahrzeugzulassungen, FZ 28: Elektrische Antriebe*. Accessed 24 November 2026. https://www.kba.de.

Lawrence, Michael, Paul Goodwin, Marcus O'Connor, and Dilek Önkal. 2006. "Judgmental forecasting: A review of progress over the last 25years." *International Journal of Forecasting* 22 (3): 493-518. https://doi.org/10.1016/j.ijforecast.2006.03.007

Makridakis, Spyros, and Michèle Hibon. 2000. "The M3-Competition: results, conclusions and implications." *International Journal of Forecasting* 16 (4): 451-476. https://doi.org/10.1016/S0169-2070(00)00057-1

Makridakis, Spyros, Evangelos Spiliotis, and Vassilios Assimakopoulos. 2020. "The M4 Competition: 100,000 time series and 61 forecasting methods." *International Journal of Forecasting* 36 (1): 54-74. https://doi.org/10.1016/j.ijforecast.2019.04.014

Meese, Richard A., and Kenneth Rogoff. 1983. "Empirical Exchange Rate Models of the Seventies: Do They Fit Out of Sample?" *Journal of International Economics* 14 (1-2): 3-24.

Moura, Leonardo de, and Sebastian Ullrich. 2021. "The Lean 4 Theorem Prover and Programming Language." *Lecture Notes in Computer Science*: 625-635. https://doi.org/10.1007/978-3-030-79876-5_37

Munafò, Marcus R., Brian A. Nosek, Dorothy V. M. Bishop, Katherine S. Button, Christopher D. Chambers, Nathalie Percie du Sert, Uri Simonsohn, Eric-Jan Wagenmakers, Jennifer J. Ware, and John P. A. Ioannidis. 2017. "A manifesto for reproducible science." *Nature Human Behaviour* 1 (1): . https://doi.org/10.1038/s41562-016-0021

Nosek, Brian A., Charles R. Ebersole, Alexander C. DeHaven, and David T. Mellor. 2018. "The preregistration revolution." *Proceedings of the National Academy of Sciences* 115 (11): 2600-2606. https://doi.org/10.1073/pnas.1708274114

Peng, Roger D.. 2011. "Reproducible Research in Computational Science." *Science* 334 (6060): 1226-1227. https://doi.org/10.1126/science.1213847

Romano, Joseph P., and Michael Wolf. 2005. "Exact and Approximate Stepdown Methods for Multiple Hypothesis Testing." *Journal of the American Statistical Association* 100 (469): 94-108. https://doi.org/10.1198/016214504000000539.

Simmons, Joseph P., Leif D. Nelson, and Uri Simonsohn. 2011. "False-Positive Psychology." *Psychological Science* 22 (11): 1359-1366. https://doi.org/10.1177/0956797611417632

Statistisches Bundesamt. 2026. *GENESIS-Online, table 46131: Passenger Car Registrations*. Accessed 24 November 2026. https://www-genesis.destatis.de.

Sturgeon, T., J. Van Biesebroeck, and G. Gereffi. 2008. "Value chains, networks and clusters: reframing the global automotive industry." *Journal of Economic Geography* 8 (3): 297-321. https://doi.org/10.1093/jeg/lbn007

Tashman, Leonard J.. 2000. "Out-of-sample tests of forecasting accuracy: an analysis and review." *International Journal of Forecasting* 16 (4): 437-450. https://doi.org/10.1016/S0169-2070(00)00065-0

Teece, David J.. 2010. "Business Models, Business Strategy and Innovation." *Long Range Planning* 43 (2-3): 172-194. https://doi.org/10.1016/j.lrp.2009.07.003

Tetlock, Philip E. 2005. *Expert Political Judgment: How Good Is It? How Can We Know?* Princeton: Princeton University Press.

Timmermann, Allan. 2006. "Chapter 4 Forecast Combinations." *Handbook of Economic Forecasting*: 135-196. https://doi.org/10.1016/S1574-0706(05)01004-9

Volkswagen AG. 2025. *Annual Report 2025*. Wolfsburg: Volkswagen AG.
