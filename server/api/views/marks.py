import csv
import io

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from api.access_control import scope_queryset_to_user_classes, user_can_access_class
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
            exams = scope_queryset_to_user_classes(ExamType.objects.all(), request.user, "class_name").order_by("-date")
            return success_response(ExamTypeSerializer(exams, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = ExamTypeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            class_name = serializer.validated_data["class_name"]
            if not user_can_access_class(request.user, class_name):
                return error_response("You can only create exams for your in-charge class", status.HTTP_403_FORBIDDEN)
            exam = serializer.save()
            return success_response(ExamTypeSerializer(exam).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class SubjectListCreateView(APIView):
    def get(self, request):
        try:
            subjects = scope_queryset_to_user_classes(Subject.objects.all(), request.user, "class_name").order_by(
                "class_name", "name"
            )
            return success_response(SubjectSerializer(subjects, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = SubjectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            class_name = serializer.validated_data["class_name"]
            if not user_can_access_class(request.user, class_name):
                return error_response("You can only create subjects for your in-charge class", status.HTTP_403_FORBIDDEN)
            subject = serializer.save()
            return success_response(SubjectSerializer(subject).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class MarkAddView(APIView):
    def post(self, request):
        try:
            serializer = StudentMarkSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            student = serializer.validated_data["student"]
            subject = serializer.validated_data["subject"]
            exam_type = serializer.validated_data["exam_type"]

            if student.class_name != subject.class_name or student.class_name != exam_type.class_name:
                return error_response("Student, subject, and exam must belong to the same class")
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only add marks for your in-charge class", status.HTTP_403_FORBIDDEN)

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

                if student.class_name != subject.class_name or student.class_name != exam.class_name:
                    return error_response(
                        f"Class mismatch for student {student.student_id}: student={student.class_name}, exam={exam.class_name}, subject={subject.class_name}"
                    )
                if not user_can_access_class(request.user, student.class_name):
                    return error_response("You can only upload marks for your in-charge class", status.HTTP_403_FORBIDDEN)

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
            marks = scope_queryset_to_user_classes(
                StudentMark.objects.select_related("student", "subject", "exam_type").all(),
                request.user,
                "student__class_name",
            ).order_by("student", "subject")
            return success_response(StudentMarkSerializer(marks, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResultListView(APIView):
    def get(self, request):
        try:
            results = scope_queryset_to_user_classes(
                StudentResult.objects.select_related("student", "exam_type").all(),
                request.user,
                "student__class_name",
            ).order_by("-exam_type__date", "student")
            return success_response(StudentResultSerializer(results, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResultGenerateReportView(APIView):
    def post(self, request, pk):
        try:
            result = StudentResult.objects.select_related("student", "exam_type").get(pk=pk)
            if not user_can_access_class(request.user, result.student.class_name):
                return error_response("You can only generate reports for your in-charge class", status.HTTP_403_FORBIDDEN)
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
            queryset = scope_queryset_to_user_classes(
                StudentResult.objects.select_related("student", "exam_type").all(),
                request.user,
                "student__class_name",
            )
            for result in queryset:
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
            if not user_can_access_class(request.user, result.student.class_name):
                return error_response("You can only send reports for your in-charge class", status.HTTP_403_FORBIDDEN)
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
            queryset = scope_queryset_to_user_classes(
                StudentResult.objects.select_related("student").all(),
                request.user,
                "student__class_name",
            )
            for result in queryset:
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
            if not user_can_access_class(request.user, exam.class_name):
                return error_response("You can only recompute results for your in-charge class", status.HTTP_403_FORBIDDEN)
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
