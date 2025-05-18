from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    photo = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'photo')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        password2 = validated_data.pop('password2', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Create user profile with photo if provided
        profile = Profile.objects.create(user=user)
        if photo:
            profile.photo = photo
            profile.save()
            
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