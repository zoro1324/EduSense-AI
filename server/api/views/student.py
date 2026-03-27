import csv
import io
import logging
from typing import cast

from django.db.models import Count
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView

from api.access_control import scope_queryset_to_user_classes, user_can_access_class
from api.models import Parent, Student
from api.services import FaceRegistrationService
from api.serializers import StudentSerializer
from api.views import error_response, success_response

logger = logging.getLogger(__name__)


class StudentListCreateView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request):
        try:
            students = Student.objects.filter(is_active=True).order_by("name")
            students = scope_queryset_to_user_classes(students, request.user, "class_name")
            return success_response(StudentSerializer(students, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.debug(f"[STUDENT] POST request received. Content-Type: {request.META.get('CONTENT_TYPE', 'unknown')}")
            logger.debug(f"[STUDENT] Request data: {request.data}")
            logger.debug(f"[STUDENT] Request files: {request.FILES}")
            
            # Extract parent data from flattened FormData
            data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
            parent_data = {}
            parent_fields = ['father_name', 'mother_name', 'whatsapp_number', 'phone_number', 'email']
            
            for field in parent_fields:
                key = f'parent.{field}'
                if key in data:
                    parent_data[field] = data.pop(key)
            
            if parent_data:
                data['parent'] = parent_data
            
            # Handle photo file
            if 'photo' in request.FILES:
                data['photo'] = request.FILES['photo']

            class_name = data.get("class_name")
            if not class_name:
                return error_response("class_name is required")
            if not user_can_access_class(request.user, class_name):
                return error_response("You can only create students for your in-charge class", status.HTTP_403_FORBIDDEN)
            
            logger.debug(f"[STUDENT] Processed data: {data}")
            
            serializer = StudentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            student = cast(Student, serializer.save())
            
            logger.info(f"[STUDENT] Student created successfully: {student.name}")
            return success_response(StudentSerializer(student).data, status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error(f"[STUDENT] Error creating student: {str(exc)}", exc_info=True)
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class StudentClassesView(APIView):
    def get(self, request):
        try:
            classes = (
                scope_queryset_to_user_classes(Student.objects.filter(is_active=True), request.user, "class_name")
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
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only view students from your in-charge class", status.HTTP_403_FORBIDDEN)
            return success_response(StudentSerializer(student).data)
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only update students from your in-charge class", status.HTTP_403_FORBIDDEN)

            incoming_class_name = request.data.get("class_name", student.class_name)
            if not user_can_access_class(request.user, incoming_class_name):
                return error_response("You can only move students within your in-charge class", status.HTTP_403_FORBIDDEN)

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
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only deactivate students from your in-charge class", status.HTTP_403_FORBIDDEN)
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
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only view students from your in-charge class", status.HTTP_403_FORBIDDEN)
            data = StudentSerializer(student).data
            return success_response(data)
        except Student.DoesNotExist:
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterFaceView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, pk):
        try:
            logger.debug(f"[FACE_REGISTER] POST request for student {pk}")
            logger.debug(f"[FACE_REGISTER] Request files: {request.FILES}")
            logger.debug(f"[FACE_REGISTER] Request data: {request.data}")
            
            student = Student.objects.get(pk=pk)
            if not user_can_access_class(request.user, student.class_name):
                return error_response("You can only register faces for your in-charge class", status.HTTP_403_FORBIDDEN)
            image_file = request.FILES.get("face_image") or request.FILES.get("file")
            service = FaceRegistrationService()
            result = service.register_face(student=student, image_file=image_file)

            if not result.success:
                logger.warning(f"[FACE_REGISTER] Registration failed for student {pk}: {result.message}")
                return error_response(result.message, status.HTTP_400_BAD_REQUEST)

            student.face_embedding_path = result.embedding_path
            student.face_registered = True
            student.save(update_fields=["face_embedding_path", "face_registered"])

            logger.info(f"[FACE_REGISTER] Face registered successfully for student: {student.name}")
            return success_response(
                {
                    "message": result.message,
                    "student_id": student.student_id,
                    "embedding_path": result.embedding_path,
                    "source": result.source,
                }
            )
                    
        except Student.DoesNotExist:
            logger.error(f"[FACE_REGISTER] Student not found: {pk}")
            return error_response("Student not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            logger.error(f"[FACE_REGISTER] Exception occurred: {str(exc)}", exc_info=True)
            return error_response(f"Face registration failed: {str(exc)}", status.HTTP_400_BAD_REQUEST)


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
                class_name = row.get("class_name", "")
                if not user_can_access_class(request.user, class_name):
                    return error_response(
                        f"You can only upload students for your in-charge class. Invalid class: {class_name}",
                        status.HTTP_403_FORBIDDEN,
                    )

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
