# Finviz Filters for Stocks Approaching a Breakout

**Research date:** 15 September 2026  
**Purpose:** Convert breakout research into practical filters available in the Finviz screener shown in the supplied screenshot.

> A screener cannot establish that a breakout *will* happen. It can identify stocks close to an objective resistance boundary and then detect whether price actually breaks and is accepted above it. The percentages below are candidate screening thresholds to validate, not proven universal constants.

## Recommended workflow

Use three saved screens rather than one overloaded screen:

1. **Setup — Near Breakout:** finds liquid stocks approaching resistance.
2. **Trigger — Breaking Out Now:** finds stocks crossing a prior high with participation.
3. **Confirmation — Breakout Holding:** checks that price remains above the old boundary after the initial break.

This preserves an essential research distinction:

- “0–3% below a high” means **near resistance**, not a breakout prediction.
- “New High” means **the boundary was crossed**, not that it will hold.
- Acceptance above the old high is the **confirmation**.

Finviz states that its 20-day, 50-day, and 52-week High/Low filters measure percentage distance from the relevant record high or low. It also defines Relative Volume, ATR, moving averages, patterns, and performance in its official documentation ([Finviz Screener Help](https://finviz.com/help/screener.ashx)).

## Preset 1 — Near Breakout

This is the main answer to “about to happen.” It searches for a liquid stock in an established uptrend, sitting just under an observable resistance level without already being extremely extended.

### Enter these filters

| Finviz filter | Recommended selection | Status | Reason |
|---|---|---|---|
| Asset Type | Stock | Universe control | Removes ETFs and other non-operating securities when researching individual stocks. |
| Country | USA | Universe control | Keeps market structure, sessions, and accounting regime consistent. |
| Market Cap. | +Small / Over $300M | Risk control | Reduces microcap manipulation, spread, and capacity problems. Raise to Mid or higher for institutional liquidity. |
| Price | Over $10 | Risk control | Avoids many low-priced, high-spread securities. This is not a return predictor. |
| Average Volume | Over 500K | Liquidity control | A practical minimum; use Over 1M for more executable results. Finviz defines this as recent three-month average shares traded. |
| Current Volume | Over 200K | Optional intraday control | Prevents early results with negligible trading. Time-of-day dependent, so omit for end-of-day screening. |
| 20-Day High/Low | 0–3% below High | Primary setup | Places price close to short-term resistance. |
| 50-Day High/Low | 0–5% below High | Primary setup | Requires proximity to an intermediate resistance boundary. |
| 52-Week High/Low | 0–10% below High | Evidence-backed context | Avoids stocks whose apparent short-term breakout remains far below major resistance. |
| 20-Day Simple Moving Average | Price above SMA20 | Trend context | Confirms the stock is not approaching resistance from a weak short-term trend. |
| 50-Day Simple Moving Average | Price above SMA50 | Trend context | Intermediate trend filter. |
| 200-Day Simple Moving Average | Price above SMA200 | Regime context | Long-term uptrend filter commonly used by breakout practitioners. |
| Performance | Month Up | Relative-path proxy | Eliminates stocks near a high only because the high collapsed toward price. |
| Performance 2 | Quarter Up | Optional | Confirms broader strength, but can remove young reversals and fresh bases. |
| RSI (14) | Not Overbought / preferably 50–70 | Secondary only | Looks for positive pressure without extreme short-term extension. If Finviz offers only one-sided choices, do not force RSI; sort and inspect it instead. |
| Pattern | Triangle Ascending, Channel Up, or TL Resistance | Optional; one preset each | Pattern candidates near resistance. Do not mix subjective patterns into the core definition. |
| Relative Volume | Over 1 | Optional early-interest filter | Finds increasing attention. Omit it if the objective is to find quiet bases before volume appears. |

### How to run it

- Leave **Signal** as `None (all stocks)` for the broad setup screen.
- Save three variants of the Pattern filter rather than treating patterns as interchangeable:
  - `Near Breakout — Ascending Triangle`
  - `Near Breakout — Trendline Resistance`
  - `Near Breakout — Channel Up`
- Sort first by **20-Day High/Low** closest to the high, then inspect **Relative Volume**, **Average Volume**, and chart structure.
- If there are too few results, loosen only one boundary at a time: 20-day from 3% to 5%, then 50-day from 5% to 10%.
- If there are too many results, raise Average Volume to 1M or Market Cap to Mid—not RSI or pattern complexity.

### Minimal version

Use this when the full screen is too restrictive:

```text
Asset Type              Stock
Price                   Over $10
Average Volume          Over 500K
20-Day High/Low         0–3% below High
50-Day SMA              Price above SMA50
200-Day SMA             Price above SMA200
```

The minimal screen is a candidate generator. It deliberately avoids pretending that many correlated technical filters provide independent evidence.

## Preset 2 — Breaking Out Now

This preset detects the event; it no longer predicts “about to happen.”

| Finviz filter | Recommended selection | Reason |
|---|---|---|
| Asset Type | Stock | Consistent security universe. |
| Market Cap. | +Small / Over $300M | Removes most microcaps. |
| Price | Over $10 | Execution-quality control. |
| Average Volume | Over 500K or Over 1M | Tradability. |
| Signal | New High **or** Unusual Volume | Finviz defines New High as a 52-week high today and Unusual Volume as the highest relative-volume names. Because only one signal can be selected, save two variants. |
| 20-Day High/Low | New High | Detects a short-term boundary crossing. |
| 50-Day High/Low | New High | Optional stronger boundary. This will reduce the result set. |
| Relative Volume | Over 1.5; use Over 2 for strict version | Participation confirmation. The exact threshold is a heuristic. |
| Change | Up 2% or more | Optional displacement filter; price-independent ATR normalization would be better. |
| Change from Open | Up | Rejects some gap-ups that are selling off after the open. |
| 20-/50-/200-Day SMA | Price above each | Trend/regime context. |
| 52-Week High/Low | 0–3% below High or New High | Focuses on major-high breakouts. Use only for the 52-week variant. |

Finviz describes `New High` as stocks making a 52-week high that day and `Unusual Volume` as stocks with the highest relative-volume ratios ([official signal definitions](https://finviz.com/help/screener)).

### Do not automatically buy the returned list

For each result, record:

- the exact prior resistance price;
- whether the current bar **closed** above it;
- breakout distance as a percentage and in ATR units;
- whether the breakout candle closed near its high;
- gap size;
- sector/industry behavior;
- whether the move is still executable after spread and slippage.

Finviz’s fixed percentage filters cannot fully replace a volatility-normalized test. A 2% move is large for one stock and ordinary noise for another.

## Preset 3 — Breakout Holding

Finviz does not directly expose “two closes above the old breakout boundary” or “successful retest” as a standard dropdown. Approximate the confirmation screen as follows:

| Finviz filter | Recommended selection | Purpose |
|---|---|---|
| 20-Day High/Low | 0–3% below High or New High | Stock remains close to the broken level/high. |
| 20-Day SMA | Price above SMA20 | Short-term acceptance context. |
| 50-Day SMA | Price above SMA50 | Intermediate trend. |
| Performance | Week Up | Some post-break follow-through. |
| Relative Volume | Over 1 | Continued participation without demanding another extreme spike. |
| Change from Open | Up or Any | Use `Any` after the breakout day so a normal retest is not excluded. |

The actual confirmation must be computed or checked on the chart:

```text
confirmed = two_completed_closes_above_original_boundary
            OR successful_retest_of_original_boundary
```

Do not replace the original boundary with each newly printed high. Store the boundary that triggered the event.

## Optional practitioner-quality overlay

These are not necessary to define a breakout. They reflect the O’Neil/Driehaus tradition of combining technical leadership with improving company results:

| Finviz filter | Candidate setting | Interpretation |
|---|---|---|
| EPS Growth Qtr Over Qtr | Over 20% | Strong recent earnings growth. Threshold is practitioner-style, not universally proven. |
| Sales Growth Qtr Over Qtr | Over 15% or 20% | Confirms growth is not produced solely by cost cutting. |
| EPS Growth This Year | Positive | Basic fundamental direction. |
| Institutional Transactions | Positive | Optional demand proxy; reporting lag makes it unsuitable as a timing trigger. |
| Earnings Date | Not within the next few days, unless event breakouts are intended | Separates ordinary technical breakouts from earnings-event trades. |

Richard Driehaus emphasized positive relative strength and strong groups, while practitioner descriptions of his approach include earnings growth and positive surprises ([Driehaus speech](https://www.driehaus.com/system/uploads/fae/file/asset/420/RHD_Speech_2014.pdf), [AAII methodology discussion](https://www.aaii.com/journal/article/momentum-investing-the-richard-driehaus-way)). William O’Neil’s CAN SLIM framework likewise combines price/volume breakouts, earnings, leadership, new highs, and market confirmation ([McGraw Hill book record](https://www.mheducation.com/highered/mhp/product/how-make-money-stocks-winning-system-good-times-or-bad.html)). These are practitioner frameworks, not proof that the particular 15% or 20% cutoffs are optimal.

## Filters not to use as primary breakout evidence

| Filter | Why not |
|---|---|
| RSI Overbought | Describes recent gains after they occurred; can exclude powerful trends or select already extended moves. |
| MACD signal alone | A smoothed transformation of price, not a resistance crossing. |
| Low Float | Can amplify a move but also spreads, slippage, halts, and manipulation risk. It predicts potential movement size, not breakout quality. |
| Short Float | A possible catalyst for forced demand, but not evidence that resistance will break. |
| Beta | Market sensitivity, not a breakout predictor. |
| ATR over a fixed dollar amount | Not comparable across stock prices. ATR divided by price would be better. |
| Candlestick name alone | Highly specification-sensitive and not an objective multi-period boundary. |
| Many simultaneous price-derived indicators | SMA, RSI, MACD, performance, and high proximity are correlated views of the same price path. |

## Evidence-to-filter map

### Direct or closely related academic evidence

1. **Trading-range breaks:** Brock, Lakonishok, and LeBaron found historical information in moving-average and trading-range rules on the DJIA from 1897–1986 ([Journal of Finance](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x)). This supports testing objective range breaks, but not the exact Finviz percentages.
2. **Conflicting after-cost evidence:** a later review notes Allen and Karjalainen’s finding that moving-average and trading-range rules did not earn consistent excess returns after transaction costs on the S&P 500 from 1928–1995 ([European Financial Management](https://onlinelibrary.wiley.com/doi/10.1111/eufm.12389)). Therefore a filter list is not a trading strategy until costs and exits are tested.
3. **52-week high:** George and Hwang find that closeness to the 52-week high explains a large portion of medium-term continuation in their sample ([Journal of Finance](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1540-6261.2004.00695.x)). This is the strongest reason to include the Finviz 52-Week High/Low filter.
4. **Industry confirmation:** industry momentum accounts for an important part of individual-stock continuation ([Moskowitz and Grinblatt](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00146)). Finviz cannot create a direct within-industry rank in the basic filter grid, so review sector/industry leadership after screening.
5. **Return continuity:** gradual sequences of returns historically continued more strongly than a few discrete jumps with the same cumulative return ([Da, Gurun, and Warachka](https://academicweb.nd.edu/~zda/Frog.pdf)). This supports preferring orderly approaches to resistance over one-day vertical spikes.
6. **Volume as context:** turnover helps identify the lifecycle of price continuation; high-volume winners can reverse sooner, so more volume is not monotonically better ([Lee and Swaminathan](https://www.lsvasset.com/pdf/research-papers/Price-Momentum-Trad-Vol-2000.pdf)).
7. **Intraday conditionality:** first-half-hour market returns predict last-half-hour returns in the cited SPY sample, especially in high-volatility/high-volume conditions, but the predictive R-squared is small and the evidence is not an individual-stock opening-range rule ([Gao, Han, Li, and Zhou](https://www.sciencedirect.com/science/article/pii/S0304405X18301351)).
8. **Costs/capacity:** price impact and liquidity materially affect deployable returns ([Korajczyk and Sadka](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2004.00656.x)); this supports the price, market-cap, and volume controls.

### Theory

- **Anchoring:** the 52-week high can act as a salient reference point, creating delayed adjustment as price approaches or crosses it.
- **Gradual information diffusion:** information reaches participants at different times, allowing post-break continuation; Hong and Stein formalize underreaction followed by trend-chasing and possible overreaction ([Journal of Finance](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00184)).
- **Attention and order clustering:** obvious highs attract stop orders, breakout orders, and attention. That can generate immediate expansion but also a rapid false break if there is no durable repricing.
- **Overreaction:** a breakout after a long extension may be late rather than early. Behavioral models predict that initial underreaction can eventually become extrapolation and reversal ([Barberis, Shleifer, and Vishny](https://scholar.harvard.edu/files/shleifer/files/model_invest_sent.pdf)).

### Quants, funds, books, and history

- Managed-futures/trend-following systems commonly use objective trend or channel rules, volatility-scaled positions, and diversification. Long-history research reconstructs positive average trend-following returns back to 1880, but at the portfolio level across asset classes—not as proof of each stock breakout ([Hurst, Ooi, and Pedersen](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)).
- Institutional momentum indexes use volatility-adjusted 6- and 12-month returns and ranking. This supports relative-strength confirmation but does not identify the first break ([MSCI methodology](https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20231120.pdf)).
- O’Neil’s *How to Make Money in Stocks* and Weinstein’s *Secrets for Profiting in Bull and Bear Markets* supply influential base-breakout, volume, relative-strength, and market-confirmation frameworks. They should be treated as practitioner hypotheses and tested point in time.
- Lefèvre’s *Reminiscences of a Stock Operator* and Schwager’s *Market Wizards* provide historical insight into buying strength, adding to winners, failure control, and position sizing. They are anecdotes/interviews subject to survivorship and narrative bias ([Wiley: Lefèvre](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/reminiscences-of-a-stock-operator-978-0-471-67876-2), [Wiley: Schwager](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/market-wizards-978-1-118-27305-0)).

## Proof of work

### Materials inspected

- The supplied Finviz filter-grid screenshot.
- Finviz’s official Screener Help, signal definitions, High/Low definitions, volume definitions, technical-analysis pattern documentation, and intraday-timeframe documentation.
- Peer-reviewed or author-hosted work on trading-range rules, 52-week highs, industry effects, return continuity, volume, intraday continuation, transaction costs, behavioral theories, and long-history trend following.
- Published institutional momentum methodology and named breakout/growth practitioner frameworks.
- Historical trading books, classified as practitioner evidence rather than statistical proof.

### Representative search trail

```text
Finviz official screener help high low relative volume filters
Finviz official chart patterns resistance breakout
Finviz signals New High Unusual Volume definitions
trading range break rule Brock Lakonishok LeBaron Journal of Finance
technical trading rules transaction costs Allen Karjalainen
52-week high momentum George Hwang Journal of Finance
industry momentum individual stock continuation Moskowitz Grinblatt
price momentum trading volume Lee Swaminathan
Frog in the Pan continuous information momentum
intraday opening range breakout volatility state academic
momentum transaction costs capacity Korajczyk Sadka
century evidence trend following breakout rules
William O'Neil CAN SLIM price volume breakout publisher
Richard Driehaus relative strength earnings group leadership
```

### Claim-strength labels used

- **Evidence-backed:** directly supported by peer-reviewed empirical work or an official methodology.
- **Closely related:** supported by continuation/trend evidence but not by the exact Finviz rule.
- **Practitioner:** documented in a manager’s or author’s framework without independent proof of the precise cutoff.
- **Heuristic:** a proposed threshold that must be tested; this includes 3%, 5%, 10%, relative volume 1.5/2, $10 price, and 500K/1M average volume.

## Final recommended screen

> **Backtest update:** a preliminary 2020–2026 test found that the screen identifies a high rate of subsequent 20-day-high crossings but did not produce excess returns versus SPY. The 50-day and 52-week proximity gates did not add incremental crossing power. See [Backtest of the Finviz-Style Breakout Filters](./finviz_breakout_backtest_results.md) before using the settings below.

If only one preset will be used, make it the **Near Breakout** screen:

```text
Asset Type              Stock
Country                 USA
Market Cap              +Small / Over $300M
Price                   Over $10
Average Volume          Over 500K
20-Day High/Low         0–3% below High
50-Day High/Low         0–5% below High
52-Week High/Low        0–10% below High
20-Day SMA              Price above SMA20
50-Day SMA              Price above SMA50
200-Day SMA             Price above SMA200
Performance             Month Up
```

Treat `Pattern`, `RSI`, `Relative Volume`, earnings growth, and sales growth as optional ranking layers. A stock does not become a breakout until a completed bar crosses the stored resistance boundary, and it does not become a confirmed breakout until it holds above or successfully retests that boundary.
