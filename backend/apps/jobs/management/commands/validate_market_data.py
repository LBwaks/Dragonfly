from django.core.management.base import BaseCommand

from apps.instruments.models import Instrument
from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from apps.market_data.services import validate_instrument_bars


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--symbols")

    def handle(self, *args, **options):
        queryset = Instrument.objects.filter(is_active=True)
        if options["symbols"]:
            queryset = queryset.filter(symbol__in=options["symbols"].upper().split(","))
        instruments = list(queryset)
        with tracked_job(
            JobRun.JobType.MARKET_VALIDATION, symbols_requested=len(instruments)
        ) as job:
            job.rows_inserted = sum(validate_instrument_bars(item) for item in instruments)
            job.symbols_succeeded = len(instruments)
