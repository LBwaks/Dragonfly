from datetime import timedelta

import django_filters
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from providers.capabilities import ProviderCapability
from providers.errors import ProviderError
from providers.routing import call_with_fallback
from providers.runtime import build_provider_registry

from .models import Instrument
from .serializers import InstrumentSerializer


class InstrumentFilter(django_filters.FilterSet):
    symbol = django_filters.CharFilter(field_name="symbol", lookup_expr="iexact")
    exchange = django_filters.CharFilter(field_name="exchange", lookup_expr="iexact")
    sector = django_filters.CharFilter(field_name="sector", lookup_expr="iexact")
    industry = django_filters.CharFilter(field_name="industry", lookup_expr="iexact")
    active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Instrument
        fields = ("symbol", "exchange", "sector", "industry", "active")


class InstrumentViewSet(ReadOnlyModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    filterset_class = InstrumentFilter
    permission_classes = [AllowAny]

    def _many(self, request, queryset, serializer_class):
        page = self.paginate_queryset(queryset)
        serializer = serializer_class(page if page is not None else queryset, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @action(detail=True)
    def prices(self, request, pk=None):
        from apps.market_data.serializers import DailyBarSerializer

        bars = self.get_object().daily_bars.filter(is_valid=True).order_by("-trading_date")
        return Response(DailyBarSerializer(bars, many=True).data)

    @action(detail=True)
    def intraday(self, request, pk=None):
        timeframe = request.query_params.get("timeframe", "5Min")
        windows = {
            "5Min": 10,
            "15Min": 30,
            "30Min": 60,
            "1Hour": 180,
            "4Hour": 730,
        }
        if timeframe not in windows:
            return Response(
                {"detail": "timeframe must be one of 5Min, 15Min, 30Min, 1Hour, 4Hour"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instrument = self.get_object()
        end = timezone.now()
        start = end - timedelta(days=windows[timeframe])
        try:
            bars = call_with_fallback(
                build_provider_registry(),
                ProviderCapability.INTRADAY_OHLCV,
                "get_intraday_bars",
                instrument.symbol,
                timeframe,
                start,
                end,
            )
        except ProviderError as exc:
            return Response(
                {"detail": str(exc), "provider": exc.provider},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            [
                {
                    "timestamp": bar.timestamp,
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                    "provider": bar.provider,
                }
                for bar in bars
            ]
        )

    @action(detail=True, url_path="live-price")
    def live_price(self, request, pk=None):
        instrument = self.get_object()
        registry = build_provider_registry()
        try:
            bar = call_with_fallback(
                registry,
                ProviderCapability.INTRADAY_OHLCV,
                "get_latest_bar",
                instrument.symbol,
            )
        except ProviderError as exc:
            return Response(
                {"detail": str(exc), "provider": exc.provider},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if instrument.price_as_of is None or bar.timestamp > instrument.price_as_of:
            instrument.latest_price = bar.close
            instrument.price_as_of = bar.timestamp
            instrument.price_provider = bar.provider
            instrument.save(
                update_fields=["latest_price", "price_as_of", "price_provider", "updated_at"]
            )
        return Response(
            {
                "symbol": instrument.symbol,
                "price": bar.close,
                "as_of": bar.timestamp,
                "provider": bar.provider,
                "feed": getattr(
                    registry.get_provider(ProviderCapability.INTRADAY_OHLCV),
                    "data_feed",
                    "",
                ),
            }
        )

    @action(detail=True)
    def technicals(self, request, pk=None):
        from apps.technicals.serializers import TechnicalDailySerializer

        rows = self.get_object().technical_history.order_by("-trading_date")[:320]
        return Response(
            TechnicalDailySerializer(rows, many=True).data,
        )

    @action(detail=True)
    def signals(self, request, pk=None):
        from apps.screeners.serializers import TradeSignalSerializer

        return self._many(
            request,
            self.get_object().trade_signals.order_by("horizon"),
            TradeSignalSerializer,
        )

    @action(detail=True)
    def profile(self, request, pk=None):
        from apps.market_data.models import InstrumentSnapshot
        from apps.market_data.serializers import InstrumentSnapshotSerializer

        return self._many(
            request,
            InstrumentSnapshot.objects.filter(instrument=self.get_object()).order_by("-as_of_date"),
            InstrumentSnapshotSerializer,
        )

    @action(detail=True)
    def fundamentals(self, request, pk=None):
        from apps.market_data.models import FundamentalSnapshot
        from apps.market_data.serializers import FundamentalSnapshotSerializer

        return self._many(
            request,
            FundamentalSnapshot.objects.filter(instrument=self.get_object()).order_by(
                "-as_of_date"
            ),
            FundamentalSnapshotSerializer,
        )

    @action(detail=True)
    def peers(self, request, pk=None):
        from apps.market_data.models import PeerRelationship
        from apps.market_data.serializers import PeerRelationshipSerializer

        return self._many(
            request,
            PeerRelationship.objects.filter(instrument=self.get_object()),
            PeerRelationshipSerializer,
        )

    @action(detail=True)
    def news(self, request, pk=None):
        from apps.market_data.serializers import CompanyNewsSerializer

        return self._many(
            request, self.get_object().news.order_by("-published_at"), CompanyNewsSerializer
        )

    @action(detail=True)
    def filings(self, request, pk=None):
        from apps.market_data.serializers import SecFilingSerializer

        return self._many(
            request, self.get_object().filings.order_by("-filing_date"), SecFilingSerializer
        )

    @action(detail=True)
    def insiders(self, request, pk=None):
        from apps.market_data.serializers import InsiderTransactionSerializer

        return self._many(
            request,
            self.get_object().insider_transactions.order_by("-transaction_date"),
            InsiderTransactionSerializer,
        )

    @action(detail=True)
    def analysts(self, request, pk=None):
        from apps.market_data.serializers import AnalystRecommendationSerializer

        return self._many(
            request,
            self.get_object().analyst_recommendations.order_by("-period"),
            AnalystRecommendationSerializer,
        )

    @action(detail=True)
    def earnings(self, request, pk=None):
        from apps.market_data.serializers import EarningsResultSerializer

        return self._many(
            request,
            self.get_object().earnings_results.order_by("-report_date"),
            EarningsResultSerializer,
        )
