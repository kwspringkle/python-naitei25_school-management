from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from admins.models import User, Dept, Subject, Class
from teachers.models import Teacher, Assign, AssignTime, Marks, AttendanceClass
from students.models import Student, StudentSubject, Attendance
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from utils.constant import TEST_NAME_CHOICES, FIRST_CHOICE_INDEX, ATTENDANCE_MIN_PERCENTAGE, ATTENDANCE_CALCULATION_BASE, DAYS_OF_WEEK, TIME_SLOTS, BREAK_PERIOD, LUNCH_PERIOD, CIE_DIVISOR
import math
from collections import defaultdict

class StudentViewsTests(TestCase):
    """Tests cho các view liên quan đến học sinh"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student1', password='testpass123')
        self.dept = Dept.objects.create(id='D001', name='Computer Science')
        self.teacher = Teacher.objects.create(id='T001', name='Test Teacher', dept=self.dept, DOB='2000-01-01')
        self.class_obj = Class.objects.create(id='C001', dept=self.dept, section='A', sem=1)
        self.subject = Subject.objects.create(dept=self.dept, id='MATH101', name='Mathematics')
        self.student = Student.objects.create(user=self.user, USN='STU001', name='Student 1', class_id=self.class_obj, DOB='2000-01-01')
        self.assign = Assign.objects.create(teacher=self.teacher, class_id=self.class_obj, subject=self.subject)
        self.student_subject = StudentSubject.objects.create(student=self.student, subject=self.subject)
        self.marks = Marks.objects.create(student_subject=self.student_subject, name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0], marks1=30)
        self.attendance_class = AttendanceClass.objects.create(
            assign=self.assign, date=timezone.now().date()
        )
        self.attendance = Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            attendanceclass=self.attendance_class,
            date=timezone.now().date(),
            status=True
        )
        self.assign_time = AssignTime.objects.create(assign=self.assign, period=TIME_SLOTS[0][0], day=DAYS_OF_WEEK[0][0])

    def test_student_dashboard_authenticated_student(self):
        """Test truy cập dashboard với học sinh đã xác thực"""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:student_dashboard'))
        self.assertTemplateUsed(response, 'students/dashboard.html')
        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['user'], self.user)

    def test_student_dashboard_non_student(self):
        """Test truy cập dashboard với người dùng không phải học sinh"""
        non_student_user = User.objects.create_user(username='teacher1', password='testpass123')
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('students:student_dashboard'))
        self.assertRedirects(response, reverse('unified_login'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), str(_('Please login with student credentials to access this page.')))

    def test_student_attendance_authorized_access(self):
        """Test hiển thị điểm danh cho tất cả môn học của học sinh"""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:attendance', args=(self.student.USN,)))
        self.assertTemplateUsed(response, 'students/attendance.html')
        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['student_class'], self.class_obj)
        attendance_data = response.context['attendance_data']
        self.assertEqual(len(attendance_data), 1)
        self.assertEqual(attendance_data[0]['subject'], self.subject)
        self.assertEqual(attendance_data[0]['teacher'], self.teacher)
        self.assertEqual(attendance_data[0]['total_classes'], 1)
        self.assertEqual(attendance_data[0]['attended_classes'], 1)
        self.assertEqual(attendance_data[0]['attendance_percentage'], 100.0)
        self.assertEqual(attendance_data[0]['classes_to_attend'], 0)
        self.assertEqual(len(attendance_data[0]['records']), 1)
        self.assertEqual(attendance_data[0]['records'][0], self.attendance)

    def test_student_attendance_unauthorized_access(self):
        """Test truy cập điểm danh với học sinh không có quyền"""
        other_user = User.objects.create_user(username='student2', password='testpass123')
        other_student = Student.objects.create(user=other_user, USN='STU002', name='Student 2', class_id=self.class_obj, DOB='2000-01-01')
        self.client.login(username='student2', password='testpass123')
        response = self.client.get(reverse('students:attendance', args=(self.student.USN,)))
        self.assertRedirects(response, reverse('students:student_dashboard'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), str(_('Access denied. You can only view your own data.')))

    def test_student_attendance_detail_authorized_access(self):
        """Test hiển thị chi tiết điểm danh cho một môn học"""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:attendance_detail', args=(self.student.USN, self.subject.id)))
        self.assertTemplateUsed(response, 'students/attendance_detail.html')
        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['subject'], self.subject)
        self.assertEqual(response.context['teacher'], self.teacher)
        self.assertEqual(response.context['student_class'], self.class_obj)
        self.assertEqual(response.context['total_classes'], 1)
        self.assertEqual(response.context['attended_classes'], 1)
        self.assertEqual(response.context['absent_classes'], 0)
        self.assertEqual(response.context['attendance_percentage'], 100.0)
        self.assertEqual(response.context['classes_to_attend'], 0)
        self.assertFalse(response.context['is_attendance_low'])
        monthly_attendance = response.context['monthly_attendance']
        month_key = self.attendance.date.strftime('%Y-%m')
        self.assertEqual(len(monthly_attendance), 1)
        self.assertEqual(monthly_attendance[month_key][0], self.attendance)

    def test_student_attendance_detail_unauthorized_subject(self):
        """Test truy cập chi tiết điểm danh với môn học không thuộc lớp của học sinh"""
        other_subject = Subject.objects.create(dept=self.dept, id='PHY101', name='Physics')
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:attendance_detail', args=(self.student.USN, other_subject.id)))
        self.assertRedirects(response, reverse('students:attendance', args=(self.student.USN,)))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), str(_('This subject is not assigned to your class.')))

    def test_student_marks_list_authorized_access(self):
        """Test hiển thị danh sách điểm số cho tất cả môn học của học sinh"""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:marks_list', args=(self.student.USN,)))
        self.assertTemplateUsed(response, 'students/marks.html')
        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['student_class'], self.class_obj)
        marks_data = response.context['marks_data']
        self.assertEqual(len(marks_data), 1)
        self.assertEqual(marks_data[0]['subject'], self.subject)
        self.assertEqual(marks_data[0]['teacher'], self.teacher)
        self.assertEqual(marks_data[0]['marks'][0], self.marks)
        self.assertEqual(marks_data[0]['attendance_percentage'], 100.0)
        self.assertEqual(marks_data[0]['cie_score'], math.ceil(30 / CIE_DIVISOR))  # 30 / 2 = 15

    def test_student_marks_list_unauthorized_access(self):
        """Test truy cập danh sách điểm số với học sinh không có quyền"""
        other_user = User.objects.create_user(username='student2', password='testpass123')
        other_student = Student.objects.create(user=other_user, USN='STU002', name='Student 2', class_id=self.class_obj, DOB='2000-01-01')
        self.client.login(username='student2', password='testpass123')
        response = self.client.get(reverse('students:marks_list', args=(self.student.USN,)))
        self.assertRedirects(response, reverse('students:student_dashboard'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), str(_('Access denied. You can only view your own data.')))

    def test_student_timetable_authorized_access(self):
        """Test hiển thị thời khóa biểu của lớp học sinh"""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:timetable', args=(self.class_obj.id,)))
        self.assertTemplateUsed(response, 'students/timetable.html')
        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['class_obj'], self.class_obj)
        timetable = response.context['timetable']
        self.assertEqual(timetable[DAYS_OF_WEEK[0][0]][TIME_SLOTS[0][0]]['subject'], self.subject)
        self.assertEqual(timetable[DAYS_OF_WEEK[0][0]][TIME_SLOTS[0][0]]['teacher'], self.teacher)
        time_slots = response.context['time_slots']
        self.assertIn(BREAK_PERIOD, time_slots)
        self.assertIn(LUNCH_PERIOD, time_slots)
        self.assertEqual(len(time_slots), 11)  # 9 TIME_SLOTS + Break + Lunch
        self.assertEqual(len(response.context['days']), 6)  # Monday to Saturday
        self.assertEqual(timetable[DAYS_OF_WEEK[0][0]][BREAK_PERIOD], None)
        self.assertEqual(timetable[DAYS_OF_WEEK[0][0]][LUNCH_PERIOD], None)

    def test_student_timetable_unauthorized_access(self):
        """Test truy cập thời khóa biểu của lớp không thuộc học sinh"""
        other_class = Class.objects.create(id='C002', dept=self.dept, section='B', sem=1)
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('students:timetable', args=(other_class.id,)))
        self.assertRedirects(response, reverse('students:student_dashboard'))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), str(_('Access denied. You can only view your own class timetable.')))

    def test_student_timetable_with_week_start(self):
        """Test thời khóa biểu với tham số week_start"""
        self.client.login(username='student1', password='testpass123')
        week_start = (timezone.now().date() - timezone.timedelta(days=timezone.now().date().weekday())).strftime('%Y-%m-%d')
        response = self.client.get(reverse('students:timetable', args=(self.class_obj.id,)), {'week_start': week_start})
        self.assertTemplateUsed(response, 'students/timetable.html')
        self.assertEqual(response.context['week_start'], week_start)
        day_to_date = response.context['day_to_date']
        self.assertEqual(day_to_date[DAYS_OF_WEEK[0][0]], week_start)
        next_week_start = (timezone.datetime.strptime(week_start, '%Y-%m-%d').date() + timezone.timedelta(days=7)).strftime('%Y-%m-%d')
        self.assertEqual(response.context['next_week_start'], next_week_start)
