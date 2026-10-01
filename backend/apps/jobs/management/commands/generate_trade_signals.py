from django.core.management.base import BaseCommand

from apps.instruments.models import Instrument
from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from apps.screeners.signals import generate_signals_for_instrument


class Command(BaseCommand):
    help = "Classify eligible stocks into bull/bear opportunities for three horizons."

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbols",
            help="Optional comma-separated subset; omit to score every eligible security.",
        )

    def handle(self, *args, **options):
        queryset = Instrument.objects.filter(screening_snapshot__isnull=False).distinct()
        if options["symbols"]:
            queryset = queryset.filter(symbol__in=options["symbols"].upper().split(","))
        instruments = list(queryset)
        with tracked_job(
            JobRun.JobType.SCREENER_EXECUTION, symbols_requested=len(instruments)
        ) as job:
            for instrument in instruments:
                try:
                    signals = generate_signals_for_instrument(instrument)
                    job.rows_updated += len(signals)
                    job.symbols_succeeded += int(bool(signals))
                    job.symbols_failed += int(not signals)
                except Exception:
                    job.symbols_failed += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Trade signals generated for {job.symbols_succeeded}/{len(instruments)} stocks"
            )
        )
