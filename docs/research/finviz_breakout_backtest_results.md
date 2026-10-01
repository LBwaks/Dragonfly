# Backtest of the Finviz-Style Breakout Filters

**Run date:** 15 September 2026  
**Market data:** Alpaca adjusted daily OHLCV  
**Test period after warm-up:** 31 December 2020–14 September 2026  
**Universe:** 108 currently active, predominantly large/liquid US stocks  
**Benchmark:** SPY  
**Modeled trading cost:** 20 basis points round trip

> This is a preliminary research backtest, not investment advice or production validation. The current-stock universe creates survivorship and selection bias.

## Result in one sentence

The filters were useful for finding stocks likely to print a 20-day breakout soon, but the full setup did **not** produce excess returns versus SPY after the modeled costs; the 50-day and 52-week proximity filters slightly reduced rather than improved breakout incidence in this sample.

## Rules tested

### Near-breakout setup

At each completed daily close, the full setup required:

```text
Price                         >= $10
Prior 63-day average volume  >= 500,000 shares
Close                         > SMA20, SMA50 and SMA200
21-day performance            > 0%
63-day performance            > 0%
Distance below prior 20d high 0% to 3%
Distance below prior 50d high 0% to 5%
Distance below prior 252d high 0% to 10%
```

Rolling highs exclude the current bar. This prevents the look-ahead error of using a bar to create and cross its own resistance level.

### Breakout event

A breakout occurred when a completed daily close exceeded the highest high of the prior 20 sessions.

### Confirmed-trigger variant

The stricter trigger added:

```text
20-day new high
Full trend filter
Relative volume >= 1.5
Daily change >= 2%
Close > Open
```

### Trade simulation

- Signal observed at the completed daily close.
- Entry at the next session’s open.
- Exit at the close after 5, 20, or 60 sessions.
- 10 basis points charged at entry and 10 at exit.
- A 20-session cooldown reduced repeated breakout signals in the same stock.
- “Setup-preceded” means the full near-breakout setup appeared within the ten sessions before the breakout.

## Does the screen predict a breakout?

The following rows use stock-day observations. They overlap through time and must not be interpreted as independent statistical trials.

| Filter stack | Observations | Break within 5d | Break within 10d | Break within 20d |
|---|---:|---:|---:|---:|
| Liquid only | 152,104 | 24.64% | 37.96% | 56.58% |
| + SMA20/50/200 and positive 1m/3m trend | 50,257 | 41.75% | 55.11% | 67.75% |
| + within 3% of prior 20d high | 30,583 | **43.35%** | **57.28%** | **69.04%** |
| + within 5% of prior 50d high | 29,386 | 43.25% | 57.14% | 68.93% |
| + within 10% of prior 52w high | 26,317 | 42.88% | 56.72% | 68.61% |

### Ablation finding

- Trend qualification produced most of the lift: **+17.11 percentage points** at five days compared with the liquid-only sample.
- Nearness to the 20-day high added another **1.60 points** at five days.
- Adding 50-day proximity changed the five-day rate by **−0.10 points**.
- Adding 52-week proximity changed it by another **−0.37 points**.

Therefore, the 52-week filter has a research rationale for subsequent continuation, but it did not improve the narrow outcome “will a 20-day high be crossed soon?” in this test. That is a useful distinction between predicting a crossing and predicting profitable follow-through.

## Unique setup events

Using the first setup observation and a 20-session cooldown produced 2,762 setup events:

| Outcome | Breakouts | Rate |
|---|---:|---:|
| 20-day breakout within 5 sessions | 1,276 | 46.20% |
| Within 10 sessions | 1,633 | 59.12% |
| Within 20 sessions | 1,947 | 70.49% |

The screen is therefore effective as an **alert prioritizer**: approximately seven out of ten independent setup entries were followed by a 20-day-high close within 20 sessions in this selected universe. That does not imply the subsequent trade beat the market.

## Returns after a breakout

Returns below are net of the modeled 20-basis-point round-trip cost.

### All distinct 20-day breakouts

| Holding period | Trades | Mean return | Median | Win rate | Mean excess vs SPY | Excess win rate |
|---|---:|---:|---:|---:|---:|---:|
| 5 sessions | 3,355 | −0.00% | 0.06% | 50.85% | **−0.25%** | 46.71% |
| 20 sessions | 3,327 | 1.02% | 0.80% | 54.64% | **−0.24%** | 46.89% |
| 60 sessions | 3,230 | 2.80% | 1.92% | 56.22% | **−0.24%** | 45.63% |

The positive raw 20- and 60-day returns largely reflect an upward market regime. On average, these trades did not outperform SPY.

### Breakouts preceded by the full near-breakout setup

| Holding period | Trades | Mean return | Median | Win rate | Mean excess vs SPY | Excess win rate |
|---|---:|---:|---:|---:|---:|---:|
| 5 sessions | 1,440 | −0.09% | −0.03% | 49.65% | **−0.20%** | 47.85% |
| 20 sessions | 1,427 | 0.65% | 0.58% | 53.96% | **−0.25%** | 46.74% |
| 60 sessions | 1,391 | 2.29% | 1.58% | 55.64% | **−1.02%** | 43.28% |

The full preparation screen did not improve breakout returns. It selected weaker 60-day excess outcomes than the unrestricted 20-day-breakout set.

### Confirmed trigger: new high + trend + relative volume +2% move

| Holding period | Trades | Mean return | Median | Win rate | Mean excess vs SPY | Median excess | Excess win rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5 sessions | 364 | 0.18% | 0.15% | 52.20% | −0.11% | −0.41% | 45.88% |
| 20 sessions | 361 | **1.51%** | **1.21%** | 55.40% | **0.19%** | −0.62% | 47.65% |
| 60 sessions | 354 | **3.02%** | 1.36% | 55.65% | **0.22%** | −1.52% | 46.61% |

The strict trigger improved mean raw returns and produced a small positive *mean* excess return at 20 and 60 sessions. However, median excess return and excess win rate remained negative. A minority of large winners pulled up the mean; this is consistent with the asymmetric payoff often associated with trend following, but it is not yet evidence of robust alpha.

### Full setup followed by the confirmed trigger

| Holding period | Trades | Mean return | Mean excess vs SPY | Excess win rate |
|---|---:|---:|---:|---:|
| 5 sessions | 179 | 0.18% | −0.11% | 46.93% |
| 20 sessions | 177 | 0.98% | −0.38% | 43.50% |
| 60 sessions | 175 | 2.79% | −0.48% | 44.57% |

Combining every proposed setup filter with the strict trigger made results worse than using the trigger alone. This is evidence against deploying the original full filter stack unchanged.

## Decision

### Retain

- Minimum price and average-volume controls for execution quality.
- Price above SMA20/50/200 and positive one-/three-month returns as the primary setup regime.
- Within 3% of the prior 20-day high as a modest alert-prioritization feature.
- On the trigger day: relative volume, a positive close from the open, and meaningful displacement.
- Next-session execution and explicit transaction costs.

### Remove or demote

- **50-day-high proximity:** added no breakout-incidence improvement after the 20-day filter.
- **52-week-high proximity as a mandatory gate:** slightly reduced crossing incidence and did not improve returns in the combined screen. Retain it as a ranking or separate structural-breakout feature.
- **The full setup as a trading rule:** useful for alerts, but did not generate benchmark-relative alpha.

### Next test

The strict trigger is the only branch that merits further research. Before production use it needs:

1. A point-in-time universe including delisted securities.
2. Walk-forward parameter selection rather than fixed thresholds chosen from one sample.
3. Market- and industry-relative-strength features.
4. ATR-normalized break distance and explicit failed-break/retest exits.
5. Market regime segmentation, especially 2022 versus strong bull periods.
6. Portfolio-level position sizing, concurrent-position limits, and drawdown measurement.
7. Bootstrap or clustered inference that respects cross-sectional and temporal dependence.

## Relationship to the research thesis

The result agrees with the caution in the literature: objective trading-range breaks can contain information, but after-cost success is not universal. Brock, Lakonishok, and LeBaron found evidence for trading-range rules in a long DJIA sample ([Journal of Finance](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x)), while later work summarized in a recent review found that some technical rules did not earn consistent excess returns after transaction costs ([European Financial Management](https://onlinelibrary.wiley.com/doi/10.1111/eufm.12389)). Transaction costs and capacity are material to momentum-like implementations ([Korajczyk and Sadka](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2004.00656.x)).

The result does not disprove the 52-week-high literature. George and Hwang study subsequent-return information associated with nearness to the 52-week high, not the narrower question of whether adding a 10%-from-high gate improves a 20-day crossing screen ([Journal of Finance](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1540-6261.2004.00695.x)).

## Proof of work and reproducibility

### Code added

- `backend/analytics/breakout_backtest.py` — point-in-time feature construction and summary functions.
- `backend/apps/jobs/management/commands/backtest_breakout_filters.py` — reproducible Django command.
- `backend/analytics/test_breakout_backtest.py` — tests covering prior-high exclusion, breakout/setup separation, cooldown, and statistics.

### Verification performed

```text
Ruff:  all checks passed
Pytest: 4 passed
```

### Data ingestion performed

- Expanded the database from three stocks to a cross-sector sample.
- Database after ingestion: 181,659 daily bars, 2 January 2020–14 September 2026.
- SPY ingested separately as the benchmark.
- Analysis retained 108 stocks with enough observations after the 252-session warm-up.

### Reproduction command

```powershell
docker compose exec -T backend python manage.py backtest_breakout_filters `
  --start 2020-01-01 `
  --end 2026-09-14 `
  --benchmark SPY `
  --round-trip-cost-bps 20 `
  --json
```

### Universe used

```text
AAPL, ABBV, ABT, ADBE, ADP, AMAT, AMD, AMGN, AMT, AMZN, APD, ARM, AVGO,
AXP, BA, BAC, BKNG, BLK, C, CAT, CI, CMCSA, CME, COF, COP, COST, CRM, CSCO,
CVS, CVX, DE, DHR, DIS, DUK, ELV, EOG, EQIX, ETN, FIS, GE, GILD, GOOG,
GOOGL, GS, HD, HON, IBM, ICE, INTC, INTU, ISRG, JNJ, JPM, KO, LIN, LLY,
LMT, LOW, MA, MCD, MCO, MDLZ, MDT, META, MRK, MS, MSFT, MU, NEE, NFLX,
NKE, NOW, NVDA, ORCL, PANW, PEP, PFE, PG, PLD, PM, PNC, PYPL, QCOM, REGN,
RTX, SBUX, SCHW, SHW, SLB, SO, SPGI, T, TGT, TMO, TMUS, TSLA, TXN, UBER,
UNH, UNP, UPS, USB, V, VRTX, VZ, WFC, WMT, XOM
```

SPY was excluded from the stock universe and used only as the benchmark.

## Limitations

- The universe consists of securities known to be active and liquid today. Failed and delisted companies are absent.
- Current large-cap selection uses future information relative to early test dates.
- Daily data cannot reproduce intraday Finviz values or same-time-of-day relative volume.
- Historical point-in-time market capitalization, country classification, and spread were unavailable.
- Market impact beyond the fixed 20-basis-point cost was not modeled.
- Stock-day incidence observations overlap, and trade returns can remain correlated across stocks and dates.
- No stop loss, profit target, retest entry, or portfolio-capital constraint was optimized.
- The test period is relatively short and includes unusual pandemic and post-pandemic regimes.

## Bottom line

Use the near-breakout filters to build a **watchlist**, not as an automatic buy signal. For further research, simplify the setup to liquidity + trend + within 3% of the 20-day high, and investigate the strict breakout trigger separately. The original 50-day and 52-week proximity gates should not remain mandatory unless a broader, point-in-time backtest shows incremental value.
