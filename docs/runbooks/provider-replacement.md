# Provider replacement

1. Implement the canonical capability interfaces and declare supported capabilities.
2. Add credentials through environment variables locally and Secret Manager in production.
3. Run adapter contract tests with mocked HTTP responses.
4. Compare normalized rows against the existing provider in staging.
5. Add the provider after the primary name in the capability route.
6. Observe failures and freshness, then promote it to the first route position.
7. Retain the previous provider as fallback through the migration window.

No technical, screener, REST, or frontend field names may change during replacement.

Current historical route:

```dotenv
OHLCV_PROVIDERS=alpaca
```

To add a fallback, register its adapter in `providers.runtime.build_provider_registry` and append its name to the route. Authentication and mapping failures require operator action and are not silently routed around; transient rate-limit, timeout, and availability failures may use the next configured provider.
