from rest_framework import serializers

from .models import JobRun


class JobRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRun
        fields = "__all__"
