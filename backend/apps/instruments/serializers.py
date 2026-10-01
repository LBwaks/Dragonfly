from rest_framework import serializers

from .models import Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = (
            "id",
            "symbol",
            "name",
            "exchange",
            "asset_type",
            "currency",
            "sector",
            "industry",
            "provider_symbol",
            "is_active",
            "market_cap",
            "latest_price",
            "price_as_of",
            "price_provider",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
