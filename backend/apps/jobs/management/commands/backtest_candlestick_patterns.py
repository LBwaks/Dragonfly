from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from analytics.breakout_backtest import PriceBar, summarize
from analytics.pattern_backtest import (
    CANDLE_PATTERNS,
    CHART_PATTERNS,
    accepted_within,
    active_groups,
    build_pattern_features,
    crossed_within,
)
from apps.market_data.models import DailyBar


class Command(BaseCommand):
    help = "Backtest transparent Finviz-style candlestick and chart-pattern approximations."

    def add_arguments(self, parser):
        parser.add_argument("--symbols", help="Comma-separated symbols; defaults to all with bars")
        parser.add_argument("--start", type=date.fromisoformat)
        parser.add_argument("--end", type=date.fromisoformat)
        parser.add_argument("--benchmark", default="SPY")
        parser.add_argument("--round-trip-cost-bps", type=float, default=20.0)
        parser.add_argument("--cooldown", type=int, default=20)
        parser.add_argument("--output", help="Optional JSON output path")

    def handle(self, *args, **options):
        requested = None
        if options["symbols"]:
            requested = {symbol.strip().upper() for symbol in options["symbols"].split(",")}

        queryset = DailyBar.objects.filter(is_valid=True).select_related("instrument")
        if requested:
            queryset = queryset.filter(instrument__symbol__in=requested)
        if options["start"]:
            queryset = queryset.filter(trading_date__gte=options["start"])
        if options["end"]:
            queryset = queryset.filter(trading_date__lte=options["end"])
        queryset = queryset.order_by("instrument__symbol", "trading_date")

        by_symbol: dict[str, list[PriceBar]] = defaultdict(list)
        for row in queryset.iterator():
            by_symbol[row.instrument.symbol].append(
                PriceBar(
                    trading_date=row.trading_date,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.adjusted_close or row.close),
                    volume=row.volume,
                )
            )

        benchmark_symbol = options["benchmark"].upper()
        benchmark_bars = by_symbol.pop(benchmark_symbol, None)
        if benchmark_bars is None:
            rows = DailyBar.objects.filter(
                is_valid=True, instrument__symbol=benchmark_symbol
            ).order_by("trading_date")
            benchmark_bars = [
                PriceBar(
                    trading_date=row.trading_date,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.adjusted_close or row.close),
                    volume=row.volume,
                )
                for row in rows
            ]
        benchmark_by_date = {bar.trading_date: bar for bar in benchmark_bars}

        eligible = {symbol: bars for symbol, bars in by_symbol.items() if len(bars) >= 313}
        if not eligible:
            raise CommandError("No symbols have enough bars for setup and forward outcomes")

        group_events: dict[str, list[dict]] = defaultdict(list)
        pattern_day_counts: dict[str, int] = defaultdict(int)
        period_start = None
        period_end = None
        one_way_cost = options["round_trip_cost_bps"] / 20_000

        for symbol, bars in eligible.items():
            features = build_pattern_features(bars)
            if not features:
                continue
            period_start = min(period_start or features[0].trading_date, features[0].trading_date)
            period_end = max(period_end or features[-1].trading_date, features[-1].trading_date)
            previous_groups: set[str] = set()
            last_event_position: dict[str, int] = {}

            for position, feature in enumerate(features):
                groups = active_groups(feature)
                for group in groups:
                    pattern_day_counts[group] += 1
                new_groups = groups - previous_groups
                for group in new_groups:
                    last_position = last_event_position.get(group, -options["cooldown"] - 1)
                    if position - last_position <= options["cooldown"]:
                        continue
                    last_event_position[group] = position
                    entry_index = feature.index + 1
                    if entry_index >= len(bars):
                        continue
                    event = {
                        "symbol": symbol,
                        "date": feature.trading_date.isoformat(),
                        "cross_5d": crossed_within(features, position, 5),
                        "cross_10d": crossed_within(features, position, 10),
                        "accepted_10d": accepted_within(features, position, 10),
                    }
                    entry_bar = bars[entry_index]
                    entry_price = entry_bar.open * (1 + one_way_cost)
                    benchmark_entry = benchmark_by_date.get(entry_bar.trading_date)
                    for horizon in (5, 20, 60):
                        exit_index = entry_index + horizon - 1
                        if exit_index >= len(bars):
                            continue
                        exit_bar = bars[exit_index]
                        net_return = exit_bar.close * (1 - one_way_cost) / entry_price - 1
                        event[f"return_{horizon}d"] = net_return
                        benchmark_exit = benchmark_by_date.get(exit_bar.trading_date)
                        if benchmark_entry and benchmark_exit:
                            benchmark_return = benchmark_exit.close / benchmark_entry.open - 1
                            event[f"excess_{horizon}d"] = net_return - benchmark_return
                    group_events[group].append(event)
                previous_groups = groups

        summaries = {}
        for group, events in group_events.items():
            summaries[group] = {
                "pattern_days": pattern_day_counts[group],
                "events": len(events),
                "cross_5d": sum(event["cross_5d"] for event in events) / len(events),
                "cross_10d": sum(event["cross_10d"] for event in events) / len(events),
                "accepted_10d": sum(event["accepted_10d"] for event in events) / len(events),
                "forward_net_returns": {
                    f"{horizon}d": summarize(
                        event[f"return_{horizon}d"]
                        for event in events
                        if f"return_{horizon}d" in event
                    )
                    for horizon in (5, 20, 60)
                },
                "forward_excess_returns_vs_benchmark": {
                    f"{horizon}d": summarize(
                        event[f"excess_{horizon}d"]
                        for event in events
                        if f"excess_{horizon}d" in event
                    )
                    for horizon in (5, 20, 60)
                },
            }

        baseline = summaries.get("baseline:trend_near_20d", {})
        baseline_cross = baseline.get("cross_5d")
        for summary in summaries.values():
            summary["cross_5d_lift_vs_baseline"] = (
                summary["cross_5d"] - baseline_cross if baseline_cross is not None else None
            )

        result = {
            "method": {
                "signal_time": "completed daily close; entry at next session open",
                "breakout_boundary": "maximum high of prior 20 completed sessions",
                "crossing_buffer": "0.10 ATR14 above the stored boundary",
                "acceptance": "at least two closes above the buffered boundary within 10 sessions",
                "baseline": (
                    "price>=10; prior-63d average volume>=500k; close>SMA20/50/200; "
                    "21d and 63d returns positive; close 0-3% below prior 20d high"
                ),
                "pattern_note": (
                    "Transparent OHLC approximations; not a reproduction of undisclosed "
                    "Finviz detection tolerances"
                ),
                "round_trip_cost_bps": options["round_trip_cost_bps"],
                "event_cooldown_sessions": options["cooldown"],
            },
            "sample": {
                "symbols": len(eligible),
                "start": period_start.isoformat() if period_start else None,
                "end": period_end.isoformat() if period_end else None,
                "benchmark": benchmark_symbol,
            },
            "patterns_tested": {
                "candlesticks": CANDLE_PATTERNS,
                "charts": CHART_PATTERNS,
            },
            "group_results": dict(sorted(summaries.items())),
            "limitations": [
                "Current active-stock universe creates survivorship and selection bias.",
                "Pattern tolerances are documented approximations, not Finviz proprietary rules.",
                "Daily bars cannot reproduce intraday screen state or same-time relative volume.",
                (
                    "Events can remain correlated across symbols and dates despite "
                    "per-symbol cooldown."
                ),
                "No multiple-testing-adjusted p-values are reported in this exploratory pass.",
                "Market impact, taxes, and gap-through-stop losses are not modeled.",
            ],
        }
        rendered = json.dumps(result, indent=2, sort_keys=True)
        if options["output"]:
            output = Path(options["output"])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered + "\n", encoding="utf-8")
            self.stderr.write(self.style.SUCCESS(f"Wrote {output}"))
        self.stdout.write(rendered)
