"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.instruments.views import InstrumentViewSet
from apps.jobs.views import JobRunViewSet
from apps.market_data.models import DomainFreshness
from apps.market_data.serializers import DomainFreshnessSerializer
from apps.market_data.views import EarningsCalendarViewSet, IpoCalendarViewSet, MarketNewsViewSet
from apps.screeners.views import ScreenerRunViewSet, ScreenerViewSet, TradeSignalViewSet


@require_GET
def live(_request):
    return JsonResponse({"status": "ok"})


@require_GET
def ready(_request):
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except OperationalError:
        return JsonResponse({"status": "unavailable", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})


router = DefaultRouter()
router.register("instruments", InstrumentViewSet, basename="instrument")
router.register("screeners", ScreenerViewSet, basename="screener")
router.register("screener-runs", ScreenerRunViewSet, basename="screener-run")
router.register("trade-signals", TradeSignalViewSet, basename="trade-signal")
router.register("system/jobs", JobRunViewSet, basename="job-run")
router.register("market/news", MarketNewsViewSet, basename="market-news")
router.register("market/earnings-calendar", EarningsCalendarViewSet, basename="earnings-calendar")
router.register("market/ipo-calendar", IpoCalendarViewSet, basename="ipo-calendar")


@require_GET
def data_health(_request):
    rows = DomainFreshness.objects.order_by("domain")
    return JsonResponse({"domains": DomainFreshnessSerializer(rows, many=True).data})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live", live, name="health-live"),
    path("health/ready", ready, name="health-ready"),
    path("health/data", data_health, name="health-data"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include(router.urls)),
]
