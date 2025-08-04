"""
URL configuration for schoolmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.i18n import i18n_patterns
from admins.common_views import unified_login, unified_logout

urlpatterns = [
    path("django-admin/", admin.site.urls),  # Django admin interface
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching
    
    # Unified login/logout for all user types
    path("login/", unified_login, name="unified_login"),
    path("logout/", unified_logout, name="unified_logout"),
    
    # Teacher URLs (outside i18n for direct access)
    path("teacher/", include("teachers.urls")),
    
    # Student URLs (outside i18n for direct access)
    path("student/", include("students.urls")),
]

# Add i18n patterns for internationalized URLs
urlpatterns += i18n_patterns(
    # Admin URLs (internationalized)
    path("admin/", include('admins.urls')),
    
    # Root path redirects to unified login
    path("", unified_login),
    
    prefix_default_language=False,
)