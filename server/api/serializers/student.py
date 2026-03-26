from rest_framework import serializers

from api.models import Parent, Student


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
            "id",
            "father_name",
            "mother_name",
            "whatsapp_number",
            "phone_number",
            "email",
        ]


class StudentSerializer(serializers.ModelSerializer):
    parent = ParentSerializer(required=False)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "name",
            "roll_number",
            "class_name",
            "date_of_birth",
            "blood_group",
            "address",
            "photo",
            "face_embedding_path",
            "face_registered",
            "is_active",
            "created_at",
            "updated_at",
            "parent",
        ]
        read_only_fields = ["created_at", "updated_at", "face_registered"]

    def create(self, validated_data):
        parent_data = validated_data.pop("parent", None)
        student = Student.objects.create(**validated_data)
        if parent_data:
            Parent.objects.create(student=student, **parent_data)
        return student

    def update(self, instance, validated_data):
        parent_data = validated_data.pop("parent", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if parent_data:
            parent, _ = Parent.objects.get_or_create(student=instance)
            for attr, value in parent_data.items():
                setattr(parent, attr, value)
            parent.save()

        return instance
