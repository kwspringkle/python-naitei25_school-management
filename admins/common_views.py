from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import UnifiedLoginForm
from utils.constant import (
    ADMIN_DASHBOARD_URL, TEACHER_DASHBOARD_URL, STUDENT_DASHBOARD_URL, UNIFIED_LOGIN_URL,
    UNIFIED_LOGIN_TEMPLATE, IS_TEACHER_ATTRIBUTE, IS_STUDENT_ATTRIBUTE,
    ADMIN_WELCOME_MSG_TEMPLATE, TEACHER_WELCOME_MSG_TEMPLATE, STUDENT_WELCOME_MSG_TEMPLATE,
    UNIFIED_NO_PERMISSION_ERROR, UNIFIED_INVALID_ROLE_ERROR, UNIFIED_FORM_ERRORS_MESSAGE,
    UNIFIED_LOGOUT_SUCCESS_MSG_TEMPLATE, UNIFIED_LOGOUT_SUCCESS_MSG_ANONYMOUS,
    FORM_CONTEXT_KEY, TITLE_CONTEXT_KEY, LOGIN_TITLE
)


@csrf_protect
def unified_login(request):
    """
    Unified login view for Admin, Teacher, and Student
    Auto-detects user role and redirects accordingly
    """
    # Redirect if already authenticated
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(ADMIN_DASHBOARD_URL)
        elif getattr(request.user, IS_TEACHER_ATTRIBUTE, False):
            return redirect(TEACHER_DASHBOARD_URL)
        elif getattr(request.user, IS_STUDENT_ATTRIBUTE, False):
            return redirect(STUDENT_DASHBOARD_URL)

    if request.method == 'POST':
        form = UnifiedLoginForm(request, data=request.POST)

        if form.is_valid():
            # Get cleaned data and authenticated user
            user = form.get_user()

            # Login user
            login(request, user)
            
            # Determine user role and redirect accordingly
            if user.is_superuser:
                messages.success(
                    request,
                    _(ADMIN_WELCOME_MSG_TEMPLATE).format(
                        user.get_full_name() or user.username)
                )
                return redirect(ADMIN_DASHBOARD_URL)
            elif getattr(user, IS_TEACHER_ATTRIBUTE, False):
                messages.success(
                    request,
                    _(TEACHER_WELCOME_MSG_TEMPLATE).format(
                        user.get_full_name() or user.username)
                )
                return redirect(TEACHER_DASHBOARD_URL)
            elif getattr(user, IS_STUDENT_ATTRIBUTE, False):
                messages.success(
                    request,
                    _(STUDENT_WELCOME_MSG_TEMPLATE).format(
                        user.get_full_name() or user.username)
                )
                return redirect(STUDENT_DASHBOARD_URL)
            else:
                # User doesn't have proper role
                logout(request)
                messages.error(request, _(UNIFIED_NO_PERMISSION_ERROR))
                form.add_error(None, _(UNIFIED_INVALID_ROLE_ERROR))
        else:
            # Form has errors
            messages.error(request, _(UNIFIED_FORM_ERRORS_MESSAGE))
    else:
        form = UnifiedLoginForm(request)

    return render(request, UNIFIED_LOGIN_TEMPLATE, {
        FORM_CONTEXT_KEY: form,
        TITLE_CONTEXT_KEY: _(LOGIN_TITLE),
    })


def unified_logout(request):
    """
    Unified logout view for all user types
    """
    user_display = request.user.get_full_name() or request.user.username if request.user.is_authenticated else None
    
    logout(request)
    
    if user_display:
        messages.success(request, _(UNIFIED_LOGOUT_SUCCESS_MSG_TEMPLATE).format(user_display))
    else:
        messages.success(request, _(UNIFIED_LOGOUT_SUCCESS_MSG_ANONYMOUS))
    
    return redirect(UNIFIED_LOGIN_URL)