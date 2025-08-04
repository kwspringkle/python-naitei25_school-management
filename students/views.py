from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from students.models import Student


@login_required
def student_dashboard(request):
    """
    Student dashboard view - only accessible to authenticated students
    """
    # Check if user is a student
    if not getattr(request.user, 'is_student', False):
        messages.error(request, _('Access denied. Student credentials required.'))
        return redirect('unified_login')
    
    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, _('Student profile not found. Please contact administrator.'))
        return redirect('unified_logout')
    
    context = {
        'student': student,
        'user': request.user,
    }
    
    return render(request, 'students/dashboard.html', context)


def student_logout(request):
    """
    Student logout view - redirects to unified logout
    """
    return redirect('unified_logout')