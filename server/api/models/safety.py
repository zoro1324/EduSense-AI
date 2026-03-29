from django.conf import settings
from django.db import models


class SafetyAlert(models.Model):
    TYPE_GROUPING = "grouping"
    TYPE_RAGGING = "ragging"
    TYPE_UNKNOWN = "unknown"

    THREAT_LOW = "low"
    THREAT_MEDIUM = "medium"
    THREAT_HIGH = "high"

    STATUS_UNRESOLVED = "unresolved"
    STATUS_RESOLVED = "resolved"
    STATUS_FALSE_ALARM = "false_alarm"

    ALERT_TYPE_CHOICES = [
        (TYPE_GROUPING, "Grouping"),
        (TYPE_RAGGING, "Ragging"),
        (TYPE_UNKNOWN, "Unknown"),
    ]
    THREAT_LEVEL_CHOICES = [
        (THREAT_LOW, "Low"),
        (THREAT_MEDIUM, "Medium"),
        (THREAT_HIGH, "High"),
    ]
    STATUS_CHOICES = [
        (STATUS_UNRESOLVED, "Unresolved"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_FALSE_ALARM, "False Alarm"),
    ]

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVEL_CHOICES)
    class_name = models.CharField(max_length=50, default="General")
    location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot = models.ImageField(upload_to="safety/snapshots/", blank=True, null=True)
    person_count = models.IntegerField(default=0)
    recognized_persons = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNRESOLVED)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    parent_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.alert_type} at {self.location} ({self.status})"
