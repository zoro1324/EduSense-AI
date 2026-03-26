from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView

from api.models import SafetyAlert
from api.serializers import SafetyAlertSerializer
from api.services import NotificationService
from api.views import error_response, success_response


class SafetyAlertListCreateView(APIView):
    def get(self, request):
        try:
            alerts = SafetyAlert.objects.all().order_by("-timestamp")
            return success_response(SafetyAlertSerializer(alerts, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = SafetyAlertSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            alert = serializer.save()
            NotificationService().send_safety_alert_admin(alert)
            return success_response(SafetyAlertSerializer(alert).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class SafetyAlertDetailView(APIView):
    def get(self, request, pk):
        try:
            alert = SafetyAlert.objects.get(pk=pk)
            return success_response(SafetyAlertSerializer(alert).data)
        except SafetyAlert.DoesNotExist:
            return error_response("Safety alert not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            alert = SafetyAlert.objects.get(pk=pk)
            serializer = SafetyAlertSerializer(alert, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except SafetyAlert.DoesNotExist:
            return error_response("Safety alert not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class SafetyResolveView(APIView):
    def post(self, request, pk):
        try:
            alert = SafetyAlert.objects.get(pk=pk)
            alert.status = SafetyAlert.STATUS_RESOLVED
            alert.resolution_note = request.data.get("resolution_note", "")
            alert.resolved_by = request.user
            alert.resolved_at = timezone.now()
            alert.save(update_fields=["status", "resolution_note", "resolved_by", "resolved_at"])
            return success_response(SafetyAlertSerializer(alert).data)
        except SafetyAlert.DoesNotExist:
            return error_response("Safety alert not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class SafetyStatsView(APIView):
    def get(self, request):
        try:
            data = {
                "total": SafetyAlert.objects.count(),
                "by_status": list(SafetyAlert.objects.values("status").annotate(total=Count("id")).order_by("status")),
                "by_threat": list(SafetyAlert.objects.values("threat_level").annotate(total=Count("id")).order_by("threat_level")),
            }
            return success_response(data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
