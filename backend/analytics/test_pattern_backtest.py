from datetime import date, timedelta

from analytics.breakout_backtest import PriceBar
from analytics.pattern_backtest import (
    accepted_within,
    build_pattern_features,
    crossed_within,
    detect_candles,
)


def _bar(index, *, open_, high, low, close, volume=1_000_000):
    return PriceBar(
        trading_date=date(2020, 1, 1) + timedelta(days=index),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def test_candlestick_geometry_is_deterministic():
    bars = [_bar(0, open_=10, high=10.1, low=9.9, close=10)]
    patterns = detect_candles(bars, 0, atr=0.2)
    assert "doji" in patterns
    assert "spinning_top_white" in patterns

    bars = [_bar(0, open_=10.8, high=11, low=9, close=10.9)]
    patterns = detect_candles(bars, 0, atr=1)
    assert "long_lower_shadow" in patterns
    assert "hammer" in patterns


def test_prior_pivot_is_not_contaminated_by_current_bar():
    bars = []
    for index in range(260):
        close = 100 + index * 0.1
        bars.append(_bar(index, open_=close, high=close, low=close * 0.999, close=close))
    prior_high = max(bar.high for bar in bars[-21:-1])
    bars[-1] = _bar(259, open_=prior_high, high=prior_high * 1.02, low=prior_high, close=prior_high)
    feature = build_pattern_features(bars)[-1]
    assert feature.pivot_20 == prior_high
    assert feature.near_20d_high is True


def test_crossing_and_acceptance_use_signal_pivot():
    bars = []
    for index in range(260):
        close = 100 + index * 0.1
        bars.append(_bar(index, open_=close, high=close, low=close * 0.999, close=close))
    features = build_pattern_features(bars)
    signal_position = len(features) - 3
    signal = features[signal_position]
    threshold = signal.pivot_20 + 0.1 * signal.atr_14
    for offset in (1, 2):
        source_index = signal.index + offset
        bars[source_index] = _bar(
            source_index,
            open_=threshold,
            high=threshold * 1.002,
            low=threshold * 0.999,
            close=threshold * 1.001,
        )
    features = build_pattern_features(bars)
    assert crossed_within(features, signal_position, 2)
    assert accepted_within(features, signal_position, 2)
