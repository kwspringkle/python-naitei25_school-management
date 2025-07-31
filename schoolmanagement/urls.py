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

urlpatterns = [
    path("django-admin/", admin.site.urls),  # Rename to avoid conflict
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching
]

# Add i18n patterns for internationalized URLs
urlpatterns += i18n_patterns(
    path("admin/", include('admins.urls')),  # Custom admin URLs
    path("", include('admins.urls')),  # Root path redirect to admin login
    prefix_default_language=False,
)
