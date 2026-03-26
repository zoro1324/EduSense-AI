from datetime import date

from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.views import APIView

from api.models import AttendanceRecord, EngagementLog, SafetyAlert, StudentResult
from api.views import error_response, success_response


class DashboardReportView(APIView):
    def get(self, request):
        try:
            today = date.today()
            data = {
                "today_attendance": AttendanceRecord.objects.filter(date=today).count(),
                "today_engagement_logs": EngagementLog.objects.filter(date=today).count(),
                "unresolved_safety_alerts": SafetyAlert.objects.filter(status=SafetyAlert.STATUS_UNRESOLVED).count(),
                "results_generated": StudentResult.objects.exclude(ai_report="").count(),
            }
            return success_response(data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceReportView(APIView):
    def get(self, request):
        try:
            report = AttendanceRecord.objects.values("status").annotate(total=Count("id")).order_by("status")
            return success_response(list(report))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngagementReportView(APIView):
    def get(self, request):
        try:
            report = EngagementLog.objects.values("class_name").annotate(avg_engagement=Avg("engagement_percent")).order_by("class_name")
            return success_response(list(report))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class SafetyReportView(APIView):
    def get(self, request):
        try:
            report = {
                "by_type": list(SafetyAlert.objects.values("alert_type").annotate(total=Count("id"))),
                "by_status": list(SafetyAlert.objects.values("status").annotate(total=Count("id"))),
            }
            return success_response(report)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcademicReportView(APIView):
    def get(self, request):
        try:
            report = StudentResult.objects.values("exam_type__name").annotate(avg_percentage=Avg("percentage")).order_by("exam_type__name")
            return success_response(list(report))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
