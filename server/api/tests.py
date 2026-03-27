from datetime import time

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from api.access_control import get_managed_class_names
from api.models import SchoolClass, TimetableEntry


class ManagedClassScopeTests(TestCase):
	def setUp(self):
		self.User = get_user_model()

	def test_non_principal_scope_merges_incharge_and_timetable_classes(self):
		teacher = self.User.objects.create_user(
			email="teacher.scope@edusense.ai",
			username="teacher.scope",
			password="Password@123",
			role=self.User.ROLE_TEACHER,
		)

		incharge_class = SchoolClass.objects.create(name="10A", section="A", incharge=teacher)
		taught_class = SchoolClass.objects.create(name="11A", section="A")

		TimetableEntry.objects.create(
			school_class=taught_class,
			day_of_week=TimetableEntry.DAY_MONDAY,
			period=1,
			subject_name="Maths",
			faculty=teacher,
			room_number="R-11A-1",
			start_time=time(9, 0),
			end_time=time(9, 45),
		)

		managed = get_managed_class_names(teacher)
		self.assertEqual(managed, [incharge_class.name, taught_class.name])

	def test_principal_scope_is_unrestricted(self):
		principal = self.User.objects.create_user(
			email="principal.scope@edusense.ai",
			username="principal.scope",
			password="Password@123",
			role=self.User.ROLE_PRINCIPAL,
		)

		self.assertIsNone(get_managed_class_names(principal))


class SeedCommandTests(TestCase):
	def test_seed_command_is_idempotent_and_creates_complete_timetable_periods(self):
		command_args = {
			"students_per_class": 2,
			"history_days": 2,
			"password": "Password@123",
			"principal_email": "principal.test@edusense.ai",
			"verbosity": 0,
		}

		call_command("seed_mock_school_data", **command_args)

		self.assertEqual(SchoolClass.objects.count(), 3)
		self.assertEqual(TimetableEntry.objects.count(), 108)
		self.assertFalse(TimetableEntry.objects.filter(subject_name="").exists())
		self.assertFalse(TimetableEntry.objects.filter(faculty__isnull=True).exists())

		snapshot_counts = {
			"users": get_user_model().objects.count(),
			"classes": SchoolClass.objects.count(),
			"timetable": TimetableEntry.objects.count(),
		}

		call_command("seed_mock_school_data", **command_args)

		self.assertEqual(get_user_model().objects.count(), snapshot_counts["users"])
		self.assertEqual(SchoolClass.objects.count(), snapshot_counts["classes"])
		self.assertEqual(TimetableEntry.objects.count(), snapshot_counts["timetable"])
