from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from ojt_tracker.models import UserRole

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    photo = serializers.ImageField(required=False, write_only=True)
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2', 'photo', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        password2 = validated_data.pop('password2', None)
        role = validated_data.pop('role')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Create user profile with photo if provided
        profile = Profile.objects.create(user=user)
        if photo:
            profile.photo = photo
            profile.save()
        
        # Create UserRole
        UserRole.objects.create(user=user, role=role)
        
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
            
        return user

class UserSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'photo_url')
    
    def get_photo_url(self, obj):
        request = self.context.get('request')
        try:
            if obj.profile and obj.profile.photo:
                if request:
                    return request.build_absolute_uri(obj.profile.photo.url)
                return obj.profile.photo.url
        except Profile.DoesNotExist:
            pass
        return None 