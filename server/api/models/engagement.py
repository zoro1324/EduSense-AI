from django.db import models


class EngagementLog(models.Model):
    STATUS_HIGH = "high"
    STATUS_MEDIUM = "medium"
    STATUS_LOW = "low"

    STATUS_CHOICES = [
        (STATUS_HIGH, "High"),
        (STATUS_MEDIUM, "Medium"),
        (STATUS_LOW, "Low"),
    ]

    class_name = models.CharField(max_length=50)
    date = models.DateField()
    period = models.IntegerField()
    timestamp = models.DateTimeField()
    total_persons = models.IntegerField()
    engaged_count = models.IntegerField()
    distracted_count = models.IntegerField()
    engagement_percent = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    snapshot_path = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.class_name} {self.date} P{self.period} {self.engagement_percent}%"


class PeriodEngagementSummary(models.Model):
    class_name = models.CharField(max_length=50)
    date = models.DateField()
    period = models.IntegerField()
    avg_engagement_percent = models.FloatField()
    min_engagement_percent = models.FloatField()
    max_engagement_percent = models.FloatField()
    dead_period_flag = models.BooleanField(default=False)

    class Meta:
        unique_together = (("class_name", "date", "period"),)

    def __str__(self):
        return f"Summary {self.class_name} {self.date} P{self.period}"
