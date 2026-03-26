from django.urls import path

from api.views.attendance import (
    AttendanceDailyView,
    AttendanceDetailUpdateView,
    AttendanceListView,
    AttendanceMarkBulkView,
    AttendanceMarkView,
    AttendanceSummaryView,
    AttendanceTodayView,
)
from api.views.auth import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    RefreshTokenViewCustom,
    UserDetailView,
    UserListCreateView,
)
from api.views.engagement import (
    EngagementHeatmapView,
    EngagementHistoryView,
    EngagementLogCreateView,
    EngagementLogsView,
    EngagementTodayView,
)
from api.views.leave import (
    LeaveApproveView,
    LeaveDetailView,
    LeaveListCreateView,
    LeaveRejectView,
    UnexcusedAbsenceListView,
    UnexcusedNotifyAllView,
    UnexcusedNotifyView,
)
from api.views.marks import (
    ExamListCreateView,
    MarkAddView,
    MarkBulkUploadView,
    MarkListView,
    RecomputeResultsView,
    ResultGenerateAllReportsView,
    ResultGenerateReportView,
    ResultListView,
    ResultSendAllReportsView,
    ResultSendReportView,
    SubjectListCreateView,
)
from api.views.notification import (
    NotificationListView,
    NotificationResendView,
    NotificationTemplateListView,
    NotificationTemplateUpdateView,
    NotificationTestView,
)
from api.views.reports import (
    AcademicReportView,
    AttendanceReportView,
    DashboardReportView,
    EngagementReportView,
    SafetyReportView,
)
from api.views.safety import SafetyAlertDetailView, SafetyAlertListCreateView, SafetyResolveView, SafetyStatsView
from api.views.student import (
    RegisterFaceView,
    StudentBulkUploadView,
    StudentClassesView,
    StudentDetailView,
    StudentListCreateView,
    StudentProfileView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/refresh/", RefreshTokenViewCustom.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/change-password/", ChangePasswordView.as_view()),

    path("users/", UserListCreateView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),

    path("students/", StudentListCreateView.as_view()),
    path("students/classes/", StudentClassesView.as_view()),
    path("students/<int:pk>/", StudentDetailView.as_view()),
    path("students/<int:pk>/profile/", StudentProfileView.as_view()),
    path("students/<int:pk>/register-face/", RegisterFaceView.as_view()),
    path("students/bulk-upload/", StudentBulkUploadView.as_view()),

    path("attendance/mark/", AttendanceMarkView.as_view()),
    path("attendance/mark-bulk/", AttendanceMarkBulkView.as_view()),
    path("attendance/", AttendanceListView.as_view()),
    path("attendance/today/", AttendanceTodayView.as_view()),
    path("attendance/summary/", AttendanceSummaryView.as_view()),
    path("attendance/daily/", AttendanceDailyView.as_view()),
    path("attendance/<int:pk>/", AttendanceDetailUpdateView.as_view()),

    path("engagement/log/", EngagementLogCreateView.as_view()),
    path("engagement/logs/", EngagementLogsView.as_view()),
    path("engagement/today/", EngagementTodayView.as_view()),
    path("engagement/history/", EngagementHistoryView.as_view()),
    path("engagement/heatmap/", EngagementHeatmapView.as_view()),

    path("safety/alerts/", SafetyAlertListCreateView.as_view()),
    path("safety/alerts/<int:pk>/", SafetyAlertDetailView.as_view()),
    path("safety/alerts/<int:pk>/resolve/", SafetyResolveView.as_view()),
    path("safety/stats/", SafetyStatsView.as_view()),

    path("leaves/", LeaveListCreateView.as_view()),
    path("leaves/<int:pk>/", LeaveDetailView.as_view()),
    path("leaves/<int:pk>/approve/", LeaveApproveView.as_view()),
    path("leaves/<int:pk>/reject/", LeaveRejectView.as_view()),
    path("leaves/unexcused/", UnexcusedAbsenceListView.as_view()),
    path("leaves/unexcused/<int:pk>/notify/", UnexcusedNotifyView.as_view()),
    path("leaves/unexcused/notify-all/", UnexcusedNotifyAllView.as_view()),

    path("marks/exams/", ExamListCreateView.as_view()),
    path("marks/subjects/", SubjectListCreateView.as_view()),
    path("marks/add/", MarkAddView.as_view()),
    path("marks/bulk-upload/", MarkBulkUploadView.as_view()),
    path("marks/", MarkListView.as_view()),
    path("marks/results/", ResultListView.as_view()),
    path("marks/results/recompute/", RecomputeResultsView.as_view()),
    path("marks/results/<int:pk>/generate-report/", ResultGenerateReportView.as_view()),
    path("marks/results/generate-all/", ResultGenerateAllReportsView.as_view()),
    path("marks/results/<int:pk>/send-report/", ResultSendReportView.as_view()),
    path("marks/results/send-all/", ResultSendAllReportsView.as_view()),

    path("notifications/", NotificationListView.as_view()),
    path("notifications/<int:pk>/resend/", NotificationResendView.as_view()),
    path("notifications/templates/", NotificationTemplateListView.as_view()),
    path("notifications/templates/<int:pk>/", NotificationTemplateUpdateView.as_view()),
    path("notifications/test/", NotificationTestView.as_view()),

    path("reports/dashboard/", DashboardReportView.as_view()),
    path("reports/attendance/", AttendanceReportView.as_view()),
    path("reports/engagement/", EngagementReportView.as_view()),
    path("reports/safety/", SafetyReportView.as_view()),
    path("reports/academic/", AcademicReportView.as_view()),
]
