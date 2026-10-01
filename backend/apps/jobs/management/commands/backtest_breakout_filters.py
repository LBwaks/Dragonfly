from __future__ import annotations

import json
from collections import defaultdict
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from analytics.breakout_backtest import (
    PriceBar,
    breakout_within,
    build_features,
    event_entry_positions,
    summarize,
)
from apps.market_data.models import DailyBar


class Command(BaseCommand):
    help = "Backtest the documented end-of-day Finviz-style breakout filters."

    def add_arguments(self, parser):
        parser.add_argument("--symbols", help="Comma-separated symbols; defaults to all with bars")
        parser.add_argument("--start", type=date.fromisoformat)
        parser.add_argument("--end", type=date.fromisoformat)
        parser.add_argument("--benchmark", default="SPY")
        parser.add_argument("--round-trip-cost-bps", type=float, default=20.0)
        parser.add_argument("--json", action="store_true", dest="as_json")

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
            benchmark_rows = DailyBar.objects.filter(
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
                for row in benchmark_rows
            ]
        benchmark_by_date = {bar.trading_date: bar for bar in benchmark_bars}

        eligible_symbols = {
            symbol: bars for symbol, bars in by_symbol.items() if len(bars) >= 313
        }
        if not eligible_symbols:
            raise CommandError("No symbols have enough bars for a 252-day setup and outcomes")

        horizons = (5, 10, 20)
        incidence_groups = (
            "liquid",
            "trend",
            "near_20d_high",
            "near_20d_50d_high",
            "near_breakout",
        )
        incidence: dict[str, dict[int, list[bool]]] = {
            group: {horizon: [] for horizon in horizons} for group in incidence_groups
        }
        setup_events: list[dict] = []
        all_breakout_trades: dict[int, list[float]] = {horizon: [] for horizon in (5, 20, 60)}
        setup_breakout_trades: dict[int, list[float]] = {
            horizon: [] for horizon in (5, 20, 60)
        }
        confirmed_trigger_trades: dict[int, list[float]] = {
            horizon: [] for horizon in (5, 20, 60)
        }
        setup_confirmed_trigger_trades: dict[int, list[float]] = {
            horizon: [] for horizon in (5, 20, 60)
        }
        all_excess_trades: dict[int, list[float]] = {horizon: [] for horizon in (5, 20, 60)}
        setup_excess_trades: dict[int, list[float]] = {
            horizon: [] for horizon in (5, 20, 60)
        }
        confirmed_trigger_excess: dict[int, list[float]] = {
            horizon: [] for horizon in (5, 20, 60)
        }
        setup_confirmed_trigger_excess: dict[int, list[float]] = {
            horizon: [] for horizon in (5, 20, 60)
        }
        signal_counts = {f"{group}_days": 0 for group in incidence_groups}
        period_start = None
        period_end = None
        one_way_cost = options["round_trip_cost_bps"] / 20_000

        for symbol, bars in eligible_symbols.items():
            features = build_features(bars)
            if not features:
                continue
            period_start = min(period_start or features[0].trading_date, features[0].trading_date)
            period_end = max(period_end or features[-1].trading_date, features[-1].trading_date)

            for position, feature in enumerate(features):
                for group in incidence:
                    if getattr(feature, group):
                        signal_counts[f"{group}_days"] += 1
                        for horizon in horizons:
                            incidence[group][horizon].append(
                                breakout_within(features, position, horizon)
                            )

            for position in event_entry_positions(
                features, attribute="near_breakout", cooldown=20
            ):
                feature = features[position]
                setup_events.append(
                    {
                        "symbol": symbol,
                        "date": feature.trading_date.isoformat(),
                        **{
                            f"breakout_within_{horizon}d": breakout_within(
                                features, position, horizon
                            )
                            for horizon in horizons
                        },
                    }
                )

            breakout_positions = event_entry_positions(
                features, attribute="breakout_20d", cooldown=20
            )
            near_dates = {feature.trading_date for feature in features if feature.near_breakout}
            for position in breakout_positions:
                feature = features[position]
                signal_index = feature.index
                preceded_by_setup = any(
                    bars[prior_index].trading_date in near_dates
                    for prior_index in range(max(0, signal_index - 10), signal_index)
                )
                entry_index = signal_index + 1
                if entry_index >= len(bars):
                    continue
                entry_bar = bars[entry_index]
                entry_price = entry_bar.open * (1 + one_way_cost)
                benchmark_entry = benchmark_by_date.get(entry_bar.trading_date)
                for horizon in (5, 20, 60):
                    exit_index = entry_index + horizon - 1
                    if exit_index >= len(bars):
                        continue
                    exit_bar = bars[exit_index]
                    net_return = (exit_bar.close * (1 - one_way_cost)) / entry_price - 1
                    all_breakout_trades[horizon].append(net_return)
                    if preceded_by_setup:
                        setup_breakout_trades[horizon].append(net_return)
                    if feature.confirmed_trigger:
                        confirmed_trigger_trades[horizon].append(net_return)
                        if preceded_by_setup:
                            setup_confirmed_trigger_trades[horizon].append(net_return)

                    benchmark_exit = benchmark_by_date.get(exit_bar.trading_date)
                    if benchmark_entry and benchmark_exit:
                        benchmark_return = benchmark_exit.close / benchmark_entry.open - 1
                        excess_return = net_return - benchmark_return
                        all_excess_trades[horizon].append(excess_return)
                        if preceded_by_setup:
                            setup_excess_trades[horizon].append(excess_return)
                        if feature.confirmed_trigger:
                            confirmed_trigger_excess[horizon].append(excess_return)
                            if preceded_by_setup:
                                setup_confirmed_trigger_excess[horizon].append(excess_return)

        incidence_summary = {}
        for group, by_horizon in incidence.items():
            incidence_summary[group] = {
                f"within_{horizon}d": {
                    "observations": len(outcomes),
                    "breakouts": sum(outcomes),
                    "rate": sum(outcomes) / len(outcomes) if outcomes else None,
                }
                for horizon, outcomes in by_horizon.items()
            }

        event_summary = {
            f"within_{horizon}d": {
                "events": len(setup_events),
                "breakouts": sum(event[f"breakout_within_{horizon}d"] for event in setup_events),
                "rate": (
                    sum(event[f"breakout_within_{horizon}d"] for event in setup_events)
                    / len(setup_events)
                    if setup_events
                    else None
                ),
            }
            for horizon in horizons
        }

        result = {
            "method": {
                "signal_time": "completed daily close",
                "entry_time": "next session open after 20-day breakout",
                "near_filter": (
                    "price>=10; prior-63d average volume>=500k; close>SMA20/50/200; "
                    "21d and 63d performance positive; 0-3% below prior 20d high; "
                    "0-5% below prior 50d high; 0-10% below prior 252d high"
                ),
                "round_trip_cost_bps": options["round_trip_cost_bps"],
                "breakout_event_cooldown_sessions": 20,
                "setup_lookback_before_breakout_sessions": 10,
                "confirmed_trigger": (
                    "20d new high; trend filter; relative volume>=1.5; "
                    "daily change>=2%; close>open"
                ),
            },
            "sample": {
                "symbols": len(eligible_symbols),
                "start": period_start.isoformat() if period_start else None,
                "end": period_end.isoformat() if period_end else None,
                **signal_counts,
                "unique_setup_events": len(setup_events),
            },
            "breakout_incidence_by_stock_day": incidence_summary,
            "unique_setup_event_outcomes": event_summary,
            "forward_net_returns_after_all_20d_breakouts": {
                f"{horizon}d": summarize(values)
                for horizon, values in all_breakout_trades.items()
            },
            "forward_net_returns_after_setup_preceded_breakouts": {
                f"{horizon}d": summarize(values)
                for horizon, values in setup_breakout_trades.items()
            },
            "forward_net_returns_after_confirmed_triggers": {
                f"{horizon}d": summarize(values)
                for horizon, values in confirmed_trigger_trades.items()
            },
            "forward_net_returns_after_setup_preceded_confirmed_triggers": {
                f"{horizon}d": summarize(values)
                for horizon, values in setup_confirmed_trigger_trades.items()
            },
            "forward_excess_returns_vs_benchmark_after_all_20d_breakouts": {
                f"{horizon}d": summarize(values)
                for horizon, values in all_excess_trades.items()
            },
            "forward_excess_returns_vs_benchmark_after_setup_preceded_breakouts": {
                f"{horizon}d": summarize(values)
                for horizon, values in setup_excess_trades.items()
            },
            "forward_excess_returns_vs_benchmark_after_confirmed_triggers": {
                f"{horizon}d": summarize(values)
                for horizon, values in confirmed_trigger_excess.items()
            },
            "forward_excess_returns_vs_benchmark_after_setup_preceded_confirmed_triggers": {
                f"{horizon}d": summarize(values)
                for horizon, values in setup_confirmed_trigger_excess.items()
            },
            "limitations": [
                "Current liquid large-cap universe creates survivorship and selection bias.",
                "Daily bars cannot reproduce intraday Finviz state or same-time relative volume.",
                (
                    "Market-cap membership is approximated by the curated universe, "
                    "not point-in-time data."
                ),
                (
                    "Stock-day incidence observations overlap; do not treat them as "
                    "independent trials."
                ),
                (
                    "The test does not include delisted stocks, borrow, taxes, or market "
                    "impact beyond costs."
                ),
            ],
        }

        rendered = json.dumps(result, indent=2, sort_keys=True)
        self.stdout.write(rendered)
