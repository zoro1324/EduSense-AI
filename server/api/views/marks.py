import csv
import io

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from api.models import ExamType, Student, StudentMark, StudentResult, Subject
from api.serializers import (
    ExamTypeSerializer,
    StudentMarkSerializer,
    StudentResultSerializer,
    SubjectSerializer,
)
from api.services import AIReportService, NotificationService
from api.utils import calculate_grade
from api.views import error_response, success_response


class ExamListCreateView(APIView):
    def get(self, request):
        try:
            exams = ExamType.objects.all().order_by("-date")
            return success_response(ExamTypeSerializer(exams, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = ExamTypeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            exam = serializer.save()
            return success_response(ExamTypeSerializer(exam).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class SubjectListCreateView(APIView):
    def get(self, request):
        try:
            subjects = Subject.objects.all().order_by("class_name", "name")
            return success_response(SubjectSerializer(subjects, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = SubjectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            subject = serializer.save()
            return success_response(SubjectSerializer(subject).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class MarkAddView(APIView):
    def post(self, request):
        try:
            serializer = StudentMarkSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            mark = serializer.instance
            if not isinstance(mark, StudentMark):
                return error_response("Unable to create mark record", status.HTTP_500_INTERNAL_SERVER_ERROR)
            percentage = (mark.marks_obtained / mark.max_marks) * 100 if mark.max_marks else 0
            mark.grade = calculate_grade(percentage)
            mark.save(update_fields=["grade"])
            return success_response(StudentMarkSerializer(mark).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class MarkBulkUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                return error_response("CSV file is required")

            decoded = file_obj.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))
            created = 0
            for row in reader:
                student = Student.objects.get(student_id=row["student_id"])
                exam = ExamType.objects.get(id=row["exam_type_id"])
                subject = Subject.objects.get(id=row["subject_id"])
                mark, was_created = StudentMark.objects.update_or_create(
                    student=student,
                    exam_type=exam,
                    subject=subject,
                    defaults={
                        "marks_obtained": float(row["marks_obtained"]),
                        "max_marks": float(row.get("max_marks", 100)),
                    },
                )
                percentage = (mark.marks_obtained / mark.max_marks) * 100 if mark.max_marks else 0
                mark.grade = calculate_grade(percentage)
                mark.save(update_fields=["grade"])
                if was_created:
                    created += 1
            return success_response({"processed": created})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class MarkListView(APIView):
    def get(self, request):
        try:
            marks = StudentMark.objects.select_related("student", "subject", "exam_type").all().order_by("student", "subject")
            return success_response(StudentMarkSerializer(marks, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResultListView(APIView):
    def get(self, request):
        try:
            results = StudentResult.objects.select_related("student", "exam_type").all().order_by("-exam_type__date", "student")
            return success_response(StudentResultSerializer(results, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResultGenerateReportView(APIView):
    def post(self, request, pk):
        try:
            result = StudentResult.objects.select_related("student", "exam_type").get(pk=pk)
            report = AIReportService(settings.GROQ_API_KEY).generate_report(result)
            if report:
                result.ai_report = report
                result.report_generated_at = timezone.now()
                result.save(update_fields=["ai_report", "report_generated_at"])
            return success_response(StudentResultSerializer(result).data)
        except StudentResult.DoesNotExist:
            return error_response("Student result not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class ResultGenerateAllReportsView(APIView):
    def post(self, request):
        try:
            generated = 0
            service = AIReportService(settings.GROQ_API_KEY)
            for result in StudentResult.objects.select_related("student", "exam_type").all():
                report = service.generate_report(result)
                if report:
                    result.ai_report = report
                    result.report_generated_at = timezone.now()
                    result.save(update_fields=["ai_report", "report_generated_at"])
                    generated += 1
            return success_response({"generated": generated})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class ResultSendReportView(APIView):
    def post(self, request, pk):
        try:
            result = StudentResult.objects.select_related("student").get(pk=pk)
            sent = NotificationService().send_result_report(result)
            if sent:
                result.report_sent = True
                result.report_sent_at = timezone.now()
                result.save(update_fields=["report_sent", "report_sent_at"])
            return success_response({"sent": sent})
        except StudentResult.DoesNotExist:
            return error_response("Student result not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class ResultSendAllReportsView(APIView):
    def post(self, request):
        try:
            sent_count = 0
            service = NotificationService()
            for result in StudentResult.objects.select_related("student").all():
                sent = service.send_result_report(result)
                if sent:
                    result.report_sent = True
                    result.report_sent_at = timezone.now()
                    result.save(update_fields=["report_sent", "report_sent_at"])
                    sent_count += 1
            return success_response({"sent_count": sent_count})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class RecomputeResultsView(APIView):
    def post(self, request):
        try:
            exam_id = request.data.get("exam_type_id")
            if not exam_id:
                return error_response("exam_type_id is required")
            exam = ExamType.objects.get(id=exam_id)
            student_totals = (
                StudentMark.objects.filter(exam_type=exam)
                .values("student")
                .annotate(total=Sum("marks_obtained"), max_total=Sum("max_marks"))
            )
            updated = 0
            for row in student_totals:
                student = Student.objects.get(pk=row["student"])
                max_total = row["max_total"] or 0
                percentage = (row["total"] / max_total) * 100 if max_total else 0
                StudentResult.objects.update_or_create(
                    student=student,
                    exam_type=exam,
                    defaults={
                        "total_marks": row["total"],
                        "max_total": max_total,
                        "percentage": percentage,
                        "grade": calculate_grade(percentage),
                    },
                )
                updated += 1
            return success_response({"updated": updated})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)
