from .capabilities import ProviderCapability
from .errors import (
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

RETRYABLE = (ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError)


def call_with_fallback(registry, capability: ProviderCapability, method: str, *args, **kwargs):
    providers = (registry.get_provider(capability), *registry.get_fallback_providers(capability))
    last_error = None
    for provider in providers:
        try:
            return getattr(provider, method)(*args, **kwargs)
        except RETRYABLE as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("No provider attempted")
