from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView

from api.access_control import is_principal, scope_queryset_to_user_classes, user_can_access_class
from api.models import FacultyProfile, SchoolClass, TimetableEntry
from api.serializers import FacultyProfileSerializer, SchoolClassSerializer, TimetableEntrySerializer
from api.views import error_response, success_response

User = get_user_model()


class SchoolClassListCreateView(APIView):
    def get(self, request):
        try:
            queryset = SchoolClass.objects.select_related("incharge").all().order_by("name")
            queryset = scope_queryset_to_user_classes(queryset, request.user, "name")
            return success_response(SchoolClassSerializer(queryset, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can create classes", status.HTTP_403_FORBIDDEN)
            serializer = SchoolClassSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            school_class = serializer.save()
            return success_response(SchoolClassSerializer(school_class).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class SchoolClassDetailView(APIView):
    def get(self, request, pk):
        try:
            school_class = SchoolClass.objects.select_related("incharge").get(pk=pk)
            if not user_can_access_class(request.user, school_class.name):
                return error_response("You can only view your in-charge class", status.HTTP_403_FORBIDDEN)
            return success_response(SchoolClassSerializer(school_class).data)
        except SchoolClass.DoesNotExist:
            return error_response("Class not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can update classes", status.HTTP_403_FORBIDDEN)
            school_class = SchoolClass.objects.get(pk=pk)
            serializer = SchoolClassSerializer(school_class, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except SchoolClass.DoesNotExist:
            return error_response("Class not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can deactivate classes", status.HTTP_403_FORBIDDEN)
            school_class = SchoolClass.objects.get(pk=pk)
            school_class.is_active = False
            school_class.save(update_fields=["is_active", "updated_at"])
            return success_response({"message": "Class deactivated"})
        except SchoolClass.DoesNotExist:
            return error_response("Class not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class FacultyListCreateView(APIView):
    def get(self, request):
        try:
            queryset = FacultyProfile.objects.select_related("user").all().order_by("employee_code")
            if not is_principal(request.user):
                return error_response("Only principal can view faculty table", status.HTTP_403_FORBIDDEN)
            return success_response(FacultyProfileSerializer(queryset, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can create faculty records", status.HTTP_403_FORBIDDEN)
            serializer = FacultyProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            faculty = serializer.save()
            return success_response(FacultyProfileSerializer(faculty).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class FacultyDetailView(APIView):
    def put(self, request, pk):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can update faculty records", status.HTTP_403_FORBIDDEN)
            faculty = FacultyProfile.objects.get(pk=pk)
            serializer = FacultyProfileSerializer(faculty, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except FacultyProfile.DoesNotExist:
            return error_response("Faculty record not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            if not is_principal(request.user):
                return error_response("Only principal can deactivate faculty records", status.HTTP_403_FORBIDDEN)
            faculty = FacultyProfile.objects.get(pk=pk)
            faculty.is_active = False
            faculty.save(update_fields=["is_active", "updated_at"])
            return success_response({"message": "Faculty deactivated"})
        except FacultyProfile.DoesNotExist:
            return error_response("Faculty record not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TimetableListCreateView(APIView):
    def get(self, request):
        try:
            queryset = TimetableEntry.objects.select_related("school_class", "faculty").all().order_by(
                "school_class__name", "day_of_week", "period"
            )
            queryset = scope_queryset_to_user_classes(queryset, request.user, "school_class__name")

            class_name = request.query_params.get("class_name")
            day_of_week = request.query_params.get("day_of_week")
            period = request.query_params.get("period")

            if class_name:
                queryset = queryset.filter(school_class__name=class_name)
            if day_of_week:
                queryset = queryset.filter(day_of_week=day_of_week)
            if period:
                queryset = queryset.filter(period=period)

            return success_response(TimetableEntrySerializer(queryset, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            school_class_id = request.data.get("school_class")
            if not school_class_id:
                return error_response("school_class is required")

            school_class = SchoolClass.objects.get(pk=school_class_id)
            if not user_can_access_class(request.user, school_class.name):
                return error_response("You can only add timetable for your in-charge class", status.HTTP_403_FORBIDDEN)

            serializer = TimetableEntrySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            entry = serializer.save()
            return success_response(TimetableEntrySerializer(entry).data, status.HTTP_201_CREATED)
        except SchoolClass.DoesNotExist:
            return error_response("Class not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class TimetableDetailView(APIView):
    def get(self, request, pk):
        try:
            entry = TimetableEntry.objects.select_related("school_class", "faculty").get(pk=pk)
            if not user_can_access_class(request.user, entry.school_class.name):
                return error_response("You can only view timetable for your in-charge class", status.HTTP_403_FORBIDDEN)
            return success_response(TimetableEntrySerializer(entry).data)
        except TimetableEntry.DoesNotExist:
            return error_response("Timetable entry not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            entry = TimetableEntry.objects.select_related("school_class").get(pk=pk)
            if not user_can_access_class(request.user, entry.school_class.name):
                return error_response("You can only update timetable for your in-charge class", status.HTTP_403_FORBIDDEN)

            school_class = entry.school_class
            incoming_class_id = request.data.get("school_class")
            if incoming_class_id:
                school_class = SchoolClass.objects.get(pk=incoming_class_id)
            if not user_can_access_class(request.user, school_class.name):
                return error_response("You can only move timetable within your in-charge class", status.HTTP_403_FORBIDDEN)

            serializer = TimetableEntrySerializer(entry, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return success_response(serializer.data)
        except TimetableEntry.DoesNotExist:
            return error_response("Timetable entry not found", status.HTTP_404_NOT_FOUND)
        except SchoolClass.DoesNotExist:
            return error_response("Class not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            entry = TimetableEntry.objects.select_related("school_class").get(pk=pk)
            if not user_can_access_class(request.user, entry.school_class.name):
                return error_response("You can only delete timetable for your in-charge class", status.HTTP_403_FORBIDDEN)
            entry.delete()
            return success_response({"message": "Timetable entry deleted"})
        except TimetableEntry.DoesNotExist:
            return error_response("Timetable entry not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
