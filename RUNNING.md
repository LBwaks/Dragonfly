# Running Dragonfly

These instructions use Windows PowerShell and Docker Desktop.

## 1. Open the project

```powershell
cd "C:\Users\HP\OneDrive - Indra\Desktop\Dragonfly"
```

## 2. Configure environment variables

If `.env` does not exist, create it from the example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and provide your API credentials:

```dotenv
ALPACA_API_KEY_ID=your_alpaca_key_id
ALPACA_API_SECRET_KEY=your_alpaca_secret_key
FINNHUB_API_KEY=your_finnhub_key
```

Alpaca supplies the instrument universe and historical OHLCV data. Finnhub supplies
quotes and supported market-intelligence data.

Never commit the real `.env` file or share its values.

## 3. Build and start the application

Make sure Docker Desktop is running, then execute:

```powershell
docker compose up -d --build
```

Check the containers:

```powershell
docker compose ps
docker compose exec backend python manage.py check
```

## 4. Synchronize instruments

On the first run, populate the instrument directory from Alpaca:

```powershell
docker compose exec backend python manage.py sync_instruments
docker compose exec backend python manage.py sync_instrument_overviews
```

The application imports active, tradable US assets from NASDAQ, NYSE, AMEX, ARCA,
and BATS.

`NASDAQ_VERIFY_SSL` is `true` by default and must remain enabled in production. If
a trusted corporate network performs TLS inspection and Docker cannot verify its
local root certificate, set it to `false` only in the local `.env`, then restore it
after installing the corporate CA certificate in Docker.

The production universe is the complete active provider universe. The `--symbols`
option is available only for debugging or intentionally creating a small manual
universe:

```powershell
docker compose exec backend python manage.py sync_instruments --symbols AMD,ARM,NVDA
```

## 5. Import historical prices

Run the complete active-security workflow with no `--symbols` option:

```powershell
docker compose exec backend python manage.py ingest_market_data
docker compose exec backend python manage.py validate_market_data
docker compose exec backend python manage.py calculate_technicals --recalculate
docker compose exec backend python manage.py rebuild_technical_snapshot
docker compose exec backend python manage.py generate_trade_signals
```

With more than 13,000 assets, the first full-universe lifetime backfill can take hours and use
substantial database storage. It is resumable: successful symbols are committed as
they finish, and a later run incrementally overlaps the most recent stored bars.
Do not add `--force` to routine updates; it deliberately downloads the configured
full history again. `MARKET_DATA_HISTORY_START=1900-01-01` requests the provider's
complete available history; the chart displays every stored daily bar.

For all later incremental updates, run the complete daily pipeline:

```powershell
docker compose exec backend python manage.py run_daily_pipeline
```

`run_daily_pipeline` refreshes the full active universe and overview metadata, then
ingests prices, validates bars, calculates technicals, rebuilds snapshots, generates
all Bull/Bear horizons, and executes saved screeners.

For Alpaca's free market-data plan, use `ALPACA_DATA_FEED=iex`. Set the feed to
`sip` only when the Alpaca account has SIP entitlement; otherwise intraday requests
return HTTP 403.

## 6. Open the application

- Web application: <http://localhost:3000>
- Instruments: <http://localhost:3000/instruments>
- API documentation: <http://localhost:8000/api/docs/>
- Django administration: <http://localhost:8000/admin/>
- Backend readiness: <http://localhost:8000/health/ready>

## 7. Create an administrator

```powershell
docker compose exec backend python manage.py createsuperuser
```

Follow the prompts, then sign in at <http://localhost:8000/admin/>.

## 8. View logs

Follow backend and frontend logs:

```powershell
docker compose logs -f backend frontend
```

Press `Ctrl+C` to stop following logs. This does not stop the containers.

View only recent backend logs:

```powershell
docker compose logs --tail=200 backend
```

## 9. Stop and restart

Stop the application without deleting database data:

```powershell
docker compose down
```

Start the existing containers again:

```powershell
docker compose up -d
```

Rebuild after changing source code or dependencies:

```powershell
docker compose up -d --build
```

## Troubleshooting

### `All symbols failed ingestion`

Inspect the latest backend logs and job records:

```powershell
docker compose logs --tail=200 backend
docker compose exec backend python manage.py shell -c "from apps.jobs.models import JobRun; print(JobRun.objects.order_by('-id').values('status','metadata','error_message').first())"
```

Confirm that both Alpaca values are present in `.env`, then rebuild the backend:

```powershell
docker compose up -d --build backend
```

### Docker Hub timeout or TLS handshake errors

Errors such as `502 Bad Gateway`, `TLS handshake timeout`, or `failed to resolve
source metadata` occur while Docker is contacting Docker Hub. They are not Django
or Dragonfly errors.

If Dragonfly was built previously, start the local images without contacting Docker
Hub:

```powershell
docker compose up -d --no-build
```

Confirm that the application is healthy:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/health/ready
```

When a new image really is required, retry the registry operation after the network
connection recovers:

```powershell
docker compose pull
docker compose up -d --build
```

If it continues to time out, restart Docker Desktop and check whether a VPN, proxy,
firewall, or DNS filter is interfering with `registry-1.docker.io`.

### Resetting the database

`docker compose down` preserves the database. Removing Docker volumes permanently
deletes stored instruments, prices, users, screeners, and job history. Do not remove
the database volume unless a complete reset is intentionally required.
