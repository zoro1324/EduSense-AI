from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import FacultyProfile, SchoolClass, TimetableEntry

User = get_user_model()


class SchoolClassSerializer(serializers.ModelSerializer):
    incharge_name = serializers.CharField(source="incharge.get_full_name", read_only=True)
    incharge_email = serializers.CharField(source="incharge.email", read_only=True)

    class Meta:
        model = SchoolClass
        fields = [
            "id",
            "name",
            "section",
            "incharge",
            "incharge_name",
            "incharge_email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FacultyProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = FacultyProfile
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "user_role",
            "employee_code",
            "department",
            "designation",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableEntrySerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="school_class.name", read_only=True)
    faculty_name = serializers.CharField(source="faculty.get_full_name", read_only=True)
    faculty_email = serializers.CharField(source="faculty.email", read_only=True)

    class Meta:
        model = TimetableEntry
        fields = [
            "id",
            "school_class",
            "class_name",
            "day_of_week",
            "period",
            "subject_name",
            "faculty",
            "faculty_name",
            "faculty_email",
            "room_number",
            "start_time",
            "end_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("start_time must be before end_time")
        return attrs
