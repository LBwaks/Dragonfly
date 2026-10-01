from datetime import date
from types import SimpleNamespace

from django.utils import timezone

from analytics import CALCULATION_VERSION
from analytics.ranking import DEFAULT_WEIGHTS, rank_rows
from apps.market_data.models import (
    AnalystRecommendation,
    EarningsEvent,
    EarningsResult,
    FundamentalSnapshot,
    InsiderSentiment,
    InstrumentSnapshot,
)
from apps.technicals.models import TechnicalDaily, TechnicalSnapshot

from .dsl import matches_rules, validate_rules
from .models import ScreenerMatch, ScreenerRun, ScreeningSnapshot


def rebuild_screening_snapshot(instrument) -> ScreeningSnapshot | None:
    try:
        technical = instrument.technical_snapshot
    except TechnicalSnapshot.DoesNotExist:
        return None
    fundamental = (
        FundamentalSnapshot.objects.filter(instrument=instrument).order_by("-as_of_date").first()
    )
    profile = (
        InstrumentSnapshot.objects.filter(instrument=instrument).order_by("-as_of_date").first()
    )
    analyst = (
        AnalystRecommendation.objects.filter(instrument=instrument).order_by("-period").first()
    )
    insider = InsiderSentiment.objects.filter(instrument=instrument).order_by("-period_end").first()
    earnings = EarningsResult.objects.filter(instrument=instrument).order_by("-report_date").first()
    upcoming = (
        EarningsEvent.objects.filter(instrument=instrument, event_date__gte=technical.trading_date)
        .order_by("event_date")
        .first()
    )
    technical_fields = {
        field: getattr(technical, field)
        for field in [
            "close",
            "sma_20",
            "sma_50",
            "sma_100",
            "sma_200",
            "ema_12",
            "ema_26",
            "rsi_14",
            "macd",
            "macd_signal",
            "macd_histogram",
            "atr_pct",
            "relative_volume",
            "return_1d",
            "return_5d",
            "return_20d",
            "return_50d",
            "return_252d",
            "distance_high_20",
            "distance_high_252",
        ]
    }
    fundamental_fields = [
        "pe",
        "pb",
        "ps",
        "ev_ebitda",
        "eps",
        "eps_growth",
        "revenue",
        "revenue_growth",
        "gross_margin",
        "operating_margin",
        "net_margin",
        "roe",
        "roa",
        "debt_equity",
        "current_ratio",
        "quick_ratio",
        "free_cash_flow",
    ]
    analyst_total = sum(
        getattr(analyst, field, 0) or 0
        for field in ["strong_buy", "buy", "hold", "sell", "strong_sell"]
    )
    defaults = {
        **technical_fields,
        **{
            field: float(getattr(fundamental, field))
            if fundamental and getattr(fundamental, field) is not None
            else None
            for field in fundamental_fields
        },
        "market_date": technical.trading_date,
        "market_cap": float(profile.market_cap)
        if profile and profile.market_cap
        else (float(instrument.market_cap) if instrument.market_cap else None),
        "shares_outstanding": (
            float(profile.shares_outstanding) if profile and profile.shares_outstanding else None
        ),
        "sector": instrument.sector,
        "industry": instrument.industry,
        "exchange": instrument.exchange,
        "analyst_buy_ratio": (
            (analyst.strong_buy + analyst.buy) / analyst_total if analyst_total else None
        ),
        "latest_insider_mspr": float(insider.mspr) if insider and insider.mspr else None,
        "insider_net_change": float(insider.change) if insider and insider.change else None,
        "insider_buy_count": insider.buy_count if insider else None,
        "insider_sell_count": insider.sell_count if insider else None,
        "days_to_earnings": (
            (upcoming.event_date - technical.trading_date).days if upcoming else None
        ),
        "latest_eps_surprise": float(earnings.eps_surprise)
        if earnings and earnings.eps_surprise is not None
        else None,
        "latest_eps_surprise_pct": float(earnings.eps_surprise_pct)
        if earnings and earnings.eps_surprise_pct is not None
        else None,
        "source_timestamps": {"technical": technical.calculated_at.isoformat()},
    }
    if analyst:
        defaults.update(
            {
                field: getattr(analyst, field)
                for field in ["strong_buy", "buy", "hold", "sell", "strong_sell"]
            }
        )
    snapshot, _ = ScreeningSnapshot.objects.update_or_create(
        instrument=instrument, defaults=defaults
    )
    return snapshot


def run_screener(screener, market_date: date | None = None) -> ScreenerRun:
    validate_rules(screener.rules)
    snapshots = list(
        ScreeningSnapshot.objects.select_related("instrument").filter(market_date=market_date)
        if market_date
        else ScreeningSnapshot.objects.select_related("instrument")
    )
    run = ScreenerRun.objects.create(
        screener=screener,
        market_date=market_date
        or max((snapshot.market_date for snapshot in snapshots), default=date.today()),
        stocks_evaluated=len(snapshots),
        calculation_version=CALCULATION_VERSION,
    )
    matches = []
    for snapshot in snapshots:
        prior = (
            TechnicalDaily.objects.filter(
                instrument=snapshot.instrument, trading_date__lt=snapshot.market_date
            )
            .order_by("-trading_date")
            .first()
        )
        previous = (
            SimpleNamespace(
                **{field.name: getattr(prior, field.name) for field in prior._meta.fields}
            )
            if prior
            else None
        )
        if matches_rules(screener.rules, snapshot, previous):
            matches.append(snapshot)
    ranked = rank_rows(matches, screener.ranking_weights or DEFAULT_WEIGHTS)
    ScreenerMatch.objects.bulk_create(
        [
            ScreenerMatch(
                screener_run=run,
                instrument=row.instrument,
                rank=index,
                score=score,
                component_scores=components,
                matched_values={
                    field: getattr(row, field, None) for field in sorted(ALLOWED_RESULT_FIELDS)
                },
            )
            for index, (row, score, components) in enumerate(ranked, 1)
        ]
    )
    run.stocks_matched = len(ranked)
    run.status = ScreenerRun.Status.SUCCESS
    run.completed_at = timezone.now()
    run.save()
    return run


ALLOWED_RESULT_FIELDS = {
    "close",
    "rsi_14",
    "relative_volume",
    "return_20d",
    "distance_high_252",
    "market_cap",
    "analyst_buy_ratio",
}
