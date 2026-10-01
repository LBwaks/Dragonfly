from decimal import Decimal

from analytics import CALCULATION_VERSION
from analytics.breakout_backtest import PriceBar
from analytics.pattern_backtest import build_pattern_features
from apps.market_data.models import DailyBar

from .models import ScreeningSnapshot, TradeSignal

BULLISH_PATTERNS = {
    "hammer",
    "dragonfly_doji",
    "long_lower_shadow",
    "marubozu_white",
    "triangle_ascending",
    "channel_up",
    "double_bottom",
    "multiple_bottom",
    "head_shoulders_inverse",
    "tl_support",
}
BEARISH_PATTERNS = {
    "inverted_hammer",
    "gravestone_doji",
    "long_upper_shadow",
    "marubozu_black",
    "triangle_descending",
    "channel_down",
    "double_top",
    "multiple_top",
    "head_shoulders",
    "tl_resistance",
}

HORIZON_CONFIG = {
    TradeSignal.Horizon.DAILY: ("return_5d", "sma_20", 500),
    TradeSignal.Horizon.WEEKLY: ("return_20d", "sma_50", 250),
    TradeSignal.Horizon.MONTHLY: ("return_50d", "sma_200", 125),
}


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _fundamental_score(snapshot: ScreeningSnapshot) -> tuple[float, float]:
    values = {
        "eps_growth": snapshot.eps_growth,
        "revenue_growth": snapshot.revenue_growth,
        "roe": snapshot.roe,
        "debt_equity": snapshot.debt_equity,
        "analyst_buy_ratio": snapshot.analyst_buy_ratio,
    }
    available = [value for value in values.values() if value is not None]
    if not available:
        return 50.0, 0.0
    parts = []
    if snapshot.eps_growth is not None:
        parts.append(_clamp(50 + snapshot.eps_growth * 200))
    if snapshot.revenue_growth is not None:
        parts.append(_clamp(50 + snapshot.revenue_growth * 200))
    if snapshot.roe is not None:
        parts.append(_clamp(50 + snapshot.roe * 150))
    if snapshot.debt_equity is not None:
        parts.append(_clamp(100 - snapshot.debt_equity * 25))
    if snapshot.analyst_buy_ratio is not None:
        parts.append(_clamp(snapshot.analyst_buy_ratio * 100))
    return sum(parts) / len(parts), len(available) / len(values)


def _latest_patterns(instrument) -> tuple[list[str], list[str]]:
    rows = list(
        DailyBar.objects.filter(instrument=instrument, is_valid=True).order_by("-trading_date")[
            :320
        ]
    )
    bars = [
        PriceBar(
            trading_date=row.trading_date,
            open=float(row.open),
            high=float(row.high),
            low=float(row.low),
            close=float(row.close),
            volume=row.volume,
        )
        for row in reversed(rows)
    ]
    features = build_pattern_features(bars)
    if not features:
        return [], []
    latest = features[-1]
    return sorted(latest.candle_patterns), sorted(latest.chart_patterns)


def generate_signals_for_instrument(instrument) -> list[TradeSignal]:
    try:
        snapshot = instrument.screening_snapshot
    except ScreeningSnapshot.DoesNotExist:
        return []

    candle_patterns, chart_patterns = _latest_patterns(instrument)
    all_patterns = set(candle_patterns + chart_patterns)
    bullish_count = len(all_patterns & BULLISH_PATTERNS)
    bearish_count = len(all_patterns & BEARISH_PATTERNS)
    bull_pattern = _clamp(50 + 14 * (bullish_count - bearish_count))
    fundamental, fundamental_completeness = _fundamental_score(snapshot)
    macro = 50.0
    signals = []

    for horizon, (return_field, average_field, return_scale) in HORIZON_CONFIG.items():
        close = float(snapshot.close or 0)
        average = getattr(snapshot, average_field)
        period_return = getattr(snapshot, return_field)
        trend = 50.0 if average is None else (80.0 if close > average else 20.0)
        momentum = 50.0 if period_return is None else _clamp(50 + period_return * return_scale)
        rsi = snapshot.rsi_14 if snapshot.rsi_14 is not None else 50.0
        rsi_score = _clamp(100 - abs(rsi - 60) * 3.0)
        macd_score = 50.0
        if snapshot.macd is not None and snapshot.macd_signal is not None:
            macd_score = 75.0 if snapshot.macd > snapshot.macd_signal else 25.0
        technical = 0.35 * trend + 0.30 * momentum + 0.20 * rsi_score + 0.15 * macd_score

        bull = 0.55 * technical + 0.20 * fundamental + 0.10 * macro + 0.15 * bull_pattern
        bear = (
            0.55 * (100 - technical)
            + 0.20 * (100 - fundamental)
            + 0.10 * (100 - macro)
            + 0.15 * (100 - bull_pattern)
        )
        is_bull = bull >= bear
        case_type = TradeSignal.CaseType.BULL if is_bull else TradeSignal.CaseType.BEAR
        score = round(max(bull, bear), 2)
        rationale = [
            f"Price {'above' if trend > 50 else 'below'} {average_field.replace('_', ' ').upper()}",
            f"{return_field.replace('_', ' ').upper()}: {(period_return or 0):.2%}",
            f"RSI(14): {rsi:.1f}",
        ]
        if all_patterns:
            rationale.append("Patterns: " + ", ".join(sorted(all_patterns)))
        else:
            rationale.append("No confirmed candle/chart pattern")
        signal, _ = TradeSignal.objects.update_or_create(
            instrument=instrument,
            horizon=horizon,
            defaults={
                "case_type": case_type,
                "as_of_date": snapshot.market_date,
                "price": Decimal(str(close)),
                "score": score,
                "technical_score": round(technical if is_bull else 100 - technical, 2),
                "fundamental_score": round(fundamental if is_bull else 100 - fundamental, 2),
                "macro_score": macro,
                "pattern_score": round(bull_pattern if is_bull else 100 - bull_pattern, 2),
                "data_completeness": round(0.75 + 0.25 * fundamental_completeness, 2),
                "candle_patterns": candle_patterns,
                "chart_patterns": chart_patterns,
                "rationale": rationale,
                "calculation_version": CALCULATION_VERSION,
            },
        )
        signals.append(signal)

    return signals
