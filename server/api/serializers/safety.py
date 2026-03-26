from rest_framework import serializers

from api.models import SafetyAlert


class SafetyAlertSerializer(serializers.ModelSerializer):
    resolved_by_name = serializers.CharField(source="resolved_by.email", read_only=True)

    class Meta:
        model = SafetyAlert
        fields = [
            "id",
            "alert_type",
            "threat_level",
            "location",
            "timestamp",
            "snapshot",
            "person_count",
            "description",
            "status",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "resolution_note",
            "parent_notified",
        ]
        read_only_fields = ["id", "timestamp", "resolved_by", "resolved_at"]
