from django.db import models


class JobRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        SUCCESS = "SUCCESS", "Success"
        PARTIAL_SUCCESS = "PARTIAL_SUCCESS", "Partial success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    class JobType(models.TextChoices):
        INSTRUMENT_SYNC = "INSTRUMENT_SYNC", "Instrument sync"
        MARKET_INGESTION = "MARKET_INGESTION", "Market ingestion"
        MARKET_VALIDATION = "MARKET_VALIDATION", "Market validation"
        TECHNICAL_CALCULATION = "TECHNICAL_CALCULATION", "Technical calculation"
        SCREENER_EXECUTION = "SCREENER_EXECUTION", "Screener execution"
        INTELLIGENCE_SYNC = "INTELLIGENCE_SYNC", "Intelligence sync"

    job_type = models.CharField(max_length=40, choices=JobType.choices)
    market_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    symbols_requested = models.PositiveIntegerField(default=0)
    symbols_succeeded = models.PositiveIntegerField(default=0)
    symbols_failed = models.PositiveIntegerField(default=0)
    rows_inserted = models.PositiveIntegerField(default=0)
    rows_updated = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-id"]
