# Create your views here.
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Screener, ScreenerRun, TradeSignal
from .serializers import (
    ScreenerMatchSerializer,
    ScreenerRunSerializer,
    ScreenerSerializer,
    TradeSignalSerializer,
)
from .services import run_screener


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.created_by_id == request.user.id


class ScreenerViewSet(ModelViewSet):
    queryset = Screener.objects.all()
    serializer_class = ScreenerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = self.queryset
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        return (
            queryset
            if self.request.user.is_staff
            else queryset.filter(created_by=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        return Response(ScreenerRunSerializer(run_screener(self.get_object())).data, status=201)

    @action(detail=True)
    def runs(self, request, pk=None):
        page = self.paginate_queryset(self.get_object().runs.all())
        return self.get_paginated_response(ScreenerRunSerializer(page, many=True).data)


class ScreenerRunViewSet(ReadOnlyModelViewSet):
    queryset = ScreenerRun.objects.all()
    serializer_class = ScreenerRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related("screener")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        return (
            queryset
            if self.request.user.is_staff
            else queryset.filter(screener__created_by=self.request.user)
        )

    @action(detail=True)
    def matches(self, request, pk=None):
        page = self.paginate_queryset(self.get_object().matches.select_related("instrument"))
        return self.get_paginated_response(ScreenerMatchSerializer(page, many=True).data)


class TradeSignalViewSet(ReadOnlyModelViewSet):
    serializer_class = TradeSignalSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["case_type", "horizon", "instrument"]

    def get_queryset(self):
        return TradeSignal.objects.select_related("instrument").all()
