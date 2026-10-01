from django.conf import settings
from django.db import models

from apps.instruments.models import Instrument


class Screener(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rules = models.JSONField()
    ranking_weights = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    is_builtin = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="screeners"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ScreenerRun(models.Model):
    class Status(models.TextChoices):
        RUNNING = "RUNNING", "Running"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    screener = models.ForeignKey(Screener, on_delete=models.CASCADE, related_name="runs")
    market_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    stocks_evaluated = models.PositiveIntegerField(default=0)
    stocks_matched = models.PositiveIntegerField(default=0)
    calculation_version = models.CharField(max_length=50)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]


class ScreenerMatch(models.Model):
    screener_run = models.ForeignKey(ScreenerRun, on_delete=models.CASCADE, related_name="matches")
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    score = models.FloatField()
    matched_values = models.JSONField(default=dict)
    component_scores = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["screener_run", "instrument"], name="uq_screener_run_instrument"
            )
        ]
        ordering = ["rank"]


class ScreeningSnapshot(models.Model):
    instrument = models.OneToOneField(
        Instrument, on_delete=models.CASCADE, related_name="screening_snapshot"
    )
    market_date = models.DateField()
    source_timestamps = models.JSONField(default=dict)
    close = models.FloatField(null=True)
    sma_20 = models.FloatField(null=True)
    sma_50 = models.FloatField(null=True)
    sma_100 = models.FloatField(null=True)
    sma_200 = models.FloatField(null=True)
    ema_12 = models.FloatField(null=True)
    ema_26 = models.FloatField(null=True)
    rsi_14 = models.FloatField(null=True)
    macd = models.FloatField(null=True)
    macd_signal = models.FloatField(null=True)
    macd_histogram = models.FloatField(null=True)
    atr_pct = models.FloatField(null=True)
    relative_volume = models.FloatField(null=True)
    return_1d = models.FloatField(null=True)
    return_5d = models.FloatField(null=True)
    return_20d = models.FloatField(null=True)
    return_50d = models.FloatField(null=True)
    return_252d = models.FloatField(null=True)
    distance_high_20 = models.FloatField(null=True)
    distance_high_252 = models.FloatField(null=True)
    market_cap = models.FloatField(null=True)
    shares_outstanding = models.FloatField(null=True)
    pe = models.FloatField(null=True)
    pb = models.FloatField(null=True)
    ps = models.FloatField(null=True)
    ev_ebitda = models.FloatField(null=True)
    eps = models.FloatField(null=True)
    eps_growth = models.FloatField(null=True)
    revenue = models.FloatField(null=True)
    revenue_growth = models.FloatField(null=True)
    gross_margin = models.FloatField(null=True)
    operating_margin = models.FloatField(null=True)
    net_margin = models.FloatField(null=True)
    roe = models.FloatField(null=True)
    roa = models.FloatField(null=True)
    debt_equity = models.FloatField(null=True)
    current_ratio = models.FloatField(null=True)
    quick_ratio = models.FloatField(null=True)
    free_cash_flow = models.FloatField(null=True)
    strong_buy = models.PositiveIntegerField(null=True)
    buy = models.PositiveIntegerField(null=True)
    hold = models.PositiveIntegerField(null=True)
    sell = models.PositiveIntegerField(null=True)
    strong_sell = models.PositiveIntegerField(null=True)
    analyst_buy_ratio = models.FloatField(null=True)
    latest_insider_mspr = models.FloatField(null=True)
    insider_net_change = models.FloatField(null=True)
    insider_buy_count = models.PositiveIntegerField(null=True)
    insider_sell_count = models.PositiveIntegerField(null=True)
    days_to_earnings = models.IntegerField(null=True)
    latest_eps_surprise = models.FloatField(null=True)
    latest_eps_surprise_pct = models.FloatField(null=True)
    sector = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    exchange = models.CharField(max_length=50, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class TradeSignal(models.Model):
    class CaseType(models.TextChoices):
        BULL = "BULL", "Bull case"
        BEAR = "BEAR", "Bear case"

    class Horizon(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"

    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="trade_signals"
    )
    horizon = models.CharField(max_length=10, choices=Horizon.choices)
    case_type = models.CharField(max_length=10, choices=CaseType.choices)
    as_of_date = models.DateField()
    price = models.DecimalField(max_digits=20, decimal_places=6)
    score = models.FloatField()
    technical_score = models.FloatField()
    fundamental_score = models.FloatField()
    macro_score = models.FloatField()
    pattern_score = models.FloatField()
    data_completeness = models.FloatField(default=0)
    candle_patterns = models.JSONField(default=list, blank=True)
    chart_patterns = models.JSONField(default=list, blank=True)
    rationale = models.JSONField(default=list, blank=True)
    calculation_version = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "horizon"], name="uq_trade_signal_instrument_horizon"
            )
        ]
        indexes = [
            models.Index(fields=["case_type", "horizon", "-score"], name="signal_case_horizon_idx")
        ]
        ordering = ["-score", "instrument__symbol"]
