from datetime import date, timedelta
from decimal import Decimal
from math import sin

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.instruments.models import Instrument
from apps.market_data.models import DailyBar
from apps.screeners.models import Screener


class Command(BaseCommand):
    def handle(self, *args, **options):
        user, _ = get_user_model().objects.get_or_create(username="demo")
        for offset, symbol in enumerate(["ARM", "NVDA", "AMD"]):
            instrument, _ = Instrument.objects.update_or_create(
                symbol=symbol,
                exchange="NASDAQ",
                defaults={"name": symbol, "sector": "Technology", "industry": "Semiconductors"},
            )
            for index in range(320):
                day = date.today() - timedelta(days=450 - index)
                price = Decimal(str(round(80 + offset * 20 + index * 0.2 + sin(index / 8), 4)))
                DailyBar.objects.update_or_create(
                    instrument=instrument,
                    trading_date=day,
                    defaults={
                        "open": price,
                        "high": price + 1,
                        "low": price - 1,
                        "close": price,
                        "adjusted_close": price,
                        "volume": 1_000_000 + index * 1000,
                        "provider": "demo",
                    },
                )
        Screener.objects.get_or_create(
            name="Momentum",
            created_by=user,
            defaults={
                "description": "Built-in momentum screen",
                "is_builtin": True,
                "rules": {
                    "logic": "AND",
                    "conditions": [
                        {"left": "close", "operator": ">", "right_field": "sma_200"},
                        {"left": "rsi_14", "operator": "between", "value": [50, 75]},
                    ],
                },
            },
        )
        self.stdout.write(self.style.SUCCESS("Demo data seeded"))
