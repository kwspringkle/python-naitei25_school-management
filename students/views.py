from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from students.models import Student, StudentSubject, Attendance
from admins.models import Class, Subject
from teachers.models import AssignTime, Assign
from utils.constant import (
    # Timetable constants
    DAYS_OF_WEEK, TIME_SLOTS, BREAK_PERIOD, LUNCH_PERIOD,
    TIMETABLE_TIME_SLOTS,
    TIMETABLE_DAYS_COUNT, TIMETABLE_PERIODS_COUNT, TIMETABLE_DEFAULT_VALUE,
    TIMETABLE_SKIP_PERIODS
)
from datetime import datetime, timedelta, date


def _check_student_access(request):
    """
    Helper function to check if user is a student
    Returns (is_student, redirect_response) tuple
    """
    if not getattr(request.user, 'is_student', False):
        messages.error(request, _('Access denied. Student credentials required.'))
        return False, redirect('unified_login')
    return True, None


def _get_student_by_usn(request, student_usn):
    """
    Helper function to get student by USN and check access permissions
    Returns (student, redirect_response) tuple
    """
    # Check student access first
    is_student, redirect_response = _check_student_access(request)
    if not is_student:
        return None, redirect_response
    
    # Get student profile
    student = get_object_or_404(Student, USN=student_usn)
    
    # Check if the logged-in user can access this student's data
    if request.user.student != student:
        messages.error(request, _('Access denied. You can only view your own data.'))
        return None, redirect('students:student_dashboard')
    
    return student, None


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


@login_required
def index(request):
    """
    Student index/homepage - redirects to dashboard
    """
    return redirect('students:student_dashboard')


@login_required
def student_attendance(request, student_usn):
    """
    View student attendance for all subjects
    """
    # Get student and check access permissions
    student, redirect_response = _get_student_by_usn(request, student_usn)
    if redirect_response:
        return redirect_response
    
    # Get all subjects for this student
    student_subjects = StudentSubject.objects.filter(student=student)
    
    attendance_data = []
    for student_subject in student_subjects:
        attendance_records = Attendance.objects.filter(
            student=student,
            subject=student_subject.subject
        ).order_by('-date')
        
        total_classes = attendance_records.count()
        attended_classes = attendance_records.filter(status=True).count()
        attendance_percentage = round((attended_classes / total_classes * 100), 2) if total_classes > 0 else 0
        
        attendance_data.append({
            'subject': student_subject.subject,
            'total_classes': total_classes,
            'attended_classes': attended_classes,
            'attendance_percentage': attendance_percentage,
            'records': attendance_records
        })
    
    context = {
        'student': student,
        'attendance_data': attendance_data,
    }
    
    return render(request, 'students/attendance.html', context)


@login_required
def student_marks_list(request, student_usn):
    """
    View student marks for all subjects
    """
    # Get student and check access permissions
    student, redirect_response = _get_student_by_usn(request, student_usn)
    if redirect_response:
        return redirect_response
    
    # Get all subjects for this student with marks
    student_subjects = StudentSubject.objects.filter(student=student)
    
    marks_data = []
    for student_subject in student_subjects:
        marks = student_subject.marks_set.all().order_by('name')
        cie_score = student_subject.get_cie()
        attendance_percentage = student_subject.get_attendance()
        
        marks_data.append({
            'subject': student_subject.subject,
            'student_subject': student_subject,
            'marks': marks,
            'cie_score': cie_score,
            'attendance_percentage': attendance_percentage,
        })
    
    context = {
        'student': student,
        'marks_data': marks_data,
    }
    
    return render(request, 'students/marks.html', context)


@login_required
def student_timetable(request, class_id):
    """
    View timetable for student's class (weekly view)
    """
    # Check if user is a student
    is_student, redirect_response = _check_student_access(request)
    if not is_student:
        return redirect_response
    
    # Get student profile
    student = request.user.student
    
    # Check if the class belongs to the student
    if student.class_id.id != class_id:
        messages.error(request, _('Access denied. You can only view your own class timetable.'))
        return redirect('students:student_dashboard')
    
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Get all assignments for this class
    assignments = Assign.objects.filter(class_id=class_obj)
    
    # Parse week_start (YYYY-MM-DD). Default to current date's Monday
    week_start_str = request.GET.get('week_start')
    try:
        base_date = datetime.strptime(week_start_str, "%Y-%m-%d").date() if week_start_str else date.today()
    except ValueError:
        base_date = date.today()

    # Compute Monday as start of the week
    monday_start = base_date - timedelta(days=base_date.weekday())

    # Create display week days (Monday to Saturday) with dates
    days = [day[0] for day in DAYS_OF_WEEK]
    day_to_date = {}
    for idx, day_name in enumerate(days):
        day_date = monday_start + timedelta(days=idx)
        day_to_date[day_name] = day_date.strftime('%Y-%m-%d')

    # Previous/Next week navigation
    prev_week_start = (monday_start - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week_start = (monday_start + timedelta(days=7)).strftime('%Y-%m-%d')

    # Create timetable matrix using constants
    time_slots = [slot[0] for slot in TIME_SLOTS]  # Get time slot names from constants
    
    # Add break and lunch periods using constants
    time_slots_with_breaks = []
    for slot in time_slots:
        time_slots_with_breaks.append(slot)
        if slot == '9:30 - 10:30':
            time_slots_with_breaks.append(BREAK_PERIOD)
        elif slot == '12:40 - 1:30':
            time_slots_with_breaks.append(LUNCH_PERIOD)
    
    time_slots = time_slots_with_breaks
    
    # Initialize timetable matrix
    timetable = {}
    for day in days:
        timetable[day] = {}
        for slot in time_slots:
            timetable[day][slot] = None
    
    # Fill timetable with assignments
    for assignment in assignments:
        assign_times = AssignTime.objects.filter(assign=assignment)
        for assign_time in assign_times:
            if assign_time.day in timetable and assign_time.period in timetable[assign_time.day]:
                timetable[assign_time.day][assign_time.period] = {
                    'subject': assignment.subject,
                    'teacher': assignment.teacher,
                    'assignment': assignment
                }
    
    context = {
        'student': student,
        'class_obj': class_obj,
        'timetable': timetable,
        'days': days,
        'day_to_date': day_to_date,
        'time_slots': time_slots,
        'week_start': monday_start.strftime('%Y-%m-%d'),
        'prev_week_start': prev_week_start,
        'next_week_start': next_week_start,
    }
    
    return render(request, 'students/timetable.html', context)