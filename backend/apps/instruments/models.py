from django.db import models


class Instrument(models.Model):
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=30, default="stock")
    currency = models.CharField(max_length=10, default="USD")
    sector = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    provider_symbol = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    market_cap = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    latest_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    price_as_of = models.DateTimeField(null=True, blank=True)
    price_provider = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["symbol", "exchange"]
        constraints = [
            models.UniqueConstraint(
                fields=["symbol", "exchange"], name="uq_instrument_symbol_exchange"
            )
        ]

    def __str__(self) -> str:
        return f"{self.symbol} ({self.exchange})"
