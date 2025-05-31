from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, login_view, logout_view

app_name = 'authentication'

urlpatterns = [
    # Web-based authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # API-based authentication
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
] 