from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from students.models import Student, Attendance
from teachers.models import Assign
from utils.constant import (
    DAYS_OF_WEEK, TIME_SLOTS, BREAK_PERIOD, LUNCH_PERIOD,
    TIMETABLE_TIME_SLOTS,
    ATTENDANCE_MIN_PERCENTAGE, ATTENDANCE_CALCULATION_BASE
)
from datetime import datetime, timedelta, date
import math


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
    View student attendance for all subjects in their class (class-based attendance)
    """
    # Get student and check access permissions
    student, redirect_response = _get_student_by_usn(request, student_usn)
    if redirect_response:
        return redirect_response
    
    # Get student's class
    student_class = student.class_id

    # Get all subjects assigned to this class through Assign model
    from teachers.models import Assign
    class_assignments = Assign.objects.filter(class_id=student_class).select_related('subject', 'teacher')

    # Filters for academic year and semester
    year = request.GET.get('academic_year', '')
    sem = request.GET.get('semester', '')

    # Default to current if not provided
    from utils.date_utils import determine_semester, determine_academic_year_start
    today = date.today()
    if not year:
        year = determine_academic_year_start(today)
    if not sem:
        sem = str(determine_semester(today))

    # Apply filters
    if year:
        class_assignments = class_assignments.filter(academic_year__icontains=year)
    if sem and sem.isdigit():
        class_assignments = class_assignments.filter(semester=int(sem))
    
    attendance_data = []
    for assignment in class_assignments:
        subject = assignment.subject
        
        # Get attendance records for this student and subject
        attendance_records = Attendance.objects.filter(
            student=student,
            subject=subject
        ).order_by('-date')
        
        total_classes = attendance_records.count()
        attended_classes = attendance_records.filter(status=True).count()
        attendance_percentage = round((attended_classes / total_classes * 100), 2) if total_classes > 0 else 0
        
        # Calculate classes to attend for 75% attendance
        classes_to_attend = 0
        if total_classes > 0:
            from utils.constant import ATTENDANCE_MIN_PERCENTAGE, ATTENDANCE_CALCULATION_BASE
            import math
            classes_to_attend = math.ceil((ATTENDANCE_MIN_PERCENTAGE * total_classes - attended_classes) / ATTENDANCE_CALCULATION_BASE)
            if classes_to_attend < 0:
                classes_to_attend = 0
        
        attendance_data.append({
            'subject': subject,
            'teacher': assignment.teacher,
            'assignment': assignment,
            'total_classes': total_classes,
            'attended_classes': attended_classes,
            'attendance_percentage': attendance_percentage,
            'classes_to_attend': classes_to_attend,
            'records': attendance_records
        })
    
    # Build filter options for dropdowns
    academic_year_strings = (
        Assign.objects
        .filter(class_id=student_class)
        .values_list('academic_year', flat=True)
        .distinct()
    )
    years_set = set()
    for year_str in academic_year_strings:
        import re
        years_found = re.findall(r'\d{4}', str(year_str))
        years_set.update(years_found)
    academic_years = sorted(list(years_set), reverse=True)

    available_semesters = sorted(list(
        Assign.objects
        .filter(class_id=student_class)
        .values_list('semester', flat=True)
        .distinct()
    ))

    context = {
        'student': student,
        'student_class': student_class,
        'attendance_data': attendance_data,
        'academic_years': academic_years,
        'available_semesters': available_semesters,
        'selected_year': year,
        'selected_semester': sem,
    }
    
    return render(request, 'students/attendance.html', context)


@login_required
def student_attendance_detail(request, student_usn, subject_id):
    """
    View detailed attendance for a specific subject in student's class
    """
    # Get student and check access permissions
    student, redirect_response = _get_student_by_usn(request, student_usn)
    if redirect_response:
        return redirect_response
    
    # Get student's class
    student_class = student.class_id
    
    # Get the subject and its assignment
    from admins.models import Subject
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Check if this subject is assigned to student's class
    try:
        assignment = Assign.objects.get(
            class_id=student_class,
            subject=subject
        ).select_related('teacher')
    except Assign.DoesNotExist:
        messages.error(request, _('This subject is not assigned to your class.'))
        return redirect('students:attendance', student_usn=student_usn)
    
    # Get attendance records for this subject
    attendance_records = Attendance.objects.filter(
        student=student,
        subject=subject
    ).select_related('attendanceclass').order_by('-date')
    
    # Calculate statistics
    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(status=True).count()
    absent_classes = total_classes - attended_classes
    attendance_percentage = round((attended_classes / total_classes * 100), 2) if total_classes > 0 else 0
    
    # Calculate classes to attend for 75% attendance
    classes_to_attend = 0
    if total_classes > 0:
        classes_to_attend = math.ceil((ATTENDANCE_MIN_PERCENTAGE * total_classes - attended_classes) / ATTENDANCE_CALCULATION_BASE)
        if classes_to_attend < 0:
            classes_to_attend = 0
    
    # Group attendance by month for better visualization
    from collections import defaultdict
    monthly_attendance = defaultdict(list)
    for record in attendance_records:
        month_key = record.date.strftime('%Y-%m')
        monthly_attendance[month_key].append(record)
    
    # Sort months in descending order
    monthly_attendance = dict(sorted(monthly_attendance.items(), reverse=True))
    
    context = {
        'student': student,
        'student_class': student_class,
        'subject': subject,
        'teacher': assignment.teacher,
        'attendance_records': attendance_records,
        'monthly_attendance': monthly_attendance,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'absent_classes': absent_classes,
        'attendance_percentage': attendance_percentage,
        'classes_to_attend': classes_to_attend,
        'is_attendance_low': attendance_percentage < 75,
    }
    
    return render(request, 'students/attendance_detail.html', context)

@login_required 
def student_attendance_detail(request, student_usn, subject_id):
    """
    View detailed attendance for a specific subject in student's class
    """
    # Get student and check access permissions
    student, redirect_response = _get_student_by_usn(request, student_usn)
    if redirect_response:
        return redirect_response
    
    # Get the subject
    from admins.models import Subject
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Check if this subject is assigned to student's class
    from teachers.models import Assign
    try:
        assignment = Assign.objects.get(class_id=student.class_id, subject=subject)
    except Assign.DoesNotExist:
        messages.error(request, _('This subject is not assigned to your class.'))
        return redirect('students:attendance', student_usn=student_usn)
    
    # Get attendance records for this subject
    attendance_records = Attendance.objects.filter(
        student=student,
        subject=subject
    ).select_related('attendanceclass').order_by('-date')
    
    # Calculate statistics
    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(status=True).count()
    absent_classes = total_classes - attended_classes
    attendance_percentage = round((attended_classes / total_classes * 100), 2) if total_classes > 0 else 0
    
    # Calculate classes to attend for 75% attendance
    from utils.constant import ATTENDANCE_MIN_PERCENTAGE, ATTENDANCE_CALCULATION_BASE
    import math
    classes_to_attend = 0
    if total_classes > 0:
        classes_to_attend = math.ceil((ATTENDANCE_MIN_PERCENTAGE * total_classes - attended_classes) / ATTENDANCE_CALCULATION_BASE)
        if classes_to_attend < 0:
            classes_to_attend = 0
    
    # Group attendance by month for better visualization
    from collections import defaultdict
    monthly_attendance = defaultdict(list)
    for record in attendance_records:
        month_key = record.date.strftime('%Y-%m')
        monthly_attendance[month_key].append(record)
    
    # Sort months in descending order
    monthly_attendance = dict(sorted(monthly_attendance.items(), reverse=True))
    
    context = {
        'student': student,
        'subject': subject,
        'assignment': assignment,
        'teacher': assignment.teacher,
        'student_class': student.class_id,
        'attendance_records': attendance_records,
        'monthly_attendance': monthly_attendance,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'absent_classes': absent_classes,
        'attendance_percentage': attendance_percentage,
        'classes_to_attend': classes_to_attend,
        'is_attendance_low': attendance_percentage < 75,
    }
    
    return render(request, 'students/attendance_detail.html', context)


@login_required
def student_marks_list(request, student_usn):
    """
    View student marks for all subjects in their class
    """
    # Get student and check access permissions
    student, redirect_response = _get_student_by_usn(request, student_usn)
    if redirect_response:
        return redirect_response
    
    # Get student's class
    student_class = student.class_id
    
    # Get all subjects assigned to this class
    class_assignments = Assign.objects.filter(
        class_id=student_class
    ).select_related('subject', 'teacher')

    # Filters for academic year and semester
    year = request.GET.get('academic_year', '')
    sem = request.GET.get('semester', '')

    # Default to current if not provided
    from utils.date_utils import determine_semester, determine_academic_year_start
    today = date.today()
    if not year:
        year = determine_academic_year_start(today)
    if not sem:
        sem = str(determine_semester(today))

    # Apply filters if valid
    if year:
        class_assignments = class_assignments.filter(academic_year__icontains=year)
    if sem and sem.isdigit():
        class_assignments = class_assignments.filter(semester=int(sem))
    
    marks_data = []
    for assignment in class_assignments:
        # Get marks for this student and subject
        from teachers.models import Marks
        marks_qs = Marks.objects.filter(
            student_subject__student=student,
            student_subject__subject=assignment.subject,
        )
        # Lọc theo bộ lọc người dùng chọn (năm/kỳ)
        if year:
            marks_qs = marks_qs.filter(academic_year__icontains=year)
        if sem and sem.isdigit():
            marks_qs = marks_qs.filter(semester=int(sem))
        marks = marks_qs.order_by('name')
        
        # Get attendance percentage
        attendance_records = Attendance.objects.filter(
            student=student,
            subject=assignment.subject
        )
        total_classes = attendance_records.count()
        attended_classes = attendance_records.filter(status=True).count()
        attendance_percentage = round((attended_classes / total_classes * 100), 2) if total_classes > 0 else 0
        
        # Calculate CIE
        from utils.constant import CIE_CALCULATION_LIMIT, CIE_DIVISOR
        marks_list = [mark.marks1 for mark in marks]
        cie_score = math.ceil(sum(marks_list[:CIE_CALCULATION_LIMIT]) / CIE_DIVISOR) if marks_list else 0
        
        marks_data.append({
            'subject': assignment.subject,
            'teacher': assignment.teacher,
            'marks': marks,
            'cie_score': cie_score,
            'attendance_percentage': attendance_percentage,
        })
    
    # Build filter options
    # Extract available years (from academic_year strings)
    academic_year_strings = (
        Assign.objects
        .filter(class_id=student_class)
        .values_list('academic_year', flat=True)
        .distinct()
    )
    years_set = set()
    for year_str in academic_year_strings:
        import re
        years_found = re.findall(r'\d{4}', str(year_str))
        years_set.update(years_found)
    academic_years = sorted(list(years_set), reverse=True)

    available_semesters = sorted(list(
        Assign.objects
        .filter(class_id=student_class)
        .values_list('semester', flat=True)
        .distinct()
    ))

    context = {
        'student': student,
        'student_class': student_class,
        'marks_data': marks_data,
        'academic_years': academic_years,
        'available_semesters': available_semesters,
        'selected_year': year,
        'selected_semester': sem,
    }
    
    return render(request, 'students/marks.html', context)


@login_required
def student_timetable(request, class_id):
    """
    View timetable for student's class (weekly view)
    """
    # Get student and check access permissions
    student = request.user.student
    if student.class_id.id != class_id:
        messages.error(request, _('Access denied. You can only view your own class timetable.'))
        return redirect('students:student_dashboard')
    
    # Import models needed for timetable
    from admins.models import Class
    from teachers.models import AssignTime
    
    # Get class and its assignments
    class_obj = get_object_or_404(Class, id=class_id)
    assignments = Assign.objects.filter(class_id=class_obj)

    # Filters for academic year and semester
    year = request.GET.get('academic_year')
    sem = request.GET.get('semester')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Get current academic year/semester if not provided
    from utils.date_utils import determine_semester, determine_academic_year_start
    today = date.today()
    if not year:
        year = determine_academic_year_start(today)
    if not sem:
        sem = str(determine_semester(today))

    # Get date range from semester if not explicitly provided
    if not (start_date and end_date) and year and sem and sem.isdigit():
        from utils.date_utils import get_semester_date_range
        try:
            start, end = get_semester_date_range(year, int(sem))
            # Convert to string for template
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")
        except (ValueError, IndexError):
            start = end = None
    else:
        # Parse explicit date range
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        except ValueError:
            start = end = None

    # Apply filters
    if year:
        assignments = assignments.filter(academic_year__icontains=year)
    if sem and sem.isdigit():
        assignments = assignments.filter(semester=int(sem))

    # Get available academic years for filter
    year_options = (
        Assign.objects
        .filter(class_id=class_obj)
        .values_list('academic_year', flat=True)
        .distinct()
        .order_by('academic_year')
    )


    
    # Get week dates
    week_start_str = request.GET.get('week_start')
    try:
        base_date = datetime.strptime(week_start_str, "%Y-%m-%d").date() if week_start_str else date.today()
    except ValueError:
        base_date = date.today()
    
    # Get Monday and create day-to-date mapping
    monday_start = base_date - timedelta(days=base_date.weekday())
    days = [day[0] for day in DAYS_OF_WEEK]
    day_to_date = {
        day_name: (monday_start + timedelta(days=idx)).strftime('%Y-%m-%d')
        for idx, day_name in enumerate(days)
    }
    
    # Navigation dates
    prev_week_start = (monday_start - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week_start = (monday_start + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Create time slots with breaks
    time_slots = [slot[0] for slot in TIME_SLOTS]
    time_slots_with_breaks = []
    for slot in time_slots:
        time_slots_with_breaks.append(slot)
        if slot == '9:30 - 10:30':
            time_slots_with_breaks.append(BREAK_PERIOD)
        elif slot == '12:40 - 1:30':
            time_slots_with_breaks.append(LUNCH_PERIOD)
    
    # Initialize and fill timetable
    timetable = {day: {slot: None for slot in time_slots_with_breaks} for day in days}
    
    # Convert day names to dates for the current week
    day_dates = {
        day: datetime.strptime(day_to_date[day], "%Y-%m-%d").date()
        for day in days
    }
    
    for assignment in assignments:
        assign_times = AssignTime.objects.filter(assign=assignment)
        
        # Filter by date range if provided
        if start and end:
            assign_times = assign_times.filter(day__in=[
                day for day, date in day_dates.items()
                if start <= date <= end
            ])
            
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
        'time_slots': time_slots_with_breaks,
        'week_start': monday_start.strftime('%Y-%m-%d'),
        'prev_week_start': prev_week_start,
        'next_week_start': next_week_start,
        'academic_year': year,
        'semester': sem,
        'year_options': list(year_options),
        'today': today.strftime('%Y-%m-%d'),
        'start_date': start_date if start_date else '',
        'end_date': end_date if end_date else '',
    }
    
    return render(request, 'students/timetable.html', context)