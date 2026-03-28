from rest_framework import serializers

from api.models import ExamType, StudentMark, StudentResult, Subject


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class StudentMarkSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    exam_name = serializers.CharField(source="exam_type.name", read_only=True)

    class Meta:
        model = StudentMark
        fields = [
            "id",
            "student",
            "student_name",
            "exam_type",
            "exam_name",
            "subject",
            "subject_name",
            "marks_obtained",
            "max_marks",
            "grade",
        ]
        read_only_fields = ["id", "grade"]


class StudentResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    class_name = serializers.CharField(source="student.class_name", read_only=True)
    exam_name = serializers.CharField(source="exam_type.name", read_only=True)

    class Meta:
        model = StudentResult
        fields = [
            "id",
            "student",
            "student_name",
            "class_name",
            "exam_type",
            "exam_name",
            "total_marks",
            "max_total",
            "percentage",
            "grade",
            "rank",
            "ai_report",
            "report_generated_at",
            "report_sent",
            "report_sent_at",
        ]
        read_only_fields = ["id", "grade", "ai_report", "report_generated_at", "report_sent", "report_sent_at"]
