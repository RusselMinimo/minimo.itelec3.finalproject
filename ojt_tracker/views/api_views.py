from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import date, timedelta, datetime
import json

from ..models import (
    UserRole, Company, OJTProgram, Student, Faculty,
    OJTPlacement, ActivityLog, Attendance, Evaluation,
    Message, Report, OJTRequest
)
from ..serializers import (
    UserRoleSerializer, CompanySerializer, OJTProgramSerializer,
    StudentSerializer, FacultySerializer, OJTPlacementSerializer,
    ActivityLogSerializer, AttendanceSerializer, EvaluationSerializer,
    MessageSerializer, ReportSerializer, DashboardStudentSerializer,
    DashboardFacultySerializer, OJTRequestSerializer
)

# This file contains all REST API ViewSets for the OJT Tracker application
# Each ViewSet provides full CRUD operations and custom actions for specific models

class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user roles"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

    @action(detail=False, methods=['get'])
    def current_user_role(self, request):
        """Get current user's role"""
        try:
            user_role = UserRole.objects.get(user=request.user)
            serializer = self.get_serializer(user_role)
            return Response(serializer.data)
        except UserRole.DoesNotExist:
            return Response({'error': 'User role not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def role_statistics(self, request):
        """Get role distribution statistics"""
        stats = UserRole.objects.values('role').annotate(count=Count('id'))
        return Response(stats)

class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing companies"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['industry', 'is_active']
    search_fields = ['name', 'contact_person', 'industry']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def active_companies(self, request):
        """Get only active companies"""
        companies = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def placements(self, request, pk=None):
        """Get all placements for a specific company"""
        company = self.get_object()
        placements = company.placements.all()
        serializer = OJTPlacementSerializer(placements, many=True)
        return Response(serializer.data)

class OJTProgramViewSet(viewsets.ModelViewSet):
    """ViewSet for managing OJT programs"""
    queryset = OJTProgram.objects.all()
    serializer_class = OJTProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'coordinator']
    search_fields = ['name', 'code']

    @action(detail=False, methods=['get'])
    def active_programs(self, request):
        """Get only active programs"""
        programs = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing students"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['program', 'year_level', 'section']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name']

    @action(detail=False, methods=['get'])
    def current_student(self, request):
        """Get current student profile"""
        try:
            student = Student.objects.get(user=request.user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

class FacultyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing faculty"""
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'position']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name']

    @action(detail=False, methods=['get'])
    def current_faculty(self, request):
        """Get current faculty profile"""
        try:
            faculty = Faculty.objects.get(user=request.user)
            serializer = self.get_serializer(faculty)
            return Response(serializer.data)
        except Faculty.DoesNotExist:
            return Response({'error': 'Faculty profile not found'}, status=status.HTTP_404_NOT_FOUND)

class OJTPlacementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing OJT placements"""
    queryset = OJTPlacement.objects.all()
    serializer_class = OJTPlacementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'company', 'supervisor', 'student__program']
    search_fields = ['student__student_id', 'company__name', 'position']

    def get_queryset(self):
        """Filter placements based on user role"""
        user = self.request.user
        try:
            user_role = UserRole.objects.get(user=user)
            if user_role.role == 'student':
                student = Student.objects.get(user=user)
                return self.queryset.filter(student=student)
            elif user_role.role == 'faculty':
                faculty = Faculty.objects.get(user=user)
                return self.queryset.filter(supervisor=faculty)
        except (UserRole.DoesNotExist, Student.DoesNotExist, Faculty.DoesNotExist):
            pass
        return self.queryset

class ActivityLogViewSet(viewsets.ModelViewSet):
    """ViewSet for managing activity logs"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['placement', 'is_approved', 'date']
    search_fields = ['activities', 'learning_outcomes']
    ordering = ['-date']

class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance records"""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['placement', 'status', 'date']
    search_fields = ['remarks']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Check in for attendance"""
        try:
            student = Student.objects.get(user=request.user)
            placement = student.placements.filter(status='active').first()
            
            if not placement:
                return Response({'error': 'No active placement found'}, status=status.HTTP_400_BAD_REQUEST)
            
            today = date.today()
            attendance, created = Attendance.objects.get_or_create(
                placement=placement,
                date=today,
                defaults={
                    'time_in': timezone.now().time(),
                    'status': 'checked_in'
                }
            )
            
            if not created and attendance.time_in:
                return Response({'error': 'Already checked in today'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(attendance)
            return Response(serializer.data)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Check out for attendance"""
        try:
            student = Student.objects.get(user=request.user)
            placement = student.placements.filter(status='active').first()
            
            if not placement:
                return Response({'error': 'No active placement found'}, status=status.HTTP_400_BAD_REQUEST)
            
            today = date.today()
            try:
                attendance = Attendance.objects.get(placement=placement, date=today)
                if not attendance.time_in:
                    return Response({'error': 'Must check in first'}, status=status.HTTP_400_BAD_REQUEST)
                
                attendance.time_out = timezone.now().time()
                attendance.status = 'checked_out'
                attendance.calculate_hours_worked()
                attendance.save()
                
                serializer = self.get_serializer(attendance)
                return Response(serializer.data)
                
            except Attendance.DoesNotExist:
                return Response({'error': 'No check-in record found for today'}, status=status.HTTP_404_NOT_FOUND)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing evaluations"""
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['placement', 'evaluator', 'evaluation_type']
    search_fields = ['strengths', 'areas_for_improvement', 'recommendations']
    ordering = ['-evaluation_period_start']

class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['message_type', 'is_read', 'is_important']
    search_fields = ['subject', 'content']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter messages for current user"""
        return self.queryset.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        )

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread messages for current user"""
        unread_messages = self.get_queryset().filter(
            recipient=request.user,
            is_read=False
        )
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reports"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'placement', 'is_sent']
    search_fields = ['placement__student__student_id']
    ordering = ['-created_at']

class OJTRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing OJT requests"""
    queryset = OJTRequest.objects.all()
    serializer_class = OJTRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'student__program']
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name', 'remarks']
    ordering_fields = ['date_submitted', 'status']
    ordering = ['-date_submitted']

    def get_queryset(self):
        """Filter requests based on user role"""
        user = self.request.user
        try:
            user_role = UserRole.objects.get(user=user)
            if user_role.role == 'student':
                student = Student.objects.get(user=user)
                return self.queryset.filter(student=student)
            elif user_role.role == 'faculty':
                # Faculty can see requests from their program students
                faculty = Faculty.objects.get(user=user)
                coordinated_programs = OJTProgram.objects.filter(coordinator=user)
                return self.queryset.filter(student__program__in=coordinated_programs)
        except (UserRole.DoesNotExist, Student.DoesNotExist, Faculty.DoesNotExist):
            pass
        return self.queryset

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's OJT requests"""
        try:
            student = Student.objects.get(user=request.user)
            requests = self.queryset.filter(student=student)
            serializer = self.get_serializer(requests, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND) 