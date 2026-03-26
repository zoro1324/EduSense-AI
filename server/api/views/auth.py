import logging
from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import ChangePasswordSerializer, UserCreateSerializer, UserSerializer
from api.views import error_response, success_response

logger = logging.getLogger(__name__)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def options(self, request, *args, **kwargs):
        logger.debug(f"[CORS] OPTIONS preflight request from: {request.META.get('HTTP_ORIGIN', 'unknown')}")
        return super().options(request, *args, **kwargs)

    def post(self, request):
        try:
            logger.debug(f"[LOGIN] POST request received from: {request.META.get('HTTP_ORIGIN', 'unknown')}")
            logger.debug(f"[LOGIN] Request headers: {dict(request.headers)}")
            logger.debug(f"[LOGIN] Request data: {request.data}")
            
            email = request.data.get("email")
            password = request.data.get("password")
            
            logger.debug(f"[LOGIN] Attempting authentication with email: {email}")
            user = authenticate(request, username=email, password=password)
            
            if not user:
                logger.warning(f"[LOGIN] Authentication failed for email: {email}")
                return error_response("Invalid credentials", status.HTTP_401_UNAUTHORIZED)
            
            logger.info(f"[LOGIN] User authenticated successfully: {email}")
            refresh = RefreshToken.for_user(user)
            return success_response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                }
            )
        except Exception as exc:
            logger.error(f"[LOGIN] Exception occurred: {str(exc)}", exc_info=True)
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    def post(self, request):
        try:
            return success_response({"message": "Logged out successfully"})
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshTokenViewCustom(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return error_response("Refresh token is required")
            refresh = RefreshToken(refresh_token)
            return success_response({"access": str(refresh.access_token)})
        except Exception as exc:
            return error_response(f"Invalid refresh token: {exc}", status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    def get(self, request):
        try:
            return success_response(UserSerializer(request.user).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = request.user
            old_password = request.data.get("old_password")
            new_password = request.data.get("new_password")
            if not old_password or not new_password:
                return error_response("Both old_password and new_password are required")
            if not user.check_password(old_password):
                return error_response("Old password is incorrect")
            user.set_password(new_password)
            user.save(update_fields=["password"])
            return success_response({"message": "Password changed successfully"})
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class UserListCreateView(APIView):
    def get(self, request):
        try:
            users = get_user_model().objects.all().order_by("-id")
            return success_response(UserSerializer(users, many=True).data)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = UserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return success_response(UserSerializer(user).data, status.HTTP_201_CREATED)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    def get(self, request, pk):
        try:
            user = get_user_model().objects.get(pk=pk)
            return success_response(UserSerializer(user).data)
        except get_user_model().DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            user = get_user_model().objects.get(pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data)
        except get_user_model().DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = get_user_model().objects.get(pk=pk)
            user.delete()
            return success_response({"message": "User deleted"})
        except get_user_model().DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
