from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView

from api.access_control import scope_queryset_to_user_classes, user_can_access_class
from api.models import AttendanceRecord, LeaveRequest, UnexcusedAbsence
from api.serializers import LeaveRequestSerializer, UnexcusedAbsenceSerializer
from api.services import NotificationService
from api.views import error_response, success_response


class LeaveListCreateView(APIView):
    def get(self, request):
        try:
            leaves = scope_queryset_to_user_classes(
                LeaveRequest.objects.select_related("student", "reviewed_by").all(),
                request.user,
                "student__class_name",
            ).order_by("-applied_on")
            return success_response(LeaveRequestSerializer(leaves, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = LeaveRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            student = serializer.validated_data["student"]
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only create leave requests for your in-charge class", status.HTTP_403_FORBIDDEN)
            leave = serializer.save()
            return success_response(LeaveRequestSerializer(leave).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class LeaveDetailView(APIView):
    def get(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            if not user_can_access_class(request.user, leave.student.class_name):
                return error_response("You can only view leave requests for your in-charge class", status.HTTP_403_FORBIDDEN)
            return success_response(LeaveRequestSerializer(leave).data)
        except LeaveRequest.DoesNotExist:
            return error_response("Leave request not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            if not user_can_access_class(request.user, leave.student.class_name):
                return error_response("You can only update leave requests for your in-charge class", status.HTTP_403_FORBIDDEN)
            serializer = LeaveRequestSerializer(leave, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            student = serializer.validated_data.get("student", leave.student)
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only move leaves within your in-charge class", status.HTTP_403_FORBIDDEN)

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
            if not user_can_access_class(request.user, leave.student.class_name):
                return error_response("You can only approve leaves for your in-charge class", status.HTTP_403_FORBIDDEN)
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
            if not user_can_access_class(request.user, leave.student.class_name):
                return error_response("You can only reject leaves for your in-charge class", status.HTTP_403_FORBIDDEN)
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
            queryset = scope_queryset_to_user_classes(
                UnexcusedAbsence.objects.select_related("student").all(),
                request.user,
                "student__class_name",
            ).order_by("-date")
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
            if not user_can_access_class(request.user, absence.student.class_name):
                return error_response("You can only notify absences for your in-charge class", status.HTTP_403_FORBIDDEN)
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
            absences = scope_queryset_to_user_classes(
                UnexcusedAbsence.objects.select_related("student").filter(parent_notified=False),
                request.user,
                "student__class_name",
            )
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
