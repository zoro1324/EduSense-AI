from datetime import date

from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView

from api.models import AttendanceRecord
from api.serializers import AttendanceRecordSerializer
from api.views import error_response, success_response


class AttendanceMarkView(APIView):
    def post(self, request):
        try:
            serializer = AttendanceRecordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
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
                serializer = AttendanceRecordSerializer(data=item)
                serializer.is_valid(raise_exception=True)
                serializer.save(marked_by=request.user)
                saved.append(serializer.data)
            return success_response(saved, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class AttendanceListView(APIView):
    def get(self, request):
        try:
            queryset = AttendanceRecord.objects.select_related("student", "marked_by").all().order_by("-date", "period")
            serializer = AttendanceRecordSerializer(queryset, many=True)
            return success_response(serializer.data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceTodayView(APIView):
    def get(self, request):
        try:
            queryset = AttendanceRecord.objects.filter(date=date.today()).select_related("student")
            serializer = AttendanceRecordSerializer(queryset, many=True)
            return success_response(serializer.data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceSummaryView(APIView):
    def get(self, request):
        try:
            summary = AttendanceRecord.objects.values("status").annotate(total=Count("id")).order_by("status")
            return success_response(list(summary))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceDailyView(APIView):
    def get(self, request):
        try:
            day = request.query_params.get("date", date.today())
            records = AttendanceRecord.objects.filter(date=day).values("period", "status").annotate(total=Count("id"))
            return success_response(list(records))
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class AttendanceDetailUpdateView(APIView):
    def put(self, request, pk):
        try:
            attendance = AttendanceRecord.objects.get(pk=pk)
            serializer = AttendanceRecordSerializer(attendance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(is_manual=True)
            return success_response(serializer.data)
        except AttendanceRecord.DoesNotExist:
            return error_response("Attendance record not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)
