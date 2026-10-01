import random
import time
from typing import Any

import httpx

from providers.base import (
    EarningsProvider,
    FilingProvider,
    FundamentalProvider,
    NewsProvider,
    QuoteProvider,
)
from providers.capabilities import ProviderCapability
from providers.common import TokenBucketRateLimiter
from providers.errors import (
    ProviderAuthenticationError,
    ProviderInvalidSymbolError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

from .mapper import map_company_profile, map_quote


class FinnhubProvider(
    QuoteProvider,
    FundamentalProvider,
    NewsProvider,
    FilingProvider,
    EarningsProvider,
):
    name = "finnhub"
    capabilities = frozenset(
        {
            ProviderCapability.QUOTE,
            ProviderCapability.COMPANY_PROFILE,
            ProviderCapability.FUNDAMENTALS,
            ProviderCapability.PEERS,
            ProviderCapability.COMPANY_NEWS,
            ProviderCapability.SEC_FILINGS,
            ProviderCapability.INSIDER_TRANSACTIONS,
            ProviderCapability.INSIDER_SENTIMENT,
            ProviderCapability.ANALYST_RECOMMENDATIONS,
            ProviderCapability.EARNINGS_HISTORY,
            ProviderCapability.EARNINGS_CALENDAR,
            ProviderCapability.IPO_CALENDAR,
        }
    )
    retryable_statuses = {429, 500, 502, 503, 504}

    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.Client | None = None,
        rate_limiter: TokenBucketRateLimiter | None = None,
        max_attempts: int = 5,
        sleeper=time.sleep,
    ) -> None:
        if not api_key:
            raise ProviderAuthenticationError("Finnhub API key is missing", provider=self.name)
        self.api_key = api_key
        self.client = client or httpx.Client(base_url="https://finnhub.io/api/v1", timeout=15)
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(55)
        self.max_attempts = max_attempts
        self.sleeper = sleeper

    def _get(self, path: str, capability: ProviderCapability, **params: Any) -> Any:
        params["token"] = self.api_key
        for attempt in range(self.max_attempts):
            self.rate_limiter.acquire()
            try:
                response = self.client.get(path, params=params)
            except httpx.TimeoutException as exc:
                error = ProviderTimeoutError(
                    "Finnhub request timed out",
                    provider=self.name,
                    capability=capability.value,
                )
                if attempt + 1 == self.max_attempts:
                    raise error from exc
                self._backoff(attempt)
                continue
            except httpx.TransportError as exc:
                error = ProviderUnavailableError(
                    "Finnhub transport failure",
                    provider=self.name,
                    capability=capability.value,
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
                    f"Finnhub returned HTTP {response.status_code}",
                    provider=self.name,
                    capability=capability.value,
                )
                if attempt + 1 == self.max_attempts:
                    raise error
                self._backoff(attempt)
                continue
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    f"Finnhub returned HTTP {response.status_code}",
                    provider=self.name,
                    capability=capability.value,
                )
            if response.status_code == 400:
                raise ProviderInvalidSymbolError(
                    "Finnhub rejected the request",
                    provider=self.name,
                    capability=capability.value,
                )
            try:
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise ProviderUnavailableError(
                    "Invalid Finnhub response",
                    provider=self.name,
                    capability=capability.value,
                ) from exc
        raise AssertionError("unreachable")

    def _backoff(self, attempt: int) -> None:
        self.sleeper((0.5 * (2**attempt)) + random.uniform(0, 0.1))

    def get_quote(self, symbol):
        return map_quote(symbol, self._get("/quote", ProviderCapability.QUOTE, symbol=symbol))

    def get_company_profile(self, symbol):
        payload = self._get("/stock/profile2", ProviderCapability.COMPANY_PROFILE, symbol=symbol)
        return map_company_profile(symbol, payload)

    def get_fundamentals(self, symbol):
        return self._get(
            "/stock/metric", ProviderCapability.FUNDAMENTALS, symbol=symbol, metric="all"
        )

    def get_company_news(self, symbol, start_date, end_date):
        return self._get(
            "/company-news",
            ProviderCapability.COMPANY_NEWS,
            symbol=symbol,
            **{"from": start_date.isoformat(), "to": end_date.isoformat()},
        )

    def get_filings(self, symbol, start_date=None, end_date=None):
        params = {"symbol": symbol}
        if start_date:
            params["from"] = start_date.isoformat()
        if end_date:
            params["to"] = end_date.isoformat()
        return self._get("/stock/filings", ProviderCapability.SEC_FILINGS, **params)

    def get_earnings_history(self, symbol):
        return self._get("/stock/earnings", ProviderCapability.EARNINGS_HISTORY, symbol=symbol)

    def get_company_peers(self, symbol):
        return self._get("/stock/peers", ProviderCapability.PEERS, symbol=symbol)

    def get_recommendation_trends(self, symbol):
        return self._get(
            "/stock/recommendation", ProviderCapability.ANALYST_RECOMMENDATIONS, symbol=symbol
        )

    def get_insider_transactions(self, symbol, start_date=None, end_date=None):
        return self._get(
            "/stock/insider-transactions",
            ProviderCapability.INSIDER_TRANSACTIONS,
            symbol=symbol,
        )

    def get_insider_sentiment(self, symbol, start_date=None, end_date=None):
        return self._get(
            "/stock/insider-sentiment",
            ProviderCapability.INSIDER_SENTIMENT,
            symbol=symbol,
            **{
                "from": start_date.isoformat() if start_date else "",
                "to": end_date.isoformat() if end_date else "",
            },
        )

    def get_earnings_calendar(self, start_date, end_date):
        return self._get(
            "/calendar/earnings",
            ProviderCapability.EARNINGS_CALENDAR,
            **{"from": start_date.isoformat(), "to": end_date.isoformat()},
        )

    def get_ipo_calendar(self, start_date, end_date):
        return self._get(
            "/calendar/ipo",
            ProviderCapability.IPO_CALENDAR,
            **{"from": start_date.isoformat(), "to": end_date.isoformat()},
        )
