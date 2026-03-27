from datetime import date

from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.views import APIView

from api.access_control import scope_queryset_to_user_classes
from api.models import AttendanceRecord, EngagementLog, SafetyAlert, StudentResult
from api.views import error_response, success_response


class DashboardReportView(APIView):
    def get(self, request):
        try:
            today = date.today()
            attendance_qs = scope_queryset_to_user_classes(AttendanceRecord.objects.all(), request.user, "student__class_name")
            engagement_qs = scope_queryset_to_user_classes(EngagementLog.objects.all(), request.user, "class_name")
            safety_qs = scope_queryset_to_user_classes(SafetyAlert.objects.all(), request.user, "class_name")
            results_qs = scope_queryset_to_user_classes(StudentResult.objects.all(), request.user, "student__class_name")
            data = {
                "today_attendance": attendance_qs.filter(date=today).count(),
                "today_engagement_logs": engagement_qs.filter(date=today).count(),
                "unresolved_safety_alerts": safety_qs.filter(status=SafetyAlert.STATUS_UNRESOLVED).count(),
                "results_generated": results_qs.exclude(ai_report="").count(),
            }
            return success_response(data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceReportView(APIView):
    def get(self, request):
        try:
            report = (
                scope_queryset_to_user_classes(AttendanceRecord.objects.all(), request.user, "student__class_name")
                .values("status")
                .annotate(total=Count("id"))
                .order_by("status")
            )
            return success_response(list(report))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngagementReportView(APIView):
    def get(self, request):
        try:
            report = (
                scope_queryset_to_user_classes(EngagementLog.objects.all(), request.user, "class_name")
                .values("class_name")
                .annotate(avg_engagement=Avg("engagement_percent"))
                .order_by("class_name")
            )
            return success_response(list(report))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class SafetyReportView(APIView):
    def get(self, request):
        try:
            alerts = scope_queryset_to_user_classes(SafetyAlert.objects.all(), request.user, "class_name")
            report = {
                "by_type": list(alerts.values("alert_type").annotate(total=Count("id"))),
                "by_status": list(alerts.values("status").annotate(total=Count("id"))),
            }
            return success_response(report)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcademicReportView(APIView):
    def get(self, request):
        try:
            report = (
                scope_queryset_to_user_classes(StudentResult.objects.all(), request.user, "student__class_name")
                .values("exam_type__name")
                .annotate(avg_percentage=Avg("percentage"))
                .order_by("exam_type__name")
            )
            return success_response(list(report))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
