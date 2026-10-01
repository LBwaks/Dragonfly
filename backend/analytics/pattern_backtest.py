from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import sqrt

from analytics.breakout_backtest import PriceBar

CANDLE_PATTERNS = (
    "long_lower_shadow",
    "long_upper_shadow",
    "hammer",
    "inverted_hammer",
    "spinning_top_white",
    "spinning_top_black",
    "doji",
    "dragonfly_doji",
    "gravestone_doji",
    "marubozu_white",
    "marubozu_black",
)

CHART_PATTERNS = (
    "horizontal_sr",
    "tl_resistance",
    "tl_support",
    "wedge_up",
    "wedge_down",
    "wedge",
    "triangle_ascending",
    "triangle_descending",
    "channel_up",
    "channel_down",
    "channel",
    "double_top",
    "double_bottom",
    "multiple_top",
    "multiple_bottom",
    "head_shoulders",
    "head_shoulders_inverse",
)


@dataclass(frozen=True)
class PatternFeature:
    index: int
    trading_date: date
    close: float
    pivot_20: float
    atr_14: float
    liquid: bool
    trend: bool
    near_20d_high: bool
    candle_patterns: frozenset[str]
    chart_patterns: frozenset[str]


def _average(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _linear_fit(values: Sequence[float], x_values: Sequence[float] | None = None):
    x = list(x_values) if x_values is not None else list(range(len(values)))
    y = list(values)
    x_mean = _average(x)
    y_mean = _average(y)
    denominator = sum((item - x_mean) ** 2 for item in x)
    slope = (
        sum(
            (x_item - x_mean) * (y_item - y_mean)
            for x_item, y_item in zip(x, y, strict=True)
        )
        / denominator
        if denominator
        else 0.0
    )
    intercept = y_mean - slope * x_mean
    rmse = sqrt(
        _average(
            [
                (y_item - (intercept + slope * x_item)) ** 2
                for x_item, y_item in zip(x, y, strict=True)
            ]
        )
    )
    return slope, intercept, rmse


def _atr(bars: Sequence[PriceBar], index: int, length: int = 14) -> float:
    true_ranges = []
    for position in range(index - length + 1, index + 1):
        previous_close = bars[position - 1].close
        bar = bars[position]
        true_ranges.append(
            max(bar.high - bar.low, abs(bar.high - previous_close), abs(bar.low - previous_close))
        )
    return _average(true_ranges)


def detect_candles(bars: Sequence[PriceBar], index: int, atr: float) -> frozenset[str]:
    bar = bars[index]
    candle_range = max(bar.high - bar.low, 1e-12)
    body = abs(bar.close - bar.open)
    upper_shadow = bar.high - max(bar.open, bar.close)
    lower_shadow = min(bar.open, bar.close) - bar.low
    body_ratio = body / candle_range
    upper_ratio = upper_shadow / candle_range
    lower_ratio = lower_shadow / candle_range
    close_location = (bar.close - bar.low) / candle_range
    patterns: set[str] = set()

    if lower_ratio >= 0.60 and close_location >= 0.50:
        patterns.add("long_lower_shadow")
    if upper_ratio >= 0.60 and close_location <= 0.50:
        patterns.add("long_upper_shadow")

    reference_body = max(body, candle_range * 0.05)
    if lower_shadow >= 2 * reference_body and upper_ratio <= 0.25 and close_location >= 0.65:
        patterns.add("hammer")
    if upper_shadow >= 2 * reference_body and lower_ratio <= 0.25 and close_location <= 0.35:
        patterns.add("inverted_hammer")

    spinning_top = body_ratio <= 0.35 and upper_ratio >= 0.15 and lower_ratio >= 0.15
    if spinning_top and bar.close >= bar.open:
        patterns.add("spinning_top_white")
    if spinning_top and bar.close < bar.open:
        patterns.add("spinning_top_black")

    doji = body_ratio <= 0.10
    if doji:
        patterns.add("doji")
    if doji and lower_ratio >= 0.60 and upper_ratio <= 0.10 and close_location >= 0.85:
        patterns.add("dragonfly_doji")
    if doji and upper_ratio >= 0.60 and lower_ratio <= 0.10 and close_location <= 0.15:
        patterns.add("gravestone_doji")

    sufficiently_large = candle_range >= 0.75 * atr
    if sufficiently_large and body_ratio >= 0.90 and bar.close > bar.open:
        patterns.add("marubozu_white")
    if sufficiently_large and body_ratio >= 0.90 and bar.close < bar.open:
        patterns.add("marubozu_black")
    return frozenset(patterns)


def _envelope_lines(window: Sequence[PriceBar]):
    bin_size = 5
    x_values: list[float] = []
    upper: list[float] = []
    lower: list[float] = []
    for start in range(0, 20, bin_size):
        subset = window[start : start + bin_size]
        x_values.append(start + (bin_size - 1) / 2)
        upper.append(max(bar.high for bar in subset))
        lower.append(min(bar.low for bar in subset))
    high_slope, high_intercept, high_rmse = _linear_fit(upper, x_values)
    low_slope, low_intercept, low_rmse = _linear_fit(lower, x_values)
    return (
        high_slope,
        high_intercept,
        high_rmse,
        low_slope,
        low_intercept,
        low_rmse,
    )


def _swing_points(window: Sequence[PriceBar], *, highs: bool) -> list[tuple[int, float]]:
    values = [bar.high if highs else bar.low for bar in window]
    points = []
    for index in range(2, len(window) - 2):
        neighbors = values[index - 2 : index] + values[index + 1 : index + 3]
        if highs and values[index] >= max(neighbors):
            points.append((index, values[index]))
        if not highs and values[index] <= min(neighbors):
            points.append((index, values[index]))
    return points


def detect_chart_patterns(
    bars: Sequence[PriceBar], index: int, atr: float
) -> frozenset[str]:
    window = bars[index - 29 : index + 1]
    line_window = window[-20:]
    price = max(bars[index].close, 1e-12)
    (
        high_slope,
        high_intercept,
        high_rmse,
        low_slope,
        low_intercept,
        low_rmse,
    ) = _envelope_lines(line_window)
    high_slope_n = high_slope / price
    low_slope_n = low_slope / price
    horizontal_limit = 0.0008
    directional_limit = 0.0004
    parallel_limit = 0.0008
    high_fit = high_rmse <= max(atr, price * 0.02)
    low_fit = low_rmse <= max(atr, price * 0.02)
    high_now = high_intercept + high_slope * 19
    low_now = low_intercept + low_slope * 19
    high_start = high_intercept
    low_start = low_intercept
    width_start = max(high_start - low_start, 1e-12)
    width_now = max(high_now - low_now, 1e-12)
    converging = width_now <= 0.85 * width_start
    stable_width = abs(width_now / width_start - 1) <= 0.25
    parallel = abs(high_slope_n - low_slope_n) <= parallel_limit
    near_resistance = abs(high_now - bars[index].close) <= atr
    near_support = abs(bars[index].close - low_now) <= atr

    high_horizontal = abs(high_slope_n) <= horizontal_limit
    low_horizontal = abs(low_slope_n) <= horizontal_limit
    high_positive = high_slope_n >= directional_limit
    low_positive = low_slope_n >= directional_limit
    high_negative = high_slope_n <= -directional_limit
    low_negative = low_slope_n <= -directional_limit

    patterns: set[str] = set()
    if high_fit and near_resistance:
        patterns.add("tl_resistance")
    if low_fit and near_support:
        patterns.add("tl_support")
    if high_horizontal and high_fit and near_resistance:
        patterns.add("horizontal_sr")
    if high_horizontal and low_horizontal and high_fit and low_fit and stable_width:
        patterns.add("channel")
    if high_horizontal and low_positive and converging and high_fit and low_fit:
        patterns.add("triangle_ascending")
    if low_horizontal and high_negative and converging and high_fit and low_fit:
        patterns.add("triangle_descending")
    if high_negative and low_positive and converging and high_fit and low_fit:
        patterns.add("wedge")
    if high_positive and low_positive and low_slope > high_slope and converging:
        patterns.add("wedge_up")
    if high_negative and low_negative and high_slope < low_slope and converging:
        patterns.add("wedge_down")
    if high_positive and low_positive and parallel and stable_width:
        patterns.add("channel_up")
    if high_negative and low_negative and parallel and stable_width:
        patterns.add("channel_down")

    peaks = _swing_points(window, highs=True)
    troughs = _swing_points(window, highs=False)
    tolerance = max(0.01 * price, 0.75 * atr)
    prior_change = bars[index].close / bars[index - 29].close - 1

    if len(peaks) >= 2:
        last_two = peaks[-2:]
        separated = last_two[1][0] - last_two[0][0] >= 4
        if separated and abs(last_two[1][1] - last_two[0][1]) <= tolerance and prior_change > 0:
            patterns.add("double_top")
    if len(peaks) >= 3:
        last_three = peaks[-3:]
        values = [item[1] for item in last_three]
        if max(values) - min(values) <= tolerance and prior_change > 0:
            patterns.add("multiple_top")
        shoulders_close = abs(values[0] - values[2]) <= tolerance
        if shoulders_close and values[1] >= max(values[0], values[2]) + 0.5 * atr:
            patterns.add("head_shoulders")

    if len(troughs) >= 2:
        last_two = troughs[-2:]
        separated = last_two[1][0] - last_two[0][0] >= 4
        if separated and abs(last_two[1][1] - last_two[0][1]) <= tolerance and prior_change < 0:
            patterns.add("double_bottom")
    if len(troughs) >= 3:
        last_three = troughs[-3:]
        values = [item[1] for item in last_three]
        if max(values) - min(values) <= tolerance and prior_change < 0:
            patterns.add("multiple_bottom")
        shoulders_close = abs(values[0] - values[2]) <= tolerance
        if shoulders_close and values[1] <= min(values[0], values[2]) - 0.5 * atr:
            patterns.add("head_shoulders_inverse")
    return frozenset(patterns)


def build_pattern_features(
    bars: Sequence[PriceBar],
    *,
    minimum_price: float = 10.0,
    minimum_average_volume: int = 500_000,
) -> list[PatternFeature]:
    if len(bars) < 253:
        return []
    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    volumes = [float(bar.volume) for bar in bars]
    features = []
    for index in range(252, len(bars)):
        close = closes[index]
        pivot_20 = max(highs[index - 20 : index])
        average_volume_63 = _average(volumes[index - 63 : index])
        liquid = close >= minimum_price and average_volume_63 >= minimum_average_volume
        trend = (
            liquid
            and close > _average(closes[index - 19 : index + 1])
            and close > _average(closes[index - 49 : index + 1])
            and close > _average(closes[index - 199 : index + 1])
            and close > closes[index - 21]
            and close > closes[index - 63]
        )
        distance = (pivot_20 - close) / pivot_20
        near_20d_high = liquid and 0 <= distance <= 0.03
        atr = _atr(bars, index)
        features.append(
            PatternFeature(
                index=index,
                trading_date=bars[index].trading_date,
                close=close,
                pivot_20=pivot_20,
                atr_14=atr,
                liquid=liquid,
                trend=trend,
                near_20d_high=near_20d_high,
                candle_patterns=detect_candles(bars, index, atr),
                chart_patterns=detect_chart_patterns(bars, index, atr),
            )
        )
    return features


def active_groups(feature: PatternFeature) -> set[str]:
    groups: set[str] = set()
    baseline = feature.trend and feature.near_20d_high
    near = feature.liquid and feature.near_20d_high
    if baseline:
        groups.add("baseline:trend_near_20d")
    for pattern in feature.candle_patterns:
        if baseline:
            groups.add(f"baseline+candle:{pattern}")
    for pattern in feature.chart_patterns:
        if near:
            groups.add(f"near+chart:{pattern}")
        if baseline:
            groups.add(f"baseline+chart:{pattern}")

    spinning_or_doji = bool(
        feature.candle_patterns
        & {"doji", "spinning_top_white", "spinning_top_black"}
    )
    lower_rejection = bool(
        feature.candle_patterns & {"long_lower_shadow", "hammer", "dragonfly_doji"}
    )
    continuation = feature.chart_patterns & {
        "triangle_ascending",
        "horizontal_sr",
        "channel",
        "wedge",
    }
    reversal = feature.chart_patterns & {
        "wedge_down",
        "double_bottom",
        "multiple_bottom",
        "head_shoulders_inverse",
    }
    for pattern in continuation:
        if baseline and spinning_or_doji:
            groups.add(f"combo:{pattern}+compression_candle")
        if baseline and lower_rejection:
            groups.add(f"combo:{pattern}+lower_rejection")
    for pattern in reversal:
        if near and lower_rejection:
            groups.add(f"combo:{pattern}+lower_rejection")
    return groups


def crossed_within(
    features: Sequence[PatternFeature], position: int, horizon: int, *, buffer_atr: float = 0.10
) -> bool:
    signal = features[position]
    threshold = signal.pivot_20 + buffer_atr * signal.atr_14
    end = min(len(features), position + horizon + 1)
    return any(feature.close > threshold for feature in features[position + 1 : end])


def accepted_within(
    features: Sequence[PatternFeature],
    position: int,
    horizon: int = 10,
    *,
    buffer_atr: float = 0.10,
) -> bool:
    signal = features[position]
    threshold = signal.pivot_20 + buffer_atr * signal.atr_14
    end = min(len(features), position + horizon + 1)
    closes_above = sum(feature.close > threshold for feature in features[position + 1 : end])
    return closes_above >= 2
