from django.core.management.base import BaseCommand

from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from apps.screeners.models import Screener
from apps.screeners.services import run_screener


class Command(BaseCommand):
    def handle(self, *args, **options):
        screeners = list(Screener.objects.filter(enabled=True))
        with tracked_job(
            JobRun.JobType.SCREENER_EXECUTION, symbols_requested=len(screeners)
        ) as job:
            for screener in screeners:
                run_screener(screener)
                job.symbols_succeeded += 1
