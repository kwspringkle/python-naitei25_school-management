from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.http import Http404
from admins.models import User, Dept, Subject, Class
from teachers.models import Teacher, Assign, Marks, AttendanceClass
from students.models import Student, StudentSubject, Attendance
from utils.constant import TEST_NAME_CHOICES, FIRST_CHOICE_INDEX, ATTENDANCE_STANDARD, CIE_STANDARD, DEFAULT_ATTENDANCE_STATUS
import uuid
from datetime import date
from django.test.utils import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class ReportViewsTestCase(TestCase):
    def setUp(self):
        # Thiết lập dữ liệu cơ bản cho các test
        self.client = Client()
        self.user = User.objects.create_user(
            username='testteacher', password='testpass123'
        )
        self.dept = Dept.objects.create(id='CS', name='Computer Science')
        self.teacher = Teacher.objects.create(
            user=self.user,
            id='T001',
            dept=self.dept,
            name='Test Teacher',
            sex='M',
            DOB='1980-01-01',
            address='Test Address',
            phone='1234567890'
        )
        self.subject = Subject.objects.create(
            dept=self.dept,
            id='CS101',
            name='Introduction to Programming',
            shortname='IntroProg'
        )
        self.class_obj = Class.objects.create(
            id='C001',
            dept=self.dept,
            section='A',
            sem=1,
            is_active=True
        )
        self.assign = Assign.objects.create(
            class_id=self.class_obj,
            subject=self.subject,
            teacher=self.teacher
        )
        self.student = Student.objects.create(
            USN='S001',
            class_id=self.class_obj,
            name='Test Student',
            sex='M',
            DOB='2000-01-01',
            address='Student Address',
            phone='0987654321'
        )
        self.student_subject = StudentSubject.objects.create(
            student=self.student,
            subject=self.subject
        )
        self.client.login(username='testteacher', password='testpass123')

    def test_t_report(self):
        """Kiểm tra thống kê trong view t_report"""
        Marks.objects.create(
            student_subject=self.student_subject,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            marks1=30
        )
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            attendanceclass=AttendanceClass.objects.create(
                assign=self.assign,
                date=date.today(),
                status=DEFAULT_ATTENDANCE_STATUS
            ),
            date=date.today(),
            status=True
        )
        response = self.client.get(
            reverse('t_report', args=(self.assign.id,))
        )
        context = response.context
        self.assertEqual(context['good_attendance_count'], 1)
        self.assertEqual(context['good_cie_count'], 1)
        self.assertEqual(context['need_support_count'], 0)
        self.assertEqual(context['pass_rate'], 100)

    def test_t_report_no_data(self):
        """Kiểm tra t_report khi không có dữ liệu điểm danh hoặc điểm số"""
        response = self.client.get(
            reverse('t_report', args=(self.assign.id,))
        )
        context = response.context
        self.assertEqual(context['good_attendance_count'], 0)
        self.assertEqual(context['good_cie_count'], 0)
        self.assertEqual(context['need_support_count'], 0)
        self.assertEqual(context['pass_rate'], 0)

    def test_t_report_unauthenticated(self):
        """Kiểm tra t_report khi chưa đăng nhập"""
        self.client.logout()
        response = self.client.get(
            reverse('t_report', args=(self.assign.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_t_report_invalid_assign(self):
        """Kiểm tra t_report với assign ID không tồn tại"""
        invalid_assign_id = 99999
        with self.assertRaises(Http404):
            self.client.get(
                reverse('t_report', args=(invalid_assign_id,))
            )
            