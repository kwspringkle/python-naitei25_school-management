from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from students.models import Student, StudentSubject, Attendance
from admins.models import Class, Subject
from teachers.models import AssignTime, Assign
from utils.constant import (
    # Dashboard constants
    DASHBOARD_WELCOME_MESSAGE, DASHBOARD_ATTENDANCE_TITLE, DASHBOARD_MARKS_TITLE, DASHBOARD_TIMETABLE_TITLE,
    DASHBOARD_ATTENDANCE_DESCRIPTION, DASHBOARD_MARKS_DESCRIPTION, DASHBOARD_TIMETABLE_DESCRIPTION,
    DASHBOARD_ATTENDANCE_BUTTON, DASHBOARD_MARKS_BUTTON, DASHBOARD_TIMETABLE_BUTTON,
    # Timetable constants
    DAYS_OF_WEEK, TIME_SLOTS, TIMETABLE_TIME_SLOTS,
    TIMETABLE_DAYS_COUNT, TIMETABLE_PERIODS_COUNT, TIMETABLE_DEFAULT_VALUE,
    TIMETABLE_SKIP_PERIODS
)


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
        # Dashboard constants from constant.py
        'welcome_message': DASHBOARD_WELCOME_MESSAGE,
        'attendance_title': DASHBOARD_ATTENDANCE_TITLE,
        'marks_title': DASHBOARD_MARKS_TITLE,
        'timetable_title': DASHBOARD_TIMETABLE_TITLE,
        'attendance_description': DASHBOARD_ATTENDANCE_DESCRIPTION,
        'marks_description': DASHBOARD_MARKS_DESCRIPTION,
        'timetable_description': DASHBOARD_TIMETABLE_DESCRIPTION,
        'attendance_button': DASHBOARD_ATTENDANCE_BUTTON,
        'marks_button': DASHBOARD_MARKS_BUTTON,
        'timetable_button': DASHBOARD_TIMETABLE_BUTTON,
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
    # Check if user is a student and can access this USN
    if not getattr(request.user, 'is_student', False):
        messages.error(request, _('Access denied. Student credentials required.'))
        return redirect('unified_login')
    
    # Get student profile
    student = get_object_or_404(Student, USN=student_usn)
    
    # Check if the logged-in user can access this student's data
    if request.user.student != student:
        messages.error(request, _('Access denied. You can only view your own attendance.'))
        return redirect('students:student_dashboard')
    
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
    # Check if user is a student and can access this USN
    if not getattr(request.user, 'is_student', False):
        messages.error(request, _('Access denied. Student credentials required.'))
        return redirect('unified_login')
    
    # Get student profile
    student = get_object_or_404(Student, USN=student_usn)
    
    # Check if the logged-in user can access this student's data
    if request.user.student != student:
        messages.error(request, _('Access denied. You can only view your own marks.'))
        return redirect('students:student_dashboard')
    
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
    View timetable for student's class
    """
    # Check if user is a student
    if not getattr(request.user, 'is_student', False):
        messages.error(request, _('Access denied. Student credentials required.'))
        return redirect('unified_login')
    
    # Get student profile
    student = request.user.student
    
    # Check if the class belongs to the student
    if student.class_id.id != class_id:
        messages.error(request, _('Access denied. You can only view your own class timetable.'))
        return redirect('students:student_dashboard')
    
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Get all assignments for this class
    assignments = Assign.objects.filter(class_id=class_obj)
    
    # Create timetable matrix
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = [
        '7:30 - 8:30',
        '8:30 - 9:30', 
        '9:30 - 10:30',
        'Break',
        '11:00 - 11:50',
        '11:50 - 12:40',
        '12:40 - 1:30',
        'Lunch',
        '2:30 - 3:30',
        '3:30 - 4:30',
        '4:30 - 5:30',
    ]
    
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
        'time_slots': time_slots,
    }
    
    return render(request, 'students/timetable.html', context)