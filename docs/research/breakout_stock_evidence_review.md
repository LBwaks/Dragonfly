# Detecting Breakout Stocks

**Evidence review and implementation blueprint for Dragonfly**  
**Research date:** 15 September 2026  
**Scope:** US equities; intraday, days-to-weeks, and months-to-one-year horizons

> This is research and system-design material, not investment advice. A signal can identify a precisely defined price breakout and estimate its probability of follow-through; it cannot prove in real time that the breakout will succeed.

## Executive conclusion

The central thesis is **breakout detection**: identify when a stock leaves a previously established price range or resistance boundary, then estimate whether that break is likely to hold. Momentum becomes supporting evidence of follow-through, not the object being detected.

The evidence supports a layered test:

1. **Boundary:** define the resistance level using only information available before the current bar.
2. **Crossing:** price closes above that level by a volatility- or spread-aware buffer.
3. **Acceptance:** price remains above the broken level, retests it successfully, or continues during subsequent completed bars.
4. **Confirmation:** relative strength, industry participation, volume/liquidity, or a catalyst supports the move.
5. **Risk:** market regime, volatility, extension, and transaction costs do not overwhelm the prospective payoff.

The cleanest research definitions are an opening-range break intraday, a close above a prior 20- or 55-session high for swing trading, and a close above a 52-week or multi-month base high for structural breakouts. A raw crossing is observable, but expected follow-through depends on confirmation and market state. The best supporting attributes are proximity to the 52-week high, horizon-matched relative strength, industry leadership, continuity of the advance, volume/liquidity, and volatility-aware distance above the boundary. Intraday evidence is narrower and more execution-sensitive than daily or multi-month evidence.

Traditional indicators such as RSI, MACD, moving-average crosses, and ADX can be useful **secondary features**, but they do not define a breakout. A breakout requires an explicit ex-ante boundary and an observable crossing. Several indicators calculated from the same closing prices must not be counted as independent confirmations.

## What a breakout should mean

For security \(i\), let the resistance boundary at time \(t\) be the maximum high over the previous \(N\) completed bars:

\[
B_{i,t}^{(N)}=\max(H_{i,t-N},\ldots,H_{i,t-1})
\]

A long breakout event occurs when the completed-bar close exceeds that boundary by a required buffer:

\[
C_{i,t} > B_{i,t}^{(N)} + \max(k\,ATR_{i,t},\;s\,Spread_{i,t})
\]

The buffer may be zero in a baseline test, but production rules should test ATR- or spread-based buffers to reject trivial crossings. A breakout candidate becomes confirmed only if it exhibits acceptance above the boundary—for example, two closes above it, a successful retest, or positive residual follow-through. The exact \(N\), \(k\), confirmation window, and exit must be selected out of sample.

This separates three questions that are often conflated:

- **Detection:** did price cross a pre-existing boundary?
- **Confirmation:** did the market accept price above that boundary?
- **Prediction:** is the conditional forward return after costs favorable?

A broad-market rally can lift a stock through resistance without stock-specific strength, while a one-tick breach can be a false breakout. Relative/residual return helps distinguish these cases.

## Evidence-ranked signal map

Ratings below are judgments from the cited literature, not guarantees. “Strong” means replicated economic evidence across long samples or markets; “moderate” means useful but conditional; “weak” means chiefly descriptive, specification-sensitive, or practitioner-based.

| Attribute | Intraday | Days–weeks | Months–year | Evidence | Interpretation |
|---|---:|---:|---:|---|---|
| Close above an ex-ante range high | Core event | Core event | Core event | Moderate | The most objective breakout definition; success remains conditional. |
| Acceptance above the old boundary | Strong | Strong | Strong | Proposed synthesis | Separates a momentary breach from a held breakout. |
| Price near or through 52-week high | No | Moderate | Strong | Strong | Anchoring evidence supports major-high breakouts better than arbitrary chart lines. |
| Horizon-matched relative/residual return | Useful | Strong | Strong | Strong | Confirms that the crossing is not merely market or sector beta. |
| Industry leadership | Moderate | Strong | Strong | Strong | Breakouts are more credible when the industry participates. |
| Continuous advance rather than one jump | Useful | Strong | Strong | Strong | Helps separate gradual diffusion from an already-consumed discrete shock. |
| Earnings/news plus post-break follow-through | Strong around event | Strong | Moderate | Strong, cost-sensitive | Supplies a reason for range revaluation; timestamps and execution costs matter. |
| Abnormal volume / turnover | Strong context | Moderate | Moderate | Moderate | Confirms participation, but extreme turnover can signal late-stage attention. |
| Prior range compression | Moderate | Plausible | Plausible | Limited/mixed | A popular setup hypothesis; it needs independent validation and is not required by breakout theory. |
| Moving-average trend state | Descriptive | Moderate | Moderate | Mixed | Useful context; not the breakout event itself. |
| Order imbalance | Useful | Limited | No | Moderate, microstructure-specific | Can confirm pressure; sensitive to feed, venue, spread, and impact. |
| RSI, MACD, stochastic oscillator | Descriptive | Weak–mixed | Weak–mixed | Weak standalone alpha | Redundant transforms of the price path, not independent proof. |
| Volatility-scaled sizing / failed-break exit | Essential | Strong | Strong | Strong risk logic | Controls loss distribution; it does not predict success by itself. |

## Horizon 1 — intraday breakouts (minutes to hours)

### What the research supports

An intraday breakout is a completed-bar close above a boundary that existed before the bar: the pre-market high, first 5/15/30-minute range, prior-day high, or rolling intraday high. These are distinct strategies and must not be pooled without labeling the boundary type.

Gao, Han, Li, and Zhou find that the first half-hour market return predicts the last half-hour return in SPY from 1993–2013, with stronger predictability during high volatility, high volume, recessions, and important news days. The reported predictive \(R^2\) is only about 1.6%, so this supports intraday follow-through as a conditional confirmation—not every opening-range break in every stock ([Journal of Financial Economics](https://www.sciencedirect.com/science/article/pii/S0304405X18301351)).

Heston, Korajczyk, and Sadka document persistent, recurring cross-sectional patterns at the same half-hour of the day, while returns at much shorter lags can reverse because of liquidity and bid-ask effects ([Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2010.01573.x), [author manuscript](https://www.bauer.uh.edu/departments/finance/documents/Heston_Korajczyk_Sadka_paper_UH.pdf)). Later futures evidence also finds a last-half-hour continuation pattern followed by reversal over subsequent days, consistent with hedging demand rather than a universal trend law ([Journal of Financial Economics](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21001598)).

Opening-range-breakout research on long futures samples also reports that results differ materially across volatility states. Because that evidence concerns crude oil and S&P 500 futures rather than individual equities, it is best treated as a regime hypothesis to test, not direct stock-level proof ([Umeå University research record](https://swopec.hhs.se/umnees/abs/umnees0861.htm), [paper](https://umu.diva-portal.org/smash/get/diva2%3A732318/FULLTEXT02.pdf)).

### Practical breakout attributes

Use bar lengths appropriate to liquidity—such as 1, 5, or 15 minutes—and require several categories to agree:

- **Boundary identity:** pre-market, opening-range, prior-day, or rolling high; store the level and the timestamp at which it became fixed.
- **Break distance:** close minus boundary in basis points, ATR units, and spread units.
- **Acceptance:** consecutive closes above the boundary, time spent above it, and retest outcome.
- **Residual follow-through:** return after the break after subtracting market and sector returns.
- **Participation:** relative volume versus the same time-of-day baseline, turnover, and—if a reliable feed exists—signed order imbalance.
- **Execution quality:** spread, depth, expected market impact, halts, and stale-quote filters.
- **Catalyst state:** timestamped earnings or material news; the signal clock begins when the information was actually tradable.

A research-ready composite is:

\[
S_{break}=0.30z(breakDistance)+0.25z(acceptance)+0.20z(relVolume)
+0.15z(residualFollowThrough)+0.10z(orderImbalance)
\]

Declare a *candidate breakout* on the first eligible close above the boundary. Upgrade it to *confirmed* only when acceptance and tradability gates pass. The weights and confirmation rules are proposed test specifications, not published universal formulas.

### What can fool it

- The bid-ask spread creates apparent reversals or continuation in last-trade data.
- The opening and closing auctions have different volume and information regimes from midday.
- A gap that opens above resistance but immediately falls back inside the old range is a failed gap-break, not confirmation.
- A statistically predictable last half-hour may be too small to monetize after spread and impact.
- Opening-range breakout is popular with traders, but its individual-stock peer-reviewed evidence is much thinner than the evidence for medium-term return continuation.

## Horizon 2 — swing breakouts (days to weeks)

This is the natural horizon for a stock to leave a multi-week base, clear a prior swing high, and demonstrate whether the market accepts the new price range.

### Highest-value attributes

1. **An ex-ante range boundary.** A close above the prior 20- or 55-day high is objective and falsifiable. Brock, Lakonishok, and LeBaron found information in moving-average and trading-range rules on the DJIA from 1897–1986, but the result is historical and vulnerable to rule selection and trading-cost assumptions ([Journal of Finance](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x)). Later reviews note that other work did not find consistent excess returns after costs, making independent replication essential ([European Financial Management](https://onlinelibrary.wiley.com/doi/10.1111/eufm.12389)).
2. **Acceptance, not merely penetration.** Measure closing distance above the old high, consecutive closes, retests, and maximum adverse excursion. The breakout is invalidated when price closes back inside the old range under the predeclared rule.
3. **Market- and industry-relative strength.** Measure 5-, 20-, and 60-session residual returns and percentile ranks. Moskowitz and Grinblatt show that industry momentum explains an important part of individual-stock continuation ([Journal of Finance](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00146), [paper](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/09/DoIndustriesExplainMomentum.pdf)).
4. **Return-path continuity.** Da, Gurun, and Warachka show that, for the same cumulative return, many small advances predicted stronger continuation than a few discrete jumps—the “frog in the pan” result ([Review of Financial Studies paper](https://academicweb.nd.edu/~zda/Frog.pdf), [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2370931)).
5. **Catalyst plus follow-through.** An earnings surprise that pushes price out of a base supplies an economic reason for the boundary change. Post-earnings-announcement drift was documented over roughly the next 60 trading days ([Bernard and Thomas](https://www.jstor.org/stable/2491062)). But later work shows concentration in less-liquid stocks and estimates that costs can consume 70–100% of paper profits ([Columbia Business School](https://business.columbia.edu/faculty/research/liquidity-and-post-earnings-announcement-drift)).
6. **Volume in context.** Lee and Swaminathan show that turnover helps identify the lifecycle of return continuation: high-volume winners may reverse sooner, so a volume surge confirms attention, not unconditional breakout success ([Journal of Finance paper](https://www.lsvasset.com/pdf/research-papers/Price-Momentum-Trad-Vol-2000.pdf)).

### Proposed swing-breakout rule for research

Flag a daily breakout candidate when all mandatory conditions hold:

- price closes above the **previous** 20-day high, excluding the current bar from the high calculation;
- the break exceeds a predeclared ATR/spread buffer;
- 20-day median dollar volume and spread pass tradability limits;
- the setup was not already triggered within a cooldown window.

Classify the first close as `CANDIDATE`. Require two closes above the boundary or a successful retest to reach `CONFIRMED`. Rank candidates using break distance, 20-/60-day residual rank, volume surprise, earnings surprise, industry strength, proximity to the 52-week high, and return continuity. This “detect, confirm, then rank” design keeps the breakout definition independent of the variables used to forecast its success.

## Horizon 3 — structural breakouts (months to one year)

### Core measurements

A structural breakout is a close above a 52-week high, a multi-month base high, or another long boundary defined mechanically before the event. Of these, the 52-week high has the strongest direct stock-level academic foundation: George and Hwang find that nearness to the 52-week high explains a large portion of momentum profits and improves on raw past return in their original tests ([Journal of Finance](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1540-6261.2004.00695.x)). The evidence concerns proximity/ranking and subsequent returns, not a guarantee that buying the exact first crossing is optimal.

Return-continuation research supplies the follow-through rationale. The classic cross-sectional result buys stocks with high past 3–12 month returns and holds them for 3–12 months ([Jegadeesh and Titman, 1993](https://www.jstor.org/stable/2328882)). Across liquid futures, time-series momentum shows return persistence over approximately 1–12 months and partial reversal at longer horizons ([Moskowitz, Ooi, and Pedersen](https://fairmodel.econ.yale.edu/ec439/mosk.pdf)). Momentum also appears across markets and asset classes ([Asness, Moskowitz, and Pedersen](https://onlinelibrary.wiley.com/doi/pdf/10.1111/jofi.12021)). These results make past strength a useful confirmation layer after a structural break, rather than defining the breakout itself.

However, Novy-Marx finds that the return from 12 to 7 months before portfolio formation carries much of the conventional stock-momentum effect; the most recent performance was less profitable, especially among large liquid stocks ([Journal of Financial Economics](https://www.sciencedirect.com/science/article/pii/S0304405X11001152)). The Kenneth French Data Library’s standard momentum factor therefore uses prior 2–12 month returns, effectively skipping the latest month ([official methodology and daily data](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor_daily.html)).

Use these attributes to estimate structural-breakout quality:

- **Boundary type and age:** 52-week high, 6-month base, or multi-year/all-time high; record how long resistance existed.
- **Break and acceptance:** distance beyond resistance in ATR units, closes above it, and retest behavior.
- **12–1 and 6–1 total return**, preferably adjusted for volatility, as follow-through context.
- **Cross-sectional percentile** within a liquidity-qualified universe and within industry.
- **Time-series sign:** whether the security’s own risk-adjusted return is positive.
- **52-week-high proximity:** \(close/high_{252}\), retained continuously before and after the crossing.
- **Residual momentum:** rank the component left after common factor exposures, reducing unintended market/size/value loadings ([Blitz, Huij, and Martens](https://pure.eur.nl/en/publications/residual-momentum/)).
- **Industry momentum** and **return continuity**.
- **Volatility and drawdown state** for sizing and crash control.

Do not assume that an older or more extended breakout is safer. De Bondt and Thaler find reversal among extreme multi-year winners and losers over subsequent years; their one-year formation case did not show the same reversal. A fresh boundary crossing and an extended multi-year winner are different states ([Journal of Finance](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1985.tb05004.x)).

## What established quants and breakout-oriented managers actually use

Pure single-stock breakout methodologies are less standardized in institutional index products than momentum methodologies. The closest systematic relatives are channel breakout, trend following, and relative-strength selection. Institutional implementations are generally simpler than indicator dashboards:

- **Channel/trend followers:** define a rolling high and enter when price crosses it, then use a shorter opposite channel or volatility-based stop for exit. The attraction is auditability, but it naturally produces many small failed breaks and relies on a smaller number of extended trends.
- **Managed-futures funds:** diversify breakout/trend rules across instruments and volatility-target positions rather than betting that every crossing will work. Trend-following evidence remains positive over a reconstructed history beginning in 1880, across decades and macro regimes ([Hurst, Ooi, and Pedersen](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)). CTA returns are materially explained by time-series momentum benchmarks ([Baltas and Kosowski](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1968996)).
- **William O’Neil/CAN SLIM:** looks for price and volume breaking from a base, combined with earnings growth, leadership, new highs, and market confirmation. This is a practitioner system, not a single peer-reviewed rule ([McGraw Hill](https://www.mheducation.com/highered/mhp/product/how-make-money-stocks-winning-system-good-times-or-bad.html)).
- **Richard Driehaus:** emphasizes stocks and groups exhibiting positive relative strength, supported by earnings growth and positive surprises ([Driehaus speech](https://www.driehaus.com/system/uploads/fae/file/asset/420/RHD_Speech_2014.pdf), [AAII description](https://www.aaii.com/journal/article/momentum-investing-the-richard-driehaus-way)).
- **Institutional momentum indexes:** MSCI combines volatility-adjusted 6- and 12-month performance, excluding the latest month ([MSCI methodology](https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20231120.pdf)); S&P ranks risk-adjusted price performance ([S&P methodology](https://www.spglobal.com/spdji/tc/documents/methodologies/methodology-sp-momentum-indices.pdf)). These are useful confirmation and portfolio-construction references, but they do not identify the first breakout bar.

The common pattern is clear: **an objective price boundary, relative strength, volatility normalization, liquidity, diversification, and predetermined failure rules** dominate. Professional breakout systems accept a low hit rate if successful trades are sufficiently larger than failed ones; therefore precision alone is the wrong evaluation metric.

## Theory: why a breakout might hold or fail

The main theories make different but testable predictions:

- **Gradual information diffusion:** a boundary may break when information is only partly incorporated. Hong and Stein’s “newswatchers” do not observe all information immediately; subsequent diffusion can generate follow-through, while trend chasing can later cause overreaction ([Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00184)). Expected signature: a catalyst, progressive participation, industry transmission, and acceptance above resistance.
- **Anchoring at prior highs:** investors may use a salient high as a reference point and underreact as price approaches it. The 52-week-high evidence is directly relevant to long-boundary breaks ([George and Hwang](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1540-6261.2004.00695.x)).
- **Conservatism and representativeness:** Barberis, Shleifer, and Vishny model initial underreaction followed by overreaction as investors extrapolate too far ([Harvard author page](https://shleifer.scholars.harvard.edu/publications/model-investor-sentiment), [paper](https://scholar.harvard.edu/files/shleifer/files/model_invest_sent.pdf)). A breakout can therefore be early information discovery or late extrapolation.
- **Overconfidence and self-attribution:** investors overweight private signals and become more confident when public outcomes validate them; continuation ultimately reverses ([Daniel, Hirshleifer, and Subrahmanyam](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00077)).
- **Liquidity and stop clustering:** crossing an obvious high can trigger stop orders and urgent demand, producing short-lived pressure rather than durable repricing. This is why acceptance and post-break residual return must be measured separately from the crossing.

These theories support measuring the **boundary, crossing, acceptance, and context**, not merely observing that price printed a new high.

## Technical indicators: proper interpretation

| Indicator | What it actually measures | Suitable role | Main mistake |
|---|---|---|---|
| Rate of change / past return | Price change over a chosen lookback | Primary feature | Using one lookback for every horizon. |
| Moving average / crossover | Smoothed price level and lagged state transition | Regime gate or exit | Calling it an early signal; the price moved first. |
| MACD | Difference between two exponential averages, plus another smoothing | Compact trend/acceleration feature | Treating correlated MACD, MA, and ROC values as independent evidence. |
| RSI | Ratio of smoothed positive to negative changes | Path-balance or exhaustion feature | Assuming “overbought” means a strong trend must reverse. |
| ADX | Magnitude of directional movement, without bullish/bearish direction | Trend-strength filter | Using it without a separate direction feature. |
| Breakout / new high | Price crossing an ex-ante prior range | Primary event definition | Including the current bar in the boundary, or ignoring false breaks, gaps, spreads, and regime. |
| Volume / OBV | Participation or signed-volume proxy | Confirmation and liquidity filter | Assuming all high-volume moves have longer continuation. |

Lo, Mamaysky, and Wang show that several algorithmically defined chart patterns contained incremental information in US stocks from 1962–1996, but their result is not a blanket validation of visual charting ([Journal of Finance paper](https://www.mit.edu/~wangj/pap/LoMamayskyWang00.pdf)). Technical rules should therefore enter Dragonfly as precisely defined, testable variables—not subjective labels such as “nice base” or “strong breakout.”

## Books and market history

- **Edwin Lefèvre, _Reminiscences of a Stock Operator_ (1923):** historically important accounts of following the tape, adding to winners, and cutting losses. It is fictionalized biography and anecdote, not statistical proof ([Wiley edition](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/reminiscences-of-a-stock-operator-978-0-471-67876-2)).
- **William O’Neil, _How to Make Money in Stocks_:** CAN SLIM combines price/volume breakout, earnings, leadership, new highs, and market confirmation. It is a coherent practitioner hypothesis whose individual components should be tested independently ([McGraw Hill](https://www.mheducation.com/highered/mhp/product/how-make-money-stocks-winning-system-good-times-or-bad.html)).
- **Stan Weinstein, _Secrets for Profiting in Bull and Bear Markets_ (1988):** popularized the Stage 1 base to Stage 2 advance using a rising 30-week average, relative strength, volume, and group/market confirmation. Useful as a state-machine design; not itself peer-reviewed proof.
- **Jack Schwager, _Market Wizards_:** interviews show diverse entry methods but repeated emphasis on sizing, loss control, and matching the method to the trader. The sample has survivorship and narrative bias ([Wiley](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/market-wizards-978-1-118-27305-0)).

Long-history research is more persuasive than trading lore. Trend following is documented across asset classes back to 1880 in one reconstruction, while another study reports cross-sectional momentum across 215 years of multi-asset history ([Hurst, Ooi, and Pedersen](https://fairmodel.econ.yale.edu/ec439/hurst.pdf), [Geczy and Samonov](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2607730)). AQR’s practitioner review summarizes momentum evidence in US equities, Victorian-era UK data, dozens of countries, and multiple asset classes ([Fact, Fiction and Momentum Investing](https://www.aqr.com/Insights/Research/Journal-Article/Fact-Fiction-and-Momentum-Investing)). History supports persistence as a broad phenomenon, but not a fixed threshold that works unchanged in every market.

## Failure modes and controls

1. **False breakouts and whipsaws:** price crosses resistance, attracts orders, then closes back inside the old range. Measure failure at the same horizon as entry and predeclare the exit; repeated crossings in a flat range are not separate independent opportunities.
2. **Gap exhaustion:** a catalyst can move price so far beyond the boundary that the favorable information is already incorporated. Treat gap size and post-open acceptance as separate features.
3. **Momentum crashes and regime reversal:** because successful breakout portfolios often become momentum portfolios, they inherit crash exposure. Crashes cluster after market declines, during high volatility, when rebounds punish crowded short-loser positions ([Daniel and Moskowitz](https://kentdaniel.net/papers/published/jfe_16.pdf)). Volatility scaling materially improved historical risk-adjusted results in Barroso and Santa-Clara’s tests ([paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2041429)).
4. **Costs and capacity:** breakout orders compete for liquidity at conspicuous levels. Market impact increases with strategy size; liquidity-weighted construction can increase capacity ([Korajczyk and Sadka](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2004.00656.x)). Live institutional trade data confirm that cost-aware construction matters ([Frazzini, Israel, and Moskowitz](https://pages.stern.nyu.edu/~afrazzin/pdf/Trading%20Cost%20of%20Asset%20Pricing%20Anomalies%20-%20Frazzini%2C%20Israel%20and%20Moskowitz.pdf)).
5. **Publication decay and parameter mining:** trying dozens of lookbacks, buffers, volume multipliers, and base shapes can manufacture a winner. Across 97 published predictors, returns were lower out of sample and lower again after publication ([McLean and Pontiff](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365)).
6. **Horizon mismatch:** a one-minute false break can coexist with a valid monthly breakout. Never use a long-horizon boundary to justify an intraday fill without a separate execution rule.
7. **Universe and look-ahead bias:** delistings, microcaps, splits, dividends, current index membership, final daily volume, same-close fills, and including the signal bar in the trailing high can manufacture results.

## Recommended Dragonfly feature specification

Store the exact boundary and event lifecycle, then compute a separate breakout-success probability for each horizon. Do not combine them into one universal score.

For a practical mapping of this research to the Finviz filter grid, see [Finviz Filters for Stocks Approaching a Breakout](./finviz_pre_breakout_filters.md).

### Intraday fields

- `ret_1m`, `ret_5m`, `ret_15m`, `ret_from_open`
- `boundary_type`, `boundary_price`, `boundary_fixed_at`
- `break_distance_bps`, `break_distance_atr`, `break_distance_spreads`
- `bars_above_boundary`, `time_above_boundary`, `retest_result`
- `resid_ret_5m`, `resid_ret_30m`, `sector_relative_30m`
- `opening_range_break_z`, `distance_from_vwap_atr`
- `relative_volume_same_time_20d`, `dollar_volume`, `quoted_spread_bps`
- `order_imbalance` when quote/trade classification is reliable
- `news_event_age_minutes`, `halt_flag`
- `intraday_breakout_probability`, `intraday_breakout_state`

### Daily-to-weekly fields

- `ret_5d`, `ret_20d`, `ret_60d` and market/sector residual forms
- cross-sectional and within-industry percentile ranks
- `prior_high_20d`, `prior_high_55d`, `breakout_20d`, `breakout_55d`
- `break_distance_atr`, `closes_above_boundary`, `retest_depth_atr`
- `base_length_days`, `base_depth_atr`, `failed_break_count`
- `volume_z_20d`, `dollar_volume_20d`, spread proxy
- `return_continuity_20d` (positive-day share and information-discreteness measure)
- earnings surprise and point-in-time event timestamp where licensed
- `swing_breakout_probability`, `swing_breakout_state`

### Monthly-to-annual fields

- `prior_high_126d`, `prior_high_252d`, `breakout_52w`, `boundary_age_days`
- `break_distance_atr`, `weeks_above_boundary`, `structural_retest_result`
- `ret_6_1`, `ret_12_1`, volatility-adjusted equivalents as confirmation
- `residual_momentum_12_1`, `industry_momentum_12_1`
- `distance_52w_high`, `trend_200d`, `volatility_63d`, `drawdown_252d`
- `structural_breakout_probability`, `structural_breakout_state`

### Suggested state machine

`IN_RANGE → TESTING → BROKEN → CONFIRMED → EXTENDED`  
`                         ↘ FAILED`

- **In range:** price remains below the stored boundary.
- **Testing:** price is within a volatility-scaled distance of the boundary.
- **Broken:** the first eligible completed-bar close clears the boundary and buffer.
- **Confirmed:** price is accepted above the level under the chosen close/retest rule.
- **Extended:** the break has traveled far enough that reward-to-failure-level is materially worse.
- **Failed:** price returns inside the old range under the predeclared invalidation rule.

Train or calibrate each transition separately. “Approaching resistance,” “first break,” “confirmed break,” and “extended trend” are different prediction problems.

## Validation protocol

1. Freeze an investable, point-in-time universe with delistings included.
2. Adjust historical prices consistently for splits and dividends; preserve unadjusted prices for execution simulation.
3. Define boundary construction, breakout buffer, confirmation, failure, and cooldown rules before looking at forward returns.
4. Use walk-forward tests with purging/embargo around overlapping labels.
5. Report gross and net outcomes with spread, fees, slippage, impact, and borrow costs.
6. Segment results by capitalization, liquidity, market regime, industry, event/non-event, and time of day.
7. Compare every complex model with simple baselines: unbuffered 20-day breakout, buffered 55-day breakout, and 52-week-high crossing.
8. Measure probability calibration, breakout follow-through, false-break rate, expected forward residual return, maximum favorable/adverse excursion, payoff ratio, turnover, drawdown, and capacity—not just win rate.
9. Correct for multiple testing and reserve a final untouched period.
10. Paper trade with live timestamps before considering production use.

## Proof of work

### Research method

- Searched foundational and later work in the *Journal of Finance*, *Journal of Financial Economics*, *Review of Financial Studies*, *Journal of Empirical Finance*, and institutional research repositories.
- Prioritized journal pages, author manuscripts, university repositories, official factor libraries, and official index methodologies over blogs or summaries.
- Examined evidence for trading-range breaks, 52-week highs, intraday opening ranges, price continuation, industry effects, volume, earnings drift, return-path continuity, residual momentum, false-break risk, costs, capacity, and publication decay.
- Compared academic results with published MSCI and S&P methodologies, managed-futures research, and named practitioner frameworks.
- Used books for historical/practitioner context only, not as causal proof.
- Kept contradictory or limiting evidence: after-cost failures of some technical rules, false breaks, very-short-horizon reversal, long-horizon reversal, momentum crashes, liquidity costs, and post-publication decay.

### Search trail

Representative query families used:

- `stock momentum 3 to 12 months Jegadeesh Titman Journal of Finance`
- `trading range break rule Brock Lakonishok LeBaron Journal of Finance`
- `opening range breakout returns volatility states academic`
- `52-week high breakout George Hwang Journal of Finance`
- `Donchian channel breakout trend following academic evidence`
- `technical trading rules after transaction costs Allen Karjalainen`
- `time series momentum 1 to 12 months Moskowitz Ooi Pedersen`
- `intraday momentum first half hour last half hour JFE`
- `intraday cross section half hour return continuation bid ask reversal`
- `industry momentum Moskowitz Grinblatt`
- `52-week high momentum George Hwang`
- `price momentum trading volume Lee Swaminathan`
- `Frog in the Pan continuous information momentum`
- `post earnings announcement drift transaction costs liquidity`
- `residual momentum Journal of Empirical Finance`
- `moving average trading range break rules Brock Lakonishok LeBaron`
- `momentum crashes volatility managed momentum`
- `momentum transaction costs capacity institutional trades`
- `MSCI Momentum Index methodology 6 month 12 month volatility`
- `S&P Momentum Index methodology risk adjusted momentum score`
- `century evidence trend following 1880`
- `long-term reversal De Bondt Thaler`

### Evidence ledger

| Research question | Main evidence inspected | Conclusion retained |
|---|---|---|
| Can a breakout be defined objectively? | Trading-range rules; 52-week-high literature | Yes: use an ex-ante rolling high and completed-bar crossing; prediction is a separate question. |
| Is a breakout enough by itself? | Brock et al.; Lo et al.; later technical-rule review | No. It can be informative but is vulnerable to costs, whipsaw, and specification search. |
| Do intraday breakouts follow through? | Gao et al.; Heston et al.; opening-range volatility-state study | Conditionally, with time-of-day, regime, and microstructure effects; weak generalization to single stocks. |
| Does medium-term momentum support breakout follow-through? | Jegadeesh–Titman; French factor library; Asness et al. | Yes historically, especially in relative ranks, but it confirms rather than defines a breakout. |
| Does volume confirm onset? | Lee–Swaminathan; liquidity/cost papers | It adds state and tradability information, but high turnover can also signal maturity. |
| Do news and earnings matter? | Bernard–Thomas; PEAD liquidity research; intraday announcement research | Catalysts help identify information diffusion, but fast response and costs reduce realizable alpha. |
| Should market/industry be removed? | Moskowitz–Grinblatt; residual momentum | Retain both raw leadership and residual strength so beta-driven breaks can be distinguished. |
| Can one use RSI/MACD as proof? | Technical-rule and pattern literature; indicator definitions | No. Use as secondary encodings and validate exact settings. |
| What do institutional rules use? | MSCI; S&P; CTA studies | Multi-horizon returns, volatility scaling, ranking, diversification, and scheduled controls. |
| What invalidates or exhausts a breakout? | False-break logic; Novy-Marx; De Bondt–Thaler; crash studies | Return inside the range invalidates it; extension, multi-year overreaction, and regime reversal raise exhaustion risk. |
| Is backtested alpha deployable? | Korajczyk–Sadka; Frazzini et al.; McLean–Pontiff | Only after realistic costs, capacity, and genuine out-of-sample tests. |

### Important limitations of this review

- It is a structured literature review, not a formal meta-analysis.
- Reported historical relations are averages and may change after publication.
- Results from indexes, futures, or portfolios do not automatically transfer to an individual stock.
- Some seminal sources are older and use markets with different spreads, tick sizes, and dissemination speeds.
- Data/vendor feasibility—especially historical news, quotes, and order flow—must be assessed separately.

## Bottom line

For Dragonfly, the most defensible definition is: **a breakout stock closes beyond an objectively defined prior price boundary using only point-in-time data, clears a volatility/spread-aware buffer, demonstrates acceptance above that level, and remains tradable after market context and execution costs.**

Build the first model around boundary type, break distance, acceptance/retest, relative and residual strength, 52-week-high proximity, industry strength, return continuity, volume/liquidity, and volatility. Use momentum, RSI, MACD, and moving averages as confirmation or context—not as the breakout definition. Keep intraday, swing, and structural-breakout models separate and require each to earn its place in point-in-time, net-of-cost validation.
