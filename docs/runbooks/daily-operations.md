# Daily operations

Run after finalized US market data is available:

    python manage.py ingest_market_data
    python manage.py validate_market_data
    python manage.py calculate_technicals
    python manage.py rebuild_technical_snapshot
    python manage.py run_screeners

Inspect JobRun, DataQualityEvent, and /health/data after partial failures. Commands are idempotent and may be rerun with explicit symbols and dates.

Alpaca is the default historical provider. For instruments without stored bars, ingestion requests `MARKET_DATA_INITIAL_HISTORY_YEARS` (five by default). Existing instruments use a ten-calendar-day overlap. To force an explicit repair window:

    python manage.py ingest_market_data --symbols AAPL,MSFT --start 2021-01-01 --end 2026-01-01 --force

Required environment variables:

    ALPACA_API_KEY_ID
    ALPACA_API_SECRET_KEY
    ALPACA_DATA_FEED=sip
    ALPACA_ADJUSTMENT=all
    OHLCV_PROVIDERS=alpaca
