from django import forms
from django.contrib.auth.models import User
from .models import (
    UserRole, Company, OJTProgram, Student, Faculty,
    OJTPlacement, ActivityLog, Attendance, Evaluation, Message
)

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=UserRole.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            UserRole.objects.create(user=user, role=self.cleaned_data['role'])
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'program', 'year_level', 'section', 
                 'contact_number', 'emergency_contact', 'emergency_phone', 
                 'address', 'profile_picture']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'program': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('1st Year', '1st Year'),
                ('2nd Year', '2nd Year'),
                ('3rd Year', '3rd Year'),
                ('4th Year', '4th Year'),
            ]),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['employee_id', 'department', 'position', 'contact_number', 
                 'office_location', 'specialization', 'profile_picture']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'office_location': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'contact_person', 'phone', 'email', 
                 'website', 'industry', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class OJTProgramForm(forms.ModelForm):
    class Meta:
        model = OJTProgram
        fields = ['name', 'code', 'description', 'duration_weeks', 
                 'required_hours', 'coordinator']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control'}),
            'required_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'coordinator': forms.Select(attrs={'class': 'form-control'}),
        }

class OJTPlacementForm(forms.ModelForm):
    class Meta:
        model = OJTPlacement
        fields = ['student', 'company', 'supervisor', 'position', 'department',
                 'start_date', 'end_date', 'total_hours_required', 
                 'company_supervisor_name', 'company_supervisor_position',
                 'company_supervisor_email', 'company_supervisor_phone', 'description']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_hours_required': forms.NumberInput(attrs={'class': 'form-control'}),
            'company_supervisor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_supervisor_position': forms.TextInput(attrs={'class': 'form-control'}),
            'company_supervisor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company_supervisor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['date', 'time_in', 'time_out', 'activities', 
                 'learning_outcomes', 'challenges_faced', 'skills_developed']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'activities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your daily activities and tasks...'}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What did you learn today?'}),
            'challenges_faced': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any challenges or difficulties encountered?'}),
            'skills_developed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skills developed or improved'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'status', 'time_in', 'time_out', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['placement', 'evaluation_type', 'evaluation_period_start', 
                 'evaluation_period_end', 'technical_skills', 'communication_skills',
                 'teamwork', 'problem_solving', 'initiative', 'punctuality',
                 'attendance', 'overall_performance', 'strengths', 
                 'areas_for_improvement', 'recommendations', 'additional_comments']
        widgets = {
            'placement': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_type': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'evaluation_period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'technical_skills': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'communication_skills': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'teamwork': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'problem_solving': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'initiative': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'punctuality': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'attendance': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'overall_performance': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'message_type', 'content', 
                 'is_important', 'attachment']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class QuickMessageForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    message_type = forms.ChoiceField(
        choices=Message.MESSAGE_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 