from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.access_control import get_managed_class_names


class UserSerializer(serializers.ModelSerializer):
    managed_classes = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "username",
            "role",
            "phone",
            "avatar",
            "is_active",
            "first_name",
            "last_name",
            "managed_classes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_managed_classes(self, obj):
        managed = get_managed_class_names(obj)
        return [] if managed is None else managed


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "username",
            "password",
            "role",
            "phone",
            "avatar",
            "is_active",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
