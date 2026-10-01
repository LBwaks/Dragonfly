from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .base import MarketDataProvider
from .capabilities import ProviderCapability
from .errors import (
    ProviderConfigurationError,
    ProviderNotFoundError,
    UnsupportedCapabilityError,
)


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    name: str
    registered: bool
    capabilities: tuple[str, ...]


class ProviderRegistry:
    def __init__(
        self,
        routes: Mapping[ProviderCapability | str, Sequence[str] | str] | None = None,
    ) -> None:
        self._providers: dict[str, MarketDataProvider] = {}
        self._routes = self._normalize_routes(routes or {})

    @staticmethod
    def _capability(value: ProviderCapability | str) -> ProviderCapability:
        try:
            return ProviderCapability(value)
        except ValueError as exc:
            raise ProviderConfigurationError(
                f"Unknown provider capability: {value}",
                provider="registry",
                capability=str(value),
            ) from exc

    @classmethod
    def _normalize_routes(
        cls, routes: Mapping[ProviderCapability | str, Sequence[str] | str]
    ) -> dict[ProviderCapability, tuple[str, ...]]:
        normalized: dict[ProviderCapability, tuple[str, ...]] = {}
        for raw_capability, raw_names in routes.items():
            capability = cls._capability(raw_capability)
            names = (raw_names,) if isinstance(raw_names, str) else tuple(raw_names)
            cleaned = tuple(name.strip().lower() for name in names if name.strip())
            if not cleaned:
                raise ProviderConfigurationError(
                    "A provider route cannot be empty",
                    provider="registry",
                    capability=capability.value,
                )
            normalized[capability] = cleaned
        return normalized

    def register(self, provider: MarketDataProvider) -> None:
        name = provider.name.strip().lower()
        if not name:
            raise ProviderConfigurationError("Provider name cannot be empty", provider="registry")
        if name in self._providers:
            raise ProviderConfigurationError(
                f"Provider '{name}' is already registered", provider=name
            )
        self._providers[name] = provider

    def _resolve_route(self, capability: ProviderCapability) -> tuple[str, ...]:
        configured = self._routes.get(capability)
        if configured:
            return configured
        return tuple(
            name for name, provider in self._providers.items() if provider.supports(capability)
        )

    def get_provider(self, capability: ProviderCapability | str) -> MarketDataProvider:
        normalized = self._capability(capability)
        route = self._resolve_route(normalized)
        if not route:
            raise ProviderNotFoundError(
                f"No provider is configured for '{normalized.value}'",
                provider="registry",
                capability=normalized.value,
            )
        return self._get_supported(route[0], normalized)

    def get_fallback_providers(
        self, capability: ProviderCapability | str
    ) -> tuple[MarketDataProvider, ...]:
        normalized = self._capability(capability)
        return tuple(
            self._get_supported(name, normalized) for name in self._resolve_route(normalized)[1:]
        )

    def _get_supported(self, name: str, capability: ProviderCapability) -> MarketDataProvider:
        provider = self._providers.get(name)
        if provider is None:
            raise ProviderNotFoundError(
                f"Provider '{name}' is not registered",
                provider=name,
                capability=capability.value,
            )
        if not provider.supports(capability):
            raise UnsupportedCapabilityError(
                f"Provider '{name}' does not support '{capability.value}'",
                provider=name,
                capability=capability.value,
            )
        return provider

    def provider_supports(self, provider: str, capability: ProviderCapability | str) -> bool:
        instance = self._providers.get(provider.strip().lower())
        return bool(instance and instance.supports(self._capability(capability)))

    def get_provider_health(self, provider: str) -> ProviderHealth:
        name = provider.strip().lower()
        instance = self._providers.get(name)
        return ProviderHealth(
            name=name,
            registered=instance is not None,
            capabilities=tuple(sorted(capability.value for capability in instance.capabilities))
            if instance
            else (),
        )
