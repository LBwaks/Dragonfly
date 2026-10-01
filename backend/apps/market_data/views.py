from rest_framework.viewsets import ReadOnlyModelViewSet

from . import models, serializers


class MarketNewsViewSet(ReadOnlyModelViewSet):
    queryset = models.MarketNews.objects.order_by("-published_at")
    serializer_class = serializers.MarketNewsSerializer


class EarningsCalendarViewSet(ReadOnlyModelViewSet):
    queryset = models.EarningsEvent.objects.select_related("instrument").order_by("event_date")
    serializer_class = serializers.EarningsEventSerializer


class IpoCalendarViewSet(ReadOnlyModelViewSet):
    queryset = models.IpoEvent.objects.order_by("ipo_date")
    serializer_class = serializers.IpoEventSerializer
