from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta
import json

from .models import (
    UserRole, Company, OJTProgram, Student, Faculty,
    OJTPlacement, ActivityLog, Attendance, Evaluation,
    Message, Report
)
from .serializers import (
    UserRoleSerializer, CompanySerializer, OJTProgramSerializer,
    StudentSerializer, FacultySerializer, OJTPlacementSerializer,
    ActivityLogSerializer, AttendanceSerializer, EvaluationSerializer,
    MessageSerializer, ReportSerializer, DashboardStudentSerializer,
    DashboardFacultySerializer
)
from .forms import (
    StudentProfileForm, FacultyProfileForm, CompanyForm,
    OJTProgramForm, OJTPlacementForm, ActivityLogForm,
    AttendanceForm, EvaluationForm, MessageForm
)

# ============================================================================
# TEMPLATE VIEWS (for frontend rendering)
# ============================================================================

@login_required
def dashboard_view(request):
    """Main dashboard that redirects based on user role"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role == 'student':
            return redirect('ojt_tracker:student_dashboard')
        elif user_role.role == 'faculty':
            return redirect('ojt_tracker:faculty_dashboard')
        else:
            return redirect('ojt_tracker:admin_dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found. Please contact administrator.')
        return redirect('authentication:login')

@login_required
def student_dashboard_view(request):
    """Student dashboard with overview of their OJT progress"""
    try:
        student = Student.objects.get(user=request.user)
        
        # Check if student profile is complete
        profile_incomplete = not all([
            student.contact_number,
            student.emergency_contact,
            student.emergency_phone,
            student.address
        ])
        
        if profile_incomplete:
            messages.warning(request, 'Please complete your student profile to access all features.')
        
        current_placement = student.placements.filter(status='active').first()
        
        context = {
            'student': student,
            'current_placement': current_placement,
            'profile_incomplete': profile_incomplete,
        }
        
        if current_placement:
            recent_activities = current_placement.activity_logs.order_by('-date')[:5]
            total_attendance = current_placement.attendance_records.count()
            present_days = current_placement.attendance_records.filter(status='present').count()
            attendance_rate = (present_days / total_attendance * 100) if total_attendance > 0 else 0
            recent_evaluations = current_placement.evaluations.order_by('-evaluation_period_start')[:3]
            unread_messages = request.user.received_messages.filter(is_read=False)
            
            context.update({
                'recent_activities': recent_activities,
                'attendance_rate': attendance_rate,
                'total_hours_completed': current_placement.total_hours_completed,
                'total_hours_required': current_placement.total_hours_required,
                'completion_percentage': current_placement.completion_percentage,
                'recent_evaluations': recent_evaluations,
                'unread_messages': unread_messages,
            })
        
        return render(request, 'ojt_tracker/student_dashboard.html', context)
        
    except Student.DoesNotExist:
        # If student profile doesn't exist, create a basic one and redirect to profile completion
        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role == 'student':
                # Create a basic student profile
                default_program = OJTProgram.objects.filter(is_active=True).first()
                if not default_program:
                    default_program = OJTProgram.objects.create(
                        name="General OJT Program",
                        code="GEN001",
                        description="Default OJT program for new students",
                        duration_weeks=12,
                        required_hours=300,
                        is_active=True
                    )
                
                student = Student.objects.create(
                    user=request.user,
                    student_id=f"STU{request.user.id:06d}",
                    program=default_program,
                    year_level="1st Year",
                    section="A",
                    contact_number="",
                    emergency_contact="",
                    emergency_phone="",
                    address=""
                )
                messages.info(request, 'Student profile created. Please complete your profile information.')
                return redirect('ojt_tracker:student_profile')
        except:
            pass
        
        messages.error(request, 'Student profile not found. Please contact administrator.')
        return redirect('authentication:login')

@login_required
def faculty_dashboard_view(request):
    """Faculty dashboard with overview of supervised students"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        
        # Check if faculty profile is complete
        profile_incomplete = not all([
            faculty.contact_number,
            faculty.office_location
        ])
        
        if profile_incomplete:
            messages.warning(request, 'Please complete your faculty profile to access all features.')
        
        supervised_placements = faculty.supervised_placements.filter(status='active')
        pending_evaluations = supervised_placements.count()
        pending_activities = ActivityLog.objects.filter(
            placement__supervisor=faculty,
            is_approved=False
        ).order_by('-date')[:10]
        unread_messages = request.user.received_messages.filter(is_read=False)
        total_students = supervised_placements.count()
        avg_completion = supervised_placements.aggregate(
            avg_completion=Avg('total_hours_completed')
        )['avg_completion'] or 0
        
        context = {
            'faculty': faculty,
            'supervised_placements': supervised_placements,
            'pending_evaluations': pending_evaluations,
            'pending_activities': pending_activities,
            'unread_messages': unread_messages,
            'total_students': total_students,
            'avg_completion': avg_completion,
            'profile_incomplete': profile_incomplete,
        }
        
        return render(request, 'ojt_tracker/faculty_dashboard.html', context)
        
    except Faculty.DoesNotExist:
        # If faculty profile doesn't exist, create a basic one and redirect to profile completion
        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role == 'faculty':
                # Create a basic faculty profile
                faculty = Faculty.objects.create(
                    user=request.user,
                    employee_id=f"FAC{request.user.id:06d}",
                    department="General",
                    position="Faculty",
                    contact_number="",
                    office_location="",
                    specialization=""
                )
                messages.info(request, 'Faculty profile created. Please complete your profile information.')
                # For now, redirect to dashboard with the basic profile
                return redirect('ojt_tracker:faculty_dashboard')
        except:
            pass
        
        messages.error(request, 'Faculty profile not found. Please contact administrator.')
        return redirect('authentication:login')

@login_required
def admin_dashboard_view(request):
    """Admin dashboard with system overview and statistics"""
    # Get overall statistics
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_companies = Company.objects.filter(is_active=True).count()
    total_programs = OJTProgram.objects.filter(is_active=True).count()
    
    # Get placement statistics
    active_placements = OJTPlacement.objects.filter(status='active').count()
    pending_placements = OJTPlacement.objects.filter(status='pending').count()
    completed_placements = OJTPlacement.objects.filter(status='completed').count()
    
    # Get recent activities
    recent_students = Student.objects.order_by('-created_at')[:5]
    recent_placements = OJTPlacement.objects.order_by('-created_at')[:5]
    pending_approvals = ActivityLog.objects.filter(is_approved=False).count()
    
    # Get unread messages
    unread_messages = request.user.received_messages.filter(is_read=False)
    
    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_companies': total_companies,
        'total_programs': total_programs,
        'active_placements': active_placements,
        'pending_placements': pending_placements,
        'completed_placements': completed_placements,
        'recent_students': recent_students,
        'recent_placements': recent_placements,
        'pending_approvals': pending_approvals,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'ojt_tracker/admin_dashboard.html', context)

@login_required
def student_profile_view(request):
    """Student profile management"""
    try:
        student = Student.objects.get(user=request.user)
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('ojt_tracker:student_profile')
        else:
            form = StudentProfileForm(instance=student)
    except Student.DoesNotExist:
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES)
            if form.is_valid():
                student = form.save(commit=False)
                student.user = request.user
                student.save()
                messages.success(request, 'Profile created successfully!')
                return redirect('ojt_tracker:student_profile')
        else:
            form = StudentProfileForm()
    
    return render(request, 'ojt_tracker/student_profile.html', {'form': form})

@login_required
def faculty_profile_view(request):
    """Faculty profile management"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        if request.method == 'POST':
            form = FacultyProfileForm(request.POST, request.FILES, instance=faculty)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('ojt_tracker:faculty_profile')
        else:
            form = FacultyProfileForm(instance=faculty)
        
        # Add additional context for template
        context = {
            'form': form,
            'total_placements': faculty.supervised_placements.count(),
            'active_placements': faculty.supervised_placements.filter(status='active').count(),
            'conducted_evaluations': faculty.conducted_evaluations.count(),
        }
        
    except Faculty.DoesNotExist:
        if request.method == 'POST':
            form = FacultyProfileForm(request.POST, request.FILES)
            if form.is_valid():
                faculty = form.save(commit=False)
                faculty.user = request.user
                faculty.save()
                messages.success(request, 'Profile created successfully!')
                return redirect('ojt_tracker:faculty_profile')
        else:
            form = FacultyProfileForm()
        
        context = {
            'form': form,
            'total_placements': 0,
            'active_placements': 0,
            'conducted_evaluations': 0,
        }
    
    return render(request, 'ojt_tracker/faculty_profile.html', context)

@login_required
def student_placement_view(request):
    """Student placement view"""
    try:
        student = Student.objects.get(user=request.user)
        placements = student.placements.all()
        current_placement = student.placements.filter(status='active').first()
        
        context = {
            'student': student,
            'placements': placements,
            'current_placement': current_placement,
        }
        
        return render(request, 'ojt_tracker/student_placement.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please complete your profile first.')
        return redirect('ojt_tracker:student_dashboard')

@login_required
def activity_log_view(request):
    """Activity log management for students"""
    try:
        student = Student.objects.get(user=request.user)
        current_placement = student.placements.filter(status='active').first()
        
        if not current_placement:
            messages.error(request, 'No active placement found.')
            return redirect('ojt_tracker:student_dashboard')
        
        if request.method == 'POST':
            form = ActivityLogForm(request.POST)
            if form.is_valid():
                activity_log = form.save(commit=False)
                activity_log.placement = current_placement
                activity_log.save()
                messages.success(request, 'Activity log saved successfully!')
                return redirect('ojt_tracker:activity_log')
        else:
            form = ActivityLogForm()
        
        activity_logs = current_placement.activity_logs.order_by('-date')
        
        context = {
            'form': form,
            'activity_logs': activity_logs,
            'current_placement': current_placement,
        }
        
        return render(request, 'ojt_tracker/activity_log.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please complete your profile first.')
        return redirect('ojt_tracker:student_dashboard')

@login_required
def student_attendance_view(request):
    """Attendance view for students"""
    try:
        student = Student.objects.get(user=request.user)
        current_placement = student.placements.filter(status='active').first()
        
        if not current_placement:
            messages.error(request, 'No active placement found.')
            return redirect('ojt_tracker:student_dashboard')
        
        attendance_records = current_placement.attendance_records.order_by('-date')
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        late_days = attendance_records.filter(status='late').count()
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        context = {
            'attendance_records': attendance_records,
            'current_placement': current_placement,
            'stats': {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'attendance_rate': attendance_rate,
            }
        }
        
        return render(request, 'ojt_tracker/student_attendance.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please complete your profile first.')
        return redirect('ojt_tracker:student_dashboard')

@login_required
def faculty_students_view(request):
    """Faculty view of supervised students"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        supervised_placements = faculty.supervised_placements.all()
        
        context = {
            'faculty': faculty,
            'supervised_placements': supervised_placements,
        }
        
        return render(request, 'ojt_tracker/faculty_students.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:faculty_dashboard')

@login_required
def faculty_evaluations_view(request):
    """Faculty evaluation management"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        
        if request.method == 'POST':
            form = EvaluationForm(request.POST)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.evaluator = faculty
                evaluation.save()
                messages.success(request, 'Evaluation saved successfully!')
                return redirect('ojt_tracker:faculty_evaluations')
        else:
            form = EvaluationForm()
            form.fields['placement'].queryset = faculty.supervised_placements.filter(status='active')
        
        evaluations = faculty.conducted_evaluations.order_by('-evaluation_period_start')
        
        context = {
            'form': form,
            'evaluations': evaluations,
            'faculty': faculty,
        }
        
        return render(request, 'ojt_tracker/faculty_evaluations.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:faculty_dashboard')

@login_required
def faculty_reports_view(request):
    """Faculty reports view"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        reports = Report.objects.filter(
            Q(placement__supervisor=faculty) | Q(generated_by=request.user)
        ).order_by('-created_at')
        
        context = {
            'faculty': faculty,
            'reports': reports,
        }
        
        return render(request, 'ojt_tracker/faculty_reports.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:faculty_dashboard')

@login_required
def messages_view(request):
    """Messages interface"""
    if request.method == 'POST':
        # Handle mark as read action
        if 'mark_as_read' in request.POST:
            message_id = request.POST.get('mark_as_read')
            try:
                message = Message.objects.get(id=message_id, recipient=request.user)
                message.is_read = True
                message.save()
                messages.success(request, 'Message marked as read!')
            except Message.DoesNotExist:
                messages.error(request, 'Message not found.')
            return redirect('ojt_tracker:messages')
        
        # Handle reply action
        elif 'parent_message' in request.POST:
            parent_id = request.POST.get('parent_message')
            recipient_id = request.POST.get('recipient')
            subject = request.POST.get('subject')
            content = request.POST.get('content')
            message_type = request.POST.get('message_type')
            
            try:
                # Debug logging to see what we're getting
                print(f"Debug - recipient_id received: '{recipient_id}' (type: {type(recipient_id)})")
                
                # Validate that recipient_id is actually a number
                if not recipient_id or not recipient_id.isdigit():
                    # If recipient_id is not a number, it might be a name - try to find user by name
                    if recipient_id:
                        # Try to find user by full name or username
                        try:
                            # First try by username
                            recipient = User.objects.get(username=recipient_id)
                        except User.DoesNotExist:
                            # Then try by full name (first + last name combination)
                            name_parts = recipient_id.split(' ', 1)
                            if len(name_parts) == 2:
                                first_name, last_name = name_parts
                                recipient = User.objects.get(first_name=first_name, last_name=last_name)
                            else:
                                # Try single name as first name
                                recipient = User.objects.get(first_name=recipient_id)
                    else:
                        raise ValueError("No recipient specified")
                else:
                    # recipient_id is a valid number, proceed normally
                    recipient = User.objects.get(id=int(recipient_id))
                
                parent_message = Message.objects.get(id=parent_id)
                
                # Create reply message
                reply = Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    subject=subject,
                    content=content,
                    message_type=message_type,
                    parent_message=parent_message,
                    placement=parent_message.placement
                )
                messages.success(request, 'Reply sent successfully!')
            except (Message.DoesNotExist, User.DoesNotExist, ValueError) as e:
                print(f"Debug - Error occurred: {e}")
                messages.error(request, f'Unable to send reply: {str(e)}')
            except Exception as e:
                print(f"Debug - Unexpected error: {e}")
                messages.error(request, 'An unexpected error occurred while sending reply.')
            return redirect('ojt_tracker:messages')
        
        # Handle new message form
        else:
            form = MessageForm(request.POST, request.FILES)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                messages.success(request, 'Message sent successfully!')
                return redirect('ojt_tracker:messages')
    else:
        form = MessageForm()
    
    inbox_messages = request.user.received_messages.order_by('-created_at')
    sent_messages = request.user.sent_messages.order_by('-created_at')
    unread_count = inbox_messages.filter(is_read=False).count()
    
    context = {
        'form': form,
        'inbox_messages': inbox_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
    }
    
    return render(request, 'ojt_tracker/messages.html', context)

@login_required
def reports_view(request):
    """Reports interface"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        
        if user_role.role == 'student':
            try:
                student = Student.objects.get(user=request.user)
                reports = Report.objects.filter(placement__student=student)
            except Student.DoesNotExist:
                # Create basic student profile if it doesn't exist
                default_program = OJTProgram.objects.filter(is_active=True).first()
                if not default_program:
                    default_program = OJTProgram.objects.create(
                        name="General OJT Program",
                        code="GEN001",
                        description="Default OJT program for new students",
                        duration_weeks=12,
                        required_hours=300,
                        is_active=True
                    )
                
                student = Student.objects.create(
                    user=request.user,
                    student_id=f"STU{request.user.id:06d}",
                    program=default_program,
                    year_level="1st Year",
                    section="A",
                    contact_number="",
                    emergency_contact="",
                    emergency_phone="",
                    address=""
                )
                reports = Report.objects.filter(placement__student=student)
                
        elif user_role.role == 'faculty':
            try:
                faculty = Faculty.objects.get(user=request.user)
                reports = Report.objects.filter(
                    Q(placement__supervisor=faculty) | Q(generated_by=request.user)
                )
            except Faculty.DoesNotExist:
                # Create basic faculty profile if it doesn't exist
                faculty = Faculty.objects.create(
                    user=request.user,
                    employee_id=f"FAC{request.user.id:06d}",
                    department="General",
                    position="Faculty",
                    contact_number="",
                    office_location="",
                    specialization=""
                )
                reports = Report.objects.filter(
                    Q(placement__supervisor=faculty) | Q(generated_by=request.user)
                )
        else:
            reports = Report.objects.all()
        
        reports = reports.order_by('-created_at')
        
        context = {
            'reports': reports,
            'user_role': user_role,
        }
        
        return render(request, 'ojt_tracker/reports.html', context)
        
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found. Please contact administrator.')
        return redirect('ojt_tracker:dashboard')

# Admin views
@login_required
def admin_companies_view(request):
    """Admin companies management"""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company added successfully!')
            return redirect('ojt_tracker:admin_companies')
    else:
        form = CompanyForm()
    
    companies = Company.objects.all().order_by('name')
    
    context = {
        'form': form,
        'companies': companies,
    }
    
    return render(request, 'ojt_tracker/admin_companies.html', context)

@login_required
def admin_programs_view(request):
    """Admin programs management"""
    if request.method == 'POST':
        form = OJTProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program added successfully!')
            return redirect('ojt_tracker:admin_programs')
    else:
        form = OJTProgramForm()
    
    programs = OJTProgram.objects.all().order_by('name')
    
    context = {
        'form': form,
        'programs': programs,
    }
    
    return render(request, 'ojt_tracker/admin_programs.html', context)

@login_required
def admin_placements_view(request):
    """Admin placements management"""
    if request.method == 'POST':
        form = OJTPlacementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Placement added successfully!')
            return redirect('ojt_tracker:admin_placements')
    else:
        form = OJTPlacementForm()
    
    placements = OJTPlacement.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'placements': placements,
    }
    
    return render(request, 'ojt_tracker/admin_placements.html', context)

# ============================================================================
# API VIEWSETS (for REST API)
# ============================================================================

class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user roles
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/user-roles/
    """
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
    """
    ViewSet for managing companies
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/companies/
    """
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

    @action(detail=False, methods=['get'])
    def industry_statistics(self, request):
        """Get company statistics by industry"""
        stats = Company.objects.values('industry').annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        )
        return Response(stats)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a company"""
        company = self.get_object()
        company.is_active = False
        company.save()
        return Response({'message': 'Company deactivated successfully'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a company"""
        company = self.get_object()
        company.is_active = True
        company.save()
        return Response({'message': 'Company activated successfully'})

class OJTProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing OJT programs
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/ojt-programs/
    """
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

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students in a specific program"""
        program = self.get_object()
        students = program.students.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get program statistics"""
        program = self.get_object()
        stats = {
            'total_students': program.students.count(),
            'active_placements': program.students.filter(
                placements__status='active'
            ).count(),
            'completion_rate': 0,
        }
        
        total_placements = OJTPlacement.objects.filter(
            student__program=program
        ).count()
        completed_placements = OJTPlacement.objects.filter(
            student__program=program,
            status='completed'
        ).count()
        
        if total_placements > 0:
            stats['completion_rate'] = (completed_placements / total_placements) * 100
            
        return Response(stats)

    @action(detail=False, methods=['get'])
    def program_overview(self, request):
        """Get overview of all programs"""
        programs = self.queryset.annotate(
            student_count=Count('students'),
            active_placement_count=Count(
                'students__placements', 
                filter=Q(students__placements__status='active')
            )
        )
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing students
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/students/
    """
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

    @action(detail=True, methods=['get'])
    def placements(self, request, pk=None):
        """Get all placements for a student"""
        student = self.get_object()
        placements = student.placements.all()
        serializer = OJTPlacementSerializer(placements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def current_placement(self, request, pk=None):
        """Get current active placement for a student"""
        student = self.get_object()
        placement = student.placements.filter(status='active').first()
        if placement:
            serializer = OJTPlacementSerializer(placement)
            return Response(serializer.data)
        return Response({'message': 'No active placement found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get dashboard data for a student"""
        student = self.get_object()
        serializer = DashboardStudentSerializer(student)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_program(self, request):
        """Get students grouped by program"""
        program_id = request.query_params.get('program_id')
        if program_id:
            students = self.queryset.filter(program_id=program_id)
        else:
            students = self.queryset.all()
        
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

class FacultyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing faculty
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/faculty/
    """
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

    @action(detail=True, methods=['get'])
    def supervised_placements(self, request, pk=None):
        """Get all placements supervised by this faculty"""
        faculty = self.get_object()
        placements = faculty.supervised_placements.all()
        serializer = OJTPlacementSerializer(placements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get dashboard data for a faculty member"""
        faculty = self.get_object()
        serializer = DashboardFacultySerializer(faculty)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get faculty grouped by department"""
        department = request.query_params.get('department')
        if department:
            faculty = self.queryset.filter(department=department)
        else:
            faculty = self.queryset.all()
        
        serializer = self.get_serializer(faculty, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def coordinators(self, request):
        """Get faculty who are program coordinators"""
        coordinators = self.queryset.filter(coordinated_programs__isnull=False).distinct()
        serializer = self.get_serializer(coordinators, many=True)
        return Response(serializer.data)

class OJTPlacementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing OJT placements
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/ojt-placements/
    """
    queryset = OJTPlacement.objects.all()
    serializer_class = OJTPlacementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'company', 'supervisor', 'student__program']
    search_fields = ['student__student_id', 'company__name', 'position']

    def get_queryset(self):
        """Filter placements based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        if hasattr(user, 'faculty_profile'):
            return queryset.filter(supervisor=user.faculty_profile)
        
        return queryset

    @action(detail=False, methods=['get'])
    def active_placements(self, request):
        """Get all active placements"""
        placements = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(placements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activity_logs(self, request, pk=None):
        """Get activity logs for a placement"""
        placement = self.get_object()
        logs = placement.activity_logs.all()
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_records(self, request, pk=None):
        """Get attendance records for a placement"""
        placement = self.get_object()
        records = placement.attendance_records.all()
        serializer = AttendanceSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        """Get evaluations for a placement"""
        placement = self.get_object()
        evaluations = placement.evaluations.all()
        serializer = EvaluationSerializer(evaluations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a placement"""
        placement = self.get_object()
        placement.status = 'approved'
        placement.save()
        return Response({'message': 'Placement approved successfully'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a placement (set to active)"""
        placement = self.get_object()
        placement.status = 'active'
        placement.save()
        return Response({'message': 'Placement started successfully'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a placement"""
        placement = self.get_object()
        placement.status = 'completed'
        placement.save()
        return Response({'message': 'Placement completed successfully'})

class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing activity logs
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/activity-logs/
    """
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['placement', 'is_approved', 'date']
    search_fields = ['activities', 'learning_outcomes']
    ordering = ['-date']

    def get_queryset(self):
        """Filter activity logs based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if hasattr(user, 'student_profile'):
            return queryset.filter(placement__student=user.student_profile)
        
        if hasattr(user, 'faculty_profile'):
            return queryset.filter(placement__supervisor=user.faculty_profile)
        
        return queryset

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get activity logs pending approval"""
        logs = self.get_queryset().filter(is_approved=False)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an activity log"""
        log = self.get_object()
        if hasattr(request.user, 'faculty_profile'):
            log.is_approved = True
            log.approved_by = request.user.faculty_profile
            log.approved_at = timezone.now()
            log.save()
            
            # Update total hours in placement
            placement = log.placement
            placement.total_hours_completed = placement.activity_logs.filter(
                is_approved=True
            ).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
            placement.save()
            
            return Response({'message': 'Activity log approved successfully'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'])
    def weekly_summary(self, request):
        """Get weekly summary of activity logs"""
        placement_id = request.query_params.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        logs = self.get_queryset().filter(
            placement_id=placement_id,
            date__range=[start_date, end_date]
        )
        
        summary = {
            'total_hours': logs.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0,
            'total_days': logs.count(),
            'approved_logs': logs.filter(is_approved=True).count(),
            'logs': ActivityLogSerializer(logs, many=True).data
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly summary of activity logs"""
        placement_id = request.query_params.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        end_date = date.today()
        start_date = end_date.replace(day=1)
        
        logs = self.get_queryset().filter(
            placement_id=placement_id,
            date__range=[start_date, end_date]
        )
        
        summary = {
            'total_hours': logs.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0,
            'total_days': logs.count(),
            'approved_logs': logs.filter(is_approved=True).count(),
            'logs': ActivityLogSerializer(logs, many=True).data
        }
        
        return Response(summary)

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance records
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/attendance/
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['placement', 'status', 'date']
    search_fields = ['remarks']
    ordering = ['-date']

    def get_queryset(self):
        """Filter attendance based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if hasattr(user, 'student_profile'):
            return queryset.filter(placement__student=user.student_profile)
        
        if hasattr(user, 'faculty_profile'):
            return queryset.filter(placement__supervisor=user.faculty_profile)
        
        return queryset

    @action(detail=False, methods=['get'])
    def today_attendance(self, request):
        """Get today's attendance"""
        today = date.today()
        attendance = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def attendance_summary(self, request):
        """Get attendance summary for a placement"""
        placement_id = request.query_params.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        records = self.get_queryset().filter(placement_id=placement_id)
        
        summary = {
            'total_days': records.count(),
            'present_days': records.filter(status='present').count(),
            'absent_days': records.filter(status='absent').count(),
            'late_days': records.filter(status='late').count(),
            'total_hours': records.aggregate(Sum('hours_present'))['hours_present__sum'] or 0,
        }
        
        if summary['total_days'] > 0:
            summary['attendance_rate'] = (summary['present_days'] / summary['total_days']) * 100
        else:
            summary['attendance_rate'] = 0
        
        return Response(summary)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify attendance record"""
        attendance = self.get_object()
        if hasattr(request.user, 'faculty_profile'):
            attendance.verified_by = request.user.faculty_profile
            attendance.save()
            return Response({'message': 'Attendance verified successfully'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'])
    def weekly_report(self, request):
        """Get weekly attendance report"""
        placement_id = request.query_params.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        records = self.get_queryset().filter(
            placement_id=placement_id,
            date__range=[start_date, end_date]
        )
        
        report = {
            'period': f"{start_date} to {end_date}",
            'records': AttendanceSerializer(records, many=True).data,
            'summary': {
                'total_days': records.count(),
                'present_days': records.filter(status='present').count(),
                'absent_days': records.filter(status='absent').count(),
                'late_days': records.filter(status='late').count(),
            }
        }
        
        return Response(report)

class EvaluationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing evaluations
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/evaluations/
    """
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['placement', 'evaluator', 'evaluation_type']
    search_fields = ['strengths', 'areas_for_improvement', 'recommendations']
    ordering = ['-evaluation_period_start']

    def get_queryset(self):
        """Filter evaluations based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if hasattr(user, 'student_profile'):
            return queryset.filter(placement__student=user.student_profile)
        
        if hasattr(user, 'faculty_profile'):
            return queryset.filter(evaluator=user.faculty_profile)
        
        return queryset

    @action(detail=False, methods=['get'])
    def student_evaluations(self, request):
        """Get evaluations for a specific student"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        evaluations = self.get_queryset().filter(placement__student_id=student_id)
        serializer = self.get_serializer(evaluations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def performance_trends(self, request):
        """Get performance trends for a placement"""
        placement_id = request.query_params.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        evaluations = self.get_queryset().filter(placement_id=placement_id).order_by('evaluation_period_start')
        
        trends = []
        for evaluation in evaluations:
            trends.append({
                'date': evaluation.evaluation_period_start,
                'type': evaluation.evaluation_type,
                'average_score': evaluation.average_score,
                'technical_skills': evaluation.technical_skills,
                'communication_skills': evaluation.communication_skills,
                'teamwork': evaluation.teamwork,
                'problem_solving': evaluation.problem_solving,
                'initiative': evaluation.initiative,
                'punctuality': evaluation.punctuality,
                'attendance': evaluation.attendance,
                'overall_performance': evaluation.overall_performance,
            })
        
        return Response(trends)

    @action(detail=False, methods=['get'])
    def evaluation_statistics(self, request):
        """Get evaluation statistics"""
        evaluations = self.get_queryset()
        
        stats = {
            'total_evaluations': evaluations.count(),
            'average_scores': {
                'technical_skills': evaluations.aggregate(Avg('technical_skills'))['technical_skills__avg'] or 0,
                'communication_skills': evaluations.aggregate(Avg('communication_skills'))['communication_skills__avg'] or 0,
                'teamwork': evaluations.aggregate(Avg('teamwork'))['teamwork__avg'] or 0,
                'problem_solving': evaluations.aggregate(Avg('problem_solving'))['problem_solving__avg'] or 0,
                'initiative': evaluations.aggregate(Avg('initiative'))['initiative__avg'] or 0,
                'punctuality': evaluations.aggregate(Avg('punctuality'))['punctuality__avg'] or 0,
                'attendance': evaluations.aggregate(Avg('attendance'))['attendance__avg'] or 0,
                'overall_performance': evaluations.aggregate(Avg('overall_performance'))['overall_performance__avg'] or 0,
            },
            'by_type': evaluations.values('evaluation_type').annotate(
                count=Count('id'),
                avg_score=Avg('overall_performance')
            )
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def due_evaluations(self, request):
        """Get evaluations that are due"""
        # This would typically check for placements that need evaluation based on time periods
        active_placements = OJTPlacement.objects.filter(status='active')
        due_evaluations = []
        
        for placement in active_placements:
            # Check if weekly evaluation is due (every Monday)
            today = date.today()
            days_since_monday = today.weekday()
            last_monday = today - timedelta(days=days_since_monday)
            
            # Check if evaluation exists for this week
            existing_weekly = self.get_queryset().filter(
                placement=placement,
                evaluation_type='weekly',
                evaluation_period_start=last_monday
            ).exists()
            
            if not existing_weekly:
                due_evaluations.append({
                    'placement': OJTPlacementSerializer(placement).data,
                    'evaluation_type': 'weekly',
                    'due_date': last_monday,
                })
        
        return Response(due_evaluations)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/messages/
    """
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
    def inbox(self, request):
        """Get user's inbox messages"""
        messages = self.queryset.filter(recipient=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get user's sent messages"""
        messages = self.queryset.filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread messages"""
        messages = self.queryset.filter(recipient=request.user, is_read=False)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark message as read"""
        message = self.get_object()
        if message.recipient == request.user:
            message.is_read = True
            message.save()
            return Response({'message': 'Message marked as read'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to a message"""
        parent_message = self.get_object()
        data = request.data.copy()
        data['sender'] = request.user.id
        data['recipient'] = parent_message.sender.id
        data['parent_message'] = parent_message.id
        data['subject'] = f"Re: {parent_message.subject}"
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation thread between two users"""
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        messages = self.queryset.filter(
            Q(sender=request.user, recipient_id=other_user_id) |
            Q(sender_id=other_user_id, recipient=request.user)
        ).order_by('created_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reports
    Endpoints: GET, POST, PUT, PATCH, DELETE /api/reports/
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'placement', 'is_sent']
    search_fields = ['placement__student__student_id']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter reports based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if hasattr(user, 'student_profile'):
            return queryset.filter(placement__student=user.student_profile)
        
        if hasattr(user, 'faculty_profile'):
            return queryset.filter(
                Q(placement__supervisor=user.faculty_profile) |
                Q(generated_by=user)
            )
        
        return queryset

    @action(detail=False, methods=['post'])
    def generate_weekly_report(self, request):
        """Generate weekly report for a placement"""
        placement_id = request.data.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            placement = OJTPlacement.objects.get(id=placement_id)
        except OJTPlacement.DoesNotExist:
            return Response({'error': 'Placement not found'}, status=status.HTTP_404_NOT_FOUND)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # Gather report data
        activity_logs = ActivityLog.objects.filter(
            placement=placement,
            date__range=[start_date, end_date]
        )
        
        attendance_records = Attendance.objects.filter(
            placement=placement,
            date__range=[start_date, end_date]
        )
        
        report_data = {
            'placement_info': OJTPlacementSerializer(placement).data,
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'activity_summary': {
                'total_hours': activity_logs.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0,
                'total_days': activity_logs.count(),
                'approved_logs': activity_logs.filter(is_approved=True).count(),
            },
            'attendance_summary': {
                'total_days': attendance_records.count(),
                'present_days': attendance_records.filter(status='present').count(),
                'absent_days': attendance_records.filter(status='absent').count(),
                'late_days': attendance_records.filter(status='late').count(),
            },
            'activities': ActivityLogSerializer(activity_logs, many=True).data,
            'attendance': AttendanceSerializer(attendance_records, many=True).data,
        }
        
        # Create report record
        report = Report.objects.create(
            report_type='weekly',
            placement=placement,
            generated_by=request.user,
            report_period_start=start_date,
            report_period_end=end_date,
            report_data=report_data
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def generate_monthly_report(self, request):
        """Generate monthly report for a placement"""
        placement_id = request.data.get('placement_id')
        if not placement_id:
            return Response({'error': 'placement_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            placement = OJTPlacement.objects.get(id=placement_id)
        except OJTPlacement.DoesNotExist:
            return Response({'error': 'Placement not found'}, status=status.HTTP_404_NOT_FOUND)
        
        end_date = date.today()
        start_date = end_date.replace(day=1)
        
        # Gather comprehensive monthly data
        activity_logs = ActivityLog.objects.filter(
            placement=placement,
            date__range=[start_date, end_date]
        )
        
        attendance_records = Attendance.objects.filter(
            placement=placement,
            date__range=[start_date, end_date]
        )
        
        evaluations = Evaluation.objects.filter(
            placement=placement,
            evaluation_period_start__range=[start_date, end_date]
        )
        
        report_data = {
            'placement_info': OJTPlacementSerializer(placement).data,
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'activity_summary': {
                'total_hours': activity_logs.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0,
                'total_days': activity_logs.count(),
                'approved_logs': activity_logs.filter(is_approved=True).count(),
                'average_daily_hours': activity_logs.aggregate(Avg('hours_worked'))['hours_worked__avg'] or 0,
            },
            'attendance_summary': {
                'total_days': attendance_records.count(),
                'present_days': attendance_records.filter(status='present').count(),
                'absent_days': attendance_records.filter(status='absent').count(),
                'late_days': attendance_records.filter(status='late').count(),
                'attendance_rate': 0,
            },
            'evaluation_summary': {
                'total_evaluations': evaluations.count(),
                'average_scores': evaluations.aggregate(
                    avg_technical=Avg('technical_skills'),
                    avg_communication=Avg('communication_skills'),
                    avg_teamwork=Avg('teamwork'),
                    avg_overall=Avg('overall_performance')
                ) if evaluations.exists() else {},
            },
            'activities': ActivityLogSerializer(activity_logs, many=True).data,
            'attendance': AttendanceSerializer(attendance_records, many=True).data,
            'evaluations': EvaluationSerializer(evaluations, many=True).data,
        }
        
        # Calculate attendance rate
        if report_data['attendance_summary']['total_days'] > 0:
            report_data['attendance_summary']['attendance_rate'] = (
                report_data['attendance_summary']['present_days'] / 
                report_data['attendance_summary']['total_days']
            ) * 100
        
        # Create report record
        report = Report.objects.create(
            report_type='monthly',
            placement=placement,
            generated_by=request.user,
            report_period_start=start_date,
            report_period_end=end_date,
            report_data=report_data
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_report(self, request, pk=None):
        """Mark report as sent"""
        report = self.get_object()
        report.is_sent = True
        report.sent_at = timezone.now()
        report.save()
        return Response({'message': 'Report marked as sent'})

    @action(detail=False, methods=['get'])
    def report_analytics(self, request):
        """Get analytics for reports"""
        reports = self.get_queryset()
        
        analytics = {
            'total_reports': reports.count(),
            'by_type': reports.values('report_type').annotate(count=Count('id')),
            'sent_reports': reports.filter(is_sent=True).count(),
            'pending_reports': reports.filter(is_sent=False).count(),
            'recent_reports': ReportSerializer(
                reports.order_by('-created_at')[:10], many=True
            ).data,
        }
        
        return Response(analytics) 