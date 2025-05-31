from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from ..models import UserRole, Student, Faculty, OJTProgram, ActivityLog

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
        # If faculty profile doesn't exist, create a basic one
        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role == 'faculty':
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
                return redirect('ojt_tracker:faculty_dashboard')
        except:
            pass
        
        messages.error(request, 'Faculty profile not found. Please contact administrator.')
        return redirect('authentication:login')

@login_required
def admin_dashboard_view(request):
    """Admin dashboard with system overview"""
    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role != 'admin':
            messages.error(request, 'Access denied. Administrator privileges required.')
            return redirect('ojt_tracker:dashboard')
    except UserRole.DoesNotExist:
        messages.error(request, 'User role not found.')
        return redirect('authentication:login')

    # Get statistics for admin dashboard
    from ..models import Company, OJTPlacement, OJTRequest
    
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_companies = Company.objects.filter(is_active=True).count()
    active_placements = OJTPlacement.objects.filter(status='active').count()
    pending_requests = OJTRequest.objects.filter(status='pending').count()

    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_companies': total_companies,
        'active_placements': active_placements,
        'pending_requests': pending_requests,
    }

    return render(request, 'ojt_tracker/admin_dashboard.html', context) 