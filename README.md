# Dragonfly

Dragonfly is a provider-agnostic US-equity market intelligence and screening platform. Alpaca supplies adjusted historical daily OHLCV by default; Finnhub supplies quotes and market-intelligence datasets. Both are isolated behind capability-based adapters.

## Docker quick start

```bash
cp .env.example .env
docker compose up --build
```

Open the API docs at http://localhost:8000/api/docs/. Health endpoints are `/health/live` and `/health/ready`; instruments are available at `/api/v1/instruments/`.

The API container applies migrations on startup. Create an administrator with `docker compose exec backend python manage.py createsuperuser`.

## Market-data configuration

Add credentials to `.env`:

```dotenv
ALPACA_API_KEY_ID=your-key-id
ALPACA_API_SECRET_KEY=your-secret-key
ALPACA_DATA_FEED=sip
ALPACA_ADJUSTMENT=all
ALPACA_ASSETS_BASE_URL=https://paper-api.alpaca.markets
UNIVERSE_PROVIDERS=alpaca
OHLCV_PROVIDERS=alpaca
```

Populate or refresh the active US asset directory before ingesting prices:

```bash
docker compose exec backend python manage.py sync_instruments
```

This reads Alpaca's complete active, tradable NASDAQ/NYSE/AMEX/ARCA/BATS universe.
The optional `--symbols` argument is intended only for debugging or an explicitly
restricted universe; production commands omit it.

The first ingestion for an instrument requests all provider-available history from
`MARKET_DATA_HISTORY_START` (1900-01-01 by default). Later runs overlap the latest
stored data so corrected bars are safely upserted:

```bash
docker compose exec backend python manage.py ingest_market_data
docker compose exec backend python manage.py run_daily_pipeline
```

With no `--symbols` argument these commands apply to every active security. The
daily pipeline also refreshes the provider universe and overview metadata before
processing market data and rankings.

Refresh list-page sector/current-price enrichment and rebuild Bull/Bear opportunity scores:

```bash
docker compose exec backend python manage.py sync_instrument_overviews
docker compose exec backend python manage.py generate_trade_signals
```

TLS verification for the Nasdaq overview import is enabled by default. The local
`NASDAQ_VERIFY_SSL=false` override is intended only for development networks with
a trusted TLS-inspection proxy; production must use certificate verification.

Provider selection is configuration-driven. To migrate or add fallback providers, implement the canonical adapter and change the ordered capability route; analytics, screeners, APIs, and frontend contracts remain unchanged.

## Local development

Python 3.12+ is required. PostgreSQL is used by Docker and production; tests default to SQLite.

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate
python -m pip install -e ".[dev]"
python manage.py migrate
ruff check .
pytest
```

Copy `.env.example` for configuration and never commit real credentials.
