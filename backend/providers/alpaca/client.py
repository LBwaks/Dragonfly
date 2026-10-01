import random
import time
from datetime import date, datetime
from typing import Any

import httpx

from providers.base import HistoricalBarProvider, IntradayBarProvider, SymbolUniverseProvider
from providers.capabilities import ProviderCapability
from providers.common import TokenBucketRateLimiter
from providers.errors import (
    ProviderAuthenticationError,
    ProviderInvalidSymbolError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

from .mapper import map_assets, map_bars, map_intraday_bars


class AlpacaProvider(HistoricalBarProvider, IntradayBarProvider, SymbolUniverseProvider):
    name = "alpaca"
    capabilities = frozenset(
        {
            ProviderCapability.SYMBOL_UNIVERSE,
            ProviderCapability.HISTORICAL_OHLCV,
            ProviderCapability.INTRADAY_OHLCV,
        }
    )
    retryable_statuses = {429, 500, 502, 503, 504}
    valid_adjustments = {"raw", "split", "dividend", "spin-off", "all"}
    valid_feeds = {"sip", "iex", "boats", "otc"}

    def __init__(
        self,
        api_key_id: str,
        api_secret_key: str,
        *,
        data_feed: str = "sip",
        adjustment: str = "all",
        assets_base_url: str = "https://paper-api.alpaca.markets",
        asset_exchanges: tuple[str, ...] = ("NASDAQ", "NYSE", "AMEX", "ARCA", "BATS"),
        client: httpx.Client | None = None,
        assets_client: httpx.Client | None = None,
        rate_limiter: TokenBucketRateLimiter | None = None,
        max_attempts: int = 5,
        sleeper=time.sleep,
    ) -> None:
        if not api_key_id or not api_secret_key:
            raise ProviderAuthenticationError(
                "Alpaca API key ID and secret key are required", provider=self.name
            )
        data_feed = data_feed.strip().lower()
        adjustment = adjustment.strip().lower()
        if data_feed not in self.valid_feeds:
            raise ValueError(f"Unsupported Alpaca data feed: {data_feed}")
        if adjustment not in self.valid_adjustments:
            raise ValueError(f"Unsupported Alpaca adjustment: {adjustment}")
        self.data_feed = data_feed
        self.adjustment = adjustment
        headers = {
            "APCA-API-KEY-ID": api_key_id,
            "APCA-API-SECRET-KEY": api_secret_key,
        }
        self.client = client or httpx.Client(
            base_url="https://data.alpaca.markets",
            headers=headers,
            timeout=30,
        )
        self.assets_client = assets_client or httpx.Client(
            base_url=assets_base_url.rstrip("/"), headers=headers, timeout=30
        )
        self.asset_exchanges = frozenset(exchange.upper() for exchange in asset_exchanges)
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(190)
        self.max_attempts = max_attempts
        self.sleeper = sleeper

    def _get(
        self,
        path: str,
        *,
        capability: ProviderCapability = ProviderCapability.HISTORICAL_OHLCV,
        client: httpx.Client | None = None,
        **params: Any,
    ) -> Any:
        capability_name = capability.value
        request_client = client or self.client
        for attempt in range(self.max_attempts):
            self.rate_limiter.acquire()
            try:
                response = request_client.get(path, params=params)
            except httpx.TimeoutException as exc:
                error = ProviderTimeoutError(
                    "Alpaca request timed out", provider=self.name, capability=capability_name
                )
                if attempt + 1 == self.max_attempts:
                    raise error from exc
                self._backoff(attempt)
                continue
            except httpx.TransportError as exc:
                error = ProviderUnavailableError(
                    "Alpaca transport failure", provider=self.name, capability=capability_name
                )
                if attempt + 1 == self.max_attempts:
                    raise error from exc
                self._backoff(attempt)
                continue

            if response.status_code in self.retryable_statuses:
                error_type = (
                    ProviderRateLimitError
                    if response.status_code == 429
                    else ProviderUnavailableError
                )
                error = error_type(
                    f"Alpaca returned HTTP {response.status_code}",
                    provider=self.name,
                    capability=capability_name,
                )
                if attempt + 1 == self.max_attempts:
                    raise error
                self._backoff(attempt)
                continue
            if response.status_code in {401, 403}:
                message = f"Alpaca returned HTTP {response.status_code}"
                if response.status_code == 403:
                    message = (
                        f"Alpaca denied access to the '{self.data_feed}' feed. "
                        "Use ALPACA_DATA_FEED=iex for the free plan or enable SIP access."
                    )
                raise ProviderAuthenticationError(
                    message,
                    provider=self.name,
                    capability=capability_name,
                )
            if response.status_code in {400, 404, 422}:
                raise ProviderInvalidSymbolError(
                    "Alpaca rejected the bars request",
                    provider=self.name,
                    capability=capability_name,
                )
            try:
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise ProviderUnavailableError(
                    "Invalid Alpaca response", provider=self.name, capability=capability_name
                ) from exc
            return payload
        raise AssertionError("unreachable")

    def get_daily_bars(self, symbol: str, start_date: date, end_date: date):
        symbol = symbol.strip().upper()
        if not symbol or start_date > end_date:
            raise ProviderInvalidSymbolError(
                "Invalid symbol or date range",
                provider=self.name,
                capability=ProviderCapability.HISTORICAL_OHLCV.value,
            )

        raw_bars: list[dict[str, Any]] = []
        page_token = None
        while True:
            params = {
                "timeframe": "1Day",
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "adjustment": self.adjustment,
                "feed": self.data_feed,
                "limit": 10_000,
            }
            if page_token:
                params["page_token"] = page_token
            payload = self._get(f"/v2/stocks/{symbol}/bars", **params)
            if not isinstance(payload, dict):
                raise ProviderUnavailableError(
                    "Invalid Alpaca bars response",
                    provider=self.name,
                    capability=ProviderCapability.HISTORICAL_OHLCV.value,
                )
            page = payload.get("bars", [])
            if not isinstance(page, list):
                raise ProviderUnavailableError(
                    "Invalid Alpaca bars response",
                    provider=self.name,
                    capability=ProviderCapability.HISTORICAL_OHLCV.value,
                )
            raw_bars.extend(page)
            page_token = payload.get("next_page_token")
            if not page_token:
                break
        return map_bars(symbol, raw_bars, adjusted=self.adjustment != "raw")

    def get_intraday_bars(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ):
        symbol = symbol.strip().upper()
        valid_timeframes = {"5Min", "15Min", "30Min", "1Hour", "4Hour"}
        if not symbol or timeframe not in valid_timeframes or start >= end:
            raise ProviderInvalidSymbolError(
                "Invalid symbol, timeframe, or date range",
                provider=self.name,
                capability=ProviderCapability.INTRADAY_OHLCV.value,
            )

        raw_bars: list[dict[str, Any]] = []
        page_token = None
        while True:
            params = {
                "timeframe": timeframe,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "adjustment": self.adjustment,
                "feed": self.data_feed,
                "limit": 10_000,
            }
            if page_token:
                params["page_token"] = page_token
            payload = self._get(f"/v2/stocks/{symbol}/bars", **params)
            if not isinstance(payload, dict) or not isinstance(payload.get("bars", []), list):
                raise ProviderUnavailableError(
                    "Invalid Alpaca intraday bars response",
                    provider=self.name,
                    capability=ProviderCapability.INTRADAY_OHLCV.value,
                )
            raw_bars.extend(payload.get("bars", []))
            page_token = payload.get("next_page_token")
            if not page_token:
                break
        return map_intraday_bars(symbol, raw_bars)

    def get_latest_bar(self, symbol: str):
        symbol = symbol.strip().upper()
        if not symbol:
            raise ProviderInvalidSymbolError(
                "Invalid symbol",
                provider=self.name,
                capability=ProviderCapability.INTRADAY_OHLCV.value,
            )
        payload = self._get(
            f"/v2/stocks/{symbol}/bars/latest",
            feed=self.data_feed,
        )
        raw_bar = payload.get("bar") if isinstance(payload, dict) else None
        if not isinstance(raw_bar, dict):
            raise ProviderUnavailableError(
                "Invalid Alpaca latest bar response",
                provider=self.name,
                capability=ProviderCapability.INTRADAY_OHLCV.value,
            )
        return map_intraday_bars(symbol, [raw_bar])[0]

    def get_symbol_universe(self):
        payload = self._get(
            "/v2/assets",
            capability=ProviderCapability.SYMBOL_UNIVERSE,
            client=self.assets_client,
            status="active",
            asset_class="us_equity",
        )
        if not isinstance(payload, list):
            raise ProviderUnavailableError(
                "Invalid Alpaca assets response",
                provider=self.name,
                capability=ProviderCapability.SYMBOL_UNIVERSE.value,
            )
        return map_assets(payload, self.asset_exchanges)

    def _backoff(self, attempt: int) -> None:
        self.sleeper((0.5 * (2**attempt)) + random.uniform(0, 0.1))
