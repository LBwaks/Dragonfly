from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.instruments.models import Instrument
from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from apps.market_data.calendar import NyseCalendar
from apps.market_data.services import upsert_daily_bars
from providers.capabilities import ProviderCapability
from providers.routing import call_with_fallback
from providers.runtime import build_provider_registry


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--symbols",
            help="Optional comma-separated subset; omit to ingest every active security.",
        )
        parser.add_argument("--start", type=date.fromisoformat)
        parser.add_argument("--end", type=date.fromisoformat)
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **options):
        end = options["end"] or NyseCalendar().latest_completed_session()
        queryset = Instrument.objects.filter(is_active=True)
        if options["symbols"]:
            queryset = queryset.filter(symbol__in=options["symbols"].upper().split(","))
        instruments = list(queryset)
        registry = build_provider_registry()
        provider = registry.get_provider(ProviderCapability.HISTORICAL_OHLCV)
        with tracked_job(
            JobRun.JobType.MARKET_INGESTION,
            market_date=end,
            symbols_requested=len(instruments),
        ) as job:
            failures = {}
            for instrument in instruments:
                try:
                    latest_bar_date = (
                        instrument.daily_bars.order_by("-trading_date")
                        .values_list("trading_date", flat=True)
                        .first()
                    )
                    if options["start"]:
                        start = options["start"]
                    elif options["force"]:
                        start = settings.MARKET_DATA_HISTORY_START
                    elif latest_bar_date:
                        start = latest_bar_date - timedelta(days=10)
                    else:
                        start = settings.MARKET_DATA_HISTORY_START
                    bars = call_with_fallback(
                        registry,
                        ProviderCapability.HISTORICAL_OHLCV,
                        "get_daily_bars",
                        instrument.symbol,
                        start,
                        end,
                    )
                    inserted, updated = upsert_daily_bars(instrument, list(bars))
                    job.rows_inserted += inserted
                    job.rows_updated += updated
                    job.symbols_succeeded += 1
                except Exception as exc:
                    failures[instrument.symbol] = str(exc)
                    job.symbols_failed += 1
            job.metadata = {"failures": failures, "provider": provider.name}
            if instruments and not job.symbols_succeeded:
                details = "; ".join(f"{symbol}: {message}" for symbol, message in failures.items())
                raise CommandError(f"All symbols failed ingestion ({details})")

        if failures:
            details = "; ".join(f"{symbol}: {message}" for symbol, message in failures.items())
            self.stderr.write(self.style.WARNING(f"Partial ingestion failures: {details}"))
        self.stdout.write(
            self.style.SUCCESS(
                "Market data ingestion complete: "
                f"{job.symbols_succeeded}/{job.symbols_requested} symbols, "
                f"{job.rows_inserted} inserted, {job.rows_updated} updated, "
                f"provider={provider.name}, through={end.isoformat()}"
            )
        )
