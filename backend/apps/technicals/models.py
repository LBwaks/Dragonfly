from django.db import models

from apps.instruments.models import Instrument


class TechnicalFields(models.Model):
    close = models.FloatField()
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
    atr_14 = models.FloatField(null=True)
    atr_pct = models.FloatField(null=True)
    bollinger_upper = models.FloatField(null=True)
    bollinger_middle = models.FloatField(null=True)
    bollinger_lower = models.FloatField(null=True)
    bollinger_width = models.FloatField(null=True)
    avg_volume_20 = models.FloatField(null=True)
    relative_volume = models.FloatField(null=True)
    volume_change_20 = models.FloatField(null=True)
    return_1d = models.FloatField(null=True)
    return_5d = models.FloatField(null=True)
    return_20d = models.FloatField(null=True)
    return_50d = models.FloatField(null=True)
    return_252d = models.FloatField(null=True)
    high_20 = models.FloatField(null=True)
    high_50 = models.FloatField(null=True)
    high_252 = models.FloatField(null=True)
    low_20 = models.FloatField(null=True)
    low_50 = models.FloatField(null=True)
    distance_high_20 = models.FloatField(null=True)
    distance_high_252 = models.FloatField(null=True)

    class Meta:
        abstract = True


class TechnicalDaily(TechnicalFields):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="technical_history"
    )
    trading_date = models.DateField()
    calculation_version = models.CharField(max_length=50)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "trading_date"], name="uq_technical_daily"
            )
        ]
        indexes = [
            models.Index(fields=["instrument", "-trading_date"], name="tech_instrument_date_idx"),
            models.Index(fields=["trading_date"], name="tech_date_idx"),
        ]


class TechnicalSnapshot(TechnicalFields):
    instrument = models.OneToOneField(
        Instrument, on_delete=models.CASCADE, related_name="technical_snapshot"
    )
    trading_date = models.DateField()
    calculation_version = models.CharField(max_length=50)
    calculated_at = models.DateTimeField(auto_now=True)
