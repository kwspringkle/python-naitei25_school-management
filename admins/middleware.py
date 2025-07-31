from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.deprecation import MiddlewareMixin


class AdminPermissionMiddleware(MiddlewareMixin):
    """
    Middleware to check admin permissions for admin panel access
    """

    # URLs that don't require admin permission check
    EXEMPT_URLS = [
        'admin_login',
        'set_language',  # Language switching
    ]

    # URL patterns that don't require admin permission check
    EXEMPT_URL_PATTERNS = [
        '/i18n/',  # Django i18n URLs
        '/django-admin/',  # Django default admin
    ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process view before it's called
        """
        # Get current URL name
        url_name = request.resolver_match.url_name if request.resolver_match else None
        current_path = request.path

        # Skip permission check for exempt URLs
        if url_name in self.EXEMPT_URLS:
            return None

        # Skip permission check for exempt URL patterns
        for pattern in self.EXEMPT_URL_PATTERNS:
            if current_path.startswith(pattern):
                return None

        # Skip permission check if not in admin area
        if not current_path.startswith('/admin/') and not current_path.startswith('/en/admin/') and not current_path.startswith('/vi/admin/'):
            return None

        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.info(request, _('Please login to access the admin area.'))
            return redirect('admin_login')

        # Check if user has admin permissions
        if not request.user.is_superuser:
            messages.error(request, _(
                'You do not have permission to access the admin area.'))
            return redirect('admin_login')

        # Permission check passed, continue to view
        return None


class AdminSecurityMiddleware(MiddlewareMixin):
    """
    Additional security middleware for admin panel
    """

    def process_request(self, request):
        """
        Process request before view matching
        """
        # Add security headers for admin area
        current_path = request.path

        if (current_path.startswith('/admin/') or
            current_path.startswith('/en/admin/') or
                current_path.startswith('/vi/admin/')):

            # Add additional security for admin area
            request.META['HTTP_X_ADMIN_AREA'] = True

        return None

    def process_response(self, request, response):
        """
        Process response after view execution
        """
        current_path = request.path

        if (current_path.startswith('/admin/') or
            current_path.startswith('/en/admin/') or
                current_path.startswith('/vi/admin/')):

            # Add security headers for admin area
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response


class AdminActivityLogMiddleware(MiddlewareMixin):
    """
    Middleware to log admin activities
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Log admin activities
        """
        current_path = request.path

        # Only log activities in admin area
        if not (current_path.startswith('/admin/') or
                current_path.startswith('/en/admin/') or
                current_path.startswith('/vi/admin/')):
            return None

        # Skip logging for certain URLs
        if (request.resolver_match and
                request.resolver_match.url_name in ['admin_login']):
            return None

        # Log admin activity (you can extend this to save to database)
        if request.user.is_authenticated and request.user.is_superuser:
            import logging
            logger = logging.getLogger('admin_activity')

            logger.info(
                f"Admin Activity - User: {request.user.username}, "
                f"Action: {request.method} {current_path}, "
                f"IP: {self.get_client_ip(request)}, "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )

        return None

    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
