from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user-roles', views.UserRoleViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'ojt-programs', views.OJTProgramViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'faculty', views.FacultyViewSet)
router.register(r'ojt-placements', views.OJTPlacementViewSet)
router.register(r'activity-logs', views.ActivityLogViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'evaluations', views.EvaluationViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'reports', views.ReportViewSet)

app_name = 'ojt_tracker'

urlpatterns = [
    path('api/', include(router.urls)),
    # Dashboard views
    path('', views.dashboard_view, name='dashboard'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('faculty-dashboard/', views.faculty_dashboard_view, name='faculty_dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Student views
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('student/placement/', views.student_placement_view, name='student_placement'),
    path('student/activity-log/', views.activity_log_view, name='activity_log'),
    path('student/attendance/', views.student_attendance_view, name='student_attendance'),
    
    # Faculty views
    path('faculty/students/', views.faculty_students_view, name='faculty_students'),
    path('faculty/evaluations/', views.faculty_evaluations_view, name='faculty_evaluations'),
    path('faculty/reports/', views.faculty_reports_view, name='faculty_reports'),
    path('faculty/profile/', views.faculty_profile_view, name='faculty_profile'),
    
    # Admin views
    path('admin/companies/', views.admin_companies_view, name='admin_companies'),
    path('admin/programs/', views.admin_programs_view, name='admin_programs'),
    path('admin/placements/', views.admin_placements_view, name='admin_placements'),
    
    # Common views
    path('messages/', views.messages_view, name='messages'),
    path('reports/', views.reports_view, name='reports'),
] 