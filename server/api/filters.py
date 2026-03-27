import django_filters

from api.models import AttendanceRecord, EngagementLog, LeaveRequest, SafetyAlert, StudentMark, StudentResult


class AttendanceRecordFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = AttendanceRecord
        fields = ["student", "status", "period", "date", "start_date", "end_date"]


class EngagementLogFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = EngagementLog
        fields = ["class_name", "period", "status", "date", "start_date", "end_date"]


class SafetyAlertFilter(django_filters.FilterSet):
    start_timestamp = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    end_timestamp = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = SafetyAlert
        fields = ["alert_type", "threat_level", "status", "class_name", "location", "start_timestamp", "end_timestamp"]


class LeaveRequestFilter(django_filters.FilterSet):
    class Meta:
        model = LeaveRequest
        fields = ["student", "status", "start_date", "end_date"]


class StudentMarkFilter(django_filters.FilterSet):
    class Meta:
        model = StudentMark
        fields = ["student", "exam_type", "subject"]


class StudentResultFilter(django_filters.FilterSet):
    class Meta:
        model = StudentResult
        fields = ["student", "exam_type", "grade"]
