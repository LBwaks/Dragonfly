from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from providers.errors import ProviderMappingError
from providers.models import NormalizedCompanyProfile, NormalizedQuote


def _decimal(value: Any, *, nullable: bool = True) -> Decimal | None:
    if value in (None, ""):
        if nullable:
            return None
        raise ValueError("value is required")
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"invalid decimal: {value}") from exc


def map_quote(symbol: str, payload: dict[str, Any]) -> NormalizedQuote:
    try:
        timestamp = datetime.fromtimestamp(int(payload["t"]), tz=UTC)
        return NormalizedQuote(
            symbol=symbol,
            price=_decimal(payload["c"], nullable=False),
            open=_decimal(payload.get("o")),
            high=_decimal(payload.get("h")),
            low=_decimal(payload.get("l")),
            previous_close=_decimal(payload.get("pc")),
            timestamp=timestamp,
            provider="finnhub",
            raw_payload=payload,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderMappingError(
            "Invalid Finnhub quote response", provider="finnhub", capability="quote"
        ) from exc


def map_company_profile(symbol: str, payload: dict[str, Any]) -> NormalizedCompanyProfile:
    try:
        ipo_date = date.fromisoformat(payload["ipo"]) if payload.get("ipo") else None
        return NormalizedCompanyProfile(
            symbol=symbol,
            name=payload["name"],
            exchange=payload.get("exchange", ""),
            currency=payload.get("currency", "USD"),
            provider="finnhub",
            ipo_date=ipo_date,
            market_cap=_decimal(payload.get("marketCapitalization")),
            shares_outstanding=_decimal(payload.get("shareOutstanding")),
            sector=payload.get("finnhubIndustry", ""),
            website=payload.get("weburl", ""),
            logo_url=payload.get("logo", ""),
            raw_payload=payload,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderMappingError(
            "Invalid Finnhub company profile response",
            provider="finnhub",
            capability="company_profile",
        ) from exc
