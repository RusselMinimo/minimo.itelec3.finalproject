from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from ojt_tracker.models import UserRole
from django.db import transaction


class CustomLoginForm(AuthenticationForm):
    """Custom login form with Tailwind CSS styling"""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false'
        }),
        label='Username'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false'
        }),
        label='Password'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text and customize error messages
        for field in self.fields.values():
            field.help_text = None
        
    error_messages = {
        'invalid_login': 'Please enter a correct username and password. Note that both fields may be case-sensitive.',
        'inactive': 'This account is inactive.',
    }


class CustomRegistrationForm(forms.Form):
    """Custom registration form with relaxed password validation"""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Choose a unique username',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'data-lpignore': 'true',  # LastPass ignore
            'data-form-type': 'other'  # Prevent auto-classification
        }),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Enter your first name',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'words',
            'spellcheck': 'false',
            'data-lpignore': 'true',
            'data-form-type': 'other'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Enter your last name',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'words',
            'spellcheck': 'false',
            'data-lpignore': 'true',
            'data-form-type': 'other'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'data-lpignore': 'true',
            'data-form-type': 'other'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Enter a password (minimum 6 characters)',
            'autocomplete': 'new-password',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'data-lpignore': 'true',
            'data-form-type': 'other'
        }),
        help_text='Your password must be at least 6 characters long.'
    )
    
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'data-lpignore': 'true',
            'data-form-type': 'other'
        }),
        help_text='Enter the same password as before, for verification.'
    )
    
    role = forms.ChoiceField(
        choices=UserRole.ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'role-radio-group'
        }),
        label='I am registering as a:'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text for cleaner UI in the template
        for field in self.fields.values():
            field.help_text = None

    def clean_username(self):
        """Validate username uniqueness and format"""
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("Username is required.")
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        
        # Basic username validation (allow alphanumeric and common symbols)
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and @/./+/-/_ characters.")
        
        return username

    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        
        return email

    def clean_password1(self):
        """Validate password with relaxed rules"""
        password = self.cleaned_data.get('password1')
        if not password:
            raise ValidationError("Password is required.")
        
        # Only check minimum length (6 characters)
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        
        return password

    def clean_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if not password2:
            raise ValidationError("Password confirmation is required.")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        
        return password2

    def clean(self):
        """Additional form-wide validation"""
        cleaned_data = super().clean()
        
        # Ensure all required fields are present
        required_fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']
        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, f"{field_name.replace('_', ' ').title()} is required.")
        
        # Explicit validation for role field
        role = cleaned_data.get('role')
        if role and role not in dict(UserRole.ROLE_CHOICES):
            self.add_error('role', f"Invalid role: {role}")
            
        return cleaned_data

    def save(self, commit=True):
        """Create and save the user with the provided information"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Create user instance
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        # Set password
        user.set_password(self.cleaned_data['password1'])
        
        # Get role from cleaned data
        role = self.cleaned_data.get('role')
        
        if commit:
            # Save user first in a transaction
            try:
                with transaction.atomic():
                    user.save()
                    
                    # Create UserRole with explicit role
                    user_role = UserRole.objects.create(
                        user=user,
                        role=role
                    )
                    
                    # Create corresponding profile based on role
                    if role == 'student':
                        from ojt_tracker.models import Student, OJTProgram
                        # Get a default program or create a placeholder
                        default_program = OJTProgram.objects.filter(is_active=True).first()
                        if not default_program:
                            # Create a default program if none exists
                            default_program = OJTProgram.objects.create(
                                name="General OJT Program",
                                code="GEN001",
                                description="Default OJT program for new students",
                                duration_weeks=12,
                                required_hours=300,
                                is_active=True
                            )
                        
                        # Create Student profile with required fields
                        Student.objects.create(
                            user=user,
                            student_id=f"STU{user.id:06d}",  # Generate student ID
                            program=default_program,
                            year_level="1st Year",  # Default value
                            section="A",  # Default value
                            contact_number="",  # To be filled later
                            emergency_contact="",  # To be filled later
                            emergency_phone="",  # To be filled later
                            address=""  # To be filled later
                        )
                        logger.info(f"Student profile created for user {user.username}")
                        
                    elif role == 'faculty':
                        from ojt_tracker.models import Faculty
                        # Create Faculty profile with required fields
                        Faculty.objects.create(
                            user=user,
                            employee_id=f"FAC{user.id:06d}",  # Generate employee ID
                            department="General",  # Default value
                            position="Faculty",  # Default value
                            contact_number="",  # To be filled later
                            office_location="",  # To be filled later
                            specialization=""  # Optional field
                        )
                        logger.info(f"Faculty profile created for user {user.username}")
                    
                    # For admin role, no additional profile is needed
                    
                    # Verify the role was saved
                    UserRole.objects.get(user=user)
                    logger.info(f"User registration completed successfully: {user.username} as {role}")
                    
            except Exception as e:
                # If any error occurs, log it and reraise
                logger.error(f"Error creating user with role {role}: {str(e)}", exc_info=True)
                raise
        
        return user 