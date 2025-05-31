from django import forms
from django.contrib.auth.models import User
from ..models import ActivityLog, Attendance, Evaluation, Message

class ActivityLogForm(forms.ModelForm):
    """Form for student activity logging"""
    class Meta:
        model = ActivityLog
        fields = ['date', 'time_in', 'time_out', 'activities', 
                 'learning_outcomes', 'challenges_faced', 'skills_developed']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'activities': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe your daily activities and tasks...'
            }),
            'learning_outcomes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'What did you learn today?'
            }),
            'challenges_faced': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Any challenges or difficulties encountered?'
            }),
            'skills_developed': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Skills developed or improved'
            }),
        }

class AttendanceForm(forms.ModelForm):
    """Form for attendance management"""
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
    """Form for student evaluation"""
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
    """Form for sending messages"""
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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Filter recipients based on user role
            self.fields['recipient'].queryset = User.objects.exclude(id=self.user.id)

class QuickMessageForm(forms.Form):
    """Form for quick message sending"""
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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['recipient'].queryset = User.objects.exclude(id=self.user.id) 