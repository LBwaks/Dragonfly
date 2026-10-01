# Finviz-Style Pre-Breakout Pattern Backtest

**Run date:** 15 September 2026  
**Data window:** 31 December 2020 through 14 September 2026  
**Universe:** 108 currently active US stocks with sufficient locally stored daily OHLCV history  
**Benchmark:** SPY  
**Trading-cost assumption:** 20 basis points round trip

## Executive finding

The test does **not** support using any of the tested candlestick or chart-pattern labels as a standalone pre-breakout signal.

The trend-and-near-high baseline crossed its pre-signal 20-day resistance plus 0.10 ATR within five sessions on **49.29%** of 3,293 events. The strongest large-sample pattern result was trend-line resistance at **51.76%** (+2.47 percentage points), but its mean excess returns versus SPY were negative at 5, 20, and 60 sessions. White marubozu achieved **51.01%** (+1.73 points) on only 345 events and likewise failed to deliver a stable excess-return edge.

The practical conclusion is that pattern labels may describe market structure, but this sample does not justify treating them as sufficient evidence that a profitable breakout is imminent. Confirmation by an actual close through resistance, relative volume, market/sector regime, and risk controls should carry more weight.

## Point-in-time design

Each signal was evaluated after a completed daily bar. Features used only information then available. The resistance boundary was the maximum high of the prior 20 completed sessions, excluding the signal bar. A breakout required a later close above that stored boundary plus 0.10 ATR(14).

The baseline required:

- Price at least $10 and prior-63-session average volume at least 500,000 shares.
- Close above SMA(20), SMA(50), and SMA(200).
- Positive 21- and 63-session returns.
- Close between 0% and 3% below the prior 20-session high.

A new event was recorded when a tested condition became active, followed by a 20-session per-symbol cooldown. Returns entered at the next session's open. The reported net returns subtract 20 basis points round trip. Breakout acceptance required at least two closes over the buffered boundary within 10 sessions.

## Baseline

| Events | Cross in 5d | Cross in 10d | Accepted in 10d | Mean net 5d | Mean excess 5d | Mean excess 20d | Mean excess 60d |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3,293 | 49.29% | 62.80% | 54.87% | 0.01% | -0.19% | -0.28% | -0.59% |

Even the baseline did not outperform SPY on average. This matters: a higher breakout-crossing rate is not automatically a profitable trading edge.

## Candlestick results

All rows below include the baseline conditions plus the named candlestick.

| Pattern | Events | Cross in 5d | Lift vs baseline | Accepted in 10d | Mean excess 20d |
|---|---:|---:|---:|---:|---:|
| Marubozu White | 345 | 51.01% | +1.73 pp | 56.81% | +0.25% |
| Spinning Top White | 2,161 | 50.12% | +0.84 pp | 54.23% | -0.26% |
| Doji | 1,873 | 49.76% | +0.47 pp | 54.35% | -0.13% |
| Dragonfly Doji | 176 | 48.30% | -0.99 pp | 54.55% | -0.65% |
| Long Upper Shadow | 1,654 | 48.19% | -1.09 pp | 53.87% | -0.14% |
| Inverted Hammer | 1,384 | 47.18% | -2.10 pp | 53.32% | -0.24% |
| Spinning Top Black | 2,109 | 46.99% | -2.29 pp | 51.49% | -0.39% |
| Long Lower Shadow | 1,771 | 46.92% | -2.36 pp | 52.52% | -0.22% |
| Hammer | 1,545 | 46.73% | -2.56 pp | 52.88% | -0.34% |
| Gravestone Doji | 129 | 46.51% | -2.77 pp | 50.39% | -0.84% |
| Marubozu Black | 129 | 27.91% | -21.38 pp | 41.09% | -0.50% |

White marubozu was the only candle with a positive 20-session mean excess return, but that result was small (+0.25%), had a negative median excess return (-0.61%), and reversed to -0.97% mean excess by 60 sessions. It is not a robust standalone edge.

## Chart-pattern results

All rows below include the complete baseline plus the named chart approximation.

| Pattern | Events | Cross in 5d | Lift vs baseline | Accepted in 10d | Mean excess 20d |
|---|---:|---:|---:|---:|---:|
| TL Resistance | 3,016 | 51.76% | +2.47 pp | 56.23% | -0.36% |
| Wedge Up | 2,199 | 49.02% | -0.27 pp | 54.21% | -0.24% |
| Multiple Top | 901 | 47.95% | -1.34 pp | 54.27% | -0.31% |
| Double Top | 1,876 | 47.87% | -1.42 pp | 52.77% | -0.16% |
| Channel Up | 2,280 | 46.27% | -3.02 pp | 52.11% | -0.32% |
| Inverse Head & Shoulders | 412 | 45.39% | -3.89 pp | 50.00% | -0.89% |
| Horizontal S/R | 1,369 | 43.61% | -5.68 pp | 49.31% | -0.58% |
| Double Bottom | 321 | 43.30% | -5.99 pp | 48.60% | -0.34% |
| Channel | 603 | 41.46% | -7.83 pp | 48.42% | -1.03% |
| Multiple Bottom | 169 | 40.83% | -8.46 pp | 48.52% | -0.60% |
| Triangle Ascending | 860 | 40.81% | -8.48 pp | 46.63% | -0.67% |
| TL Support | 2,238 | 39.59% | -9.69 pp | 47.01% | -0.33% |
| Head & Shoulders | 272 | 37.13% | -12.15 pp | 43.38% | -1.31% |
| Channel Down | 273 | 35.16% | -14.13 pp | 43.59% | -0.16% |
| Wedge Down | 78 | 32.05% | -17.24 pp | 35.90% | -0.90% |
| Wedge | 278 | 31.65% | -17.64 pp | 42.81% | -0.05% |
| Triangle Descending | 278 | 25.90% | -23.39 pp | 33.81% | -0.92% |

Trend-line resistance increased the chance of a mechanical resistance cross, but did not improve economic returns: its mean excess returns were -0.22%, -0.36%, and -0.60% at 5, 20, and 60 sessions. That is a useful distinction between predicting a boundary crossing and predicting tradable alpha.

## Combined-pattern results

The combinations paired lower-shadow rejection candles or compression candles (doji/spinning top) with selected bullish structures. None beat the baseline crossing rate. The best was Horizontal S/R + lower rejection at 45.69% (-3.59 points); the worst was Wedge Down + lower rejection at 24.00% (-25.29 points). These combinations should not be promoted into production rules from this test.

## Interpretation

1. **Candlestick names add little information by themselves.** The candle's location, prior trend, volatility, volume, and confirmation matter more than its label.
2. **A resistance-like structure can predict a crossing without predicting alpha.** TL Resistance increased the mechanical crossing frequency, but returns did not beat SPY after costs.
3. **Some classical reversal structures are mismatched to this task.** Bottoming patterns can occur far from an immediate 20-day-high breakout and become weaker when forced into a near-high setup.
4. **Do not select the best row as a finished strategy.** Fifty-eight related groups were examined. Choosing the winner after seeing all results creates multiple-testing bias.

## What this test can and cannot establish

This is a reproducible exploratory backtest, not investment advice or a production-ready strategy validation. Important limitations are:

- The universe contains currently active stocks, creating survivorship and selection bias.
- Finviz does not publish its detector tolerances; these are transparent OHLCV approximations, not a reproduction of Finviz's proprietary labels.
- Daily bars cannot reconstruct an intraday screen or same-time relative volume.
- Events remain correlated across symbols and dates.
- Market impact, taxes, delistings, and gap-through-stop losses are not modeled.
- Results are in-sample across the whole window and are not corrected for trying many patterns.

Before production use, repeat the study on a point-in-time historical universe, freeze detector parameters, reserve an untouched out-of-sample period, cluster uncertainty by date, and test market/sector and relative-volume confirmation without selecting thresholds on the test set.

## Reproduction and proof of work

Run inside the backend container:

```shell
python manage.py backtest_candlestick_patterns \
  --benchmark SPY \
  --round-trip-cost-bps 20 \
  --output /tmp/candlestick_pattern_backtest.json
```

Artifacts:

- Raw machine-readable output: `output/research/candlestick_pattern_backtest.json`
- Pattern feature and detector implementation: `backend/analytics/pattern_backtest.py`
- Django command and reporting logic: `backend/apps/jobs/management/commands/backtest_candlestick_patterns.py`
- Unit tests: `backend/analytics/test_pattern_backtest.py`

Verification performed:

```text
ruff: all checks passed
pytest: 7 passed (pattern and existing breakout backtest suites)
```

