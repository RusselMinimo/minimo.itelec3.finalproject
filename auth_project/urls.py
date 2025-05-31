"""
URL configuration for auth_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_login(request):
    """Redirect root URL to login page"""
    return redirect('authentication:login')

urlpatterns = [
    path('', redirect_to_login, name='home'),  # Redirect root to login
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('app/', include('ojt_tracker.urls')),  # OJT Tracker under /app/
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Static files are served automatically by Django during development

# Admin site customization
admin.site.site_header = "OJT Tracker Administration"
admin.site.site_title = "OJT Tracker Admin"
admin.site.index_title = "Welcome to OJT Tracker Administration"
