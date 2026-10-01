from analytics import CALCULATION_VERSION, calculate_technicals
from apps.market_data.models import DailyBar

from .models import TechnicalDaily, TechnicalSnapshot

TECHNICAL_FIELD_NAMES = [
    field.name
    for field in TechnicalDaily._meta.fields
    if field.name
    not in {"id", "instrument", "trading_date", "calculation_version", "calculated_at"}
]


def calculate_for_instrument(instrument, market_date=None):
    bars = DailyBar.objects.filter(instrument=instrument, is_valid=True)
    if market_date:
        bars = bars.filter(trading_date__lte=market_date)
    bars = list(bars.order_by("-trading_date")[:320])
    rows = [
        {
            "trading_date": bar.trading_date,
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "adjusted_close": float(bar.adjusted_close) if bar.adjusted_close else None,
            "volume": bar.volume,
        }
        for bar in reversed(bars)
    ]
    calculated = calculate_technicals(rows)
    if not calculated:
        return None
    latest = calculated[-1]
    values = {field: latest.get(field) for field in TECHNICAL_FIELD_NAMES}
    daily, _ = TechnicalDaily.objects.update_or_create(
        instrument=instrument,
        trading_date=latest["trading_date"],
        defaults={**values, "calculation_version": CALCULATION_VERSION},
    )
    TechnicalSnapshot.objects.update_or_create(
        instrument=instrument,
        defaults={
            **values,
            "trading_date": latest["trading_date"],
            "calculation_version": CALCULATION_VERSION,
        },
    )
    return daily
