from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    UserRole, Student, Faculty, Company, OJTProgram, 
    OJTPlacement, Attendance, Report, Evaluation, Message
)

# Register UserRole model
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

# Register Student model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_user_name', 'get_user_email', 'program', 'year_level')
    list_filter = ('program', 'year_level')
    search_fields = ('student_id', 'user__username', 'user__email', 'program__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    get_user_name.short_description = 'Name'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

# Register Faculty model
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_user_name', 'get_user_email', 'department', 'position')
    list_filter = ('department', 'position')
    search_fields = ('employee_id', 'user__username', 'user__email', 'department')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    get_user_name.short_description = 'Name'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

# Register Company model
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'industry', 'is_active')
    list_filter = ('industry', 'is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

# Register OJT Program model
@admin.register(OJTProgram)
class OJTProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description_short', 'duration_weeks', 'required_hours', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def description_short(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

# Register OJT Placement model
@admin.register(OJTPlacement)
class OJTPlacementAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'company', 'position', 'supervisor', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date', 'company')
    search_fields = ('student__user__username', 'company__name', 'position')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    def get_student_name(self, obj):
        return obj.student.user.username
    get_student_name.short_description = 'Student'

# Register Attendance model
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'date', 'time_in', 'time_out', 'status', 'hours_present')
    list_filter = ('status', 'date')
    search_fields = ('placement__student__user__username', 'placement__student__student_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    def get_student_name(self, obj):
        return obj.placement.student.user.username
    get_student_name.short_description = 'Student'

# Register Report model
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'report_type', 'report_period_start', 'report_period_end', 'is_sent')
    list_filter = ('report_type', 'is_sent', 'report_period_start')
    search_fields = ('placement__student__user__username', 'report_type')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'report_period_start'
    
    def get_student_name(self, obj):
        return obj.placement.student.user.username
    get_student_name.short_description = 'Student'

# Register Evaluation model
@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'evaluator', 'evaluation_type', 'overall_performance', 'evaluation_period_start')
    list_filter = ('evaluation_type', 'overall_performance', 'evaluation_period_start')
    search_fields = ('placement__student__user__username', 'evaluator__user__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'evaluation_period_start'
    
    def get_student_name(self, obj):
        return obj.placement.student.user.username
    get_student_name.short_description = 'Student'

# Register Message model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'content')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

# Customize admin site header and title
admin.site.site_header = "OJT Tracker Administration"
admin.site.site_title = "OJT Tracker Admin"
admin.site.index_title = "Welcome to OJT Tracker Administration" 