from datetime import datetime

from django.conf import settings
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from api.models import NotificationLog, NotificationTemplate


class NotificationService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    @staticmethod
    def _format_indian_phone(phone):
        digits = "".join(ch for ch in str(phone) if ch.isdigit())
        if len(digits) == 10:
            digits = f"91{digits}"
        return f"+{digits}" if not str(phone).startswith("+") else str(phone)

    def get_template(self, template_type, variables=None):
        variables = variables or {}
        try:
            template = NotificationTemplate.objects.get(template_type=template_type)
            return template.template_body.format_map({**variables, "datetime": datetime.now().isoformat()})
        except NotificationTemplate.DoesNotExist:
            return ""
        except Exception:
            return ""

    def send_whatsapp(self, phone, message, student=None, notification_type=None):
        formatted_phone = self._format_indian_phone(phone)
        to_number = formatted_phone if formatted_phone.startswith("whatsapp:") else f"whatsapp:{formatted_phone}"
        try:
            response = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to_number,
            )
            NotificationLog.objects.create(
                notification_type=notification_type or NotificationLog.TYPE_WEEKLY_SUMMARY,
                student=student,
                parent_name=student.parent.father_name if student and hasattr(student, "parent") else "Parent",
                parent_phone=phone,
                channel=NotificationLog.CHANNEL_WHATSAPP,
                message_body=message,
                status=NotificationLog.STATUS_SENT,
                twilio_sid=response.sid,
            )
            return True
        except TwilioException as exc:
            NotificationLog.objects.create(
                notification_type=notification_type or NotificationLog.TYPE_WEEKLY_SUMMARY,
                student=student,
                parent_name=student.parent.father_name if student and hasattr(student, "parent") else "Parent",
                parent_phone=phone,
                channel=NotificationLog.CHANNEL_WHATSAPP,
                message_body=message,
                status=NotificationLog.STATUS_FAILED,
                error_message=str(exc),
            )
            return False
        except Exception as exc:
            NotificationLog.objects.create(
                notification_type=notification_type or NotificationLog.TYPE_WEEKLY_SUMMARY,
                student=student,
                parent_name=student.parent.father_name if student and hasattr(student, "parent") else "Parent",
                parent_phone=phone,
                channel=NotificationLog.CHANNEL_WHATSAPP,
                message_body=message,
                status=NotificationLog.STATUS_FAILED,
                error_message=str(exc),
            )
            return False

    def send_sms(self, phone, message, student=None, notification_type=None):
        formatted_phone = self._format_indian_phone(phone)
        try:
            response = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_SMS_FROM,
                to=formatted_phone,
            )
            NotificationLog.objects.create(
                notification_type=notification_type or NotificationLog.TYPE_WEEKLY_SUMMARY,
                student=student,
                parent_name=student.parent.father_name if student and hasattr(student, "parent") else "Parent",
                parent_phone=phone,
                channel=NotificationLog.CHANNEL_SMS,
                message_body=message,
                status=NotificationLog.STATUS_SENT,
                twilio_sid=response.sid,
            )
            return True
        except TwilioException as exc:
            NotificationLog.objects.create(
                notification_type=notification_type or NotificationLog.TYPE_WEEKLY_SUMMARY,
                student=student,
                parent_name=student.parent.father_name if student and hasattr(student, "parent") else "Parent",
                parent_phone=phone,
                channel=NotificationLog.CHANNEL_SMS,
                message_body=message,
                status=NotificationLog.STATUS_FAILED,
                error_message=str(exc),
            )
            return False
        except Exception as exc:
            NotificationLog.objects.create(
                notification_type=notification_type or NotificationLog.TYPE_WEEKLY_SUMMARY,
                student=student,
                parent_name=student.parent.father_name if student and hasattr(student, "parent") else "Parent",
                parent_phone=phone,
                channel=NotificationLog.CHANNEL_SMS,
                message_body=message,
                status=NotificationLog.STATUS_FAILED,
                error_message=str(exc),
            )
            return False

    def send_absent_alert(self, student, date):
        message = self.get_template(
            NotificationLog.TYPE_ABSENT,
            {"student_name": student.name, "date": str(date), "school_name": settings.SCHOOL_NAME},
        )
        if not message:
            message = f"{student.name} is absent on {date}. - {settings.SCHOOL_NAME}"

        if not hasattr(student, "parent"):
            return False

        if self.send_whatsapp(
            student.parent.whatsapp_number,
            message,
            student=student,
            notification_type=NotificationLog.TYPE_ABSENT,
        ):
            return True
        return self.send_sms(
            student.parent.phone_number,
            message,
            student=student,
            notification_type=NotificationLog.TYPE_ABSENT,
        )

    def send_leave_approved(self, leave_request):
        student = leave_request.student
        if not hasattr(student, "parent"):
            return False
        message = self.get_template(
            NotificationLog.TYPE_LEAVE_APPROVED,
            {
                "student_name": student.name,
                "start_date": str(leave_request.start_date),
                "end_date": str(leave_request.end_date),
                "school_name": settings.SCHOOL_NAME,
            },
        )
        if not message:
            message = f"Leave approved for {student.name} from {leave_request.start_date} to {leave_request.end_date}."
        return self.send_whatsapp(
            student.parent.whatsapp_number,
            message,
            student=student,
            notification_type=NotificationLog.TYPE_LEAVE_APPROVED,
        )

    def send_leave_rejected(self, leave_request):
        student = leave_request.student
        if not hasattr(student, "parent"):
            return False
        message = self.get_template(
            NotificationLog.TYPE_LEAVE_REJECTED,
            {
                "student_name": student.name,
                "start_date": str(leave_request.start_date),
                "end_date": str(leave_request.end_date),
                "rejection_reason": leave_request.rejection_reason,
                "school_name": settings.SCHOOL_NAME,
            },
        )
        if not message:
            message = (
                f"Leave rejected for {student.name} ({leave_request.start_date} to {leave_request.end_date}). "
                f"Reason: {leave_request.rejection_reason}"
            )
        return self.send_whatsapp(
            student.parent.whatsapp_number,
            message,
            student=student,
            notification_type=NotificationLog.TYPE_LEAVE_REJECTED,
        )

    def send_result_report(self, student_result):
        student = student_result.student
        if not hasattr(student, "parent"):
            return False
        message = self.get_template(
            NotificationLog.TYPE_RESULT_REPORT,
            {
                "student_name": student.name,
                "exam_name": student_result.exam_type.name,
                "percentage": str(student_result.percentage),
                "grade": student_result.grade,
                "ai_report": student_result.ai_report,
                "school_name": settings.SCHOOL_NAME,
            },
        )
        if not message:
            message = (
                f"Result Report for {student.name} ({student_result.exam_type.name}): "
                f"{student_result.percentage}% ({student_result.grade}).\n\n{student_result.ai_report}"
            )
        return self.send_whatsapp(
            student.parent.whatsapp_number,
            message,
            student=student,
            notification_type=NotificationLog.TYPE_RESULT_REPORT,
        )

    def send_safety_alert_admin(self, alert):
        message = (
            f"URGENT SAFETY ALERT: {alert.alert_type} at {alert.location}. "
            f"Threat={alert.threat_level}, Persons={alert.person_count}."
        )
        return self.send_sms(
            settings.ADMIN_PHONE,
            message,
            student=None,
            notification_type=NotificationLog.TYPE_SAFETY_ALERT,
        )
