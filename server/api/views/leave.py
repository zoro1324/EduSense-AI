from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView

from api.models import AttendanceRecord, LeaveRequest, UnexcusedAbsence
from api.serializers import LeaveRequestSerializer, UnexcusedAbsenceSerializer
from api.services import NotificationService
from api.views import error_response, success_response


class LeaveListCreateView(APIView):
    def get(self, request):
        try:
            leaves = LeaveRequest.objects.select_related("student", "reviewed_by").all().order_by("-applied_on")
            return success_response(LeaveRequestSerializer(leaves, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = LeaveRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            leave = serializer.save()
            return success_response(LeaveRequestSerializer(leave).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class LeaveDetailView(APIView):
    def get(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            return success_response(LeaveRequestSerializer(leave).data)
        except LeaveRequest.DoesNotExist:
            return error_response("Leave request not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            serializer = LeaveRequestSerializer(leave, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except LeaveRequest.DoesNotExist:
            return error_response("Leave request not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class LeaveApproveView(APIView):
    def post(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            leave.status = LeaveRequest.STATUS_APPROVED
            leave.reviewed_by = request.user
            leave.reviewed_at = timezone.now()
            leave.rejection_reason = ""
            leave.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])
            sent = NotificationService().send_leave_approved(leave)
            if sent:
                leave.parent_notified = True
                leave.notification_sent_at = timezone.now()
                leave.save(update_fields=["parent_notified", "notification_sent_at"])
            return success_response(LeaveRequestSerializer(leave).data)
        except LeaveRequest.DoesNotExist:
            return error_response("Leave request not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class LeaveRejectView(APIView):
    def post(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            leave.status = LeaveRequest.STATUS_REJECTED
            leave.reviewed_by = request.user
            leave.reviewed_at = timezone.now()
            leave.rejection_reason = request.data.get("rejection_reason", "")
            leave.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])
            sent = NotificationService().send_leave_rejected(leave)
            if sent:
                leave.parent_notified = True
                leave.notification_sent_at = timezone.now()
                leave.save(update_fields=["parent_notified", "notification_sent_at"])
            return success_response(LeaveRequestSerializer(leave).data)
        except LeaveRequest.DoesNotExist:
            return error_response("Leave request not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class UnexcusedAbsenceListView(APIView):
    def get(self, request):
        try:
            date_value = request.query_params.get("date")
            queryset = UnexcusedAbsence.objects.select_related("student").all().order_by("-date")
            if date_value:
                queryset = queryset.filter(date=date_value)
            else:
                queryset = queryset.filter(parent_notified=False)
            return success_response(UnexcusedAbsenceSerializer(queryset, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnexcusedNotifyView(APIView):
    def post(self, request, pk):
        try:
            absence = UnexcusedAbsence.objects.select_related("student__parent").get(pk=pk)
            sent = NotificationService().send_absent_alert(absence.student, absence.date)
            if sent:
                absence.parent_notified = True
                absence.notified_at = timezone.now()
                absence.save(update_fields=["parent_notified", "notified_at"])
            return success_response({"notified": sent})
        except UnexcusedAbsence.DoesNotExist:
            return error_response("Unexcused absence not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class UnexcusedNotifyAllView(APIView):
    def post(self, request):
        try:
            absences = UnexcusedAbsence.objects.select_related("student").filter(parent_notified=False)
            sent_count = 0
            service = NotificationService()
            for absence in absences:
                sent = service.send_absent_alert(absence.student, absence.date)
                if sent:
                    absence.parent_notified = True
                    absence.notified_at = timezone.now()
                    absence.save(update_fields=["parent_notified", "notified_at"])
                    sent_count += 1
            return success_response({"sent_count": sent_count})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)
