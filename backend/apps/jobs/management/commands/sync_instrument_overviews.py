from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.instruments.models import Instrument
from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from providers.capabilities import ProviderCapability
from providers.runtime import build_provider_registry


class Command(BaseCommand):
    help = "Refresh sector, industry, market cap, and latest price from the overview provider."

    def handle(self, *args, **options):
        provider = build_provider_registry().get_provider(ProviderCapability.INSTRUMENT_OVERVIEW)
        rows = provider.get_instrument_overviews()
        by_symbol = {row.symbol: row for row in rows}
        instruments = list(Instrument.objects.filter(symbol__in=by_symbol))
        provider_match_count = len(instruments)
        as_of = timezone.now()

        with tracked_job(
            JobRun.JobType.INTELLIGENCE_SYNC, symbols_requested=len(by_symbol)
        ) as job:
            for instrument in instruments:
                row = by_symbol[instrument.symbol]
                instrument.sector = row.sector or instrument.sector
                instrument.industry = row.industry or instrument.industry
                instrument.market_cap = row.market_cap or instrument.market_cap
                instrument.latest_price = row.price or instrument.latest_price
                instrument.price_as_of = as_of if row.price is not None else instrument.price_as_of
                instrument.price_provider = (
                    provider.name if row.price is not None else instrument.price_provider
                )
            updated_by_id = {instrument.id: instrument for instrument in instruments}
            for instrument in Instrument.objects.filter(sector="", name__icontains="ETF"):
                instrument.sector = "ETF"
                instrument.industry = instrument.industry or "Exchange-Traded Fund"
                updated_by_id[instrument.id] = instrument
            instruments = list(updated_by_id.values())
            Instrument.objects.bulk_update(
                instruments,
                [
                    "sector",
                    "industry",
                    "market_cap",
                    "latest_price",
                    "price_as_of",
                    "price_provider",
                    "updated_at",
                ],
                batch_size=1000,
            )
            job.rows_updated = len(instruments)
            job.symbols_succeeded = provider_match_count
            job.symbols_failed = max(0, len(by_symbol) - provider_match_count)
            job.metadata = {
                "provider": provider.name,
                "etfs_classified": len(instruments) - provider_match_count,
            }

        self.stdout.write(
            self.style.SUCCESS(
                f"Overview sync complete: {len(instruments)} instruments updated, "
                f"provider={provider.name}"
            )
        )
