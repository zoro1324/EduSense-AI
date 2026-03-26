from django.conf import settings
from django.db import models


class AttendanceRecord(models.Model):
    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"
    STATUS_LATE = "late"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_LATE, "Late"),
    ]

    PERIOD_CHOICES = [(i, f"Period {i}") for i in range(1, 7)]

    student = models.ForeignKey("api.Student", on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    period = models.IntegerField(choices=PERIOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance",
    )
    is_manual = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = (("student", "date", "period"),)

    def __str__(self):
        return f"{self.student.name} {self.date} P{self.period} {self.status}"
