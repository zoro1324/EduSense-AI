from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import (
	AttendanceRecord,
	CustomUser,
	EngagementLog,
	ExamType,
	LeaveRequest,
	NotificationLog,
	NotificationTemplate,
	Parent,
	SafetyAlert,
	Student,
	StudentMark,
	StudentResult,
	Subject,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	model = CustomUser
	list_display = ("email", "username", "role", "is_active", "is_staff")
	ordering = ("email",)
	fieldsets = UserAdmin.fieldsets + (
		(
			"Additional Info",
			{
				"fields": (
					"role",
					"phone",
					"avatar",
					"created_at",
					"updated_at",
				)
			},
		),
	)
	readonly_fields = ("created_at", "updated_at")


class ParentInline(admin.StackedInline):
	model = Parent
	extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("student_id", "name", "roll_number", "class_name", "face_registered", "is_active")
	search_fields = ("name", "roll_number", "class_name")
	list_filter = ("class_name", "is_active", "face_registered")
	inlines = [ParentInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
	list_display = ("student", "date", "period", "status", "marked_by", "is_manual")
	list_filter = ("status", "date", "period", "is_manual")
	search_fields = ("student__name", "student__roll_number")


@admin.register(EngagementLog)
class EngagementLogAdmin(admin.ModelAdmin):
	list_display = ("class_name", "date", "period", "engagement_percent", "status")
	list_filter = ("class_name", "date", "period", "status")


@admin.register(SafetyAlert)
class SafetyAlertAdmin(admin.ModelAdmin):
	list_display = ("alert_type", "threat_level", "location", "status", "timestamp")
	list_filter = ("alert_type", "threat_level", "status")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
	list_display = ("student", "start_date", "end_date", "status", "reviewed_by")
	list_filter = ("status",)


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
	list_display = ("name", "class_name", "academic_year", "date")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ("name", "class_name")


@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
	list_display = ("student", "exam_type", "subject", "marks_obtained", "grade")


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
	list_display = ("student", "exam_type", "percentage", "grade", "rank", "report_sent")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
	list_display = ("notification_type", "student", "parent_phone", "channel", "status", "sent_at")
	list_filter = ("notification_type", "channel", "status")


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
	list_display = ("template_type", "updated_at")
