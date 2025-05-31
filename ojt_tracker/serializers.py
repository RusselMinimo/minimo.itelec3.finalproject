from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserRole, Company, OJTProgram, Student, Faculty,
    OJTPlacement, ActivityLog, Attendance, Evaluation,
    Message, Report, OJTRequest
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class OJTProgramSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True)
    
    class Meta:
        model = OJTProgram
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class FacultySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Faculty
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class OJTPlacementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.user.get_full_name', read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = OJTPlacement
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_hours_completed']

class ActivityLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='placement.student.student_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.user.get_full_name', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'hours_worked']

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='placement.student.student_id', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.user.get_full_name', read_only=True)
    can_check_in = serializers.BooleanField(read_only=True)
    can_check_out = serializers.BooleanField(read_only=True)
    is_checked_in = serializers.BooleanField(read_only=True)
    company_name = serializers.CharField(source='placement.company.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'hours_present', 'is_late']

class EvaluationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='placement.student.student_id', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.user.get_full_name', read_only=True)
    average_score = serializers.ReadOnlyField()
    
    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    placement_info = serializers.CharField(source='placement.__str__', read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class ReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='placement.student.student_id', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Specialized serializers for dashboard views
class DashboardStudentSerializer(serializers.ModelSerializer):
    current_placement = OJTPlacementSerializer(source='placements.first', read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    total_hours_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'user', 'program', 'year_level', 'section', 
                 'current_placement', 'completion_percentage', 'total_hours_completed']

class DashboardFacultySerializer(serializers.ModelSerializer):
    """Serializer for faculty dashboard data"""
    student_count = serializers.IntegerField(read_only=True)
    pending_evaluations = serializers.IntegerField(read_only=True)
    pending_activities = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Faculty
        fields = ['id', 'employee_id', 'user', 'department', 'position',
                 'student_count', 'pending_evaluations', 'pending_activities']

class OJTRequestSerializer(serializers.ModelSerializer):
    """Serializer for OJT requests"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    student_program = serializers.CharField(source='student.program.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OJTRequest
        fields = ['id', 'student', 'student_name', 'student_id', 'student_program',
                 'date_submitted', 'status', 'status_display', 'remarks', 
                 'admin_response', 'reviewed_by', 'reviewed_by_name', 
                 'reviewed_at', 'updated_at', 'can_be_approved', 'can_be_rejected']
        read_only_fields = ['id', 'date_submitted', 'reviewed_by', 'reviewed_at', 'updated_at'] 