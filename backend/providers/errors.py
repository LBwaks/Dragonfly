class ProviderError(Exception):
    """Base error raised by market-data providers."""

    def __init__(self, message: str, *, provider: str, capability: str | None = None):
        super().__init__(message)
        self.provider = provider
        self.capability = capability


class ProviderConfigurationError(ProviderError):
    """Provider registration or routing is invalid."""


class ProviderNotFoundError(ProviderConfigurationError):
    """A configured provider has not been registered."""


class UnsupportedCapabilityError(ProviderConfigurationError):
    """A provider does not implement the requested capability."""


class ProviderRateLimitError(ProviderError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderAuthenticationError(ProviderError):
    pass


class ProviderInvalidSymbolError(ProviderError):
    pass


class ProviderUnavailableError(ProviderError):
    pass


class ProviderMappingError(ProviderError):
    pass
