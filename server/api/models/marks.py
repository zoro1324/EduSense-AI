from django.db import models


class ExamType(models.Model):
    UNIT_TEST_1 = "Unit Test 1"
    UNIT_TEST_2 = "Unit Test 2"
    QUARTERLY = "Quarterly"
    HALF_YEARLY = "Half Yearly"
    ANNUAL = "Annual"

    NAME_CHOICES = [
        (UNIT_TEST_1, "Unit Test 1"),
        (UNIT_TEST_2, "Unit Test 2"),
        (QUARTERLY, "Quarterly"),
        (HALF_YEARLY, "Half Yearly"),
        (ANNUAL, "Annual"),
    ]

    name = models.CharField(max_length=50, choices=NAME_CHOICES)
    academic_year = models.CharField(max_length=20)
    date = models.DateField()
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} {self.class_name} {self.academic_year}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)

    class Meta:
        unique_together = (("name", "class_name"),)

    def __str__(self):
        return f"{self.name} ({self.class_name})"


class StudentMark(models.Model):
    student = models.ForeignKey("api.Student", on_delete=models.CASCADE, related_name="marks")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    marks_obtained = models.FloatField()
    max_marks = models.FloatField(default=100)
    grade = models.CharField(max_length=10, blank=True)

    class Meta:
        unique_together = (("student", "exam_type", "subject"),)

    def __str__(self):
        return f"{self.student.name} {self.subject.name} {self.marks_obtained}/{self.max_marks}"


class StudentResult(models.Model):
    student = models.ForeignKey("api.Student", on_delete=models.CASCADE, related_name="results")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="results")
    total_marks = models.FloatField()
    max_total = models.FloatField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=10)
    rank = models.IntegerField(null=True, blank=True)
    ai_report = models.TextField(blank=True)
    report_generated_at = models.DateTimeField(null=True, blank=True)
    report_sent = models.BooleanField(default=False)
    report_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (("student", "exam_type"),)

    def __str__(self):
        return f"{self.student.name} {self.exam_type.name} {self.percentage}%"
