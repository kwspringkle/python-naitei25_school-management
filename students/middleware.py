from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class StudentPermissionMiddleware:
    """
    Middleware to ensure only authenticated students can access student-specific views
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check if user has permission to access student views
        """
        # Define student-specific URL patterns
        student_urls = [
            'student_dashboard',
            'student_logout',
        ]
        
        # Check if current view is student-specific
        if request.resolver_match and request.resolver_match.url_name in student_urls:
            # Allow access if user is authenticated and is a student
            if request.user.is_authenticated and getattr(request.user, 'is_student', False):
                return None
            
            # Redirect to unified login if not authenticated or not a student
            messages.error(request, _('Please login with student credentials to access this page.'))
            return redirect('unified_login')
        
        return None