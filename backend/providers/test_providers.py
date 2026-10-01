from datetime import UTC, date, datetime
from decimal import Decimal

import httpx
import pytest
from django.test import override_settings

from providers.alpaca import AlpacaProvider
from providers.base import HistoricalBarProvider, QuoteProvider
from providers.capabilities import ProviderCapability
from providers.common import TokenBucketRateLimiter
from providers.errors import (
    ProviderConfigurationError,
    ProviderNotFoundError,
    UnsupportedCapabilityError,
)
from providers.models import NormalizedDailyBar, NormalizedQuote
from providers.nasdaq import NasdaqProvider
from providers.registry import ProviderRegistry
from providers.runtime import build_provider_registry


class FakeQuoteProvider(QuoteProvider):
    capabilities = frozenset({ProviderCapability.QUOTE, ProviderCapability.COMPANY_PROFILE})

    def __init__(self, name: str):
        self.name = name

    def get_quote(self, symbol):
        return NormalizedQuote(
            symbol=symbol,
            price=Decimal("100"),
            open=Decimal("99"),
            high=Decimal("101"),
            low=Decimal("98"),
            previous_close=Decimal("98.50"),
            timestamp=datetime(2026, 9, 11, 20, tzinfo=UTC),
            provider=self.name,
        )

    def get_company_profile(self, symbol):
        raise NotImplementedError


class FakeBarProvider(HistoricalBarProvider):
    name = "bars"
    capabilities = frozenset({ProviderCapability.HISTORICAL_OHLCV})

    def get_daily_bars(self, symbol, start_date, end_date):
        return ()


def test_normalized_quote_canonicalizes_identity_and_timestamp():
    timestamp = datetime(2026, 9, 11, 16, tzinfo=UTC)
    quote = NormalizedQuote(
        symbol=" nvda ",
        price=Decimal("177.82"),
        open=None,
        high=None,
        low=None,
        previous_close=None,
        timestamp=timestamp,
        provider=" FinnHub ",
    )
    assert quote.symbol == "NVDA"
    assert quote.provider == "finnhub"
    assert quote.timestamp.tzinfo is UTC


def test_normalized_daily_bar_rejects_invalid_ohlcv():
    with pytest.raises(ValueError, match="high"):
        NormalizedDailyBar(
            symbol="AMD",
            trading_date=date(2026, 9, 11),
            open=Decimal("100"),
            high=Decimal("99"),
            low=Decimal("98"),
            close=Decimal("100"),
            adjusted_close=None,
            volume=1_000,
            provider="mock",
        )


def test_registry_routes_primary_and_fallback_in_configured_order():
    primary = FakeQuoteProvider("primary")
    fallback = FakeQuoteProvider("fallback")
    registry = ProviderRegistry({ProviderCapability.QUOTE: ["primary", "fallback"]})
    registry.register(fallback)
    registry.register(primary)

    assert registry.get_provider("quote") is primary
    assert registry.get_fallback_providers("quote") == (fallback,)
    assert registry.provider_supports("primary", "company_profile")


def test_registry_falls_back_to_registration_order_without_a_route():
    registry = ProviderRegistry()
    quotes = FakeQuoteProvider("quotes")
    bars = FakeBarProvider()
    registry.register(quotes)
    registry.register(bars)

    assert registry.get_provider("historical_ohlcv") is bars
    assert registry.get_provider("quote") is quotes


def test_registry_rejects_invalid_registration_and_routes():
    registry = ProviderRegistry({"quote": "missing"})
    with pytest.raises(ProviderNotFoundError):
        registry.get_provider("quote")

    registry = ProviderRegistry({"quote": "bars"})
    registry.register(FakeBarProvider())
    with pytest.raises(UnsupportedCapabilityError):
        registry.get_provider("quote")

    duplicate = ProviderRegistry()
    duplicate.register(FakeQuoteProvider("same"))
    with pytest.raises(ProviderConfigurationError, match="already registered"):
        duplicate.register(FakeQuoteProvider("same"))


def test_provider_health_does_not_perform_external_io():
    registry = ProviderRegistry()
    registry.register(FakeBarProvider())

    health = registry.get_provider_health("bars")
    assert health.registered is True
    assert health.capabilities == ("historical_ohlcv",)
    assert registry.get_provider_health("unknown").registered is False


def test_alpaca_bars_are_paginated_authenticated_and_normalized():
    requests = []

    def handler(request):
        requests.append(request)
        assert request.headers["APCA-API-KEY-ID"] == "key-id"
        assert request.headers["APCA-API-SECRET-KEY"] == "secret"
        assert request.url.params["timeframe"] == "1Day"
        assert request.url.params["adjustment"] == "all"
        assert request.url.params["feed"] == "sip"
        if "page_token" not in request.url.params:
            return httpx.Response(
                200,
                json={
                    "bars": [
                        {
                            "t": "2026-09-10T04:00:00Z",
                            "o": 100,
                            "h": 105,
                            "l": 99,
                            "c": 104,
                            "v": 1000,
                        }
                    ],
                    "next_page_token": "next",
                },
            )
        assert request.url.params["page_token"] == "next"
        return httpx.Response(
            200,
            json={
                "bars": [
                    {"t": "2026-09-11T04:00:00Z", "o": 104, "h": 108, "l": 103, "c": 107, "v": 1200}
                ],
                "next_page_token": None,
            },
        )

    provider = AlpacaProvider(
        "key-id",
        "secret",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://data.alpaca.test",
            headers={
                "APCA-API-KEY-ID": "key-id",
                "APCA-API-SECRET-KEY": "secret",
            },
        ),
        rate_limiter=TokenBucketRateLimiter(100_000),
    )

    bars = provider.get_daily_bars(" aapl ", date(2026, 9, 10), date(2026, 9, 11))

    assert len(requests) == 2
    assert [bar.trading_date for bar in bars] == [date(2026, 9, 10), date(2026, 9, 11)]
    assert bars[0].symbol == "AAPL"
    assert bars[0].provider == "alpaca"
    assert bars[0].adjusted_close == Decimal("104")


def test_alpaca_intraday_bars_preserve_timestamp_and_timeframe():
    def handler(request):
        assert request.url.params["timeframe"] == "15Min"
        return httpx.Response(
            200,
            json={
                "bars": [
                    {
                        "t": "2026-09-25T14:30:00Z",
                        "o": 100,
                        "h": 102,
                        "l": 99,
                        "c": 101,
                        "v": 1200,
                    }
                ],
                "next_page_token": None,
            },
        )

    provider = AlpacaProvider(
        "key-id",
        "secret",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://data.alpaca.test",
        ),
        rate_limiter=TokenBucketRateLimiter(100_000),
    )
    bars = provider.get_intraday_bars(
        "AAPL",
        "15Min",
        datetime(2026, 9, 25, 13, tzinfo=UTC),
        datetime(2026, 9, 25, 20, tzinfo=UTC),
    )

    assert len(bars) == 1
    assert bars[0].timestamp == datetime(2026, 9, 25, 14, 30, tzinfo=UTC)
    assert bars[0].close == Decimal("101")


def test_alpaca_latest_bar_returns_live_price_timestamp():
    def handler(request):
        assert request.url.path.endswith("/v2/stocks/AMD/bars/latest")
        assert request.url.params["feed"] == "iex"
        return httpx.Response(
            200,
            json={
                "bar": {
                    "t": "2026-10-01T19:59:00Z",
                    "o": 612,
                    "h": 614,
                    "l": 611,
                    "c": 613,
                    "v": 4200,
                }
            },
        )

    provider = AlpacaProvider(
        "key-id",
        "secret",
        data_feed="iex",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://data.alpaca.test",
        ),
        rate_limiter=TokenBucketRateLimiter(100_000),
    )
    bar = provider.get_latest_bar("amd")

    assert bar.close == Decimal("613")
    assert bar.timestamp == datetime(2026, 10, 1, 19, 59, tzinfo=UTC)


def test_alpaca_symbol_universe_filters_and_normalizes_active_us_assets():
    def handler(request):
        assert request.headers["APCA-API-KEY-ID"] == "key-id"
        assert request.url.params["status"] == "active"
        assert request.url.params["asset_class"] == "us_equity"
        return httpx.Response(
            200,
            json=[
                {
                    "class": "us_equity",
                    "status": "active",
                    "tradable": True,
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "exchange": "NASDAQ",
                },
                {
                    "class": "us_equity",
                    "status": "active",
                    "tradable": True,
                    "symbol": "OTCM",
                    "name": "OTC Markets Group",
                    "exchange": "OTC",
                },
                {
                    "class": "us_equity",
                    "status": "inactive",
                    "tradable": False,
                    "symbol": "OLD",
                    "name": "Old Corp",
                    "exchange": "NYSE",
                },
            ],
        )

    assets_client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://paper-api.alpaca.test",
        headers={"APCA-API-KEY-ID": "key-id", "APCA-API-SECRET-KEY": "secret"},
    )
    provider = AlpacaProvider("key-id", "secret", assets_client=assets_client)

    instruments = provider.get_symbol_universe()

    assert len(instruments) == 1
    assert instruments[0].symbol == "AAPL"
    assert instruments[0].name == "Apple Inc."
    assert instruments[0].exchange == "NASDAQ"
    assert instruments[0].provider == "alpaca"


def test_nasdaq_overview_normalizes_sector_and_price():
    def handler(request):
        assert request.url.params["download"] == "true"
        return httpx.Response(
            200,
            json={
                "data": {
                    "rows": [
                        {
                            "symbol": "AAPL",
                            "sector": "Technology",
                            "industry": "Computer Manufacturing",
                            "lastsale": "$250.12",
                            "marketCap": "3750000000000",
                        }
                    ]
                }
            },
        )

    provider = NasdaqProvider(
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.nasdaq.test"
        )
    )
    overview = provider.get_instrument_overviews()[0]

    assert overview.symbol == "AAPL"
    assert overview.sector == "Technology"
    assert overview.price == Decimal("250.12")


@override_settings(
    MARKET_DATA_PROVIDERS={"historical_ohlcv": ["alpaca"], "quote": ["finnhub"]},
    ALPACA_API_KEY_ID="alpaca-id",
    ALPACA_API_SECRET_KEY="alpaca-secret",
    ALPACA_DATA_FEED="sip",
    ALPACA_ADJUSTMENT="all",
    FINNHUB_API_KEY="finnhub-key",
)
def test_runtime_registry_routes_capabilities_to_distinct_providers():
    registry = build_provider_registry()

    assert registry.get_provider("historical_ohlcv").name == "alpaca"
    assert registry.get_provider("symbol_universe").name == "alpaca"
    assert registry.get_provider("quote").name == "finnhub"
    assert not registry.provider_supports("finnhub", "historical_ohlcv")
