from contextlib import contextmanager

from django.utils import timezone

from .models import JobRun


@contextmanager
def tracked_job(job_type, *, market_date=None, symbols_requested=0, metadata=None):
    job = JobRun.objects.create(
        job_type=job_type,
        market_date=market_date,
        status=JobRun.Status.RUNNING,
        started_at=timezone.now(),
        symbols_requested=symbols_requested,
        metadata=metadata or {},
    )
    try:
        yield job
    except Exception as exc:
        job.status = JobRun.Status.FAILED
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save()
        raise
    else:
        job.status = JobRun.Status.PARTIAL_SUCCESS if job.symbols_failed else JobRun.Status.SUCCESS
        job.finished_at = timezone.now()
        job.save()
