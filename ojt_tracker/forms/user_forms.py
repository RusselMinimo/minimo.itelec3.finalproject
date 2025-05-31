from django import forms
from django.contrib.auth.models import User
from ..models import UserRole, Student, Faculty

class UserRegistrationForm(forms.ModelForm):
    """Form for user registration with role selection"""
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
    """Form for student profile management"""
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
    """Form for faculty profile management"""
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