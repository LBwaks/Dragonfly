from rest_framework import serializers

from .models import TechnicalDaily


class TechnicalDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalDaily
        fields = "__all__"
