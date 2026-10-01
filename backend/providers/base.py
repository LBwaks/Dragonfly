from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date, datetime
from typing import Any, ClassVar

from .capabilities import ProviderCapability
from .models import (
    NormalizedCompanyProfile,
    NormalizedDailyBar,
    NormalizedInstrument,
    NormalizedInstrumentOverview,
    NormalizedIntradayBar,
    NormalizedQuote,
)


class MarketDataProvider(ABC):
    name: ClassVar[str]
    capabilities: ClassVar[frozenset[ProviderCapability]] = frozenset()

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities


class SymbolUniverseProvider(MarketDataProvider):
    @abstractmethod
    def get_symbol_universe(self) -> Iterable[NormalizedInstrument]:
        raise NotImplementedError


class InstrumentOverviewProvider(MarketDataProvider):
    @abstractmethod
    def get_instrument_overviews(self) -> Iterable[NormalizedInstrumentOverview]:
        raise NotImplementedError


class QuoteProvider(MarketDataProvider):
    @abstractmethod
    def get_quote(self, symbol: str) -> NormalizedQuote:
        raise NotImplementedError

    @abstractmethod
    def get_company_profile(self, symbol: str) -> NormalizedCompanyProfile:
        raise NotImplementedError


class HistoricalBarProvider(MarketDataProvider):
    @abstractmethod
    def get_daily_bars(
        self, symbol: str, start_date: date, end_date: date
    ) -> Iterable[NormalizedDailyBar]:
        raise NotImplementedError


class IntradayBarProvider(MarketDataProvider):
    @abstractmethod
    def get_latest_bar(self, symbol: str) -> NormalizedIntradayBar:
        raise NotImplementedError

    @abstractmethod
    def get_intraday_bars(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Iterable[NormalizedIntradayBar]:
        raise NotImplementedError


class FundamentalProvider(MarketDataProvider):
    @abstractmethod
    def get_fundamentals(self, symbol: str) -> Any:
        raise NotImplementedError


class NewsProvider(MarketDataProvider):
    @abstractmethod
    def get_company_news(self, symbol: str, start_date: date, end_date: date) -> Any:
        raise NotImplementedError


class FilingProvider(MarketDataProvider):
    @abstractmethod
    def get_filings(
        self, symbol: str, start_date: date | None = None, end_date: date | None = None
    ) -> Any:
        raise NotImplementedError


class EarningsProvider(MarketDataProvider):
    @abstractmethod
    def get_earnings_history(self, symbol: str) -> Any:
        raise NotImplementedError
