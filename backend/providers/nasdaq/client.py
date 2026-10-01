from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from providers.base import InstrumentOverviewProvider
from providers.capabilities import ProviderCapability
from providers.errors import ProviderUnavailableError
from providers.models import NormalizedInstrumentOverview


class NasdaqProvider(InstrumentOverviewProvider):
    name = "nasdaq"
    capabilities = frozenset({ProviderCapability.INSTRUMENT_OVERVIEW})

    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        verify_ssl: bool = True,
    ) -> None:
        self.client = client or httpx.Client(
            base_url="https://api.nasdaq.com",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://www.nasdaq.com",
                "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
            },
            timeout=45,
            verify=verify_ssl,
        )

    @staticmethod
    def _decimal(value: Any) -> Decimal | None:
        if value in (None, "", "N/A", "--"):
            return None
        cleaned = str(value).replace("$", "").replace(",", "").strip()
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError) as exc:
            raise ProviderUnavailableError(
                "Invalid Nasdaq numeric value",
                provider="nasdaq",
                capability=ProviderCapability.INSTRUMENT_OVERVIEW.value,
            ) from exc

    def get_instrument_overviews(self):
        try:
            response = self.client.get(
                "/api/screener/stocks",
                params={"tableonly": "true", "limit": 25, "offset": 0, "download": "true"},
            )
            response.raise_for_status()
            rows = response.json()["data"]["rows"]
            return tuple(
                NormalizedInstrumentOverview(
                    symbol=row["symbol"],
                    sector=(row.get("sector") or "").strip(),
                    industry=(row.get("industry") or "").strip(),
                    price=self._decimal(row.get("lastsale")),
                    market_cap=self._decimal(row.get("marketCap")),
                    provider=self.name,
                    raw_payload=row,
                )
                for row in rows
                if row.get("symbol")
            )
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise ProviderUnavailableError(
                "Nasdaq instrument overview request failed",
                provider=self.name,
                capability=ProviderCapability.INSTRUMENT_OVERVIEW.value,
            ) from exc
