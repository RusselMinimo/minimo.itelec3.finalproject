from django import forms
from ..models import Company, OJTProgram, OJTPlacement, OJTRequest

class CompanyForm(forms.ModelForm):
    """Form for company management"""
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
    """Form for OJT program management"""
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
    """Form for OJT placement management"""
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

class OJTRequestForm(forms.ModelForm):
    """Form for OJT request submission"""
    class Meta:
        model = OJTRequest
        fields = ['remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Please provide any additional information about your OJT request...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        if self.student:
            # Check if student already has a pending request
            existing_pending_request = OJTRequest.objects.filter(
                student=self.student,
                status='pending'
            ).first()
            
            if existing_pending_request:
                raise forms.ValidationError(
                    'You already have a pending OJT request. Please wait for admin approval before submitting a new one.'
                )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.student:
            instance.student = self.student
        if commit:
            instance.save()
        return instance

class OJTRequestReviewForm(forms.ModelForm):
    """Form for admin OJT request review"""
    class Meta:
        model = OJTRequest
        fields = ['admin_response']
        widgets = {
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Provide feedback or comments for the student...'
            }),
        } 