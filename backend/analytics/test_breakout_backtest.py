from datetime import date, timedelta

from analytics.breakout_backtest import PriceBar, build_features, event_entry_positions, summarize


def _bars(closes):
    start = date(2020, 1, 1)
    return [
        PriceBar(
            trading_date=start + timedelta(days=index),
            open=close,
            high=close,
            low=close * 0.999,
            close=close,
            volume=1_000_000,
        )
        for index, close in enumerate(closes)
    ]


def test_near_breakout_uses_prior_high_and_completed_close():
    closes = [100 + index * 0.1 for index in range(260)]
    closes[-1] = max(closes[-21:-1]) * 0.998
    features = build_features(_bars(closes))
    assert features[-1].near_breakout is True
    assert features[-1].breakout_20d is False
    assert features[-1].confirmed_trigger is False


def test_breakout_is_distinct_from_near_filter():
    closes = [100 + index * 0.1 for index in range(260)]
    closes[-1] = max(closes[-21:-1]) * 1.01
    features = build_features(_bars(closes))
    assert features[-1].near_breakout is False
    assert features[-1].breakout_20d is True


def test_event_entries_require_transition_and_cooldown():
    closes = [100 + index * 0.1 for index in range(260)]
    features = build_features(_bars(closes))
    positions = event_entry_positions(features, attribute="breakout_20d", cooldown=20)
    assert len(positions) == 1


def test_summarize_reports_return_statistics():
    result = summarize([0.1, -0.05, 0.02])
    assert result["count"] == 3
    assert result["win_rate"] == 2 / 3
    assert result["median"] == 0.02
