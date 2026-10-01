# Patterns That Suggest an Upside Breakout Is Approaching

**Research date:** 15 September 2026  
**Scope:** Liquid US common stocks; daily swing horizon, with notes for intraday and structural breakouts  
**Purpose:** Define testable pre-breakout features for Dragonfly, supported by academic, practitioner, historical, and internal evidence.

> This is research and system-design material, not investment advice. No chart pattern proves that a breakout will occur. The correct output is a ranked watchlist with an estimated probability, followed by a separate confirmation rule.

## Executive finding

The most defensible pre-breakout state is:

1. The stock is already in a positive medium- and long-term trend.
2. Price is within roughly one ATR, or about 0-3%, of a resistance level defined before the current bar.
3. The range and true range have contracted without a material loss of relative strength.
4. Pullbacks are becoming shallower and down-volume is drying up.
5. The stock and its industry are outperforming the market.
6. A fundamental information event or improving estimates provides a possible reason for repricing.
7. The actual entry waits for a close through resistance with abnormal volume and acceptance above the old boundary.

Only items 1-5 belong to the **pre-breakout forecast**. Item 7 is a **breakout confirmation**, not advance prediction.

The strongest direct academic evidence supports objective range highs, 52-week-high proximity, medium-term relative strength, industry strength, and information underreaction. Volatility contraction, volume dry-up, repeated resistance tests, and higher lows are widely used by successful breakout practitioners, but the exact definitions and thresholds have much weaker independent evidence. They should enter Dragonfly as testable features, not mandatory truths.

## Recommended pattern: the Trend-Compression-Pivot sequence

### 1. Prior trend - mandatory

The stock should be above its 20-, 50-, and 200-day moving averages, with the 50-day average above the 200-day average and the 200-day average rising. Its 63- and 126-session return should rank well against the investable universe and its industry.

Why it matters: an upside break from a weak long-term trend is often only a countertrend rally. Jegadeesh and Titman documented continuation in stocks with strong prior 3-12 month performance. George and Hwang found that nearness to the 52-week high contains more forecasting information than raw past return in their tests. Industry momentum also explains a substantial part of individual-stock momentum.

Sources: [Jegadeesh and Titman (1993)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1993.tb04702.x), [George and Hwang (2004)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2004.00695.x), [Moskowitz and Grinblatt (1999)](https://www.andreisimonov.com/Microstr_PhD/MSU_09/MoskowitzGrinblatt99.pdf).

### 2. An objective pivot - mandatory

Define resistance without using the current bar:

```text
pivot_20[t] = max(high[t-20 : t-1])
distance_to_pivot_atr = (pivot_20[t] - close[t]) / ATR14[t]
```

The candidate should normally be below the pivot but close enough to reach it without an exceptional move:

```text
0 < distance_to_pivot_atr <= 1.0
```

Also test 55-session and 252-session pivots as separate strategies. Do not require all three simultaneously.

Why it matters: Brock, Lakonishok, and LeBaron found information in trading-range-break rules over the 1897-1986 DJIA sample. Later work shows that performance is not universal and is sensitive to data snooping, market, costs, and period. The boundary is therefore a valid event definition, not proof of alpha.

Sources: [Brock, Lakonishok, and LeBaron (1992)](https://support-and-resistance.technicalanalysis.org.uk/BrockLakonishokLeBaron1992.pdf), [Sullivan, Timmermann, and White (1999)](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00163), [Fan and Wang (2018), conflicting NASDAQ evidence](https://www.sciencedirect.com/org/science/article/abs/pii/S1463577118002196).

### 3. Volatility and range contraction - useful, directionless

Compute both an absolute and a stock-relative measure:

```text
atr_ratio = ATR14 / SMA(ATR14, 50)
bb_width = (upper_BB20 - lower_BB20) / middle_BB20
range_ratio = (highest_high_5 - lowest_low_5) / (highest_high_20 - lowest_low_20)
```

Candidate thresholds to test:

- `atr_ratio <= 0.75`
- `bb_width` in the stock's lowest 20% over the prior 252 sessions
- `range_ratio <= 0.60`
- each of the last two pullbacks is smaller than the previous pullback

Interpretation: compression can precede expansion, but it does not predict whether the expansion will be upward or downward. Direction must come from prior trend, relative strength, and the eventual pivot cross.

The contraction-expansion principle appears in Toby Crabel's *Day Trading with Short Term Price Patterns and Opening Range Breakout*. A peer-reviewed opening-range study found significantly positive results in US crude-oil futures under its specification, but that is not direct evidence for individual US stocks. ARCH/GARCH research supports time-varying and clustered volatility, not the stronger claim that every low-volatility base must expand upward.

Sources: [Opening-range-breakout study](https://www.sciencedirect.com/science/article/pii/S1544612312000438), [Engle's ARCH paper](https://web.pdx.edu/~crkl/ec572/readings/Engle82.pdf).

### 4. Supply contraction and constructive price-volume behavior - supporting feature

Test:

```text
volume_dry_up = median(volume_5) / median(volume_50) <= 0.70
up_down_volume_ratio = sum(volume on up closes, 20d) / sum(volume on down closes, 20d)
```

Prefer quiet pullbacks, smaller volume on down days, and occasional accumulation days. Do not assume that high historical turnover is always bullish. Lee and Swaminathan found that turnover changes the magnitude and persistence of momentum and that high-volume winners can reverse sooner. Volume is therefore contextual.

The strongest breakout-day evidence found in this review comes from O'Neil Global Advisors. Its 1995-2021 US study included about 197,000 daily base breakouts, excluded the least liquid half of stocks, and reported 63-session alpha of 0.67% for breakout volume below +50% versus 2.79% when volume was at least +150% relative to the 50-day average. In that paper, +150% means 2.5 times average volume. The hit rate remained near 57%, so the improvement came from payoff size rather than dramatically higher accuracy. This is firm research based on proprietary pattern recognition, not an independent peer-reviewed replication.

Sources: [Lee and Swaminathan (2000)](https://doi.org/10.1111/0022-1082.00280), [O'Neil Global Advisors - Breakouts: Pump up the Volume](https://www.oneilglobaladvisors.com/documents/FG/oneil/research/617948_OGA_Breakouts-OGA.pdf), [Blume, Easley, and O'Hara (1994)](https://volume.technicalanalysis.org.uk/BlEO94.pdf).

### 5. Relative and industry strength - mandatory ranking features

Measure the stock against SPY and its sector ETF:

```text
residual_20 = stock_return_20 - beta_126 * spy_return_20
residual_63 = stock_return_63 - beta_252 * spy_return_63
industry_relative_63 = industry_return_63 - spy_return_63
```

Prefer top-quintile stock residual strength and a positive or top-tercile industry signal. A relative-strength line reaching a high before the stock price reaches its own pivot is a useful practitioner hypothesis to test.

Sources: [Moskowitz and Grinblatt (1999)](https://www.andreisimonov.com/Microstr_PhD/MSU_09/MoskowitzGrinblatt99.pdf), [AQR - A Century of Evidence on Trend Following](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/AQR-JPM-Fall-2017.pdf).

### 6. Information catalyst - optional but economically meaningful

Rank higher when, during the previous 20 sessions:

- reported EPS beat consensus;
- revenue also beat consensus;
- forward EPS estimates were revised upward;
- the earnings gap held rather than immediately filling.

Post-earnings-announcement drift is one of the better-documented forms of delayed price adjustment. Jegadeesh and Livnat found the drift was stronger when revenue and earnings surprises had the same sign. Later research shows that liquidity and costs can consume much of the paper return, so this is a ranking input rather than a guaranteed trade.

Sources: [Jegadeesh and Livnat (2006)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=903767), [review of PEAD research](https://doi.org/10.1016/j.jbef.2020.100446), [liquidity and PEAD](https://business.columbia.edu/faculty/research/liquidity-and-post-earnings-announcement-drift).

### 7. Trigger and acceptance - confirmation, not forecast

The watchlist becomes an actionable breakout only after a completed close clears the stored pivot:

```text
breakout = close[t] > pivot[t] + max(0.10 * ATR14[t], 2 * spread[t])
volume_confirmation = volume[t] / average_volume_50[t] >= 1.5
close_quality = (close[t] - low[t]) / (high[t] - low[t]) >= 0.75
```

Test a strict volume variant at `2.5x`, based on the strongest O'Neil study bucket. Confirm acceptance using either a second close above the original pivot or a retest that closes back above it. The pivot must remain the original pre-event value; do not move it upward after the signal.

## Evidence-ranked feature list

| Feature | Role | Evidence grade | Keep in first model? |
|---|---|---|---|
| Positive 3-12 month relative strength | Precondition/rank | Strong academic | Yes |
| Strong industry/sector | Rank | Strong academic | Yes |
| Distance to prior 20/55/252-day high | Event proximity | Moderate-to-strong, horizon dependent | Yes, as separate features |
| Price above rising 50/200-day averages | Regime | Moderate/mixed | Yes |
| ATR and range contraction | Movement readiness | Plausible; limited directional evidence | Yes, continuous feature |
| Shrinking pullbacks/higher lows | Supply-pressure proxy | Practitioner | Yes, experimental |
| Five-day volume dry-up | Supply proxy | Practitioner/mixed academic | Yes, experimental |
| Positive earnings and revenue surprise | Catalyst/rank | Strong academic for drift | Yes when point-in-time data exist |
| Breakout-day relative volume | Confirmation | Strong firm study; moderate independent theory | Yes |
| Close near top of breakout bar | Confirmation | Practitioner | Yes, experimental |
| RSI/MACD/stochastic | Redundant transforms | Weak standalone | No mandatory gate |
| Low float/high short interest | Move amplifier and risk | Not breakout-direction evidence | No mandatory gate |
| Institutional ownership change | Slow, delayed data | Weak for timing | No trigger use |

## What books and experienced managers contribute

These sources are valuable for hypotheses and risk rules, not independent statistical proof:

- William O'Neil, *How to Make Money in Stocks*: cup-with-handle, flat base, pivot, earnings growth, leadership, and breakout volume. Fidelity's technical guide summarizes the cup-with-handle as a prior advance, rounded base, short handle, and increased volume on the breakout ([Fidelity](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cup-with-handle)).
- Mark Minervini, *Trade Like a Stock Market Wizard*: volatility-contraction pattern, progressively smaller pullbacks, volume contraction, and a tight pivot. This is the clearest practitioner version of the pre-breakout setup.
- Stan Weinstein, *Secrets for Profiting in Bull and Bear Markets*: Stage 1 base transitioning into Stage 2, rising long-term trend, relative strength, and volume on the break.
- Nicolas Darvas, *How I Made $2,000,000 in the Stock Market*: price boxes, entry only after the upper boundary breaks, and a simultaneous stop. The performance claim is autobiographical and historically disputed, so the durable contribution is the explicit boundary and risk rule rather than the headline return.
- Jesse Livermore as presented in Edwin Lefevre's *Reminiscences of a Stock Operator*: trade at pivotal points, add only when price confirms, and cut failed trades. It is market history and narrative evidence, not a controlled study.
- Richard Donchian and later managed-futures/CTA practice: channel breakouts, volatility scaling, diversification, and accepting many small false breaks in exchange for a few large trends. Long-history trend evidence supports the portfolio logic across asset classes, not the prediction that any individual stock will break out.

## Theories that explain the pattern

1. **Gradual information diffusion:** news reaches investors at different times, causing underreaction and later continuation. Hong and Stein formalize this mechanism ([Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00184)).
2. **Anchoring at prior highs:** investors treat a visible high as a reference point, delaying adjustment as price approaches it. This is consistent with the 52-week-high effect.
3. **Disposition effect and supply:** holders sell winners near remembered purchase prices or highs; repeated absorption can reduce available supply. Grinblatt and Han link unrealized gains, the disposition effect, and momentum ([Journal of Financial Economics](https://www.sciencedirect.com/science/article/pii/S0304405X05000747)).
4. **Attention and order clustering:** obvious highs attract attention, stop orders, and breakout orders. Barber and Odean show retail investors disproportionately buy attention-grabbing stocks such as those with abnormal volume or extreme returns ([Review of Financial Studies](https://academic.oup.com/rfs/article-abstract/21/2/785/1585282)). This can create a burst but also a reversal after temporary pressure.
5. **Trend-following feedback:** confirmation attracts systematic and discretionary trend followers. This can extend a genuine repricing but also produce overshoot.

## What Dragonfly's own backtest proves

The existing point-in-time test used 108 stocks, 181,659 daily bars from 2 January 2020 through 14 September 2026, SPY as benchmark, and 20 basis points of round-trip cost.

- Liquid stocks alone crossed a prior 20-day high within five sessions on 24.64% of stock-days.
- Adding positive trend and SMA20/50/200 qualification raised this to 41.75%: a 17.11 percentage-point lift.
- Adding proximity within 3% of the prior 20-day high raised it to 43.35%: a further 1.60 points.
- Adding 50-day and 52-week proximity reduced the five-day rate slightly.
- Among 2,762 unique setup events, 46.20% crossed within five sessions and 70.49% within 20 sessions.
- The strict breakout trigger produced 0.19% mean excess return over SPY at 20 sessions and 0.22% at 60 sessions, but median excess return and excess win rate were negative.
- Combining every setup gate with the trigger made results worse.

Conclusion from the internal evidence: trend plus closeness to the 20-day pivot is useful for **alert prioritization**, but the original full filter stack is not a validated alpha strategy. The next experiment should test compression, relative strength, industry strength, return continuity, catalyst, and acceptance as continuous features with ablation—not add them all as hard gates.

Internal source: [Dragonfly breakout backtest](./finviz_breakout_backtest_results.md).

## Research specification for the next backtest

### Label

At the close of day `t`, use only data available then. Define:

```text
positive_event_5d = any(close[t+1:t+5] > pivot_20[t] + 0.10*ATR14[t])
successful_breakout = positive_event_5d
                      and max_excess_return_20d >= 3%
                      and max_adverse_excursion_before_success > -2*ATR14[t]
```

Report the crossing label separately from the profitable-follow-through label.

### Candidate features

Use continuous values rather than prematurely optimized yes/no cutoffs:

- distances to 20-, 55-, and 252-day highs in ATR units;
- SMA structure and slopes;
- 20-, 63-, and 126-day market- and industry-relative returns;
- ATR ratio, Bollinger width percentile, and 5/20-day range ratio;
- pullback-depth sequence and higher-low slope;
- 5/50-day volume ratio and up/down-volume ratio;
- return-path continuity;
- point-in-time earnings surprise, revenue surprise, and estimate revisions;
- market breadth, SPY trend, and sector trend;
- spread, dollar volume, and gap risk.

### Validation

- Use expanding or walk-forward time splits.
- Purge overlapping label windows and embargo adjacent observations.
- Include delisted securities and point-in-time index membership where possible.
- Optimize on training data only; freeze thresholds before the test period.
- Report precision, recall, calibration, Brier score, forward excess-return distribution, drawdown, turnover, and net returns.
- Cluster or bootstrap by date and symbol; stock-day rows are not independent.
- Include commissions, spread, slippage, gap-through-stop losses, and capacity.
- Compare every complex model with three baselines: liquid-only, trend-only, and trend-plus-20-day-pivot-proximity.

## Proof of work

### Sources examined by category

- Peer-reviewed research on trading-range breaks, technical-pattern recognition, cross-sectional momentum, 52-week highs, industry momentum, volume, earnings drift, volatility, data snooping, and attention.
- Author- or institution-hosted papers from NBER, Columbia, AQR, and university repositories.
- O'Neil Global Advisors' 1995-2021 study of approximately 197,000 breakout events.
- Practitioner frameworks from O'Neil, Minervini, Weinstein, Darvas, Livermore/Lefevre, Donchian, and managed-futures practice.
- Dragonfly's existing 2020-2026 point-in-time breakout backtest and ablation results.

### Representative search trail

```text
trading range breakout technical rule Journal of Finance
52-week high momentum George Hwang
Foundations of Technical Analysis Lo Mamaysky Wang
price momentum trading volume Lee Swaminathan
industry momentum Moskowitz Grinblatt
post earnings announcement drift revenue surprise
volatility contraction opening range breakout study
data snooping technical trading rules Sullivan Timmermann White
O'Neil breakout volume 1995 2021 study
Mark Minervini volatility contraction pattern
Stan Weinstein Stage 2 breakout volume
Nicolas Darvas box theory historical evidence
AQR century evidence trend following 1880
```

### Evidence limits

- Published return-continuation evidence does not prove the exact day of a breakout.
- Compression predicts movement potential more naturally than direction.
- Practitioner success stories suffer survivorship and narrative bias.
- O'Neil's large study evaluates already-triggered breakouts, not advance prediction, and uses proprietary pattern recognition.
- Many technical variables are correlated transformations of the same OHLCV series.
- A result can be statistically significant and still be uneconomic after spread, impact, and taxes.

## Final recommendation

Build Dragonfly's first production watchlist around **trend + 20-day pivot proximity**, because that combination produced the clearest lift in the project's own test. Add compression, relative strength, industry strength, return continuity, and catalyst as separately reported scores. Do not require 50-day and 52-week proximity as hard gates. Keep breakout-day volume and price acceptance in a separate confirmation model.

The system should say **“breakout candidate: estimated probability X%”**, never “a breakout will happen.”
