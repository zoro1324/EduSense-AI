from datetime import date
import logging

from django.conf import settings
from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api.access_control import scope_queryset_to_user_classes, user_can_access_class
from api.models import AttendanceRecord, Student
from api.services import FaceRecognitionService, resolve_current_period_for_class
from api.serializers import AttendanceRecordSerializer
from api.views import error_response, success_response

logger = logging.getLogger(__name__)
TOKEN_WARNING_EMITTED = False


def _is_auto_period(raw_period):
    return raw_period in [None, "", "auto", "AUTO", "Auto"]


def _parse_explicit_period(raw_period):
    try:
        period = int(raw_period)
    except (TypeError, ValueError) as exc:
        raise ValueError("period must be an integer between 1 and 6") from exc

    if period not in [choice[0] for choice in AttendanceRecord.PERIOD_CHOICES]:
        raise ValueError("period must be between 1 and 6")
    return period


def _resolve_period_for_student(student, raw_period):
    if not _is_auto_period(raw_period):
        return _parse_explicit_period(raw_period), "request", None

    period, timetable_entry = resolve_current_period_for_class(student.class_name)
    if period is None:
        raise ValueError(
            f"No active timetable slot found for class '{student.class_name}'. "
            "Please set period start/end times in Academic Planner."
        )

    return period, "timetable", timetable_entry


def _append_auto_note(existing_note, timetable_entry):
    if not timetable_entry:
        return existing_note

    window = f"{timetable_entry.start_time}-{timetable_entry.end_time}"
    auto_note = (
        f"Auto period from timetable ({timetable_entry.day_of_week.title()} P{timetable_entry.period} {window})"
    )
    if existing_note:
        return f"{existing_note} | {auto_note}"
    return auto_note


class AttendanceMarkView(APIView):
    def post(self, request):
        try:
            data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
            if not data.get("date"):
                data["date"] = date.today().isoformat()

            student_id = data.get("student")
            if not student_id:
                return error_response("student is required")

            student = Student.objects.filter(pk=student_id, is_active=True).first()
            if not student:
                return error_response("Student not found", status.HTTP_404_NOT_FOUND)

            period, period_source, timetable_entry = _resolve_period_for_student(student, data.get("period"))
            data["period"] = period
            if period_source == "timetable":
                data["note"] = _append_auto_note(data.get("note", ""), timetable_entry)

            serializer = AttendanceRecordSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            student = serializer.validated_data["student"]
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only mark attendance for your in-charge class", status.HTTP_403_FORBIDDEN)
            serializer.save(marked_by=request.user)
            return success_response(serializer.data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class AttendanceMarkBulkView(APIView):
    def post(self, request):
        try:
            records = request.data.get("records", [])
            if not isinstance(records, list):
                return error_response("records must be a list")

            saved = []
            for item in records:
                if not isinstance(item, dict):
                    return error_response("each records item must be an object")

                item_data = dict(item)
                if not item_data.get("date"):
                    item_data["date"] = date.today().isoformat()

                student_id = item_data.get("student")
                if not student_id:
                    return error_response("student is required for each records item")

                student = Student.objects.filter(pk=student_id, is_active=True).first()
                if not student:
                    return error_response(f"Student not found for id: {student_id}", status.HTTP_404_NOT_FOUND)

                period, period_source, timetable_entry = _resolve_period_for_student(student, item_data.get("period"))
                item_data["period"] = period
                if period_source == "timetable":
                    item_data["note"] = _append_auto_note(item_data.get("note", ""), timetable_entry)

                serializer = AttendanceRecordSerializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                student = serializer.validated_data["student"]
                if not user_can_access_class(request.user, student.class_name):
                    return error_response(
                        "You can only mark attendance for your in-charge class",
                        status.HTTP_403_FORBIDDEN,
                    )
                serializer.save(marked_by=request.user)
                saved.append(serializer.data)
            return success_response(saved, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class AttendanceListView(APIView):
    def get(self, request):
        try:
            queryset = AttendanceRecord.objects.select_related("student", "marked_by").all().order_by("-date", "period")
            queryset = scope_queryset_to_user_classes(queryset, request.user, "student__class_name")
            serializer = AttendanceRecordSerializer(queryset, many=True)
            return success_response(serializer.data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceTodayView(APIView):
    def get(self, request):
        try:
            queryset = AttendanceRecord.objects.filter(date=date.today()).select_related("student")
            queryset = scope_queryset_to_user_classes(queryset, request.user, "student__class_name")
            serializer = AttendanceRecordSerializer(queryset, many=True)
            return success_response(serializer.data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceSummaryView(APIView):
    def get(self, request):
        try:
            summary = (
                scope_queryset_to_user_classes(AttendanceRecord.objects.all(), request.user, "student__class_name")
                .values("status")
                .annotate(total=Count("id"))
                .order_by("status")
            )
            return success_response(list(summary))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceDailyView(APIView):
    def get(self, request):
        try:
            day = request.query_params.get("date", date.today())
            records = (
                scope_queryset_to_user_classes(AttendanceRecord.objects.filter(date=day), request.user, "student__class_name")
                .values("period", "status")
                .annotate(total=Count("id"))
            )
            return success_response(list(records))
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class AttendanceDetailUpdateView(APIView):
    def put(self, request, pk):
        try:
            attendance = AttendanceRecord.objects.get(pk=pk)
            if not user_can_access_class(request.user, attendance.student.class_name):
                return error_response("You can only update attendance for your in-charge class", status.HTTP_403_FORBIDDEN)
            serializer = AttendanceRecordSerializer(attendance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            student = serializer.validated_data.get("student", attendance.student)
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only move records within your in-charge class", status.HTTP_403_FORBIDDEN)
            serializer.save(is_manual=True)
            return success_response(serializer.data)
        except AttendanceRecord.DoesNotExist:
            return error_response("Attendance record not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class AttendanceCameraMarkView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        global TOKEN_WARNING_EMITTED
        try:
            expected_token = getattr(settings, "ESP32_DEVICE_TOKEN", "")
            incoming_token = request.headers.get("X-Device-Token", "")
            if expected_token and incoming_token != expected_token:
                return error_response("Invalid device token", status.HTTP_401_UNAUTHORIZED)

            if not expected_token and not TOKEN_WARNING_EMITTED:
                logger.warning("[ATTENDANCE_CAMERA] ESP32_DEVICE_TOKEN is not set; endpoint is open")
                TOKEN_WARNING_EMITTED = True

            raw_period = request.query_params.get("period")
            class_name = request.query_params.get("class_name", "").strip()

            raw_threshold = request.query_params.get("threshold")
            threshold = getattr(settings, "ESP32_FACE_MATCH_THRESHOLD", 0.6)
            if raw_threshold is not None:
                try:
                    threshold = float(raw_threshold)
                except ValueError:
                    return error_response("threshold must be a decimal value")

            content_type = (request.META.get("CONTENT_TYPE") or "").lower()
            image_file = None
            image_bytes = None

            if "multipart/form-data" in content_type:
                image_file = request.FILES.get("face_image") or request.FILES.get("file")
                if not image_file:
                    return error_response("Upload image as face_image or file field")
            else:
                image_bytes = request.body
                if not image_bytes:
                    return error_response("Request body is empty. Send JPEG bytes or multipart file")

            recognition_service = FaceRecognitionService()
            recognition_result = recognition_service.recognize_face(
                image_file=image_file,
                image_bytes=image_bytes,
                threshold=threshold,
            )

            if not recognition_result.success:
                return error_response(recognition_result.message, status.HTTP_400_BAD_REQUEST)

            if not recognition_result.matched:
                return success_response(
                    {
                        "marked": False,
                        "recognized": False,
                        "message": recognition_result.message,
                        "similarity": round(recognition_result.similarity, 4),
                    }
                )

            candidate_students = Student.objects.filter(
                name=recognition_result.student_name,
                is_active=True,
            ).order_by("-face_registered", "student_id")

            if class_name:
                candidate_students = candidate_students.filter(class_name=class_name)

            if not candidate_students.exists():
                return error_response(
                    f"Recognized student '{recognition_result.student_name}' not found in active records",
                    status.HTTP_404_NOT_FOUND,
                )

            if candidate_students.count() > 1:
                logger.warning(
                    "[ATTENDANCE_CAMERA] Multiple students found for recognized name '%s'; using first match",
                    recognition_result.student_name,
                )

            student = candidate_students.first()
            try:
                period, period_source, timetable_entry = _resolve_period_for_student(student, raw_period)
            except ValueError as exc:
                return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

            attendance_date = date.today()
            attendance, created = AttendanceRecord.objects.update_or_create(
                student=student,
                date=attendance_date,
                period=period,
                defaults={
                    "status": AttendanceRecord.STATUS_PRESENT,
                    "is_manual": False,
                    "note": _append_auto_note("Marked via ESP32-CAM face recognition", timetable_entry),
                },
            )

            return success_response(
                {
                    "marked": True,
                    "created": created,
                    "recognized": True,
                    "student_id": student.student_id,
                    "student_name": student.name,
                    "class_name": student.class_name,
                    "date": attendance.date.isoformat(),
                    "period": attendance.period,
                    "period_source": period_source,
                    "status": attendance.status,
                    "similarity": round(recognition_result.similarity, 4),
                    "message": "Attendance marked as present",
                },
                status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.exception("[ATTENDANCE_CAMERA] Unexpected error")
            return error_response(exc, status.HTTP_400_BAD_REQUEST)
