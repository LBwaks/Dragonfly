# Finviz Candlestick and Chart Patterns for Anticipating Upside Breakouts

**Research date:** 15 September 2026  
**Scope:** Exact pattern families visible in the supplied Finviz Candlestick and Pattern dropdowns  
**Target:** A liquid US stock closing above a pre-existing resistance boundary within the next 1-10 daily sessions, followed by acceptance and positive market-relative return

> Research and product-design material, not investment advice. A pattern can improve a watchlist's base rate without creating a profitable trading strategy after costs.

## Executive decision

For an upside breakout watchlist, place the most weight on **multi-bar chart structure**, not a one-bar candle name.

The best Finviz combinations to test first are:

1. **Triangle Ascending + Spinning Top/Doji or Long Lower Shadow**
2. **Horizontal S/R or Channel + Spinning Top/Doji**
3. **Wedge + Spinning Top/Doji**, but only when the prior trend is upward
4. **Wedge Down + Hammer/Long Lower Shadow**, for a reversal-breakout model separate from continuation breakouts
5. **Head & Shoulders Inverse or Double/Multiple Bottom + Long Lower Shadow/Hammer**, only when price is near the neckline

The most useful one-bar signals are not inherently bullish:

- Doji and spinning tops describe balance/indecision, not direction.
- Hammer, dragonfly doji, and long lower shadow describe rejection of lower prices only when they occur at meaningful support.
- White marubozu is best treated as a breakout **trigger**, not a forecast that a breakout is about to happen.
- Long upper shadow, gravestone doji, and black marubozu should normally reduce an upside-breakout score.

## What Finviz is actually detecting

Finviz defines a candlestick filter as an OHLC formation and a chart pattern as a shape created by price action. Its chart-pattern documentation defines trendlines, wedges, triangles, channels, tops, bottoms, and head-and-shoulders structures. Finviz states that trendline breaks, especially with high volume, may gain momentum, but it does not publish a peer-reviewed validation of its proprietary detection thresholds.

Official sources: [Finviz Screener Help](https://finviz.com/help/screener), [Finviz Charts and Patterns](https://finviz.com/help/technical-analysis/charts-patterns).

This creates three implementation cautions:

1. A Finviz label is a candidate annotation, not a completed trading signal.
2. Finviz does not disclose every tolerance used to decide whether highs are “equal,” lines are parallel, or wicks are “long.”
3. Dragonfly should calculate its own continuous geometry from OHLCV data so the backtest and production screen use identical definitions.

## Overall ranking of the chart-pattern dropdown

| Finviz chart pattern | Conventional role | Upside breakout soon | Use in Dragonfly | Evidence judgment |
|---|---|---:|---|---|
| Triangle Ascending | Bullish continuation | High candidate value | Primary continuation setup | Best menu choice, but still requires close above resistance |
| Horizontal S/R | Neutral range boundary | High near upper boundary | Primary objective base | Strong event definition; direction comes from trend/location |
| Channel | Horizontal continuation/range | High near upper boundary | Primary base variant | Clean, auditable resistance |
| Wedge | Converging up support/down resistance | Moderate-high in prior uptrend | Continuation compression | Direction depends on prior trend and actual break |
| Wedge Down | Falling wedge, reversal | Moderate | Separate reversal-breakout model | Conventional bullish reversal; evidence not universal |
| Head & Shoulders Inverse | Bottom reversal | Moderate near neckline | Separate reversal-breakout model | Only complete above neckline |
| Multiple Bottom | Bottom reversal | Moderate near neckline | Separate reversal-breakout model | More support tests, but must cross resistance |
| Double Bottom | Bottom reversal | Moderate near neckline | Separate reversal-breakout model | Common, definition-sensitive |
| TL Resistance | Sloping resistance | Moderate | Boundary feature | Useful level; more subjective than horizontal resistance |
| Channel Up | Rising parallel trend | Low-moderate | Trend context, not primary | Upper break may be acceleration or exhaustion |
| TL Support | Rising/falling support | Low | Risk/invalidation feature | Does not define an upside resistance break |
| Channel Down | Falling parallel trend | Low before trigger | Reversal model only | Wait for upper-channel break |
| Triangle Descending | Bearish continuation convention | Low | Negative/context feature | Upward failure is possible, not the base case |
| Wedge Up | Rising wedge, reversal convention | Low/negative | Exclude from long continuation screen | Finviz classifies it as reversal |
| Double Top | Top reversal | Negative | Exclude or bearish label | Not bullish until structure is invalidated above highs |
| Multiple Top | Top reversal | Negative | Exclude or bearish label | Repeated rejection, not proof of absorption |
| Head & Shoulders | Top reversal | Negative | Exclude or bearish label | Completion is a downside neckline break |

## Deep review of each chart pattern

### Triangle Ascending - highest-priority Finviz setup

Finviz defines this as rising trendline support under horizontal resistance. The bullish story is that buyers accept progressively higher lows while supply repeatedly appears at the same ceiling.

Required state:

```text
at least 2-3 swing highs within 0.5-1.0 ATR of one another
at least 2 rising swing lows
positive slope of support
near-zero slope of resistance
current close within 1 ATR of resistance
```

Why it is relevant: it contains both an objective pivot and contracting downside excursion. It is still incomplete until price closes above horizontal resistance. A wick above the line is not enough.

Best candle overlay: narrow spinning top, doji with small total range, or long lower shadow after a shallow final pullback. A white marubozu through resistance is the trigger.

Risks: visually chosen pivots, late entries near the apex, and false breaks. Bulkowski's practitioner datasets show that famous patterns can have meaningful failure rates and performance changes across editions and regimes; use his work as a hypothesis catalogue rather than a forecast.

### Horizontal S/R and Channel - highest-priority neutral bases

A horizontal channel is the cleanest test of whether a bounded range is about to resolve. It does not imply direction by itself.

For an upside candidate require:

```text
close in upper 25% of channel
positive 63-day market-relative return
rising or flat 50-day average
no repeated large upper-wick rejection
range/ATR contraction during latest approach
```

Academic relevance: Kavajecz and Odders-White found that technical support and resistance levels coincided with peaks in limit-order-book depth. Osler found that foreign-exchange orders clustered around support/resistance and that stop orders could intensify movement after a level broke. These papers support a liquidity mechanism for levels; the FX result is not direct US-stock proof.

Sources: [Kavajecz and Odders-White, Review of Financial Studies](https://academic.oup.com/rfs/article-abstract/17/4/1043/1570736), [Osler, Federal Reserve Bank of New York](https://www.newyorkfed.org/research/staff_reports/sr125.html).

### Wedge - useful compression, conditional direction

Finviz uses “Wedge” for rising support and falling resistance and classifies it as a continuation pattern. This is close to a symmetrical triangle.

Use only when:

- the trend preceding the wedge is positive;
- price is in the upper half of the wedge;
- relative strength does not break down during consolidation;
- the pattern has not reached the final few percent of its apex;
- the upper boundary is stored before the trigger.

The converging lines indicate reduced range, not guaranteed upside. Run upward and downward outcome labels in the research dataset.

### Wedge Down - reversal-breakout candidate

Finviz defines both boundaries as declining and classifies the formation as a reversal. The bullish hypothesis is seller exhaustion, but a falling price channel can simply keep falling.

Require evidence of transition:

- downside ranges or bodies contract;
- lower lows stop accelerating;
- a long lower shadow or hammer appears at support;
- relative strength improves before price;
- price closes above the upper wedge line.

Before the last condition, label it `REVERSAL_WATCH`, not `BREAKOUT_READY`.

### Wedge Up - unfavorable for an upside screen

Both boundaries rise while converging. Finviz classifies this as reversal. Rising price with narrowing progress can represent weakening demand.

Default action: exclude from the primary long-breakout preset. A close above the upper wedge line can be studied as a rare continuation failure of the conventional pattern, but it should not receive the same prior as an ascending triangle.

### TL Resistance and TL Support

Trendline resistance can be a useful breakout boundary, but small changes in swing-point selection can materially change its slope. Require at least three non-adjacent touches and store the regression/tolerance rules.

Trendline support is not an upside-breakout pattern. Use it to evaluate:

- whether the candidate's rising structure remains intact;
- where a failed-break stop might lie;
- whether a hammer or long lower shadow occurred at meaningful support.

### Channel Up

An upward channel indicates an existing trend. Buying an upper-channel penetration may capture acceleration, but it can also buy temporary overextension. For “about to break out,” a rising channel is weaker than a flat ceiling with rising lows.

Use channel slope, distance to upper line, and relative strength as continuous features. Do not give the label a high score by itself.

### Channel Down

This is a downtrend until proven otherwise. A lower-support bounce or bullish candle inside the channel is not a breakout. Upgrade only after a close above the pre-existing upper channel line and subsequent acceptance.

### Triangle Descending

Horizontal support and falling resistance conventionally imply bearish continuation. An upside break can become powerful because it invalidates the bearish structure, but that is a confirmed exception, not an advance bullish signal.

Default action: exclude from the continuation watchlist; keep as a separate `FAILED_BEARISH_PATTERN` event after an upside close through the descending resistance line.

### Double and Multiple Bottom

Finviz defines a prior downtrend, two or more similar lows, and horizontal resistance at the intervening high. The formation is not complete until resistance breaks.

These can be valuable reversal-breakout candidates when:

- the later low undercuts or tests support but closes strongly;
- selling range and volume decline;
- the right side forms higher lows;
- price approaches the neckline with improving relative strength.

Do not mix bottom-reversal events with continuation breakouts; their factor exposures and failure behavior differ.

### Double and Multiple Top

Finviz defines these as reversal structures after an uptrend, completed by a support break. Two equal highs can also resemble resistance being tested, but the Finviz “top” label carries rejection context.

For an upside-breakout screener, repeated long upper shadows or lower closes after each test are negative. Only reclassify after price closes above all prior top highs with abnormal volume. Before that, exclude or penalize.

### Head & Shoulders and Head & Shoulders Inverse

Standard Head & Shoulders is a bearish reversal pattern and should be excluded from an upside continuation watchlist.

Inverse Head & Shoulders is a bullish reversal candidate, but it is incomplete before a neckline break. The right shoulder can be watched for a hammer/long lower shadow and diminishing downside pressure. Store the neckline before the breakout.

Lo, Mamaysky, and Wang used automated nonparametric recognition on US stocks from 1962-1996 and found that several technical formations, including head-and-shoulders and double-bottom families, changed conditional return distributions. The paper supports systematic pattern definitions, not visual certainty or universal profits.

Source: [Lo, Mamaysky, and Wang](https://business.columbia.edu/sites/default/files-efs/pubfiles/19268/Lo-Mamaysky_wang_foundations.pdf).

## Overall ranking of the candlestick dropdown

| Finviz candlestick | Traditional message | Value before upside breakout | Dragonfly treatment |
|---|---|---:|---|
| Long Lower Shadow | Lower-price rejection | Moderate at base support | Positive contextual modifier |
| Hammer | Bullish reversal after decline | Moderate at final pullback/support | Positive contextual modifier; require confirmation |
| Dragonfly Doji | Strong lower rejection, close near high | Moderate at support | Positive but rare/context-sensitive |
| Spinning Top White | Indecision/small body | Low-moderate if total range is narrow | Compression modifier, direction-neutral |
| Spinning Top Black | Indecision/small body | Low-moderate if total range is narrow | Same as white; color should be tested |
| Doji | Open approximately equals close | Low | Use body/range geometry, not label alone |
| Inverted Hammer | Potential bullish reversal after decline | Low-moderate | Reversal model only; needs next-bar confirmation |
| Marubozu White | Strong one-sided buying | High as trigger, low as pre-signal | Breakout/confirmation feature |
| Long Upper Shadow | Higher-price rejection | Negative near resistance | Penalty/false-break warning |
| Gravestone Doji | Open/close near low after upper excursion | Negative near resistance | Stronger rejection penalty |
| Marubozu Black | Strong one-sided selling | Negative | Exclude/failed-setup signal |

## Deep review of each candlestick

### Long Lower Shadow

The market traded materially lower but recovered before the close. It is constructive only when the rejected prices correspond to base support, a rising trendline, moving-average support, or the lower edge of a valid pattern.

Quantify rather than trusting the label:

```text
lower_wick_ratio = (min(open, close) - low) / (high - low)
close_location = (close - low) / (high - low)

candidate if lower_wick_ratio >= 0.60 and close_location >= 0.60
```

Near resistance, a long lower shadow can be irrelevant if the total range is huge or price remains far below the pivot.

### Long Upper Shadow

Price traded higher but was rejected before the close. Immediately below resistance, this is the opposite of the desired acceptance signal.

Penalize when:

```text
upper_wick_ratio >= 0.50
and distance_to_pivot_atr <= 1.0
and close_location <= 0.50
```

Repeated upper shadows at the same level are stronger negative evidence than one isolated wick. A later close above all wick highs can invalidate the penalty.

### Hammer

A hammer has a small body near the high and a long lower shadow after a decline. The identical geometry after an advance is traditionally called a hanging man, so location and prior trend are essential.

For breakout research, a hammer is most relevant on the final shallow pullback of a base, not on the bar touching upper resistance. Require the next completed bar to hold above the hammer midpoint or high.

### Inverted Hammer

This candle probes higher after a decline but closes back near the lower portion. The upper wick is potential demand exploration, yet it is also rejection. Traditional use requires next-bar bullish confirmation.

Use only in the reversal-breakout branch and assign less weight than a lower-shadow hammer.

### Spinning Top White and Black

Small bodies with meaningful upper and lower shadows describe two-sided trade. They can be useful at a triangle apex or below resistance only when the **entire high-low range** is also small relative to ATR.

Do not assume white is materially more bullish than black. Test body color by ablation after matching for close location and range.

### Doji

Open and close are nearly equal, but the full range can be narrow or very wide. Therefore Doji is not synonymous with volatility contraction.

Recommended replacement features:

```text
body_to_range
range_to_atr
upper_wick_ratio
lower_wick_ratio
close_location
distance_to_pivot_atr
```

### Dragonfly Doji

Open and close lie near the high with a long lower shadow. It is a more extreme lower-rejection geometry. Rank positively only at support within an otherwise constructive base; require liquidity and next-bar confirmation because rare patterns are vulnerable to small samples.

### Gravestone Doji

Open and close lie near the low with a long upper shadow. Near resistance this indicates failure to hold higher prices. Use it as a false-break/rejection feature, not an upside predictor.

### Marubozu White

A large white body with minimal shadows indicates one-sided buying. If it crosses resistance and closes near its high, the breakout has already happened.

Treat as confirmation:

```text
body_to_range >= 0.85
close_location >= 0.90
close > stored_pivot + breakout_buffer
relative_volume >= threshold
```

Avoid chasing when the candle is several ATRs above the pivot; model extension and next-open slippage.

### Marubozu Black

A large black body with minimal shadows signals one-sided selling. Inside a pre-breakout base it is a setup failure unless the next bar immediately recovers. Use it as a negative or invalidation event.

## What peer-reviewed candlestick research shows

The literature does not support treating these dropdown names as universally profitable signals:

- Caginalp and Laurent reported predictive information in mechanically defined candlestick price patterns on S&P 500 stocks, providing early positive evidence ([Applied Mathematical Finance](https://www.tandfonline.com/doi/abs/10.1080/135048698334637)).
- Marshall, Young, and Rose's bootstrap analysis concluded that the tested candlestick strategies were not profitable on DJIA stocks during 1992-2002 ([Journal of Banking & Finance](https://www.sciencedirect.com/science/article/pii/S0378426605002116)).
- A 5-minute study of all 30 DJIA constituents found no single candle rule beat buy-and-hold after costs and data-snooping correction ([Duvingage, Mazza, and Petitjean](https://ideas.repec.org/p/cor/louvrp/2671.html)).
- A ten-year SET50 study found little reliable direction prediction; RSI, stochastic, and money-flow filters generally did not improve results ([SAGE Open](https://journals.sagepub.com/doi/full/10.1177/2158244017736799)).
- A 2015 DJIA study found profitability for eight three-day reversal patterns under one holding strategy after a 0.5% assumed cost and data-snooping adjustment, but not under another holding strategy. This is direct evidence that exits and definitions can determine the conclusion ([Journal of Banking & Finance](https://www.sciencedirect.com/science/article/pii/S0378426615002678)).
- A 2021 Chinese-equity study found useful one-day predictions from machine-learning-filtered two- and three-day combinations, while warning about small pattern samples, overfitting, and the need for mature-market validation ([PLOS One](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255558)).

Conclusion: **OHLC geometry can contain conditional information, but the portable edge of isolated candle names is weak and context-dependent.**

## What chart-pattern research and theory show

- Brock, Lakonishok, and LeBaron found information in moving-average and trading-range-break rules using DJIA data from 1897-1986. This supports objective boundaries, not any one visual pattern ([Journal of Finance paper](https://support-and-resistance.technicalanalysis.org.uk/BrockLakonishokLeBaron1992.pdf)).
- Sullivan, Timmermann, and White showed why technical-rule research must adjust for data snooping across the full rule universe ([Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00163)).
- Lo, Mamaysky, and Wang found that several algorithmically recognized patterns changed conditional return distributions in a large 1962-1996 US-stock sample ([paper](https://business.columbia.edu/sites/default/files-efs/pubfiles/19268/Lo-Mamaysky_wang_foundations.pdf)).
- Friesen, Weller, and Dunham provide a confirmation-bias model capable of producing head-and-shoulders and double-top-like price behavior and find positive autocorrelation in sequential price jumps ([Journal of Banking & Finance](https://ideas.repec.org/a/eee/jbfina/v33y2009i6p1089-1100.html)).
- A probabilistic-neural-network study covering ten indices and DJIA components evaluated ascending/descending triangles, wedges, channels, tops, bottoms, cup-and-handle, and head-and-shoulders families; its finding that performance differs by pattern reinforces the need for pattern-specific validation ([Algorithmic Finance](https://journals.sagepub.com/doi/10.3233/AF-160059)).

## Books, practitioners, quants, and market history

### Books and historical lineage

- Steve Nison's *Japanese Candlestick Charting Techniques* brought Japanese candlestick methods into widespread Western use and explicitly presents them as tools to combine with Western analysis ([publisher](https://www.penguinrandomhouse.com/books/350650/japanese-candlestick-charting-techniques-by-steve-nison/)).
- Thomas Bulkowski's *Encyclopedia of Candlestick Charts* tabulates 103 formations with identification and behavioral statistics. It is practitioner research, not a peer-reviewed causal study ([Wiley](https://doi.org/10.1002/9781119202288)).
- Bulkowski's *Encyclopedia of Chart Patterns* is a useful catalogue of pattern definitions, breakout directions, failure rates, and measured moves. Its “perfect trade” statistics are better for relative comparison than achievable return forecasts.
- Edwards and Magee's *Technical Analysis of Stock Trends* codified classical triangles, channels, support/resistance, tops, bottoms, and head-and-shoulders analysis.
- Toby Crabel's *Day Trading with Short Term Price Patterns and Opening Range Breakout* supplies NR4/NR7, inside-day, and contraction-expansion hypotheses.
- O'Neil, Minervini, Weinstein, Darvas, Donchian, and the Turtle tradition converge on a broader process: trend, base/contraction, explicit pivot, confirmation, and predefined failure—not isolated candle prediction.

### What professional managers use

Menkhoff's survey of 692 fund managers across five countries found that 87% gave technical analysis at least some importance, and technical analysis was most important at horizons of weeks. This documents use rather than profit. [Journal of Banking & Finance](https://www.sciencedirect.com/science/article/pii/S0378426610001755).

Systematic managers generally convert the screenshots into numerical features:

- swing-point coordinates and line-fit error;
- line slopes, convergence, and time to apex;
- number, spacing, and dispersion of resistance touches;
- range, body, wick, gap, and close-location ratios;
- ATR and volume percentiles;
- market/industry-relative strength;
- breakout distance, volume, and acceptance;
- spread, slippage, turnover, and capacity.

## Recommended Finviz presets

Finviz permits one Pattern and one Candlestick selection per screen, so save separate presets rather than trying to represent every hypothesis in one query.

### Preset A - continuation compression

```text
Pattern                 Triangle Ascending
Candlestick             Doji OR Spinning Top White/Black (separate presets)
20-Day High/Low         0-3% below High
Price                   Above SMA20, SMA50, SMA200
Performance             Month Up
Average Volume          Over 500K; preferably Over 1M
Price                   Over $10
```

Doji is only a search proxy. Manually or programmatically require a small **total range**, not just a small body.

### Preset B - horizontal base

```text
Pattern                 Horizontal S/R or Channel
Candlestick             Spinning Top or Doji
20-Day High/Low         0-3% below High
Price/SMA/volume        Same as Preset A
```

Verify that price is near the upper boundary, because Horizontal S/R and Channel can also return stocks near support.

### Preset C - bullish rejection inside a continuation base

```text
Pattern                 Triangle Ascending or Wedge
Candlestick             Long Lower Shadow
Price/SMA/volume        Same as Preset A
```

Use only if the lower shadow occurs at the lower support or final shallow pullback, not randomly in the middle of the structure.

### Preset D - reversal breakout

```text
Pattern                 Wedge Down, Double Bottom, Multiple Bottom,
                        or Head & Shoulders Inverse (separate presets)
Candlestick             Hammer, Long Lower Shadow, or Dragonfly Doji
```

This produces a **reversal watchlist**. It is not a breakout until price closes above the upper boundary or neckline.

### Preset E - breaking out now

```text
Pattern                 Triangle Ascending, Channel, or Horizontal S/R
Candlestick             Marubozu White
20-Day High/Low         New High
Relative Volume         Over 1.5; test Over 2.5 separately
Change from Open        Up
```

This is a trigger screen, not “about to happen.” Reject signals that close back below the stored resistance line or are excessively extended in ATR units.

## Dragonfly scoring proposal

Do not assign a fixed published probability to a Finviz label. Start with a transparent score for ranking and then calibrate it from the walk-forward test.

```text
structure_score:
  +3 Triangle Ascending
  +3 Horizontal S/R or Channel, when price is near resistance
  +2 Wedge in prior uptrend
  +1 Wedge Down / inverse H&S / bottom pattern in reversal model
  -2 Triangle Descending or Wedge Up
  -3 Double/Multiple Top or Head & Shoulders

candle_modifier:
  +1 Long Lower Shadow / Hammer / Dragonfly at verified support
  +1 narrow-range Spinning Top or Doji near pivot
   0 Inverted Hammer pending confirmation
  -1 Long Upper Shadow near pivot
  -2 Gravestone Doji near pivot
  -3 Marubozu Black

trigger_modifier:
  +3 Marubozu White crossing stored pivot with volume
```

These points are proposed engineering priors, not research-derived coefficients. Production probabilities must come from calibrated out-of-sample results.

## Required backtest design

### Three separate labels

```text
cross_5d:
  any close in t+1..t+5 exceeds stored resistance + 0.10 ATR

accept_10d:
  cross_5d and either two closes above resistance
  or a successful retest closing back above it

profitable_20d:
  accept_10d and net market-relative return after costs > 0
```

### Required experiment matrix

For every chart pattern:

1. Pattern alone, with trend/liquidity controls.
2. Pattern plus each candlestick individually.
3. Pattern plus candle geometry as continuous variables.
4. Pattern plus breakout-day volume.
5. Pattern plus acceptance/retest.
6. Same pattern in bull, bear, high-volatility, and low-volatility regimes.

For each combination report sample size, crossing precision, incremental lift, calibration, mean/median excess return, excess win rate, maximum favorable/adverse excursion, turnover, spread, and net return.

### Bias controls

- Use the pattern state available at the original historical date, not today's reconstructed Finviz label.
- Freeze swing points and resistance before the forecast begins.
- Purge overlapping forward windows and cluster uncertainty by date and symbol.
- Include delisted stocks and point-in-time universe membership.
- Correct for testing many pattern/candle combinations using a reality-check, false-discovery-rate, or held-out test set.
- Match controls by date, sector, size, liquidity, trend, and volatility.
- Include gap-through-entry, gap-through-stop, bid-ask spread, slippage, and market impact.

## Proof of work

### Materials examined

- The two supplied screenshots and every visible Finviz Pattern/Candlestick menu item.
- Finviz's official screener, candlestick detection, and chart-pattern documentation.
- Peer-reviewed research on candlestick profitability, chart-pattern recognition, trading-range breaks, support/resistance liquidity, order clustering, data snooping, and fund-manager use.
- Positive, negative, and specification-sensitive findings across US, Japanese, Thai, Taiwanese, Chinese, index-futures, foreign-exchange, and intraday samples.
- Books and practitioner work by Nison, Bulkowski, Edwards/Magee, Crabel, O'Neil, Minervini, Weinstein, Darvas, Donchian, and Turtle-system practitioners.
- Dragonfly's existing 2020-2026 breakout backtest, used as the baseline rather than ignored.

### Representative search trail

```text
Finviz official chart patterns triangle wedge channel support resistance
Finviz candlestick Long Lower Shadow Dragonfly Doji Marubozu
candlestick trading strategy bootstrap DJIA Journal Banking Finance
candlestick intraday DJIA data snooping transaction costs
candlestick profitability S&P 500 Japan Taiwan Thailand China
ascending triangle wedge double bottom head shoulders empirical study
Lo Mamaysky Wang technical pattern recognition US stocks
support resistance limit order book depth Kavajecz Odders-White
stop loss clustering support resistance Osler Federal Reserve
price patterns confirmation bias Friesen Weller Dunham
fund managers use technical analysis Menkhoff
Bulkowski encyclopedia chart patterns statistics
Nison Japanese candlestick history publisher
```

### Evidence-strength policy

- **Strongest:** peer-reviewed, mechanically defined, broad or long sample, costs and multiple-testing addressed.
- **Moderate:** peer-reviewed but market-specific, indirect, or without a direct pre-breakout label.
- **Practitioner:** documented method or large proprietary study without independent replication.
- **Proposed:** Dragonfly definition, threshold, or score awaiting validation.

## Final recommendation

For the main Dragonfly upside-breakout model, prioritize:

```text
Triangle Ascending
Horizontal S/R near the upper boundary
Horizontal Channel near the upper boundary
Wedge in an existing uptrend
```

Use candlesticks only as modifiers:

```text
Positive at verified support:
Long Lower Shadow, Hammer, Dragonfly Doji

Compression near pivot:
Spinning Top White/Black, narrow-range Doji

Trigger:
Marubozu White through resistance with volume

Negative near resistance:
Long Upper Shadow, Gravestone Doji, Marubozu Black
```

Keep Wedge Down, Double/Multiple Bottom, and Inverse Head & Shoulders in a separate reversal-breakout model. Exclude Wedge Up, Triangle Descending, Double/Multiple Top, and standard Head & Shoulders from the default bullish continuation preset.

The user-facing status should distinguish:

- `PATTERN_FORMING`
- `NEAR_RESISTANCE`
- `BREAKOUT_TRIGGERED`
- `BREAKOUT_ACCEPTED`
- `BREAKOUT_FAILED`

That distinction is more defensible than declaring that any Finviz pattern means a breakout “will happen.”
