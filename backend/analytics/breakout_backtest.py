from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from statistics import mean, median


@dataclass(frozen=True)
class PriceBar:
    trading_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class BreakoutFeature:
    index: int
    trading_date: date
    liquid: bool
    trend: bool
    near_20d_high: bool
    near_20d_50d_high: bool
    near_breakout: bool
    breakout_20d: bool
    confirmed_trigger: bool


def _average(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def build_features(
    bars: Sequence[PriceBar],
    *,
    minimum_price: float = 10.0,
    minimum_average_volume: int = 500_000,
) -> list[BreakoutFeature]:
    """Build point-in-time versions of the proposed Finviz filters.

    The current bar is deliberately excluded from rolling highs and average volume.
    Moving averages and performance include the completed current close, matching an
    end-of-day screen that is acted on no earlier than the next session.
    """
    if len(bars) < 253:
        return []

    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    volumes = [float(bar.volume) for bar in bars]
    features: list[BreakoutFeature] = []

    for index in range(252, len(bars)):
        close = closes[index]
        prior_high_20 = max(highs[index - 20 : index])
        prior_high_50 = max(highs[index - 50 : index])
        prior_high_252 = max(highs[index - 252 : index])
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

        distance_20 = (prior_high_20 - close) / prior_high_20
        distance_50 = (prior_high_50 - close) / prior_high_50
        distance_252 = (prior_high_252 - close) / prior_high_252
        near_20d_high = trend and 0 <= distance_20 <= 0.03
        near_20d_50d_high = near_20d_high and 0 <= distance_50 <= 0.05
        near_breakout = near_20d_50d_high and 0 <= distance_252 <= 0.10
        breakout_20d = liquid and close > prior_high_20
        confirmed_trigger = (
            breakout_20d
            and trend
            and volumes[index] / average_volume_63 >= 1.5
            and close / closes[index - 1] - 1 >= 0.02
            and close > bars[index].open
        )

        features.append(
            BreakoutFeature(
                index=index,
                trading_date=bars[index].trading_date,
                liquid=liquid,
                trend=trend,
                near_20d_high=near_20d_high,
                near_20d_50d_high=near_20d_50d_high,
                near_breakout=near_breakout,
                breakout_20d=breakout_20d,
                confirmed_trigger=confirmed_trigger,
            )
        )
    return features


def breakout_within(
    features: Sequence[BreakoutFeature], feature_position: int, horizon: int
) -> bool:
    end = min(len(features), feature_position + horizon + 1)
    return any(item.breakout_20d for item in features[feature_position + 1 : end])


def event_entry_positions(
    features: Sequence[BreakoutFeature],
    *,
    attribute: str,
    cooldown: int,
) -> list[int]:
    """Return non-overlapping state-entry positions for a boolean feature."""
    positions: list[int] = []
    previous_value = False
    last_position = -cooldown - 1
    for position, feature in enumerate(features):
        value = bool(getattr(feature, attribute))
        if value and not previous_value and position - last_position > cooldown:
            positions.append(position)
            last_position = position
        previous_value = value
    return positions


def summarize(values: Iterable[float]) -> dict[str, float | int | None]:
    observations = list(values)
    if not observations:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "win_rate": None,
            "minimum": None,
            "maximum": None,
        }
    return {
        "count": len(observations),
        "mean": mean(observations),
        "median": median(observations),
        "win_rate": sum(value > 0 for value in observations) / len(observations),
        "minimum": min(observations),
        "maximum": max(observations),
    }
