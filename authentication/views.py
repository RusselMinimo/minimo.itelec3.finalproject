from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from rest_framework import generics, permissions, parsers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, UserSerializer
from .forms import CustomLoginForm, CustomRegistrationForm
from django.contrib.auth.models import User
from ojt_tracker.models import UserRole
from django.db import transaction
import logging
from django.http import JsonResponse

# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

def get_role_based_redirect_url(user):
    """Get the appropriate redirect URL based on user role"""
    try:
        user_role = UserRole.objects.get(user=user)
        if user_role.role == 'student':
            return 'ojt_tracker:student_dashboard'
        elif user_role.role == 'faculty':
            return 'ojt_tracker:faculty_dashboard'
        elif user_role.role == 'admin':
            return 'ojt_tracker:admin_dashboard'
        else:
            return 'ojt_tracker:dashboard'  # Fallback to general dashboard
    except UserRole.DoesNotExist:
        logger.error(f"UserRole not found for user: {user.username}")
        messages.warning(None, 'User role not found. Please contact administrator.')
        return 'ojt_tracker:dashboard'

# Template-based views for web interface
@ensure_csrf_cookie
@csrf_protect
@never_cache
def login_view(request):
    """Web-based login and registration view using Django forms"""
    login_form = CustomLoginForm()
    registration_form = CustomRegistrationForm()
    
    # Determine which form to show initially
    show_register = False
    
    if request.method == 'POST':
        # Debug CSRF token information
        logger.info(f"CSRF Token from POST: {request.POST.get('csrfmiddlewaretoken', 'NOT FOUND')}")
        logger.info(f"CSRF Cookie: {request.COOKIES.get('csrftoken', 'NOT FOUND')}")
        logger.info(f"Request META CSRF: {request.META.get('CSRF_COOKIE', 'NOT FOUND')}")
        
        # Check which form was submitted
        if 'login_submit' in request.POST:
            # Handle login
            login_form = CustomLoginForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                
                # Get role-based redirect URL
                next_url = request.GET.get('next')
                if not next_url:
                    next_url = get_role_based_redirect_url(user)
                    
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid credentials. Please check your username and password.')
                
        elif 'register_submit' in request.POST:
            # Handle registration
            registration_form = CustomRegistrationForm(request.POST)
            show_register = True
            
            if registration_form.is_valid():
                try:
                    with transaction.atomic():
                        user = registration_form.save()
                        
                        # Verify UserRole was created
                        try:
                            user_role = UserRole.objects.get(user=user)
                            logger.info(f"UserRole created: {user_role.role} for user {user.username}")
                        except UserRole.DoesNotExist:
                            logger.error(f"UserRole NOT created for user {user.username}")
                            messages.error(request, 'Registration failed: Role assignment error. Please try again.')
                            user.delete()  # Clean up the user if role wasn't created
                            return render(request, 'authentication/login.html', {
                                'login_form': login_form,
                                'registration_form': registration_form,
                                'show_register': show_register,
                            })
                        
                        # Automatically log in the new user
                        login(request, user)
                        
                        # Get role-based redirect URL
                        redirect_url = get_role_based_redirect_url(user)
                        role_display = dict(UserRole.ROLE_CHOICES).get(registration_form.cleaned_data['role'], 'User')
                        
                        messages.success(request, f'Welcome to OJT Tracker, {user.get_full_name()}! Your {role_display} account has been created successfully.')
                        return redirect(redirect_url)
                        
                except Exception as e:
                    logger.error(f"Registration error: {str(e)}", exc_info=True)
                    messages.error(request, f'Registration failed: {str(e)}. Please try again.')
            else:
                messages.error(request, 'Please correct the errors below and try again.')
    
    context = {
        'login_form': login_form,
        'registration_form': registration_form,
        'show_register': show_register,
    }
    return render(request, 'authentication/login.html', context)

@login_required
def logout_view(request):
    """Web-based logout view"""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Goodbye {user_name}! You have been successfully logged out.')
    return redirect('authentication:login')

# Add this view for debugging
@ensure_csrf_cookie
def csrf_debug(request):
    """Debug view to check CSRF token"""
    return JsonResponse({
        'csrf_token': request.META.get('CSRF_COOKIE'),
        'method': request.method,
        'headers': dict(request.headers),
        'cookies': request.COOKIES,
    })
