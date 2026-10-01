# Candlestick Patterns That May Precede an Upside Breakout

**Research date:** 15 September 2026  
**Market:** Liquid US common stocks  
**Primary horizon:** Daily bars, predicting a resistance break during the next 1-10 sessions

> Research and system-design material, not investment advice. A candle is a four-number summary of one bar. A named candle alone cannot establish that an upside breakout is imminent.

## Answer in one sentence

The most defensible candlestick setup is not a hammer or engulfing candle. It is a **sequence of inside and/or narrow-range candles with progressively smaller ranges and bodies, forming immediately below an objective resistance pivot while the stock and its industry remain in an uptrend**. That setup identifies compression; the upside direction still requires a bullish trend and an actual close above the pivot.

## Evidence-based ranking

| Rank | Pattern | What it suggests | Directional before trigger? | Evidence assessment |
|---:|---|---|---|---|
| 1 | Inside Day + NR7 | Strong one-bar range compression | No | Best research candidate; practitioner-based, mechanically clean |
| 2 | Double/Triple Inside Day | Multi-bar contraction and balance | No | Plausible; limited direct peer-reviewed stock evidence |
| 3 | Progressive Narrowing Sequence | Volatility contraction over 3-5 bars | No | Strong practitioner convergence; exact rule unvalidated |
| 4 | Tight Bullish Closes | Demand holds price near highs while range contracts | Weakly bullish | Plausible contextual feature, not a canonical candle |
| 5 | Rising Three Methods | Pause inside an established upward impulse | Bullish continuation hypothesis | Traditional; mixed/limited independent evidence |
| 6 | Hammer or Bullish Engulfing at the final base pullback | Rejection of lower prices | Bullish only at base support | Mixed; not a direct breakout predictor |
| Avoid | Doji alone | Indecision | No | Weak standalone evidence |
| Avoid | Three White Soldiers / bullish marubozu | Move already underway | Yes, but late | Trigger/continuation state, not “about to break out” |
| Avoid | Shooting Star / repeated long upper wicks at pivot | Rejection at resistance | Bearish warning | Negative candidate feature |

## Pattern 1 - Inside Day + NR7

### Mechanical definition

For daily bar `t`:

```text
inside_day[t] = high[t] < high[t-1] and low[t] > low[t-1]
range[t] = high[t] - low[t]
nr7[t] = range[t] == min(range[t-6:t])
inside_nr7[t] = inside_day[t] and nr7[t]
```

Require the bar to occur close to a pivot:

```text
0 < (pivot_20[t] - close[t]) / ATR14[t] <= 1.0
```

Interpretation: the inside day shows that the entire session remained within the previous session's range; NR7 shows it was the smallest range in seven sessions. Together they describe unusually tight short-term balance. They do **not** predict which side will break.

Toby Crabel popularized NR4, NR7, inside-day combinations, and opening-range breakouts in *Day Trading with Short Term Price Patterns and Opening Range Breakout*. A peer-reviewed opening-range paper explicitly relates its test to Crabel's contraction-expansion principle and finds positive results in its US crude-oil-futures specification. This supports testing the mechanism, but it is not direct proof for individual US stocks.

Sources: [NR7 definition and Crabel attribution](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/narrow-range-day-nr7), [opening-range-breakout study](https://www.sciencedirect.com/science/article/pii/S1544612312000438).

## Pattern 2 - Double or Triple Inside Day

### Mechanical definition

```text
inside_1 = high[t] <= high[t-1] and low[t] >= low[t-1]
inside_2 = high[t-1] <= high[t-2] and low[t-1] >= low[t-2]
double_inside = inside_1 and inside_2
```

For a stricter nested version, require each bar to fit inside the immediately preceding bar. Also retain a looser “multiple bars inside one mother bar” feature because nested bars are rare.

Useful measurements:

- mother-bar range in ATR units;
- number of contained bars;
- cumulative volume during containment versus the prior 20 days;
- distance from mother-bar high and the independent 20-day pivot;
- location of closes within the mother bar.

Interpretation: repeated containment is visible volatility compression. It becomes an upside candidate only when the higher-timeframe trend is positive and the upper boundary aligns with meaningful resistance.

Evidence grade: **experimental**. The definition is objective and audit-friendly, but this review did not find strong peer-reviewed US-stock evidence that double-inside days alone predict profitable upside breaks.

## Pattern 3 - Progressive Narrowing Sequence

This is the candlestick implementation of the volatility-contraction pattern used by Mark Minervini and closely related to the contraction-expansion principle used by Crabel.

### Mechanical definition

Test both strict and tolerant forms:

```text
strict_narrowing = range[t] < range[t-1] < range[t-2]

tolerant_narrowing = median(range[t-2:t])
                     <= 0.65 * median(range[t-9:t-3])

body_ratio = abs(close - open) / max(high - low, epsilon)
```

Additional desirable features:

- pullback depths contract, for example 12%, then 7%, then 3%;
- real bodies become smaller;
- closes remain in the upper half of the local base;
- volume contracts during the last 3-5 bars;
- relative strength remains near a high.

Interpretation: sellers are moving price less on each pullback, which practitioners interpret as diminishing supply. The sequence still needs a pivot and trigger; narrowing at the bottom of a downtrend can break lower.

Evidence grade: **strong practitioner hypothesis, limited direct academic validation**.

## Pattern 4 - Tight Bullish Closes below resistance

This is more useful to a quant system than a traditional candle name.

### Mechanical definition

Over the last three bars:

```text
all(close_location >= 0.60)
max(close_3) - min(close_3) <= 0.35 * ATR14
median(range_3) <= 0.70 * median(range_20)
close[t] > close[t-3]
```

where:

```text
close_location = (close - low) / (high - low)
```

Interpretation: price is not moving much, yet closes remain relatively firm. This may be more informative than a single doji because it describes **location, persistence, and contraction** rather than only a small body.

Evidence grade: **proposed quantitative synthesis**. It must be validated against trend- and volatility-matched control observations.

## Pattern 5 - Rising Three Methods

Traditional construction:

1. A relatively large bullish candle.
2. Roughly three small candles consolidate, mostly within the first candle's range.
3. A later bullish candle closes above the first candle's high.

Only the middle consolidation is pre-breakout information. The final long candle is already the trigger. Code it as a family of inequalities rather than requiring exactly three middle candles.

```text
impulse = return[t-4] >= 1.0 * ATR_percent[t-4]
contained_pause = max(high[t-3:t-1]) <= high[t-4] + tolerance
                  and min(low[t-3:t-1]) >= low[t-4] - tolerance
small_pause = median(range[t-3:t-1]) <= 0.60 * range[t-4]
```

Evidence grade: **traditional continuation pattern with weak pattern-specific proof**. Candlestick results change materially with trend and exit definitions. A 2015 Journal of Banking & Finance paper found some three-day reversal strategies profitable after data-snooping adjustment under one holding strategy but not another, demonstrating specification sensitivity rather than a universal edge.

Source: [Lu, Chen, and Hsu (2015)](https://www.sciencedirect.com/science/article/pii/S0378426615002678).

## Pattern 6 - Hammer or Bullish Engulfing at the last pullback

These are reversal/rejection patterns, not direct resistance-break patterns.

Use them only when all of the following are true:

- the stock is in a broader uptrend;
- the candle occurs at the lower half or support of a valid base;
- the next bar confirms rather than immediately violating the low;
- price remains close enough to the pivot for a breakout within the forecast horizon.

Example hammer features:

```text
body = abs(close - open)
lower_shadow = min(open, close) - low
upper_shadow = high - max(open, close)

hammer = lower_shadow >= 2 * body
         and upper_shadow <= body
         and close_location >= 0.60
```

Example bullish engulfing features:

```text
previous_bearish = close[t-1] < open[t-1]
current_bullish = close[t] > open[t]
body_engulfs = open[t] <= close[t-1] and close[t] >= open[t-1]
```

Evidence is mixed. Some papers find conditional profitability in specific markets and with specific exits, while large US, Japanese, intraday DJIA, and Thai studies find little or no robust standalone value. Therefore Dragonfly should test the numeric wick/body features, location in the base, and confirmation—not assume that the name “hammer” creates an edge.

Sources: [Marshall, Young, and Rose (2006)](https://www.sciencedirect.com/science/article/pii/S0378426605002116), [Thai SET50 study](https://journals.sagepub.com/doi/full/10.1177/2158244017736799), [DJIA intraday study](https://ideas.repec.org/p/cor/louvrp/2671.html).

## Patterns that should not be primary pre-breakout signals

### Doji or spinning top alone

A small body shows that open and close are close. It says little about the total high-low range, where the bar sits relative to resistance, or direction. Replace `doji = true` with continuous body, wick, range, and pivot-location features.

### Three White Soldiers

Three large rising candles describe an advance that is already underway and can be extended. It may be a continuation feature, but it does not answer “about to break out.”

### Bullish marubozu

A large body closing near the high is valuable on the breakout bar as displacement/acceptance. Before a breakout, it often means the trigger has already occurred.

### Long upper shadows at resistance

Repeated closes far below the high show rejection. Treat upper-wick pressure as a negative feature:

```text
upper_wick_ratio = (high - max(open, close)) / (high - low)
```

Penalize candidates when the median upper-wick ratio near the pivot is high, unless later bars absorb and close above those wick highs.

### Memorized pattern names without location

The same candle at base support, in the middle of a range, and immediately below resistance represents different market states. Location and prior trend must be explicit features.

## What the journal literature actually says

The literature is conflicting, market-specific, and highly sensitive to definitions:

- Caginalp and Laurent tested candlestick price patterns on S&P 500 stocks and reported predictive power, an early positive result ([Applied Mathematical Finance](https://www.tandfonline.com/doi/abs/10.1080/135048698334637)).
- Marshall, Young, and Rose's bootstrap study concluded that candlestick strategies were not profitable on DJIA stocks over 1992-2002 ([Journal of Banking & Finance](https://www.sciencedirect.com/science/article/pii/S0378426605002116)).
- Their later work found the tested strategies were not generally profitable for large US stocks ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980583)).
- A 5-minute study of the 30 DJIA constituents found no candlestick rule beat buy-and-hold after transaction costs and data-snooping correction ([Duvingage, Mazza, and Petitjean](https://ideas.repec.org/p/cor/louvrp/2671.html)).
- A ten-year SET50 study found most bullish and bearish patterns statistically indistinguishable from zero; RSI, stochastic, and money-flow filters generally did not improve accuracy ([SAGE Open](https://journals.sagepub.com/doi/full/10.1177/2158244017736799)).
- A 2021 PLOS One study found that machine-learning-filtered two- and three-day combinations predicted one-day Chinese-market returns in its out-of-sample period, including an assumed 0.2% cost. The authors warn that many three-day combinations had small samples and overfitting risk; they also call for testing in mature markets ([PLOS One](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255558)).

The defensible conclusion is not “candlesticks do not work” or “candlesticks work.” It is: **named candles have weak portability; numeric OHLC geometry combined with trend, location, liquidity, and a separately defined event is testable.**

## What quants and fund managers do

Menkhoff surveyed 692 fund managers in five countries. Eighty-seven percent placed at least some importance on technical analysis, and it was the most important analysis category at horizons of weeks. This proves professional use, not profitability. The users tended to connect price behavior with psychology and trend-following.

Source: [Menkhoff (2010), Journal of Banking & Finance](https://www.sciencedirect.com/science/article/pii/S0378426610001755).

Systematic managers generally do not trade poetic candle names. They encode:

- normalized body and wick sizes;
- close location within the bar;
- range and ATR percentiles;
- inside/outside relationships;
- gaps;
- distance to rolling highs;
- volume and liquidity;
- market/industry-relative return;
- confirmation and execution cost.

Donchian/Turtle-style managers use objective 20- or 55-day channel breaks and volatility-based sizing. Their historical contribution is the separation of entry, risk, and portfolio construction—not an advance prediction from one candle. Long-history trend-following evidence back to 1880 supports diversified trend systems across asset classes, not individual candlestick names.

Source: [AQR - A Century of Evidence on Trend-Following Investing](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/AQR-JPM-Fall-2017.pdf).

## Books and market history

- Steve Nison's *Japanese Candlestick Charting Techniques* introduced these techniques broadly to Western traders. Nison stresses combining candles with other technical tools; the publisher does not present the book as a controlled statistical validation ([Penguin Random House](https://www.penguinrandomhouse.com/books/350650/japanese-candlestick-charting-techniques-by-steve-nison/)).
- Thomas Bulkowski's *Encyclopedia of Candlestick Charts* defines and tabulates 103 formations. It is a valuable hypothesis catalogue, but its statistics must be independently replicated with point-in-time data and costs ([Wiley](https://doi.org/10.1002/9781119202288)).
- Toby Crabel's 1990 work supplies the most relevant bar-pattern family for “about to break out”: NR4, NR7, inside days, and opening-range activation.
- Mark Minervini's volatility-contraction pattern extends the same idea across multiple pullbacks and bars.
- O'Neil's base/pivot framework adds the essential higher-level location: a tight candle is relevant when it forms on the right side of a valid base near resistance.
- Japanese candle history is often attributed directly to eighteenth-century rice trader Munehisa Homma, but Nison's historical research places modern candle-chart development more plausibly in Japan's later Meiji period. Historical origin does not establish predictive validity.

## Dragonfly implementation specification

### Store geometry, then derive names

For every bar, calculate:

```text
range_pct = (high - low) / close
body_pct = abs(close - open) / close
body_to_range = abs(close - open) / max(high - low, epsilon)
upper_wick_to_range = (high - max(open, close)) / max(high - low, epsilon)
lower_wick_to_range = (min(open, close) - low) / max(high - low, epsilon)
close_location = (close - low) / max(high - low, epsilon)
gap_atr = (open - previous_close) / ATR14
range_percentile_20
range_percentile_252
```

Then derive `inside_day`, `nr4`, `nr7`, `inside_nr7`, `double_inside`, `hammer`, `engulfing`, and `rising_three_pause`. The model should receive both numeric geometry and pattern flags.

### Candidate rule for the first backtest

```text
trend = close > SMA20 > SMA50 > SMA200
        and slope(SMA50, 20) > 0

near_pivot = 0 < (prior_high_20 - close) / ATR14 <= 1.0

candle_compression = inside_nr7
                     or double_inside
                     or tolerant_narrowing

candidate = liquid and trend and near_pivot and candle_compression
```

Do not require bullish color. A red narrow-range candle can still be constructive compression; candle color should be a feature tested by ablation.

### Outcome labels

Keep three labels separate:

```text
cross_5d = any(close[t+1:t+5] > pivot[t] + 0.10*ATR14[t])

accept_10d = cross_5d and
             (two closes above pivot or successful retest)

profitable_20d = accept_10d and
                 forward_excess_return_20d_after_costs > 0
```

This prevents a model that predicts a brief crossing from being mistaken for a profitable strategy.

### Required ablation tests

Compare:

1. liquid universe only;
2. trend + pivot proximity baseline;
3. baseline + inside day;
4. baseline + NR7;
5. baseline + inside-day-and-NR7 intersection;
6. baseline + double inside;
7. baseline + progressive narrowing;
8. baseline + hammer at recent base support;
9. baseline + bullish engulfing at recent base support;
10. each pattern with and without volume contraction;
11. each pattern with breakout-day relative volume and acceptance.

Report incremental lift over the same trend-, volatility-, sector-, and calendar-matched baseline. Use walk-forward splits, purged label windows, date/symbol clustering, delisted stocks, and realistic spread/slippage.

## Proof of work

### Research categories examined

- Peer-reviewed candlestick studies covering US, Japanese, Thai, Taiwanese, Chinese, equity-index-futures, and intraday DJIA samples.
- Positive, negative, and specification-sensitive findings rather than only supportive papers.
- Pattern-recognition and machine-learning research using OHLC/candlestick representations.
- Fund-manager survey evidence on real professional use of technical analysis.
- Books by Nison, Bulkowski, Crabel, Minervini, and O'Neil.
- Historical Donchian/Turtle channel-breakout and Japanese candlestick traditions.
- Dragonfly's existing breakout research and 2020-2026 backtest, which establishes trend plus 20-day-pivot proximity as the baseline to beat.

### Representative search trail

```text
candlestick technical trading strategies Journal of Banking Finance
predictive power candlestick price patterns S&P 500
inside day narrow range breakout empirical study
NR4 NR7 Toby Crabel opening range breakout
candlestick intraday DJIA transaction costs data snooping
candlestick profitability Japan Taiwan Thailand stock market
machine learning candlestick patterns out of sample
fund managers use of technical analysis Menkhoff
Steve Nison candlestick history publisher
Bulkowski encyclopedia candlestick statistical analysis
Turtle Donchian channel breakout fund managers
```

### Claim labels

- **Academic:** supported directly or indirectly by peer-reviewed work.
- **Practitioner:** documented in a professional method or book but not independently validated at the stated cutoff.
- **Proposed:** a Dragonfly feature or threshold created for testing.
- **Negative evidence:** a study found no robust or portable standalone profitability.

## Final decision

Implement and backtest these first:

1. `inside_nr7_near_pivot`
2. `double_inside_near_pivot`
3. `progressive_narrowing_near_pivot`
4. `tight_high_closes_near_pivot`
5. `rising_three_pause_near_pivot`

Retain hammer and bullish engulfing only as optional **base-support rejection** features. Do not make doji, three white soldiers, marubozu, RSI, or MACD mandatory gates.

The production message should read: **“Candlestick compression detected below resistance; upside breakout not confirmed.”**
