from django.db import models


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=10)
    address = models.TextField()
    photo = models.ImageField(upload_to="students/photos/", blank=True, null=True)
    face_embedding_path = models.CharField(max_length=500, blank=True)
    face_registered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.roll_number} - {self.name}"


class Parent(models.Model):
    student = models.OneToOneField(Student, related_name="parent", on_delete=models.CASCADE)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"Parent of {self.student.name}"
