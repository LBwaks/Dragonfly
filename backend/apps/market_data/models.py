from django.db import models

from apps.instruments.models import Instrument


class DailyBar(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="daily_bars")
    trading_date = models.DateField()
    open = models.DecimalField(max_digits=20, decimal_places=6)
    high = models.DecimalField(max_digits=20, decimal_places=6)
    low = models.DecimalField(max_digits=20, decimal_places=6)
    close = models.DecimalField(max_digits=20, decimal_places=6)
    adjusted_close = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    volume = models.BigIntegerField()
    provider = models.CharField(max_length=50)
    provider_record_id = models.CharField(max_length=255, blank=True)
    source_timestamp = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "trading_date"], name="uq_daily_bar_instrument_date"
            )
        ]
        indexes = [
            models.Index(fields=["instrument", "-trading_date"], name="bar_instrument_date_idx"),
            models.Index(fields=["trading_date"], name="bar_date_idx"),
        ]
        ordering = ["instrument", "trading_date"]


class CorporateAction(models.Model):
    class ActionType(models.TextChoices):
        SPLIT = "SPLIT", "Split"
        DIVIDEND = "DIVIDEND", "Dividend"

    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="corporate_actions"
    )
    action_date = models.DateField()
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    split_ratio = models.DecimalField(max_digits=16, decimal_places=8, null=True, blank=True)
    dividend_amount = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DataQualityEvent(models.Model):
    class EventType(models.TextChoices):
        INVALID_OHLC = "INVALID_OHLC", "Invalid OHLC"
        MISSING_BAR = "MISSING_BAR", "Missing bar"
        STALE_DATA = "STALE_DATA", "Stale data"
        PRICE_GAP = "PRICE_GAP", "Price gap"
        ZERO_VOLUME = "ZERO_VOLUME", "Zero volume"
        DUPLICATE_DATA = "DUPLICATE_DATA", "Duplicate data"
        POSSIBLE_CORPORATE_ACTION = "POSSIBLE_CORPORATE_ACTION", "Possible corporate action"

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        ERROR = "ERROR", "Error"

    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="quality_events"
    )
    trading_date = models.DateField(null=True, blank=True)
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    message = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ProviderSnapshotBase(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    as_of_date = models.DateField()
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class InstrumentSnapshot(ProviderSnapshotBase):
    market_cap = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    shares_outstanding = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    beta = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    week_52_high = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    week_52_low = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "as_of_date", "provider"], name="uq_instrument_snapshot"
            )
        ]


class FundamentalSnapshot(ProviderSnapshotBase):
    pe = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    pb = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    ps = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    ev_ebitda = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    eps = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    eps_growth = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    revenue = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    revenue_growth = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    gross_margin = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    operating_margin = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    net_margin = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    roe = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    roa = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    debt_equity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    current_ratio = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    quick_ratio = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    free_cash_flow = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "as_of_date", "provider"], name="uq_fundamental_snapshot"
            )
        ]


class PeerRelationship(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="peer_links")
    peer_instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="peer_of"
    )
    provider = models.CharField(max_length=50)
    as_of_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "peer_instrument", "provider"], name="uq_peer_relationship"
            )
        ]


class NewsBase(models.Model):
    provider = models.CharField(max_length=50)
    provider_article_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    source = models.CharField(max_length=255, blank=True)
    headline = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    url = models.URLField(max_length=1000)
    category = models.CharField(max_length=100, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    ingested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CompanyNews(NewsBase):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="news")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_article_id"], name="uq_company_news_article"
            )
        ]


class MarketNews(NewsBase):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_article_id"], name="uq_market_news_article"
            )
        ]


class SecFiling(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="filings")
    form_type = models.CharField(max_length=40)
    filing_date = models.DateField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    accession_number = models.CharField(max_length=100)
    report_url = models.URLField(max_length=1000, blank=True)
    primary_document_url = models.URLField(max_length=1000, blank=True)
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InsiderTransaction(models.Model):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="insider_transactions"
    )
    insider_name = models.CharField(max_length=255)
    insider_role = models.CharField(max_length=255, blank=True)
    transaction_date = models.DateField()
    filing_date = models.DateField(null=True, blank=True)
    transaction_code = models.CharField(max_length=30, blank=True)
    shares_change = models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
    transaction_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    holdings_after = models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
    provider = models.CharField(max_length=50)
    provider_transaction_id = models.CharField(max_length=255, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InsiderSentiment(models.Model):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="insider_sentiments"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    mspr = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    change = models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
    buy_count = models.PositiveIntegerField(default=0)
    sell_count = models.PositiveIntegerField(default=0)
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AnalystRecommendation(models.Model):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="analyst_recommendations"
    )
    period = models.DateField()
    strong_buy = models.PositiveIntegerField(default=0)
    buy = models.PositiveIntegerField(default=0)
    hold = models.PositiveIntegerField(default=0)
    sell = models.PositiveIntegerField(default=0)
    strong_sell = models.PositiveIntegerField(default=0)
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "period", "provider"], name="uq_analyst_recommendation"
            )
        ]


class EarningsEvent(models.Model):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="earnings_events"
    )
    event_date = models.DateField()
    fiscal_year = models.IntegerField(null=True, blank=True)
    fiscal_quarter = models.PositiveSmallIntegerField(null=True, blank=True)
    eps_estimate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    revenue_estimate = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    session = models.CharField(max_length=20, blank=True)
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EarningsResult(models.Model):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="earnings_results"
    )
    report_date = models.DateField()
    fiscal_year = models.IntegerField(null=True, blank=True)
    fiscal_quarter = models.PositiveSmallIntegerField(null=True, blank=True)
    eps_actual = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    eps_estimate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    eps_surprise = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    eps_surprise_pct = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    revenue_actual = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    revenue_estimate = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    revenue_surprise_pct = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class IpoEvent(models.Model):
    symbol = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255)
    ipo_date = models.DateField()
    exchange = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    shares = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)
    provider = models.CharField(max_length=50)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DomainFreshness(models.Model):
    class Status(models.TextChoices):
        CURRENT = "CURRENT", "Current"
        STALE = "STALE", "Stale"
        PARTIAL = "PARTIAL", "Partial"
        FAILED = "FAILED", "Failed"
        DISABLED = "DISABLED", "Disabled"

    domain = models.CharField(max_length=50, unique=True)
    latest_success_at = models.DateTimeField(null=True, blank=True)
    latest_source_date = models.DateField(null=True, blank=True)
    expected_freshness_hours = models.PositiveIntegerField(default=24)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STALE)
    details = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
