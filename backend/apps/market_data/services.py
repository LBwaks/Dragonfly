from decimal import Decimal

from django.db import transaction

from providers.models import NormalizedDailyBar

from .models import DailyBar, DataQualityEvent


@transaction.atomic
def upsert_daily_bars(instrument, bars: list[NormalizedDailyBar]) -> tuple[int, int]:
    by_date = {bar.trading_date: bar for bar in bars}
    if any(bar.symbol != instrument.symbol for bar in by_date.values()):
        raise ValueError("bar symbol does not match instrument")
    existing_dates = set(
        DailyBar.objects.filter(
            instrument=instrument, trading_date__in=by_date
        ).values_list("trading_date", flat=True)
    )
    objects = [
        DailyBar(
            instrument=instrument,
            trading_date=bar.trading_date,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            adjusted_close=bar.adjusted_close,
            volume=bar.volume,
            provider=bar.provider,
            is_valid=True,
        )
        for bar in by_date.values()
    ]
    if objects:
        DailyBar.objects.bulk_create(
            objects,
            update_conflicts=True,
            unique_fields=["instrument", "trading_date"],
            update_fields=[
                "open",
                "high",
                "low",
                "close",
                "adjusted_close",
                "volume",
                "provider",
                "is_valid",
                "updated_at",
            ],
        )
    updated = len(existing_dates)
    return len(by_date) - updated, updated


def validate_instrument_bars(instrument, gap_threshold=Decimal("0.30")) -> int:
    events = 0
    previous = None
    for bar in instrument.daily_bars.order_by("trading_date"):
        issues = []
        if bar.high < max(bar.open, bar.low, bar.close) or bar.low > min(
            bar.open, bar.high, bar.close
        ):
            issues.append((DataQualityEvent.EventType.INVALID_OHLC, "ERROR", "Invalid OHLC range"))
        if bar.volume == 0:
            issues.append((DataQualityEvent.EventType.ZERO_VOLUME, "WARNING", "Zero volume"))
        if previous and previous.close:
            gap = abs(bar.open / previous.close - 1)
            if gap >= gap_threshold:
                issues.append(
                    (
                        DataQualityEvent.EventType.PRICE_GAP,
                        "WARNING",
                        f"Overnight gap of {gap:.2%}",
                    )
                )
        bar.is_valid = not any(severity == "ERROR" for _, severity, _ in issues)
        bar.save(update_fields=["is_valid"])
        for event_type, severity, message in issues:
            DataQualityEvent.objects.update_or_create(
                instrument=instrument,
                trading_date=bar.trading_date,
                event_type=event_type,
                resolved=False,
                defaults={"severity": severity, "message": message},
            )
            events += 1
        previous = bar
    return events
