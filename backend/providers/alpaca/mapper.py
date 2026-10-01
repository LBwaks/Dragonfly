from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from providers.errors import ProviderMappingError
from providers.models import NormalizedDailyBar, NormalizedInstrument, NormalizedIntradayBar


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"invalid decimal: {value}") from exc


def map_bars(
    symbol: str,
    payload: list[dict[str, Any]],
    *,
    adjusted: bool,
) -> tuple[NormalizedDailyBar, ...]:
    bars = []
    try:
        for item in payload:
            close = _decimal(item["c"])
            bars.append(
                NormalizedDailyBar(
                    symbol=symbol,
                    trading_date=datetime.fromisoformat(item["t"].replace("Z", "+00:00")).date(),
                    open=_decimal(item["o"]),
                    high=_decimal(item["h"]),
                    low=_decimal(item["l"]),
                    close=close,
                    adjusted_close=close if adjusted else None,
                    volume=int(item["v"]),
                    provider="alpaca",
                    raw_payload=item,
                )
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderMappingError(
            "Invalid Alpaca bars response",
            provider="alpaca",
            capability="historical_ohlcv",
        ) from exc
    return tuple(bars)


def map_intraday_bars(
    symbol: str, payload: list[dict[str, Any]]
) -> tuple[NormalizedIntradayBar, ...]:
    bars = []
    try:
        for item in payload:
            bars.append(
                NormalizedIntradayBar(
                    symbol=symbol,
                    timestamp=datetime.fromisoformat(item["t"].replace("Z", "+00:00")),
                    open=_decimal(item["o"]),
                    high=_decimal(item["h"]),
                    low=_decimal(item["l"]),
                    close=_decimal(item["c"]),
                    volume=int(item["v"]),
                    provider="alpaca",
                    raw_payload=item,
                )
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderMappingError(
            "Invalid Alpaca intraday bars response",
            provider="alpaca",
            capability="intraday_ohlcv",
        ) from exc
    return tuple(bars)


def map_assets(
    payload: list[dict[str, Any]], allowed_exchanges: frozenset[str]
) -> tuple[NormalizedInstrument, ...]:
    instruments = []
    try:
        for item in payload:
            exchange = str(item.get("exchange", "")).strip().upper()
            if (
                item.get("class") != "us_equity"
                or item.get("status") != "active"
                or not item.get("tradable")
                or exchange not in allowed_exchanges
            ):
                continue
            symbol = str(item["symbol"]).strip().upper()
            instruments.append(
                NormalizedInstrument(
                    symbol=symbol,
                    name=str(item.get("name") or symbol).strip(),
                    exchange=exchange,
                    asset_type="stock",
                    currency="USD",
                    provider_symbol=symbol,
                    is_active=True,
                    provider="alpaca",
                    raw_payload=item,
                )
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderMappingError(
            "Invalid Alpaca assets response",
            provider="alpaca",
            capability="symbol_universe",
        ) from exc
    return tuple(instruments)
