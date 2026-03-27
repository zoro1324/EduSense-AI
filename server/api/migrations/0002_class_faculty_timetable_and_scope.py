from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def seed_school_classes(apps, schema_editor):
    Student = apps.get_model("api", "Student")
    SchoolClass = apps.get_model("api", "SchoolClass")

    class_names = (
        Student.objects.exclude(class_name="")
        .values_list("class_name", flat=True)
        .distinct()
    )
    for name in class_names:
        SchoolClass.objects.get_or_create(name=name)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("principal", "Principal"),
                    ("admin", "Admin"),
                    ("teacher", "Teacher"),
                    ("staff", "Staff"),
                ],
                default="staff",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="safetyalert",
            name="class_name",
            field=models.CharField(default="General", max_length=50),
        ),
        migrations.CreateModel(
            name="FacultyProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee_code", models.CharField(max_length=50, unique=True)),
                ("department", models.CharField(blank=True, max_length=100)),
                ("designation", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="faculty_profile", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["employee_code"]},
        ),
        migrations.CreateModel(
            name="SchoolClass",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
                ("section", models.CharField(blank=True, max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "incharge",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="incharge_classes", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="TimetableEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "day_of_week",
                    models.CharField(
                        choices=[
                            ("monday", "Monday"),
                            ("tuesday", "Tuesday"),
                            ("wednesday", "Wednesday"),
                            ("thursday", "Thursday"),
                            ("friday", "Friday"),
                            ("saturday", "Saturday"),
                        ],
                        max_length=20,
                    ),
                ),
                ("period", models.PositiveSmallIntegerField()),
                ("subject_name", models.CharField(max_length=100)),
                ("room_number", models.CharField(blank=True, max_length=30)),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("end_time", models.TimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "faculty",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="timetable_entries", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "school_class",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="timetable_entries", to="api.schoolclass"),
                ),
            ],
            options={"ordering": ["school_class__name", "day_of_week", "period"]},
        ),
        migrations.AlterUniqueTogether(
            name="timetableentry",
            unique_together={("school_class", "day_of_week", "period")},
        ),
        migrations.RunPython(seed_school_classes, noop_reverse),
    ]
