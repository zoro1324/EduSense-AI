from rest_framework import serializers

from api.models import EngagementLog, PeriodEngagementSummary


class EngagementLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementLog
        fields = "__all__"


class PeriodEngagementSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodEngagementSummary
        fields = "__all__"
