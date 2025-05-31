from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from datetime import date, timedelta
import json

from ..models import (
    UserRole, Student, Faculty, Company, OJTProgram, 
    OJTPlacement, ActivityLog, Attendance, Evaluation,
    Message, Report, OJTRequest
)
from ..forms import (
    StudentProfileForm, FacultyProfileForm, CompanyForm,
    OJTProgramForm, OJTPlacementForm, ActivityLogForm,
    AttendanceForm, EvaluationForm, MessageForm, 
    OJTRequestForm, OJTRequestReviewForm
)

# ============================================================================
# STUDENT VIEWS
# ============================================================================

@login_required
def student_profile_view(request):
    """Student profile management"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('ojt_tracker:dashboard')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('ojt_tracker:student_profile')
    else:
        form = StudentProfileForm(instance=student)

    context = {
        'student': student,
        'form': form,
    }
    return render(request, 'ojt_tracker/student_profile.html', context)

@login_required
def student_placement_view(request):
    """Student placement details view"""
    try:
        student = Student.objects.get(user=request.user)
        current_placement = student.placements.filter(status='active').first()
        placement_history = student.placements.exclude(status='active').order_by('-start_date')
        
        context = {
            'student': student,
            'current_placement': current_placement,
            'placement_history': placement_history,
        }
        return render(request, 'ojt_tracker/student_placement.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('ojt_tracker:dashboard')

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
                activity = form.save(commit=False)
                activity.placement = current_placement
                activity.save()
                messages.success(request, 'Activity log submitted successfully!')
                return redirect('ojt_tracker:activity_log')
        else:
            form = ActivityLogForm()
        
        activities = current_placement.activity_logs.order_by('-date')[:20]
        
        context = {
            'student': student,
            'current_placement': current_placement,
            'form': form,
            'activities': activities,
        }
        return render(request, 'ojt_tracker/activity_log.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('ojt_tracker:dashboard')

@login_required
def student_attendance_view(request):
    """Student attendance tracking"""
    try:
        student = Student.objects.get(user=request.user)
        current_placement = student.placements.filter(status='active').first()
        
        if not current_placement:
            messages.error(request, 'No active placement found.')
            return redirect('ojt_tracker:student_dashboard')
        
        # Get attendance records
        attendance_records = current_placement.attendance_records.order_by('-date')[:30]
        
        # Calculate statistics
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status__in=['present', 'checked_out']).count()
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Check today's attendance
        today = date.today()
        today_attendance = current_placement.attendance_records.filter(date=today).first()
        
        context = {
            'student': student,
            'current_placement': current_placement,
            'attendance_records': attendance_records,
            'attendance_rate': attendance_rate,
            'total_days': total_days,
            'present_days': present_days,
            'today_attendance': today_attendance,
        }
        return render(request, 'ojt_tracker/student_attendance.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('ojt_tracker:dashboard')

@login_required
def student_ojt_request_view(request):
    """View for students to submit OJT requests"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please contact administrator.')
        return redirect('ojt_tracker:dashboard')
    
    # Get current request status
    current_request = student.ojt_requests.filter(status__in=['pending', 'approved']).first()
    
    if request.method == 'POST':
        form = OJTRequestForm(request.POST, student=student)
        if form.is_valid():
            ojt_request = form.save()
            messages.success(request, 'Your OJT request has been submitted successfully. Please wait for admin approval.')
            return redirect('ojt_tracker:student_ojt_request')
    else:
        form = OJTRequestForm(student=student)
    
    # Get request history
    request_history = student.ojt_requests.order_by('-date_submitted')
    
    context = {
        'student': student,
        'form': form,
        'current_request': current_request,
        'request_history': request_history,
    }
    return render(request, 'ojt_tracker/student_ojt_request.html', context)

# ============================================================================
# FACULTY VIEWS
# ============================================================================

@login_required
def faculty_profile_view(request):
    """Faculty profile management"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:dashboard')

    if request.method == 'POST':
        form = FacultyProfileForm(request.POST, request.FILES, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('ojt_tracker:faculty_profile')
    else:
        form = FacultyProfileForm(instance=faculty)

    context = {
        'faculty': faculty,
        'form': form,
    }
    return render(request, 'ojt_tracker/faculty_profile.html', context)

@login_required
def faculty_students_view(request):
    """Faculty view of supervised students"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        supervised_placements = faculty.supervised_placements.filter(status='active')
        
        context = {
            'faculty': faculty,
            'supervised_placements': supervised_placements,
        }
        return render(request, 'ojt_tracker/faculty_students.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:dashboard')

@login_required
def faculty_evaluations_view(request):
    """Faculty evaluations management"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        evaluations = Evaluation.objects.filter(evaluator=faculty).order_by('-evaluation_period_start')
        
        context = {
            'faculty': faculty,
            'evaluations': evaluations,
        }
        return render(request, 'ojt_tracker/faculty_evaluations.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:dashboard')

@login_required
def faculty_reports_view(request):
    """Faculty reports management"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        
        # Get supervised placements for report generation
        supervised_placements = faculty.supervised_placements.all()
        reports = Report.objects.filter(
            placement__supervisor=faculty
        ).order_by('-created_at')
        
        # Calculate statistics
        total_students = supervised_placements.filter(status='active').count()
        total_evaluations = Evaluation.objects.filter(evaluator=faculty).count()
        total_reports = reports.count()
        monthly_reports = reports.filter(
            created_at__month=date.today().month,
            created_at__year=date.today().year
        ).count()
        
        context = {
            'faculty': faculty,
            'reports': reports,
            'total_students': total_students,
            'total_evaluations': total_evaluations,
            'total_reports': total_reports,
            'monthly_reports': monthly_reports,
        }
        return render(request, 'ojt_tracker/faculty_reports.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('ojt_tracker:dashboard')

# ============================================================================
# ADMIN VIEWS
# ============================================================================

@login_required
def admin_companies_view(request):
    """Admin companies management"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('ojt_tracker:dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login')

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
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('ojt_tracker:dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login')

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
    """Admin view for managing OJT placements"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('ojt_tracker:dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login')
    
    placements = OJTPlacement.objects.all().order_by('-created_at')
    context = {
        'placements': placements,
    }
    return render(request, 'ojt_tracker/admin_placements.html', context)

@login_required
def admin_ojt_requests_view(request):
    """Admin view for managing OJT requests"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('ojt_tracker:dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    requests = OJTRequest.objects.select_related('student__user', 'student__program', 'reviewed_by')
    
    # Apply filters
    if status_filter != 'all':
        requests = requests.filter(status=status_filter)
    
    # Order by submission date
    requests = requests.order_by('-date_submitted')
    
    # Statistics for dashboard
    stats = {
        'total_requests': OJTRequest.objects.count(),
        'pending_requests': OJTRequest.objects.filter(status='pending').count(),
        'approved_requests': OJTRequest.objects.filter(status='approved').count(),
        'rejected_requests': OJTRequest.objects.filter(status='rejected').count(),
    }
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
        'stats': stats,
    }
    return render(request, 'ojt_tracker/admin_ojt_requests.html', context)

@login_required
def admin_ojt_request_detail_view(request, request_id):
    """Admin view for detailed OJT request management"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('ojt_tracker:dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login')
    
    ojt_request = get_object_or_404(OJTRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_response = request.POST.get('admin_response', '')
        
        if action == 'approve':
            if ojt_request.approve(request.user, admin_response):
                messages.success(request, f'OJT request from {ojt_request.student.user.get_full_name()} has been approved.')
            else:
                messages.error(request, 'Unable to approve this request.')
        elif action == 'reject':
            if ojt_request.reject(request.user, admin_response):
                messages.success(request, f'OJT request from {ojt_request.student.user.get_full_name()} has been rejected.')
            else:
                messages.error(request, 'Unable to reject this request.')
        
        return redirect('ojt_tracker:admin_ojt_request_detail', request_id=request_id)
    
    # Review form for admin response
    review_form = OJTRequestReviewForm(instance=ojt_request)
    
    context = {
        'ojt_request': ojt_request,
        'review_form': review_form,
    }
    return render(request, 'ojt_tracker/admin_ojt_request_detail.html', context)

# ============================================================================
# COMMON VIEWS
# ============================================================================

@login_required
def messages_view(request):
    """Messages view for communication"""
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
                messages.error(request, 'Message not found or you do not have permission to mark it as read.')
            return redirect('ojt_tracker:messages')
        
        # Handle delete message action  
        elif 'delete_message' in request.POST:
            message_id = request.POST.get('delete_message')
            try:
                message = Message.objects.filter(
                    Q(sender=request.user) | Q(recipient=request.user),
                    id=message_id
                ).first()
                if message:
                    message_subject = message.subject
                    message.delete()
                    messages.success(request, f'Message "{message_subject}" deleted successfully!')
                else:
                    messages.error(request, 'Message not found or you do not have permission to delete it.')
            except Exception as e:
                messages.error(request, 'An error occurred while deleting the message.')
            return redirect('ojt_tracker:messages')
        
        # Handle compose new message
        else:
            form = MessageForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                messages.success(request, 'Message sent successfully!')
                return redirect('ojt_tracker:messages')
    else:
        form = MessageForm(user=request.user)

    # Get user's messages
    inbox_messages = request.user.received_messages.order_by('-created_at')[:20]
    sent_messages = request.user.sent_messages.order_by('-created_at')[:20]
    unread_count = request.user.received_messages.filter(is_read=False).count()

    context = {
        'form': form,
        'inbox_messages': inbox_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
    }
    return render(request, 'ojt_tracker/messages.html', context)

@login_required
def reports_view(request):
    """General reports view"""
    # This view can be customized based on user role
    try:
        user_role = UserRole.objects.get(user=request.user)
        
        if user_role.role == 'student':
            try:
                student = Student.objects.get(user=request.user)
                current_placement = student.placements.filter(status='active').first()
                reports = Report.objects.filter(placement=current_placement) if current_placement else []
            except Student.DoesNotExist:
                reports = []
        elif user_role.role == 'faculty':
            try:
                faculty = Faculty.objects.get(user=request.user)
                reports = Report.objects.filter(placement__supervisor=faculty)
            except Faculty.DoesNotExist:
                reports = []
        else:  # admin
            reports = Report.objects.all()
        
        context = {
            'reports': reports.order_by('-created_at'),
            'user_role': user_role.role,
        }
        return render(request, 'ojt_tracker/reports.html', context)
        
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login') 