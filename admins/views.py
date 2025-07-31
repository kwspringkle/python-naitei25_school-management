# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext_lazy as _

# Local application imports
from utils.constant import ADMIN_DATETIME_FORMAT
from .forms import AdminLoginForm

# Model imports
from students.models import Student
from teachers.models import Teacher
from admins.models import Dept, Subject, Class


@csrf_protect
def admin_login(request):
    """
    Custom admin login view with form validation and clean data
    """
    # Redirect authenticated admin users
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    # Initialize form
    form = AdminLoginForm(request=request)

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)

        if form.is_valid():
            # Get cleaned data and authenticated user
            user = form.get_user()

            # Login user
            login(request, user)
            messages.success(
                request,
                _('Welcome %(name)s!') % {
                    'name': user.get_full_name() or user.username}
            )
            return redirect('admin_dashboard')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    context = {
        'form': form
    }
    return render(request, 'admins/login.html', context)


def admin_dashboard(request):
    """
    Admin dashboard view
    Note: Admin permission check is handled by AdminPermissionMiddleware
    """
    # Basic statistics
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_departments': Dept.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classes': Class.objects.count(),
        'admin_user': request.user,
        'date_format': ADMIN_DATETIME_FORMAT,
    }

    return render(request, 'admins/dashboard.html', context)


def admin_logout(request):
    """
    Admin logout view
    Note: Admin permission check is handled by AdminPermissionMiddleware
    """
    if request.user.is_authenticated and request.user.is_superuser:
        messages.success(request, _('You have been logged out successfully.'))
    logout(request)
    return redirect('admin_login')
