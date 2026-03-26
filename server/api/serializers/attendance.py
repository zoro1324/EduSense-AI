from rest_framework import serializers

from api.models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    marked_by_name = serializers.CharField(source="marked_by.email", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "student",
            "student_name",
            "date",
            "period",
            "status",
            "marked_at",
            "marked_by",
            "marked_by_name",
            "is_manual",
            "note",
        ]
        read_only_fields = ["id", "marked_at", "marked_by"]
