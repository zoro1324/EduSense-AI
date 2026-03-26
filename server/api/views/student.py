import csv
import io

from django.db.models import Count
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from api.models import Parent, Student
from api.serializers import StudentSerializer
from api.views import error_response, success_response


class StudentListCreateView(APIView):
    def get(self, request):
        try:
            students = Student.objects.filter(is_active=True).order_by("name")
            return success_response(StudentSerializer(students, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = StudentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            student = serializer.save()
            return success_response(StudentSerializer(student).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class StudentClassesView(APIView):
    def get(self, request):
        try:
            classes = (
                Student.objects.filter(is_active=True)
                .values("class_name")
                .annotate(total=Count("student_id"))
                .order_by("class_name")
            )
            return success_response(list(classes))
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentDetailView(APIView):
    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            return success_response(StudentSerializer(student).data)
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            serializer = StudentSerializer(student, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            student.is_active = False
            student.save(update_fields=["is_active"])
            return success_response({"message": "Student deactivated"})
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentProfileView(APIView):
    def get(self, request, pk):
        try:
            student = Student.objects.select_related("parent").get(pk=pk)
            data = StudentSerializer(student).data
            return success_response(data)
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterFaceView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            face_embedding_path = request.data.get("face_embedding_path", "")
            student.face_embedding_path = face_embedding_path
            student.face_registered = True
            student.save(update_fields=["face_embedding_path", "face_registered"])
            return success_response({"message": "Face registered", "student_id": student.student_id})
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class StudentBulkUploadView(APIView):
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
                student, was_created = Student.objects.get_or_create(
                    roll_number=row["roll_number"],
                    defaults={
                        "name": row["name"],
                        "class_name": row["class_name"],
                        "date_of_birth": row["date_of_birth"],
                        "blood_group": row.get("blood_group", ""),
                        "address": row.get("address", ""),
                    },
                )
                if was_created:
                    Parent.objects.get_or_create(
                        student=student,
                        defaults={
                            "father_name": row.get("father_name", ""),
                            "mother_name": row.get("mother_name", ""),
                            "whatsapp_number": row.get("whatsapp_number", ""),
                            "phone_number": row.get("phone_number", ""),
                            "email": row.get("email", ""),
                        },
                    )
                    created += 1

            return success_response({"created": created})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)
