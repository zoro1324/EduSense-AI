from django.db import models


class NotificationLog(models.Model):
    TYPE_ABSENT = "absent"
    TYPE_LEAVE_APPROVED = "leave_approved"
    TYPE_LEAVE_REJECTED = "leave_rejected"
    TYPE_RESULT_REPORT = "result_report"
    TYPE_SAFETY_ALERT = "safety_alert"
    TYPE_WEEKLY_SUMMARY = "weekly_summary"
    TYPE_ATTENDANCE_WARNING = "attendance_warning"

    CHANNEL_WHATSAPP = "whatsapp"
    CHANNEL_SMS = "sms"

    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_FAILED = "failed"
    STATUS_PENDING = "pending"

    NOTIFICATION_TYPE_CHOICES = [
        (TYPE_ABSENT, "Absent"),
        (TYPE_LEAVE_APPROVED, "Leave Approved"),
        (TYPE_LEAVE_REJECTED, "Leave Rejected"),
        (TYPE_RESULT_REPORT, "Result Report"),
        (TYPE_SAFETY_ALERT, "Safety Alert"),
        (TYPE_WEEKLY_SUMMARY, "Weekly Summary"),
        (TYPE_ATTENDANCE_WARNING, "Attendance Warning"),
    ]

    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, "WhatsApp"),
        (CHANNEL_SMS, "SMS"),
    ]

    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_FAILED, "Failed"),
        (STATUS_PENDING, "Pending"),
    ]

    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    student = models.ForeignKey("api.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications")
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=20)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    message_body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    twilio_sid = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.notification_type} to {self.parent_phone} ({self.status})"


class NotificationTemplate(models.Model):
    template_type = models.CharField(max_length=50, unique=True)
    template_body = models.TextField()
    variables = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.template_type
