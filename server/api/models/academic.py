from django.conf import settings
from django.db import models


class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    section = models.CharField(max_length=20, blank=True)
    incharge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incharge_classes",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}{f' ({self.section})' if self.section else ''}"


class FacultyProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
    )
    employee_code = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_code"]

    def __str__(self):
        return f"{self.employee_code} - {self.user.email}"


class TimetableEntry(models.Model):
    DAY_MONDAY = "monday"
    DAY_TUESDAY = "tuesday"
    DAY_WEDNESDAY = "wednesday"
    DAY_THURSDAY = "thursday"
    DAY_FRIDAY = "friday"
    DAY_SATURDAY = "saturday"

    DAY_CHOICES = [
        (DAY_MONDAY, "Monday"),
        (DAY_TUESDAY, "Tuesday"),
        (DAY_WEDNESDAY, "Wednesday"),
        (DAY_THURSDAY, "Thursday"),
        (DAY_FRIDAY, "Friday"),
        (DAY_SATURDAY, "Saturday"),
    ]

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    period = models.PositiveSmallIntegerField()
    subject_name = models.CharField(max_length=100)
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="timetable_entries",
    )
    room_number = models.CharField(max_length=30, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("school_class", "day_of_week", "period"),)
        ordering = ["school_class__name", "day_of_week", "period"]

    def __str__(self):
        return f"{self.school_class.name} {self.day_of_week} P{self.period}"
