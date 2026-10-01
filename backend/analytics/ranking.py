from collections.abc import Mapping, Sequence
from typing import Any

DEFAULT_WEIGHTS = {
    "trend": 0.30,
    "momentum": 0.25,
    "volume": 0.20,
    "price_structure": 0.15,
    "volatility": 0.10,
}


def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    expected = set(DEFAULT_WEIGHTS)
    if set(weights) != expected:
        raise ValueError(f"Ranking weights must contain: {', '.join(sorted(expected))}")
    normalized = {key: float(value) for key, value in weights.items()}
    if any(value < 0 for value in normalized.values()):
        raise ValueError("Ranking weights cannot be negative")
    if abs(sum(normalized.values()) - 1.0) > 1e-9:
        raise ValueError("Ranking weights must sum to 1.0")
    return normalized


def component_scores(row: Any) -> dict[str, float]:
    def value(name: str, default: float = 0.0) -> float:
        raw = getattr(row, name, None)
        return default if raw is None else float(raw)

    trend = 50 + 25 * (value("close") > value("sma_50")) + 25 * (value("sma_50") > value("sma_200"))
    rsi = value("rsi_14", 50)
    momentum = max(0, min(100, 50 + value("return_20d") * 250 + (rsi - 50)))
    volume = max(0, min(100, value("relative_volume", 1) * 50))
    structure = max(0, min(100, 100 + value("distance_high_252") * 200))
    volatility = max(0, min(100, 100 - value("atr_pct") * 1000))
    return {
        "trend": float(trend),
        "momentum": momentum,
        "volume": volume,
        "price_structure": structure,
        "volatility": volatility,
    }


def rank_rows(
    rows: Sequence[Any], weights: Mapping[str, float] | None = None
) -> list[tuple[Any, float, dict[str, float]]]:
    weights = validate_weights(weights or DEFAULT_WEIGHTS)
    scored = []
    for row in rows:
        components = component_scores(row)
        total = sum(components[key] * weights[key] for key in weights)
        scored.append((row, round(total, 6), components))
    return sorted(scored, key=lambda item: (-item[1], item[0].instrument.symbol))
