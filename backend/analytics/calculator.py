from collections.abc import Iterable, Mapping
from typing import Any

import polars as pl

CALCULATION_VERSION = "1.0.0"


def calculate_technicals(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    frame = pl.DataFrame(list(rows))
    if frame.is_empty():
        return []
    required = {"trading_date", "open", "high", "low", "close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {', '.join(sorted(missing))}")

    frame = frame.sort("trading_date").with_columns(
        pl.col("open").cast(pl.Float64),
        pl.col("high").cast(pl.Float64),
        pl.col("low").cast(pl.Float64),
        pl.col("close").cast(pl.Float64),
        pl.col("volume").cast(pl.Float64),
    )
    price = pl.coalesce(["adjusted_close", "close"]).cast(pl.Float64)
    frame = frame.with_columns(price.alias("_price"))

    delta = pl.col("_price").diff()
    gain = delta.clip(lower_bound=0).ewm_mean(alpha=1 / 14, adjust=False, min_samples=14)
    loss = (-delta.clip(upper_bound=0)).ewm_mean(alpha=1 / 14, adjust=False, min_samples=14)
    previous_close = pl.col("_price").shift(1)
    true_range = pl.max_horizontal(
        pl.col("high") - pl.col("low"),
        (pl.col("high") - previous_close).abs(),
        (pl.col("low") - previous_close).abs(),
    )
    ema_12 = pl.col("_price").ewm_mean(span=12, adjust=False)
    ema_26 = pl.col("_price").ewm_mean(span=26, adjust=False)

    frame = frame.with_columns(
        pl.col("_price").rolling_mean(20).alias("sma_20"),
        pl.col("_price").rolling_mean(50).alias("sma_50"),
        pl.col("_price").rolling_mean(100).alias("sma_100"),
        pl.col("_price").rolling_mean(200).alias("sma_200"),
        ema_12.alias("ema_12"),
        ema_26.alias("ema_26"),
        (100 - (100 / (1 + gain / loss))).alias("rsi_14"),
        (ema_12 - ema_26).alias("macd"),
        true_range.rolling_mean(14).alias("atr_14"),
        pl.col("volume").rolling_mean(20).alias("avg_volume_20"),
        pl.col("_price").rolling_max(20).alias("high_20"),
        pl.col("_price").rolling_max(50).alias("high_50"),
        pl.col("_price").rolling_max(252).alias("high_252"),
        pl.col("_price").rolling_min(20).alias("low_20"),
        pl.col("_price").rolling_min(50).alias("low_50"),
    )
    frame = frame.with_columns(
        pl.col("macd").ewm_mean(span=9, adjust=False).alias("macd_signal"),
        pl.col("_price").rolling_std(20).alias("_std_20"),
        (pl.col("volume") / pl.col("avg_volume_20")).alias("relative_volume"),
        (pl.col("volume") / pl.col("volume").shift(20) - 1).alias("volume_change_20"),
        *[
            (pl.col("_price") / pl.col("_price").shift(period) - 1).alias(f"return_{label}")
            for period, label in [(1, "1d"), (5, "5d"), (20, "20d"), (50, "50d"), (252, "252d")]
        ],
        (pl.col("atr_14") / pl.col("_price")).alias("atr_pct"),
        (pl.col("_price") / pl.col("high_20") - 1).alias("distance_high_20"),
        (pl.col("_price") / pl.col("high_252") - 1).alias("distance_high_252"),
    )
    frame = frame.with_columns(
        (pl.col("macd") - pl.col("macd_signal")).alias("macd_histogram"),
        (pl.col("sma_20") + 2 * pl.col("_std_20")).alias("bollinger_upper"),
        pl.col("sma_20").alias("bollinger_middle"),
        (pl.col("sma_20") - 2 * pl.col("_std_20")).alias("bollinger_lower"),
        (4 * pl.col("_std_20") / pl.col("sma_20")).alias("bollinger_width"),
        pl.col("_price").alias("close"),
    ).drop("_price", "_std_20")
    return frame.to_dicts()
