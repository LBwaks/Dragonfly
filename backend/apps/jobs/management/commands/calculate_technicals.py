from datetime import date

from django.core.management.base import BaseCommand

from apps.instruments.models import Instrument
from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from apps.technicals.services import calculate_for_instrument


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--symbols",
            help="Optional comma-separated subset; omit to calculate every active security.",
        )
        parser.add_argument("--market-date", type=date.fromisoformat)
        parser.add_argument("--recalculate", action="store_true")

    def handle(self, *args, **options):
        queryset = Instrument.objects.filter(is_active=True)
        if options["symbols"]:
            queryset = queryset.filter(symbol__in=options["symbols"].upper().split(","))
        instruments = list(queryset)
        with tracked_job(
            JobRun.JobType.TECHNICAL_CALCULATION,
            market_date=options["market_date"],
            symbols_requested=len(instruments),
        ) as job:
            for instrument in instruments:
                try:
                    result = calculate_for_instrument(instrument, options["market_date"])
                    job.symbols_succeeded += int(result is not None)
                except Exception:
                    job.symbols_failed += 1
