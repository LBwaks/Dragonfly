from django.conf import settings

from .alpaca import AlpacaProvider
from .finnhub import FinnhubProvider
from .nasdaq import NasdaqProvider
from .registry import ProviderRegistry


def build_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry(settings.MARKET_DATA_PROVIDERS)
    registry.register(NasdaqProvider(verify_ssl=getattr(settings, "NASDAQ_VERIFY_SSL", True)))
    alpaca_key_id = getattr(settings, "ALPACA_API_KEY_ID", "")
    alpaca_secret = getattr(settings, "ALPACA_API_SECRET_KEY", "")
    if alpaca_key_id or alpaca_secret:
        registry.register(
            AlpacaProvider(
                alpaca_key_id,
                alpaca_secret,
                data_feed=getattr(settings, "ALPACA_DATA_FEED", "sip"),
                adjustment=getattr(settings, "ALPACA_ADJUSTMENT", "all"),
                assets_base_url=getattr(
                    settings, "ALPACA_ASSETS_BASE_URL", "https://paper-api.alpaca.markets"
                ),
                asset_exchanges=tuple(
                    getattr(
                        settings,
                        "ALPACA_ASSET_EXCHANGES",
                        ["NASDAQ", "NYSE", "AMEX", "ARCA", "BATS"],
                    )
                ),
            )
        )
    finnhub_key = getattr(settings, "FINNHUB_API_KEY", "")
    if finnhub_key:
        registry.register(FinnhubProvider(finnhub_key))
    return registry
