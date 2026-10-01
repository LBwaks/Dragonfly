from rest_framework import serializers

from .dsl import RuleValidationError, validate_rules
from .models import Screener, ScreenerMatch, ScreenerRun, TradeSignal


class ScreenerSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Screener
        fields = "__all__"
        read_only_fields = ("is_builtin", "created_at", "updated_at")

    def validate_rules(self, value):
        try:
            return validate_rules(value)
        except RuleValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ScreenerMatchSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="instrument.symbol", read_only=True)

    class Meta:
        model = ScreenerMatch
        fields = "__all__"


class ScreenerRunSerializer(serializers.ModelSerializer):
    matches = ScreenerMatchSerializer(many=True, read_only=True)

    class Meta:
        model = ScreenerRun
        fields = "__all__"


class TradeSignalSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="instrument.symbol", read_only=True)
    name = serializers.CharField(source="instrument.name", read_only=True)
    sector = serializers.CharField(source="instrument.sector", read_only=True)
    exchange = serializers.CharField(source="instrument.exchange", read_only=True)
    instrument_id = serializers.IntegerField(source="instrument.id", read_only=True)

    class Meta:
        model = TradeSignal
        fields = "__all__"
