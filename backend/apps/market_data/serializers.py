from rest_framework import serializers

from . import models


class DailyBarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DailyBar
        exclude = ("created_at", "updated_at")


def serializer_for(model):
    class GeneratedSerializer(serializers.ModelSerializer):
        class Meta:
            model = None
            fields = "__all__"

    GeneratedSerializer.Meta.model = model
    GeneratedSerializer.__name__ = f"{model.__name__}Serializer"
    GeneratedSerializer.__qualname__ = GeneratedSerializer.__name__
    return GeneratedSerializer


InstrumentSnapshotSerializer = serializer_for(models.InstrumentSnapshot)
FundamentalSnapshotSerializer = serializer_for(models.FundamentalSnapshot)
PeerRelationshipSerializer = serializer_for(models.PeerRelationship)
CompanyNewsSerializer = serializer_for(models.CompanyNews)
MarketNewsSerializer = serializer_for(models.MarketNews)
SecFilingSerializer = serializer_for(models.SecFiling)
InsiderTransactionSerializer = serializer_for(models.InsiderTransaction)
InsiderSentimentSerializer = serializer_for(models.InsiderSentiment)
AnalystRecommendationSerializer = serializer_for(models.AnalystRecommendation)
EarningsEventSerializer = serializer_for(models.EarningsEvent)
EarningsResultSerializer = serializer_for(models.EarningsResult)
IpoEventSerializer = serializer_for(models.IpoEvent)
DomainFreshnessSerializer = serializer_for(models.DomainFreshness)
