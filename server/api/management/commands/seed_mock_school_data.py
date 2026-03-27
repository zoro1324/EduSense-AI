from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from api.models import (
    AttendanceRecord,
    CustomUser,
    EngagementLog,
    ExamType,
    FacultyProfile,
    LeaveRequest,
    NotificationLog,
    NotificationTemplate,
    Parent,
    PeriodEngagementSummary,
    SafetyAlert,
    SchoolClass,
    Student,
    StudentMark,
    StudentResult,
    Subject,
    TimetableEntry,
    UnexcusedAbsence,
)
from api.utils import calculate_grade

User = get_user_model()


class Command(BaseCommand):
    help = "Seed full mock school data for local development and demos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--students-per-class",
            type=int,
            default=20,
            help="Number of students to seed per class (default: 20)",
        )
        parser.add_argument(
            "--history-days",
            type=int,
            default=5,
            help="Instructional days of attendance and engagement history to seed (default: 5)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="Password@123",
            help="Default password for all seeded users",
        )
        parser.add_argument(
            "--principal-email",
            type=str,
            default="principal@edusense.ai",
            help="Principal email address",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run seeding in a transaction and roll back at the end",
        )

    def handle(self, *args, **options):
        students_per_class = options["students_per_class"]
        history_days = options["history_days"]
        default_password = options["password"]
        principal_email = options["principal_email"]
        dry_run = options["dry_run"]

        if students_per_class <= 0:
            raise CommandError("--students-per-class must be greater than 0")
        if history_days <= 0:
            raise CommandError("--history-days must be greater than 0")

        with transaction.atomic():
            stats = self._seed_all(
                students_per_class=students_per_class,
                history_days=history_days,
                default_password=default_password,
                principal_email=principal_email,
            )

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS("Mock seed completed"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run enabled: all changes rolled back"))

        for model_name, counters in stats.items():
            self.stdout.write(
                f"- {model_name}: created={counters['created']}, updated={counters['updated']}"
            )

    def _seed_all(
        self,
        *,
        students_per_class: int,
        history_days: int,
        default_password: str,
        principal_email: str,
    ) -> Dict[str, Dict[str, int]]:
        stats: Dict[str, Dict[str, int]] = {}
        today = date.today()
        tz = timezone.get_current_timezone()
        academic_year = f"{today.year}-{(today.year + 1) % 100:02d}"

        class_specs = [
            {
                "name": "10A",
                "section": "A",
                "subjects": ["Tamil", "English", "Maths", "Science", "Social", "Computer Science"],
            },
            {
                "name": "11A",
                "section": "A",
                "subjects": ["English", "Physics", "Chemistry", "Maths", "Biology", "Computer Science"],
            },
            {
                "name": "12A",
                "section": "A",
                "subjects": ["English", "Physics", "Chemistry", "Maths", "Biology", "Economics"],
            },
        ]

        teacher_specs = [
            {
                "email": "anitha.teacher@edusense.ai",
                "username": "anitha.teacher",
                "first_name": "Anitha",
                "last_name": "Raman",
                "role": CustomUser.ROLE_TEACHER,
                "employee_code": "TCH-001",
                "department": "Science",
                "designation": "PG Teacher",
            },
            {
                "email": "bharath.teacher@edusense.ai",
                "username": "bharath.teacher",
                "first_name": "Bharath",
                "last_name": "Kumar",
                "role": CustomUser.ROLE_TEACHER,
                "employee_code": "TCH-002",
                "department": "Mathematics",
                "designation": "PG Teacher",
            },
            {
                "email": "chitra.teacher@edusense.ai",
                "username": "chitra.teacher",
                "first_name": "Chitra",
                "last_name": "Devi",
                "role": CustomUser.ROLE_TEACHER,
                "employee_code": "TCH-003",
                "department": "Languages",
                "designation": "Senior Teacher",
            },
            {
                "email": "dinesh.teacher@edusense.ai",
                "username": "dinesh.teacher",
                "first_name": "Dinesh",
                "last_name": "Raj",
                "role": CustomUser.ROLE_TEACHER,
                "employee_code": "TCH-004",
                "department": "Social Science",
                "designation": "Teacher",
            },
            {
                "email": "easwari.teacher@edusense.ai",
                "username": "easwari.teacher",
                "first_name": "Easwari",
                "last_name": "Priya",
                "role": CustomUser.ROLE_TEACHER,
                "employee_code": "TCH-005",
                "department": "Computer Science",
                "designation": "Teacher",
            },
            {
                "email": "farook.teacher@edusense.ai",
                "username": "farook.teacher",
                "first_name": "Farook",
                "last_name": "Ali",
                "role": CustomUser.ROLE_TEACHER,
                "employee_code": "TCH-006",
                "department": "General",
                "designation": "Teacher",
            },
        ]

        principal_user = self._upsert_user(
            stats,
            email=principal_email,
            username="principal.edusense",
            first_name="Priya",
            last_name="Natarajan",
            role=CustomUser.ROLE_PRINCIPAL,
            password=default_password,
            phone="9000000001",
            is_staff=True,
            is_superuser=False,
        )

        staff_user = self._upsert_user(
            stats,
            email="mentor.staff@edusense.ai",
            username="mentor.staff",
            first_name="Mentor",
            last_name="Staff",
            role=CustomUser.ROLE_STAFF,
            password=default_password,
            phone="9000000002",
            is_staff=False,
            is_superuser=False,
        )

        teachers = []
        for spec in teacher_specs:
            teacher = self._upsert_user(
                stats,
                email=spec["email"],
                username=spec["username"],
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                role=spec["role"],
                password=default_password,
                phone="9000000000",
                is_staff=False,
                is_superuser=False,
            )
            teachers.append(teacher)

            profile, created = FacultyProfile.objects.update_or_create(
                user=teacher,
                defaults={
                    "employee_code": spec["employee_code"],
                    "department": spec["department"],
                    "designation": spec["designation"],
                    "is_active": True,
                },
            )
            self._track(stats, "FacultyProfile", created)

        school_classes: List[SchoolClass] = []
        class_incharge_map = {}
        for idx, class_spec in enumerate(class_specs):
            incharge_teacher = teachers[idx % len(teachers)]
            school_class, created = SchoolClass.objects.update_or_create(
                name=class_spec["name"],
                defaults={
                    "section": class_spec["section"],
                    "incharge": incharge_teacher,
                    "is_active": True,
                },
            )
            self._track(stats, "SchoolClass", created)
            school_classes.append(school_class)
            class_incharge_map[school_class.name] = incharge_teacher

        period_slots = {
            1: (time(9, 0), time(9, 45)),
            2: (time(9, 50), time(10, 35)),
            3: (time(10, 40), time(11, 25)),
            4: (time(11, 30), time(12, 15)),
            5: (time(13, 15), time(14, 0)),
            6: (time(14, 5), time(14, 50)),
        }
        day_order = [
            TimetableEntry.DAY_MONDAY,
            TimetableEntry.DAY_TUESDAY,
            TimetableEntry.DAY_WEDNESDAY,
            TimetableEntry.DAY_THURSDAY,
            TimetableEntry.DAY_FRIDAY,
            TimetableEntry.DAY_SATURDAY,
        ]

        for class_index, school_class in enumerate(school_classes):
            subjects = class_specs[class_index]["subjects"]
            for day_index, day_name in enumerate(day_order):
                for period in range(1, 7):
                    if period == 6 and day_name in {
                        TimetableEntry.DAY_FRIDAY,
                        TimetableEntry.DAY_SATURDAY,
                    }:
                        faculty = staff_user
                        subject_name = "Activity"
                    else:
                        subject_name = subjects[(period + day_index - 1) % len(subjects)]
                        faculty = teachers[(class_index + day_index + period - 1) % len(teachers)]

                    start_time, end_time = period_slots[period]
                    entry, created = TimetableEntry.objects.update_or_create(
                        school_class=school_class,
                        day_of_week=day_name,
                        period=period,
                        defaults={
                            "subject_name": subject_name,
                            "faculty": faculty,
                            "room_number": f"R-{school_class.name}-{period}",
                            "start_time": start_time,
                            "end_time": end_time,
                            "is_active": True,
                        },
                    )
                    self._track(stats, "TimetableEntry", created)

        class_students: Dict[str, List[Student]] = {school_class.name: [] for school_class in school_classes}
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

        for class_index, school_class in enumerate(school_classes):
            grade = int(school_class.name[:2])
            for i in range(1, students_per_class + 1):
                roll_number = f"{school_class.name}{i:03d}"
                name = f"Student {school_class.name}-{i:02d}"
                dob_year = today.year - (grade + 5)
                month = ((i + class_index) % 12) + 1
                day = ((i * 2 + class_index) % 27) + 1
                student, created = Student.objects.update_or_create(
                    roll_number=roll_number,
                    defaults={
                        "name": name,
                        "class_name": school_class.name,
                        "date_of_birth": date(dob_year, month, day),
                        "blood_group": blood_groups[(i + class_index) % len(blood_groups)],
                        "address": f"{i} Main Street, Block {school_class.name}",
                        "face_embedding_path": "",
                        "face_registered": False,
                        "is_active": True,
                    },
                )
                self._track(stats, "Student", created)
                class_students[school_class.name].append(student)

                parent, p_created = Parent.objects.update_or_create(
                    student=student,
                    defaults={
                        "father_name": f"Parent Father {school_class.name}-{i:02d}",
                        "mother_name": f"Parent Mother {school_class.name}-{i:02d}",
                        "whatsapp_number": f"90010{class_index}{i:04d}",
                        "phone_number": f"90020{class_index}{i:04d}",
                        "email": f"parent.{roll_number.lower()}@example.com",
                    },
                )
                self._track(stats, "Parent", p_created)

        instructional_days = self._recent_instructional_days(today, history_days)

        for school_class in school_classes:
            incharge_user = class_incharge_map[school_class.name]
            students_in_class = class_students[school_class.name]
            class_size = len(students_in_class)

            for day_value in instructional_days:
                for period in range(1, 7):
                    for student in students_in_class:
                        score = (student.student_id * 17 + day_value.toordinal() * 3 + period * 19) % 100
                        if score < 82:
                            status = AttendanceRecord.STATUS_PRESENT
                        elif score < 90:
                            status = AttendanceRecord.STATUS_LATE
                        else:
                            status = AttendanceRecord.STATUS_ABSENT

                        attendance, created = AttendanceRecord.objects.update_or_create(
                            student=student,
                            date=day_value,
                            period=period,
                            defaults={
                                "status": status,
                                "marked_by": incharge_user,
                                "is_manual": status != AttendanceRecord.STATUS_PRESENT,
                                "note": "Seeded mock attendance",
                            },
                        )
                        self._track(stats, "AttendanceRecord", created)

                    start_time, _ = period_slots[period]
                    naive_timestamp = datetime.combine(day_value, start_time) + timedelta(minutes=5)
                    if timezone.is_aware(timezone.now()):
                        log_timestamp = timezone.make_aware(naive_timestamp, tz)
                    else:
                        log_timestamp = naive_timestamp

                    baseline = 78 - (period * 4)
                    if period == 5:
                        baseline -= 20
                    class_offset = (int(school_class.name[:2]) - 10) * 2
                    day_swing = (day_value.toordinal() + period) % 11 - 5
                    percent = max(28, min(96, baseline + class_offset + day_swing))

                    engaged_count = int(round(class_size * (percent / 100)))
                    distracted_count = max(0, class_size - engaged_count)
                    status_value = self._engagement_status(percent)

                    log, created = EngagementLog.objects.update_or_create(
                        class_name=school_class.name,
                        date=day_value,
                        period=period,
                        timestamp=log_timestamp,
                        defaults={
                            "total_persons": class_size,
                            "engaged_count": engaged_count,
                            "distracted_count": distracted_count,
                            "engagement_percent": float(percent),
                            "status": status_value,
                            "snapshot_path": f"seed/{school_class.name}/{day_value.isoformat()}-p{period}.jpg",
                        },
                    )
                    self._track(stats, "EngagementLog", created)

                    summary, s_created = PeriodEngagementSummary.objects.update_or_create(
                        class_name=school_class.name,
                        date=day_value,
                        period=period,
                        defaults={
                            "avg_engagement_percent": float(percent),
                            "min_engagement_percent": float(percent),
                            "max_engagement_percent": float(percent),
                            "dead_period_flag": percent < 40,
                        },
                    )
                    self._track(stats, "PeriodEngagementSummary", s_created)

        exam_specs = [
            (ExamType.UNIT_TEST_1, today - timedelta(days=45)),
            (ExamType.QUARTERLY, today - timedelta(days=20)),
        ]

        subjects_by_class: Dict[str, List[Subject]] = {}
        for class_index, school_class in enumerate(school_classes):
            subject_rows: List[Subject] = []
            for subject_name in class_specs[class_index]["subjects"]:
                subject, created = Subject.objects.update_or_create(
                    name=subject_name,
                    class_name=school_class.name,
                    defaults={},
                )
                self._track(stats, "Subject", created)
                subject_rows.append(subject)
            subjects_by_class[school_class.name] = subject_rows

        for school_class in school_classes:
            students_in_class = class_students[school_class.name]
            subject_rows = subjects_by_class[school_class.name]

            for exam_index, (exam_name, exam_date) in enumerate(exam_specs):
                exam, exam_created = ExamType.objects.update_or_create(
                    name=exam_name,
                    class_name=school_class.name,
                    academic_year=academic_year,
                    defaults={"date": exam_date},
                )
                self._track(stats, "ExamType", exam_created)

                for student in students_in_class:
                    total_marks = 0.0
                    max_total = 0.0
                    for subject_index, subject in enumerate(subject_rows):
                        marks_obtained = 52 + ((student.student_id + subject_index * 9 + exam_index * 13) % 49)
                        max_marks = 100.0
                        percentage = (marks_obtained / max_marks) * 100
                        grade = calculate_grade(percentage)

                        mark, mark_created = StudentMark.objects.update_or_create(
                            student=student,
                            exam_type=exam,
                            subject=subject,
                            defaults={
                                "marks_obtained": float(marks_obtained),
                                "max_marks": max_marks,
                                "grade": grade,
                            },
                        )
                        self._track(stats, "StudentMark", mark_created)

                        total_marks += float(marks_obtained)
                        max_total += max_marks

                    result_percentage = (total_marks / max_total) * 100 if max_total else 0.0
                    result, result_created = StudentResult.objects.update_or_create(
                        student=student,
                        exam_type=exam,
                        defaults={
                            "total_marks": total_marks,
                            "max_total": max_total,
                            "percentage": result_percentage,
                            "grade": calculate_grade(result_percentage),
                            "rank": None,
                            "ai_report": "",
                            "report_generated_at": None,
                            "report_sent": False,
                            "report_sent_at": None,
                        },
                    )
                    self._track(stats, "StudentResult", result_created)

        review_time = timezone.now() - timedelta(hours=4)
        for class_index, school_class in enumerate(school_classes):
            students_in_class = class_students[school_class.name]
            if len(students_in_class) < 4:
                continue

            leave_rows: List[Tuple[Student, str, int]] = [
                (students_in_class[0], LeaveRequest.STATUS_PENDING, 1),
                (students_in_class[1], LeaveRequest.STATUS_APPROVED, 2),
                (students_in_class[2], LeaveRequest.STATUS_REJECTED, 3),
            ]

            for student, leave_status, start_offset in leave_rows:
                start_date = today + timedelta(days=start_offset)
                end_date = start_date
                reviewed_by = principal_user if leave_status != LeaveRequest.STATUS_PENDING else None
                reviewed_at = review_time if reviewed_by else None
                rejection_reason = "Insufficient reason" if leave_status == LeaveRequest.STATUS_REJECTED else ""
                parent_notified = leave_status != LeaveRequest.STATUS_PENDING

                leave, leave_created = LeaveRequest.objects.update_or_create(
                    student=student,
                    start_date=start_date,
                    end_date=end_date,
                    defaults={
                        "reason": "Seeded leave request",
                        "status": leave_status,
                        "reviewed_by": reviewed_by,
                        "reviewed_at": reviewed_at,
                        "rejection_reason": rejection_reason,
                        "parent_notified": parent_notified,
                        "notification_sent_at": reviewed_at,
                    },
                )
                self._track(stats, "LeaveRequest", leave_created)

            absence_student = students_in_class[3]
            absence, absence_created = UnexcusedAbsence.objects.update_or_create(
                student=absence_student,
                date=today - timedelta(days=1),
                defaults={
                    "parent_notified": False,
                    "notified_at": None,
                },
            )
            self._track(stats, "UnexcusedAbsence", absence_created)

        for school_class in school_classes:
            unresolved, unresolved_created = SafetyAlert.objects.update_or_create(
                alert_type=SafetyAlert.TYPE_GROUPING,
                threat_level=SafetyAlert.THREAT_MEDIUM,
                class_name=school_class.name,
                location=f"{school_class.name} Corridor",
                description="Seeded medium grouping alert",
                defaults={
                    "person_count": 5,
                    "status": SafetyAlert.STATUS_UNRESOLVED,
                    "resolved_by": None,
                    "resolved_at": None,
                    "resolution_note": "",
                    "parent_notified": False,
                },
            )
            self._track(stats, "SafetyAlert", unresolved_created)

            resolved, resolved_created = SafetyAlert.objects.update_or_create(
                alert_type=SafetyAlert.TYPE_RAGGING,
                threat_level=SafetyAlert.THREAT_HIGH,
                class_name=school_class.name,
                location=f"{school_class.name} Ground",
                description="Seeded high severity alert (resolved)",
                defaults={
                    "person_count": 3,
                    "status": SafetyAlert.STATUS_RESOLVED,
                    "resolved_by": principal_user,
                    "resolved_at": timezone.now() - timedelta(hours=2),
                    "resolution_note": "Intervened and resolved by administration",
                    "parent_notified": True,
                },
            )
            self._track(stats, "SafetyAlert", resolved_created)

        templates = {
            "absent": (
                "Dear {parent_name}, {student_name} is absent for period {period} on {date}.",
                "parent_name,student_name,period,date",
            ),
            "leave_approved": (
                "Dear {parent_name}, leave for {student_name} from {start_date} to {end_date} is approved.",
                "parent_name,student_name,start_date,end_date",
            ),
            "leave_rejected": (
                "Dear {parent_name}, leave for {student_name} was rejected. Please contact class incharge.",
                "parent_name,student_name",
            ),
            "result_report": (
                "Dear {parent_name}, result for {student_name}: {percentage}% ({grade}).",
                "parent_name,student_name,percentage,grade",
            ),
            "safety_alert": (
                "Safety alert reported for {class_name} at {location}. Please stay alert.",
                "class_name,location",
            ),
            "weekly_summary": (
                "Weekly summary for {student_name}: attendance {attendance}%, engagement {engagement}%.",
                "student_name,attendance,engagement",
            ),
            "attendance_warning": (
                "Attendance warning for {student_name}: below threshold.",
                "student_name",
            ),
        }

        for template_type, (body, variables) in templates.items():
            template, created = NotificationTemplate.objects.update_or_create(
                template_type=template_type,
                defaults={
                    "template_body": body,
                    "variables": variables,
                },
            )
            self._track(stats, "NotificationTemplate", created)

        for school_class in school_classes:
            students_in_class = class_students[school_class.name]
            if not students_in_class:
                continue

            sample_student = students_in_class[0]
            parent = Parent.objects.get(student=sample_student)
            message = (
                f"Attendance warning for {sample_student.name} ({school_class.name}) "
                f"on {today.isoformat()}"
            )

            notif, created = NotificationLog.objects.update_or_create(
                notification_type=NotificationLog.TYPE_ATTENDANCE_WARNING,
                channel=NotificationLog.CHANNEL_WHATSAPP,
                parent_phone=parent.whatsapp_number,
                message_body=message,
                defaults={
                    "student": sample_student,
                    "parent_name": parent.father_name,
                    "status": NotificationLog.STATUS_DELIVERED,
                    "twilio_sid": f"MOCK-{sample_student.roll_number}",
                    "error_message": "",
                },
            )
            self._track(stats, "NotificationLog", created)

        return stats

    def _upsert_user(
        self,
        stats: Dict[str, Dict[str, int]],
        *,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        role: str,
        password: str,
        phone: str,
        is_staff: bool,
        is_superuser: bool,
    ):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "phone": phone,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )

        updated = False
        if not created:
            fields_to_update = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "phone": phone,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            }
            dirty_fields = []
            for field_name, value in fields_to_update.items():
                if getattr(user, field_name) != value:
                    setattr(user, field_name, value)
                    dirty_fields.append(field_name)
            if dirty_fields:
                user.save(update_fields=dirty_fields)
                updated = True

        if not user.check_password(password):
            user.set_password(password)
            user.save(update_fields=["password"])
            updated = True

        if created:
            self._track(stats, "CustomUser", True)
        elif updated:
            self._track(stats, "CustomUser", False)

        return user

    def _recent_instructional_days(self, today: date, days_count: int) -> List[date]:
        days: List[date] = []
        offset = 0
        while len(days) < days_count:
            value = today - timedelta(days=offset)
            offset += 1
            if value.weekday() == 6:
                continue
            days.append(value)
        days.sort()
        return days

    def _engagement_status(self, percent: int) -> str:
        if percent >= 70:
            return EngagementLog.STATUS_HIGH
        if percent >= 40:
            return EngagementLog.STATUS_MEDIUM
        return EngagementLog.STATUS_LOW

    def _track(self, stats: Dict[str, Dict[str, int]], key: str, created: bool) -> None:
        if key not in stats:
            stats[key] = {"created": 0, "updated": 0}
        if created:
            stats[key]["created"] += 1
        else:
            stats[key]["updated"] += 1
