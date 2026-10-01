from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace

import httpx
import pytest

from analytics import calculate_technicals
from apps.instruments.models import Instrument
from apps.market_data.models import DailyBar
from apps.market_data.services import upsert_daily_bars
from apps.screeners.dsl import RuleValidationError, matches_rules, validate_rules
from apps.screeners.models import ScreeningSnapshot, TradeSignal
from apps.screeners.signals import generate_signals_for_instrument
from providers.common import TokenBucketRateLimiter
from providers.finnhub.client import FinnhubProvider
from providers.models import NormalizedDailyBar


def test_analytics_are_deterministic():
    rows = [
        {
            "trading_date": date(2025, 1, 1),
            "open": 100 + index,
            "high": 102 + index,
            "low": 99 + index,
            "close": 101 + index,
            "adjusted_close": 101 + index,
            "volume": 1000 + index,
        }
        for index in range(260)
    ]
    first = calculate_technicals(rows)
    second = calculate_technicals(rows)
    assert first == second
    assert first[-1]["sma_200"] == pytest.approx(260.5)
    assert first[-1]["return_20d"] > 0


def test_dsl_rejects_injection_and_detects_one_time_crossovers():
    with pytest.raises(RuleValidationError):
        validate_rules(
            {
                "logic": "AND",
                "conditions": [{"left": "close; DROP TABLE", "operator": ">", "value": 0}],
            }
        )
    rule = {
        "logic": "AND",
        "conditions": [{"left": "sma_50", "operator": "crosses_above", "right_field": "sma_200"}],
    }
    assert matches_rules(
        rule,
        SimpleNamespace(sma_50=201, sma_200=200),
        SimpleNamespace(sma_50=199, sma_200=200),
    )
    assert not matches_rules(
        rule,
        SimpleNamespace(sma_50=202, sma_200=200),
        SimpleNamespace(sma_50=201, sma_200=200),
    )


@pytest.mark.django_db
def test_daily_bar_upsert_is_idempotent():
    instrument = Instrument.objects.create(symbol="ARM", name="Arm", exchange="NASDAQ")
    bar = NormalizedDailyBar(
        symbol="ARM",
        trading_date=date(2026, 9, 11),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("99"),
        close=Decimal("104"),
        adjusted_close=Decimal("104"),
        volume=1000,
        provider="test",
    )
    assert upsert_daily_bars(instrument, [bar]) == (1, 0)
    assert upsert_daily_bars(instrument, [bar]) == (0, 1)
    assert instrument.daily_bars.count() == 1


def test_finnhub_quote_is_mocked_and_normalized():
    def handler(request):
        assert request.url.params["token"] == "secret"
        return httpx.Response(
            200,
            json={
                "c": 177.82,
                "o": 175,
                "h": 180,
                "l": 174,
                "pc": 176,
                "t": int(datetime(2026, 9, 11, tzinfo=UTC).timestamp()),
            },
        )

    provider = FinnhubProvider(
        "secret",
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://finnhub.test"
        ),
        rate_limiter=TokenBucketRateLimiter(100000),
    )
    quote = provider.get_quote("nvda")
    assert quote.symbol == "NVDA"
    assert quote.provider == "finnhub"


@pytest.mark.django_db
def test_trade_signals_classify_all_three_horizons():
    instrument = Instrument.objects.create(symbol="TEST", name="Test", exchange="NASDAQ")
    start = date(2025, 1, 1)
    DailyBar.objects.bulk_create(
        [
            DailyBar(
                instrument=instrument,
                trading_date=start.fromordinal(start.toordinal() + index),
                open=100 + index / 10,
                high=102 + index / 10,
                low=99 + index / 10,
                close=101 + index / 10,
                adjusted_close=101 + index / 10,
                volume=1_000_000,
                provider="test",
            )
            for index in range(260)
        ]
    )
    ScreeningSnapshot.objects.create(
        instrument=instrument,
        market_date=date(2025, 9, 17),
        close=126.9,
        sma_20=126,
        sma_50=124,
        sma_200=115,
        rsi_14=62,
        macd=2,
        macd_signal=1,
        return_5d=0.02,
        return_20d=0.08,
        return_50d=0.15,
    )

    signals = generate_signals_for_instrument(instrument)

    assert len(signals) == 3
    assert {signal.horizon for signal in signals} == {"DAILY", "WEEKLY", "MONTHLY"}
    assert all(0 <= signal.score <= 100 for signal in signals)
    assert TradeSignal.objects.filter(instrument=instrument).count() == 3
