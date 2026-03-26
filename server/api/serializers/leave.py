from rest_framework import serializers

from api.models import LeaveRequest, UnexcusedAbsence


class LeaveRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.email", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "student",
            "student_name",
            "start_date",
            "end_date",
            "reason",
            "applied_on",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "rejection_reason",
            "parent_notified",
            "notification_sent_at",
        ]
        read_only_fields = ["id", "applied_on", "reviewed_by", "reviewed_at"]


class UnexcusedAbsenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = UnexcusedAbsence
        fields = ["id", "student", "student_name", "date", "parent_notified", "notified_at"]
        read_only_fields = ["id", "notified_at"]
