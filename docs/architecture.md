# Dragonfly architecture

External APIs are isolated behind capability-based provider adapters. Ingestion normalizes and persists data in PostgreSQL; analytics and screeners read only canonical database records. Django management commands run restartable jobs outside the web process. DRF serves stored data to the Next.js application.

The default provider allocation is capability-specific:

- Alpaca: active US asset universe and adjusted historical daily OHLCV.
- Finnhub: current quotes, profiles, fundamentals, news, filings, peers, insider data, analyst recommendations, earnings, and IPO calendars.

Provider classes declare only capabilities they implement. Runtime services use `build_provider_registry()` and never instantiate a concrete provider directly. Ordered routes such as `OHLCV_PROVIDERS=alpaca,another_provider` control primary and fallback selection.

The critical daily path is: ingest → validate → calculate technicals → rebuild screening snapshot → run screeners. A failed critical stage stops downstream work. All data uses UTC timestamps while trading dates retain the US market session date.
