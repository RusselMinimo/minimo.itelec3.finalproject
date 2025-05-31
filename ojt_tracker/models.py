from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, datetime

class UserRole(models.Model):
    """Extended user model to define roles (Student, Faculty, Admin)"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Company(models.Model):
    """Model for companies where students do their OJT"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name

class OJTProgram(models.Model):
    """Model for OJT Programs/Courses"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    duration_weeks = models.PositiveIntegerField()
    required_hours = models.PositiveIntegerField()
    coordinator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'role__role': 'faculty'},
        related_name='coordinated_programs'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Student(models.Model):
    """Extended student model with OJT-specific information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(OJTProgram, on_delete=models.CASCADE, related_name='students')
    year_level = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class Faculty(models.Model):
    """Faculty model for supervisors and coordinators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    office_location = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='faculty_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Faculty"
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

class OJTPlacement(models.Model):
    """Model for student placements in companies"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='placements')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='placements')
    supervisor = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='supervised_placements')
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_hours_required = models.PositiveIntegerField()
    total_hours_completed = models.PositiveIntegerField(default=0)
    company_supervisor_name = models.CharField(max_length=100)
    company_supervisor_position = models.CharField(max_length=100)
    company_supervisor_email = models.EmailField()
    company_supervisor_phone = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'start_date']
    
    def __str__(self):
        return f"{self.student.student_id} at {self.company.name}"
    
    @property
    def completion_percentage(self):
        if self.total_hours_required > 0:
            return min((self.total_hours_completed / self.total_hours_required) * 100, 100)
        return 0
    
    @property
    def is_active(self):
        return self.status == 'active' and self.start_date <= date.today() <= self.end_date

class ActivityLog(models.Model):
    """Model for daily activity logging by students"""
    placement = models.ForeignKey(OJTPlacement, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    activities = models.TextField()
    learning_outcomes = models.TextField(blank=True)
    challenges_faced = models.TextField(blank=True)
    skills_developed = models.CharField(max_length=500, blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        Faculty, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_activities'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['placement', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.placement.student.student_id} - {self.date}"
    
    def save(self, *args, **kwargs):
        if self.time_in and self.time_out:
            # Calculate hours worked
            start = datetime.combine(date.today(), self.time_in)
            end = datetime.combine(date.today(), self.time_out)
            if end < start:  # Next day
                end = datetime.combine(date.today() + timezone.timedelta(days=1), self.time_out)
            duration = end - start
            self.hours_worked = duration.total_seconds() / 3600
        super().save(*args, **kwargs)

class Attendance(models.Model):
    """Model for attendance tracking"""
    placement = models.ForeignKey(OJTPlacement, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('excused', 'Excused'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    ], default='present')
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    hours_present = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    
    # New fields for enhanced tracking
    check_in_location = models.CharField(max_length=255, blank=True, null=True, help_text="Location/address when checking in")
    check_out_location = models.CharField(max_length=255, blank=True, null=True, help_text="Location/address when checking out")
    check_in_ip = models.GenericIPAddressField(blank=True, null=True, help_text="IP address used for check-in")
    check_out_ip = models.GenericIPAddressField(blank=True, null=True, help_text="IP address used for check-out")
    is_late = models.BooleanField(default=False, help_text="Marked as late if check-in is after expected time")
    expected_check_in = models.TimeField(default='08:00:00', help_text="Expected check-in time")
    break_time_out = models.TimeField(blank=True, null=True, help_text="Break start time")
    break_time_in = models.TimeField(blank=True, null=True, help_text="Break end time")
    total_break_minutes = models.IntegerField(default=0, help_text="Total break time in minutes")
    
    remarks = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_attendance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['placement', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.placement.student.student_id} - {self.date} - {self.get_status_display()}"
    
    @property
    def can_check_in(self):
        """Check if student can check in today"""
        today = timezone.now().date()
        return self.date == today and not self.time_in
    
    @property
    def can_check_out(self):
        """Check if student can check out today"""
        today = timezone.now().date()
        return self.date == today and self.time_in and not self.time_out
    
    @property
    def is_checked_in(self):
        """Check if student is currently checked in"""
        today = timezone.now().date()
        return self.date == today and self.time_in and not self.time_out
    
    def calculate_hours_worked(self):
        """Calculate total hours worked including break deductions"""
        if self.time_in and self.time_out:
            start = datetime.combine(date.today(), self.time_in)
            end = datetime.combine(date.today(), self.time_out)
            if end < start:  # Next day
                end = datetime.combine(date.today() + timezone.timedelta(days=1), self.time_out)
            duration = end - start
            total_minutes = duration.total_seconds() / 60
            # Subtract break time
            work_minutes = total_minutes - self.total_break_minutes
            return max(0, work_minutes / 60)  # Ensure non-negative hours
        return 0
    
    def save(self, *args, **kwargs):
        # Auto-calculate hours worked
        self.hours_present = self.calculate_hours_worked()
        
        # Check if late
        if self.time_in and self.expected_check_in:
            self.is_late = self.time_in > self.expected_check_in
        
        # Update status based on time_in/time_out
        if self.time_in and self.time_out:
            self.status = 'checked_out'
        elif self.time_in:
            self.status = 'checked_in'
        
        super().save(*args, **kwargs)

class Evaluation(models.Model):
    """Model for performance evaluations"""
    EVALUATION_TYPES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('midterm', 'Midterm'),
        ('final', 'Final'),
    ]
    
    placement = models.ForeignKey(OJTPlacement, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='conducted_evaluations')
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPES)
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    
    # Performance metrics (1-5 scale)
    technical_skills = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_skills = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    teamwork = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    problem_solving = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    initiative = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    attendance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    overall_performance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    recommendations = models.TextField()
    additional_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['placement', 'evaluation_type', 'evaluation_period_start']
        ordering = ['-evaluation_period_start']
    
    def __str__(self):
        return f"{self.placement.student.student_id} - {self.get_evaluation_type_display()} - {self.evaluation_period_start}"
    
    @property
    def average_score(self):
        scores = [
            self.technical_skills, self.communication_skills, self.teamwork,
            self.problem_solving, self.initiative, self.punctuality,
            self.attendance, self.overall_performance
        ]
        return sum(scores) / len(scores)

class Message(models.Model):
    """Model for communication between students and faculty"""
    MESSAGE_TYPES = [
        ('general', 'General'),
        ('feedback', 'Feedback'),
        ('inquiry', 'Inquiry'),
        ('report', 'Report'),
        ('urgent', 'Urgent'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    placement = models.ForeignKey(
        OJTPlacement, 
        on_delete=models.CASCADE, 
        related_name='messages',
        blank=True,
        null=True
    )
    subject = models.CharField(max_length=200)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"

class Report(models.Model):
    """Model for automated report generation"""
    REPORT_TYPES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('attendance', 'Attendance Report'),
        ('performance', 'Performance Report'),
        ('completion', 'Completion Report'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    placement = models.ForeignKey(OJTPlacement, on_delete=models.CASCADE, related_name='reports')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    report_period_start = models.DateField()
    report_period_end = models.DateField()
    
    # Report data (JSON field for flexibility)
    report_data = models.JSONField()
    
    file_path = models.CharField(max_length=500, blank=True)  # Path to generated PDF/Excel file
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.placement.student.student_id}"

class OJTRequest(models.Model):
    """Model for student OJT requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ojt_requests')
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, help_text="Optional remarks or additional information about the OJT request")
    admin_response = models.TextField(blank=True, help_text="Admin response or feedback for the request")
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_ojt_requests',
        limit_choices_to={'role__role': 'admin'}
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_submitted']
    
    def __str__(self):
        return f"OJT Request - {self.student.student_id} ({self.get_status_display()})"
    
    @property
    def can_be_approved(self):
        """Check if this request can be approved"""
        return self.status == 'pending'
    
    @property 
    def can_be_rejected(self):
        """Check if this request can be rejected"""
        return self.status == 'pending'
    
    def approve(self, admin_user, response=""):
        """Approve the OJT request and mark student as ready for OJT"""
        if self.can_be_approved:
            # Auto-reject any other pending requests for this student
            OJTRequest.objects.filter(
                student=self.student, 
                status='pending'
            ).exclude(id=self.id).update(
                status='rejected',
                admin_response='Auto-rejected due to approval of another request',
                reviewed_by=admin_user,
                reviewed_at=timezone.now()
            )
            
            self.status = 'approved'
            self.reviewed_by = admin_user
            self.reviewed_at = timezone.now()
            self.admin_response = response
            self.save()
            return True
        return False
    
    def reject(self, admin_user, response=""):
        """Reject the OJT request"""
        if self.can_be_rejected:
            self.status = 'rejected'
            self.reviewed_by = admin_user
            self.reviewed_at = timezone.now()
            self.admin_response = response
            self.save()
            return True
        return False 