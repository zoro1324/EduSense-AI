from rest_framework import status
from rest_framework.views import APIView

from api.access_control import is_principal, scope_queryset_to_user_classes, user_can_access_class
from api.models import NotificationLog, NotificationTemplate
from api.serializers import NotificationLogSerializer, NotificationTemplateSerializer
from api.services import NotificationService
from api.views import error_response, success_response


class NotificationListView(APIView):
    def get(self, request):
        try:
            logs = NotificationLog.objects.select_related("student").all().order_by("-sent_at")
            if not is_principal(request.user):
                logs = logs.filter(student__isnull=False)
            logs = scope_queryset_to_user_classes(logs, request.user, "student__class_name")
            return success_response(NotificationLogSerializer(logs, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationResendView(APIView):
    def post(self, request, pk):
        try:
            log = NotificationLog.objects.select_related("student").get(pk=pk)
            if log.student and not user_can_access_class(request.user, log.student.class_name):
                return error_response("You can only resend notifications for your in-charge class", status.HTTP_403_FORBIDDEN)
            if not log.student and not is_principal(request.user):
                return error_response("Only principal can resend school-level notifications", status.HTTP_403_FORBIDDEN)

            service = NotificationService()
            if log.channel == NotificationLog.CHANNEL_WHATSAPP:
                sent = service.send_whatsapp(log.parent_phone, log.message_body, student=log.student, notification_type=log.notification_type)
            else:
                sent = service.send_sms(log.parent_phone, log.message_body, student=log.student, notification_type=log.notification_type)
            return success_response({"resent": sent})
        except NotificationLog.DoesNotExist:
            return error_response("Notification log not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class NotificationTemplateListView(APIView):
    def get(self, request):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can view notification templates", status.HTTP_403_FORBIDDEN)
            templates = NotificationTemplate.objects.all().order_by("template_type")
            return success_response(NotificationTemplateSerializer(templates, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationTemplateUpdateView(APIView):
    def put(self, request, pk):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can update notification templates", status.HTTP_403_FORBIDDEN)
            template = NotificationTemplate.objects.get(pk=pk)
            serializer = NotificationTemplateSerializer(template, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except NotificationTemplate.DoesNotExist:
            return error_response("Notification template not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class NotificationTestView(APIView):
    def post(self, request):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can send test notifications", status.HTTP_403_FORBIDDEN)
            phone = request.data.get("phone")
            message = request.data.get("message", "Test message from EduSense AI")
            channel = request.data.get("channel", NotificationLog.CHANNEL_WHATSAPP)
            service = NotificationService()
            if channel == NotificationLog.CHANNEL_SMS:
                sent = service.send_sms(phone, message, notification_type=NotificationLog.TYPE_WEEKLY_SUMMARY)
            else:
                sent = service.send_whatsapp(phone, message, notification_type=NotificationLog.TYPE_WEEKLY_SUMMARY)
            return success_response({"sent": sent})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)
