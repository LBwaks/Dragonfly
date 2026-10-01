from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any


def _normalized_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol cannot be empty")
    return normalized


def _normalized_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if not normalized:
        raise ValueError("provider cannot be empty")
    return normalized


@dataclass(frozen=True, slots=True)
class NormalizedInstrument:
    symbol: str
    name: str
    exchange: str
    asset_type: str
    currency: str
    provider_symbol: str
    is_active: bool
    provider: str
    raw_payload: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _normalized_symbol(self.symbol))
        object.__setattr__(self, "provider_symbol", _normalized_symbol(self.provider_symbol))
        object.__setattr__(self, "exchange", self.exchange.strip().upper())
        object.__setattr__(self, "provider", _normalized_provider(self.provider))
        if not self.name.strip() or not self.exchange:
            raise ValueError("instrument name and exchange cannot be empty")


@dataclass(frozen=True, slots=True)
class NormalizedInstrumentOverview:
    symbol: str
    sector: str
    industry: str
    price: Decimal | None
    market_cap: Decimal | None
    provider: str
    raw_payload: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _normalized_symbol(self.symbol))
        object.__setattr__(self, "provider", _normalized_provider(self.provider))
        if self.price is not None and self.price < 0:
            raise ValueError("price cannot be negative")


@dataclass(frozen=True, slots=True)
class NormalizedQuote:
    symbol: str
    price: Decimal
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    previous_close: Decimal | None
    timestamp: datetime
    provider: str
    raw_payload: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _normalized_symbol(self.symbol))
        object.__setattr__(self, "provider", _normalized_provider(self.provider))
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        object.__setattr__(self, "timestamp", self.timestamp.astimezone(UTC))
        if self.price < 0:
            raise ValueError("price cannot be negative")


@dataclass(frozen=True, slots=True)
class NormalizedCompanyProfile:
    symbol: str
    name: str
    exchange: str
    currency: str
    provider: str
    ipo_date: date | None = None
    market_cap: Decimal | None = None
    shares_outstanding: Decimal | None = None
    sector: str = ""
    industry: str = ""
    website: str = ""
    logo_url: str = ""
    raw_payload: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _normalized_symbol(self.symbol))
        object.__setattr__(self, "provider", _normalized_provider(self.provider))
        if not self.name.strip():
            raise ValueError("name cannot be empty")


@dataclass(frozen=True, slots=True)
class NormalizedDailyBar:
    symbol: str
    trading_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adjusted_close: Decimal | None
    volume: int
    provider: str
    raw_payload: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _normalized_symbol(self.symbol))
        object.__setattr__(self, "provider", _normalized_provider(self.provider))
        if self.volume < 0:
            raise ValueError("volume cannot be negative")
        if min(self.open, self.high, self.low, self.close) < 0:
            raise ValueError("OHLC prices cannot be negative")
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("high must be at least every other OHLC price")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("low must be at most every other OHLC price")


@dataclass(frozen=True, slots=True)
class NormalizedIntradayBar:
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    provider: str
    raw_payload: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _normalized_symbol(self.symbol))
        object.__setattr__(self, "provider", _normalized_provider(self.provider))
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        object.__setattr__(self, "timestamp", self.timestamp.astimezone(UTC))
        if self.volume < 0:
            raise ValueError("volume cannot be negative")
        if min(self.open, self.high, self.low, self.close) < 0:
            raise ValueError("OHLC prices cannot be negative")
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("high must be at least every other OHLC price")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("low must be at most every other OHLC price")
