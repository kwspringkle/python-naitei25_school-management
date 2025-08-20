from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from teachers.models import Teacher
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Teacher, Assign, ExamSession, Marks, AssignTime, AttendanceClass
from students.models import Attendance, StudentSubject
from django.db import transaction

from utils.constant import (
    DAYS_OF_WEEK, TIME_SLOTS, TIMETABLE_TIME_SLOTS,
    TIMETABLE_DAYS_COUNT, TIMETABLE_PERIODS_COUNT, TIMETABLE_DEFAULT_VALUE,
    TIMETABLE_SKIP_PERIODS, TIMETABLE_ACCESS_DENIED_MESSAGE,
    FREE_TEACHERS_NO_AVAILABLE_TEACHERS_MESSAGE, FREE_TEACHERS_NO_SUBJECT_KNOWLEDGE_MESSAGE,
    TEACHER_FILTER_DISTINCT_ENABLED, TEACHER_FILTER_BY_CLASS, TEACHER_FILTER_BY_SUBJECT_KNOWLEDGE, DATE_FORMAT,
    ATTENDANCE_STANDARD, CIE_STANDARD,TEST_NAME_CHOICES
)


def _calculate_attendance_statistics(attendance_queryset):
    """
    Private function to calculate attendance statistics from an attendance queryset.
    
    Args:
        attendance_queryset: QuerySet of Attendance objects
        
    Returns:
        dict: Dictionary containing attendance statistics with keys:
            - total_students: Total number of students
            - present_students: Number of present students
            - absent_students: Number of absent students  
            - attendance_percentage: Attendance percentage (rounded to 1 decimal)
    """
    total_students = attendance_queryset.count()
    present_students = attendance_queryset.filter(status=True).count()
    absent_students = total_students - present_students
    attendance_percentage = round(
        (present_students / total_students * 100), 1
    ) if total_students > 0 else 0
    
    return {
        'total_students': total_students,
        'present_students': present_students,
        'absent_students': absent_students,
        'attendance_percentage': attendance_percentage,
    }


@login_required
def teacher_dashboard(request):
    """
    Teacher dashboard view - only accessible to authenticated teachers
    """
    # Check if user is a teacher
    if not getattr(request.user, 'is_teacher', False):
        messages.error(request, _(
            'Access denied. Teacher credentials required.'))
        return redirect('unified_login')

    # Get teacher profile
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, _(
            'Teacher profile not found. Please contact administrator.'))
        return redirect('unified_logout')

    context = {
        'teacher': teacher,
        'user': request.user,
    }

    return render(request, 't_homepage.html', context)


def teacher_logout(request):
    """
    Teacher logout view - redirects to unified logout
    """
    return redirect('unified_logout')


# Legacy view for backward compatibility
@login_required
def index(request):
    """
    Legacy teacher index view - redirects to new dashboard
    """
    return redirect('teacher_dashboard')

# Teacher Views
# Hiển thị thông tin lớp học hoặc các lựa chọn liên quan đến giáo viên.


@login_required
def t_clas(request, teacher_id, choice):
    teacher1 = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 't_clas.html', {'teacher1': teacher1, 'choice': choice})

# Hiển thị danh sách các phiên thi (ExamSession) của một assignment (môn học/lớp/giáo viên).


@login_required
def t_marks_list(request, assign_id):
    assignment = get_object_or_404(Assign, id=assign_id)
    
    # Kiểm tra xem user hiện tại có phải là giáo viên của assignment này không
    if assignment.teacher.user != request.user:
        messages.error(request, 'Bạn không có quyền truy cập assignment này!')
        return redirect('teacher_dashboard')
    
    exam_sessions_list = ExamSession.objects.filter(assign=assignment)
    
    # Xử lý tạo bài kiểm tra mới
    if request.method == 'POST' and 'create_exam' in request.POST:
        exam_name = request.POST.get('exam_name')
        if exam_name:
            try:
                new_exam, created = ExamSession.objects.get_or_create(
                    assign=assignment,
                    name=exam_name,
                    defaults={'status': False}
                )
                if created:
                    messages.success(request, _('Exam "%(exam_name)s" was created successfully!') % {'exam_name': exam_name})
                else:
                    messages.warning(request, _('Exam "%(exam_name)s" already exists!') % {'exam_name': exam_name})
            except Exception as e:
                messages.error(request, _('Error while creating exam: %(error)s') % {'error': str(e)})
        else:
            messages.error(request, _('Please enter the exam name!'))
    
        return redirect('t_marks_list', assign_id=assign_id)
    
    context = {
        'assignment': assignment,
        'm_list': exam_sessions_list,
        'exam_names': TEST_NAME_CHOICES
    }
    return render(request, 't_marks_list.html', context)

# Hiển thị form nhập điểm cho các học sinh đang học môn học này trong lớp.
# Chỉ hiển thị học sinh đã đăng ký môn học (StudentSubject).


@login_required()
def t_marks_entry(request, marks_c_id):
    with transaction.atomic():
        exam_session = get_object_or_404(ExamSession, id=marks_c_id)
        assignment = exam_session.assign
        subject = assignment.subject
        class_obj = assignment.class_id

        # Lấy các học sinh đang học môn này trong lớp này
        students_in_subject = StudentSubject.objects.filter(
            subject=subject,
            student__class_id=class_obj
        ).select_related('student')

        context = {
            'ass': assignment,
            'c': class_obj,
            'mc': exam_session,
            'students_in_subject': students_in_subject,
        }
        return render(request, 't_marks_entry.html', context)

# Xử lý dữ liệu điểm số được nhập từ form.
# Lưu điểm cho từng học sinh vào database.
# Đánh dấu trạng thái phiên thi là đã hoàn thành.


@login_required()
def marks_confirm(request, marks_c_id):
    with transaction.atomic():
        exam_session = get_object_or_404(ExamSession, id=marks_c_id)
        assignment = exam_session.assign
        subject = assignment.subject
        class_object = assignment.class_id

        students_in_subject = StudentSubject.objects.filter(
            subject=subject,
            student__class_id=class_object
        ).select_related('student')

        for student_subject in students_in_subject:
            student = student_subject.student
            student_mark = request.POST[student.USN]
            student_subject = StudentSubject.objects.get(
                subject=subject, student=student)
            marks_instance, _ = student_subject.marks_set.get_or_create(
                name=exam_session.name)
            marks_instance.marks1 = student_mark
            marks_instance.save()
        exam_session.status = True
        exam_session.save()

    return HttpResponseRedirect(reverse('t_marks_list', args=(assignment.id,)))

# Hiển thị form để chỉnh sửa điểm của các học sinh đang học môn học này trong lớp.
# Chỉ hiển thị học sinh đã đăng ký môn học (StudentSubject).
# Cho phép giáo viên cập nhật lại điểm số đã nhập.


@login_required()
def edit_marks(request, marks_c_id):
    with transaction.atomic():
        exam_session = get_object_or_404(ExamSession, id=marks_c_id)
        subject = exam_session.assign.subject
        class_object = exam_session.assign.class_id

        # Lấy các StudentSubject của học sinh thuộc lớp này và đăng ký môn này
        students_in_subject = StudentSubject.objects.filter(
            subject=subject,
            student__class_id=class_object
        ).select_related('student')

        marks_list = []
        for student_subject in students_in_subject:
            try:
                marks_instance = student_subject.marks_set.get(
                    name=exam_session.name)
                marks_list.append(marks_instance)
            except Marks.DoesNotExist:
                # Bỏ qua hoặc xử lý trường hợp không có điểm
                pass
        context = {
            'mc': exam_session,
            'm_list': marks_list,
        }
        return render(request, 'edit_marks.html', context)


@login_required()
def t_timetable(request, teacher_id):
    with transaction.atomic():
        # Check if teacher exists
        teacher = get_object_or_404(Teacher, id=teacher_id)

        # Verify the teacher belongs to the authenticated user
        if teacher.user != request.user:
            messages.error(request, _(TIMETABLE_ACCESS_DENIED_MESSAGE))
            return redirect('teacher_dashboard')

        asst = AssignTime.objects.filter(assign__teacher_id=teacher_id)
        class_matrix = [[TIMETABLE_DEFAULT_VALUE for i in range(
            TIMETABLE_PERIODS_COUNT)] for j in range(TIMETABLE_DAYS_COUNT)]

        for i, d in enumerate(DAYS_OF_WEEK):
            t = 0
            for j in range(TIMETABLE_PERIODS_COUNT):
                if j == 0:
                    class_matrix[i][0] = d[0]
                    continue
                if j in TIMETABLE_SKIP_PERIODS:
                    continue
                try:
                    a = asst.get(period=TIME_SLOTS[t][0], day=d[0])
                    class_matrix[i][j] = a
                except AssignTime.DoesNotExist:
                    pass
                t += 1

        context = {
            'class_matrix': class_matrix,
            'time_slots': TIMETABLE_TIME_SLOTS,
        }
        return render(request, 't_timetable.html', context)


@login_required()
def free_teachers(request, asst_id):
    with transaction.atomic():
        # Get the assignment time that needs replacement
        asst = get_object_or_404(AssignTime, id=asst_id)

        # Get the subject that needs to be taught
        required_subject = asst.assign.subject

        # Get unique teachers who teach in the same class (avoid duplicates)
        # Using distinct() because a teacher can have multiple assignments in the same class
        # Example: "phan thanh thắng" teaches 4 subjects in "SOICT : 2 a" class
        # Without distinct(), he would appear 4 times instead of 1
        t_list = Teacher.objects.filter(
            assign__class_id=asst.assign.class_id
        ).distinct()

        ft_list = []
        teachers_without_knowledge = []

        for t in t_list:
            # Get all teaching times for this teacher
            at_list = AssignTime.objects.filter(assign__teacher=t)

            # Check if teacher is free at the required time
            is_busy = any([
                True if at.period == asst.period and at.day == asst.day
                else False for at in at_list
            ])

            # Check if teacher has knowledge of the required subject
            has_subject_knowledge = t.assign_set.filter(
                subject=required_subject).exists()

            if not is_busy:
                if has_subject_knowledge:
                    ft_list.append(t)
                else:
                    teachers_without_knowledge.append(t)

        # Add warning message if no teachers available
        if not ft_list:
            messages.warning(request, _(
                FREE_TEACHERS_NO_AVAILABLE_TEACHERS_MESSAGE))

        return render(request, 'free_teachers.html', {
            'ft_list': ft_list,
            'required_subject': required_subject,
            'assignment_time': asst,
            'teachers_without_knowledge': teachers_without_knowledge,
            'total_teachers_checked': len(t_list),
            'available_teachers_count': len(ft_list)
        })


# Hiển thị danh sách các ngày đã điểm danh và tạo mới danh sách điểm danh theo ngày (nếu cần)
@login_required
def t_class_date(request, assign_id):
    assign = get_object_or_404(Assign, id=assign_id)
    now = timezone.now()
    att_list = assign.attendanceclass_set.all().order_by('-date')
    selected_assc = None
    class_obj = assign.class_id
    has_students = class_obj.student_set.exists()
    students = class_obj.student_set.all() if has_students else []
    
    # Thêm thống kê điểm danh cho mỗi buổi học
    att_list_with_stats = []
    for att_class in att_list:
        attendance_records = Attendance.objects.filter(
            attendanceclass=att_class, 
            subject=assign.subject
        )
        stats = _calculate_attendance_statistics(attendance_records)
        
        att_class.total_students = stats['total_students']
        att_class.present_students = stats['present_students']
        att_class.absent_students = stats['absent_students']
        att_class.attendance_percentage = stats['attendance_percentage']
        att_list_with_stats.append(att_class)

    if request.method == 'POST' and 'create_attendance' in request.POST:
        date_str = request.POST.get('attendance_date')
        try:
            attendance_date = timezone.datetime.strptime(
                date_str, DATE_FORMAT).date()
            if not AttendanceClass.objects.filter(assign=assign, date=attendance_date).exists():
                with transaction.atomic():
                    AttendanceClass.objects.create(
                        assign=assign,
                        date=attendance_date,
                        status=0  # Not Marked
                    )
            selected_assc = AttendanceClass.objects.get(
                assign=assign, date=attendance_date)
        except ValueError:
            messages.error(request, _(
                'Invalid date format. Please use YYYY-MM-DD.'))
            return redirect('t_class_date', assign_id=assign.id)

    elif request.method == 'POST' and 'confirm_attendance' in request.POST:
        assc_id = request.POST.get('assc_id')
        assc = get_object_or_404(AttendanceClass, id=assc_id)
        subject = assign.subject

        with transaction.atomic():
            for student in students:
                status_str = request.POST.get(student.USN)
                status = status_str == 'present'
                attendance_obj, created = Attendance.objects.get_or_create(
                    student=student,
                    subject=subject,
                    attendanceclass=assc,
                    date=assc.date,
                    defaults={'status': status}
                )
                if not created:
                    attendance_obj.status = status
                    attendance_obj.save()
            assc.status = 1  # Marked
            assc.save()
        messages.success(request, _('Attendance successfully recorded.'))
        return HttpResponseRedirect(reverse('t_class_date', args=(assign.id,)))

    elif request.method == 'POST' and 'select_attendance' in request.POST:
        assc_id = request.POST.get('assc_id')
        selected_assc = get_object_or_404(AttendanceClass, id=assc_id)

    # Thêm thông tin chi tiết về lớp học
    class_info = {
        'class_id': class_obj.id,
        'department': class_obj.dept.name,
        'section': class_obj.section,
        'semester': class_obj.sem,
        'total_students': len(students),
        'subject': assign.subject.name,
        'subject_code': assign.subject.id,
        'teacher': assign.teacher.name,
    }

    context = {
        'assign': assign,
        'att_list': att_list_with_stats,
        'today': now.date(),
        'selected_assc': selected_assc,
        'c': class_obj,
        'has_students': has_students,
        'students': students,
        'class_info': class_info,
    }
    return render(request, 't_class_date.html', context)

# Thông tin điểm danh


@login_required
def t_attendance(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assign = assc.assign
    class_obj = assign.class_id
    students = class_obj.student_set.all()
    total_students_in_class = students.count()
    
    # Thêm thông tin chi tiết về lớp học
    class_info = {
        'class_id': class_obj.id,
        'department': class_obj.dept.name,
        'section': class_obj.section,
        'semester': class_obj.sem,
        'total_students': total_students_in_class,
        'subject': assign.subject.name,
        'subject_code': assign.subject.id,
        'teacher': assign.teacher.name,
        'date': assc.date,
    }

    context = {
        'ass': assign,
        'c': class_obj,
        'assc': assc,
        'students': students,
        'total_students_in_class': total_students_in_class,
        'class_info': class_info,
    }
    return render(request, 't_attendance.html', context)

# View xử lý xác nhận điểm danh


@login_required
def confirm(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assign = assc.assign
    subject = assign.subject
    class_obj = assign.class_id
    has_students = class_obj.student_set.exists()  # Check if students exist
    students = class_obj.student_set.all() if has_students else [
    ]  # Fetch students only if needed

    with transaction.atomic():
        for student in students:
            status_str = request.POST.get(student.USN)
            status = status_str == 'present'
            attendance_obj, created = Attendance.objects.get_or_create(
                student=student,
                subject=subject,
                attendanceclass=assc,
                date=assc.date,
                defaults={'status': status}
            )
            if not created:
                attendance_obj.status = status
                attendance_obj.save()
        assc.status = 1  # Marked
        assc.save()

    messages.success(request, _('Attendance successfully recorded.'))
    return HttpResponseRedirect(reverse('t_class_date', args=(assc.assign.id,)))

# View hiển thị giao diện chỉnh sửa điểm danh


@login_required
def edit_att(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assign = assc.assign
    subject = assign.subject
    att_list = Attendance.objects.filter(attendanceclass=assc, subject=subject)
    class_obj = assign.class_id
    
    # Thêm thông tin chi tiết về lớp học và thống kê
    stats = _calculate_attendance_statistics(att_list)
    
    context = {
        'assc': assc,
        'att_list': att_list,
        'assign': assign,
        'class_obj': class_obj,
        'total_students': stats['total_students'],
        'present_students': stats['present_students'],
        'absent_students': stats['absent_students'],
    }
    return render(request, 't_edit_att.html', context)

# View hiển thị danh sách điểm danh


@login_required
def view_att(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assign = assc.assign
    subject = assign.subject
    att_list = Attendance.objects.filter(attendanceclass=assc, subject=subject)
    class_obj = assign.class_id
    
    # Tính toán thống kê điểm danh
    stats = _calculate_attendance_statistics(att_list)
    
    # Thêm thông tin chi tiết về lớp học
    class_info = {
        'class_id': class_obj.id,
        'department': class_obj.dept.name,
        'section': class_obj.section,
        'semester': class_obj.sem,
        'subject': assign.subject.name,
        'subject_code': assign.subject.id,
        'teacher': assign.teacher.name,
        'date': assc.date,
    }
    
    context = {
        'assc': assc,
        'att_list': att_list,
        'assign': assign,
        'total_students': stats['total_students'],
        'present_students': stats['present_students'],
        'absent_students': stats['absent_students'],
        'attendance_percentage': stats['attendance_percentage'],
        'class_info': class_info,
    }
    return render(request, 't_view_att.html', context)

#hiển thị báo cáo học tập của học sinh trong một lớp học cụ thể.

@login_required()
def t_report(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    sc_list = []
    
    # Get class information
    class_obj = ass.class_id
    subject_obj = ass.subject
    
    # Statistics counters
    # Đếm học sinh có điểm danh tốt (≥75%)
    good_attendance_count = 0
    # Đếm học sinh có CIE đạt chuẩn (≥25)
    good_cie_count = 0
    # Đếm học sinh cần hỗ trợ (điểm danh <75% HOẶC CIE <25)
    need_support_count = 0
    
    for stud in class_obj.student_set.all():
        student_subjects = StudentSubject.objects.filter(student=stud, subject=subject_obj)
        if student_subjects.exists():
            # If student is registered for this subject, add to list
            student_subject = student_subjects.first()
            sc_list.append(student_subject)
            
            # Calculate statistics with error handling
            try:
                attendance = student_subject.get_attendance()
            except:
                attendance = 0
                
            try:
                cie = student_subject.get_cie()
            except:
                cie = 0
            
            # Count statistics
            if attendance >= ATTENDANCE_STANDARD:
                good_attendance_count += 1
            if cie >= CIE_STANDARD:
                good_cie_count += 1
            if attendance < ATTENDANCE_STANDARD or cie < CIE_STANDARD:
                need_support_count += 1
    
    # Calculate pass rate
    total_students = len(sc_list)
    pass_rate = 100 if total_students == 0 else round((total_students - need_support_count) / total_students * 100)
    
    context = {
        'sc_list': sc_list,
        'class_obj': class_obj,
        'subject_obj': subject_obj,
        'assignment': ass,
        'good_attendance_count': good_attendance_count,
        'good_cie_count': good_cie_count,
        'need_support_count': need_support_count,
        'pass_rate': pass_rate,
        'ATTENDANCE_STANDARD': ATTENDANCE_STANDARD,
        'CIE_STANDARD': CIE_STANDARD,
        'attendance_success_label': f"≥{ATTENDANCE_STANDARD}%",
        'attendance_danger_label': f"<{ATTENDANCE_STANDARD}%",
        'cie_success_label': f"≥{CIE_STANDARD}",
        'cie_danger_label': f"<{CIE_STANDARD}",
    }
    
    return render(request, 't_report.html', context)
