from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class TeacherPermissionMiddleware:
    """
    Middleware to ensure only authenticated teachers can access teacher-specific views
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check if user has permission to access teacher views
        """
        # Define teacher-specific URL patterns
        teacher_urls = [
            'teacher_dashboard',
            'teacher_logout',
            'index',  # Legacy teacher index
        ]
        
        # Check if current view is teacher-specific
        if request.resolver_match and request.resolver_match.url_name in teacher_urls:
            # Allow access if user is authenticated and is a teacher
            if request.user.is_authenticated and getattr(request.user, 'is_teacher', False):
                return None
            
            # Redirect to unified login if not authenticated or not a teacher
            messages.error(request, _('Please login with teacher credentials to access this page.'))
            return redirect('unified_login')
        
        return None