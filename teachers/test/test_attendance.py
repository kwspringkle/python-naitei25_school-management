from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.http import Http404
from admins.models import User, Dept, Subject, Class
from teachers.models import Teacher, Assign, AttendanceClass
from students.models import Student, StudentSubject, Attendance
from utils.constant import DATE_FORMAT, DEFAULT_ATTENDANCE_STATUS
import uuid
from datetime import date
from django.test.utils import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class AttendanceViewsTestCase(TestCase):
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

    def test_t_class_date_create(self):
        """Kiểm tra tạo buổi điểm danh mới và thống kê trong view t_class_date"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            attendanceclass=attendance_class,
            date=date.today(),
            status=True
        )
        student2 = Student.objects.create(
            USN='S002',
            class_id=self.class_obj,
            name='Test Student 2',
            sex='F',
            DOB='2000-01-01'
        )
        Attendance.objects.create(
            student=student2,
            subject=self.subject,
            attendanceclass=attendance_class,
            date=date.today(),
            status=False
        )
        post_data = {
            'create_attendance': 'true',
            'attendance_date': timezone.now().strftime(DATE_FORMAT)
        }
        response = self.client.post(
            reverse('t_class_date', args=(self.assign.id,)),
            post_data
        )
        self.assertTrue(AttendanceClass.objects.filter(
            assign=self.assign,
            date=timezone.now().date()
        ).exists())
        response = self.client.get(
            reverse('t_class_date', args=(self.assign.id,))
        )
        context = response.context
        att_list = context['att_list']
        self.assertEqual(len(att_list), 1)
        self.assertEqual(att_list[0].total_students, 2)
        self.assertEqual(att_list[0].present_students, 1)
        self.assertEqual(att_list[0].absent_students, 1)
        self.assertEqual(att_list[0].attendance_percentage, 50.0)

    def test_t_class_date_unauthenticated(self):
        """Kiểm tra t_class_date khi chưa đăng nhập"""
        self.client.logout()
        response = self.client.get(
            reverse('t_class_date', args=(self.assign.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_t_class_date_invalid_assign(self):
        """Kiểm tra t_class_date với assign ID không tồn tại"""
        invalid_assign_id = 9999
        with self.assertRaises(Http404):
            self.client.get(
                reverse('t_class_date', args=(invalid_assign_id,))
            )

    def test_t_attendance(self):
        """Kiểm tra context của view t_attendance"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        response = self.client.get(
            reverse('t_attendance', args=(attendance_class.id,))
        )
        context = response.context
        self.assertEqual(context['ass'], self.assign)
        self.assertEqual(context['c'], self.class_obj)
        self.assertEqual(context['assc'], attendance_class)
        self.assertEqual(context['total_students_in_class'], 1)

    def test_t_attendance_unauthenticated(self):
        """Kiểm tra t_attendance khi chưa đăng nhập"""
        self.client.logout()
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        response = self.client.get(
            reverse('t_attendance', args=(attendance_class.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_t_attendance_invalid_id(self):
        """Kiểm tra t_attendance với AttendanceClass ID không tồn tại"""
        invalid_id = 999
        with self.assertRaises(Http404):
            self.client.get(
                reverse('t_attendance', args=(invalid_id,))
            )

    def test_confirm_attendance(self):
        """Kiểm tra view att_confirm lưu điểm danh đúng"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        post_data = {
            'assc_id': attendance_class.id,
            self.student.USN: 'present'
        }
        response = self.client.post(
            reverse('att_confirm', args=(attendance_class.id,)),
            post_data
        )
        attendance = Attendance.objects.get(
            student=self.student,
            subject=self.subject,
            attendanceclass=attendance_class
        )
        self.assertTrue(attendance.status)
        attendance_class.refresh_from_db()
        self.assertEqual(attendance_class.status, 1)

    def test_confirm_attendance_invalid_data(self):
        """Kiểm tra att_confirm với dữ liệu điểm danh không hợp lệ"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        post_data = {
            'assc_id': attendance_class.id,
            self.student.USN: 'invalid_status'
        }
        response = self.client.post(
            reverse('att_confirm', args=(attendance_class.id,)),
            post_data
        )
        attendance = Attendance.objects.get(
            student=self.student,
            subject=self.subject,
            attendanceclass=attendance_class
        )
        self.assertFalse(attendance.status)
        attendance_class.refresh_from_db()
        self.assertEqual(attendance_class.status, 1)

    def test_confirm_attendance_unauthenticated(self):
        """Kiểm tra att_confirm khi chưa đăng nhập"""
        self.client.logout()
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        post_data = {
            'assc_id': attendance_class.id,
            self.student.USN: 'present'
        }
        response = self.client.post(
            reverse('att_confirm', args=(attendance_class.id,)),
            post_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_confirm_attendance_invalid_id(self):
        """Kiểm tra att_confirm với AttendanceClass ID không tồn tại"""
        invalid_id = 999
        post_data = {
            'assc_id': invalid_id,
            self.student.USN: 'present'
        }
        with self.assertRaises(Http404):
            self.client.post(
                reverse('att_confirm', args=(invalid_id,))
            )

    def test_edit_att(self):
        """Kiểm tra context của view edit_att với thống kê"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            attendanceclass=attendance_class,
            date=date.today(),
            status=True
        )
        student2 = Student.objects.create(
            USN='S002',
            class_id=self.class_obj,
            name='Test Student 2',
            sex='F',
            DOB='2000-01-01'
        )
        Attendance.objects.create(
            student=student2,
            subject=self.subject,
            attendanceclass=attendance_class,
            date=date.today(),
            status=False
        )
        response = self.client.get(
            reverse('edit_att', args=(attendance_class.id,))
        )
        context = response.context
        self.assertEqual(context['total_students'], 2)
        self.assertEqual(context['present_students'], 1)
        self.assertEqual(context['absent_students'], 1)

    def test_edit_att_no_attendance(self):
        """Kiểm tra edit_att khi không có bản ghi điểm danh"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        response = self.client.get(
            reverse('edit_att', args=(attendance_class.id,))
        )
        context = response.context
        self.assertEqual(context['total_students'], 0)
        self.assertEqual(context['present_students'], 0)
        self.assertEqual(context['absent_students'], 0)

    def test_edit_att_unauthenticated(self):
        """Kiểm tra edit_att khi chưa đăng nhập"""
        self.client.logout()
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        response = self.client.get(
            reverse('edit_att', args=(attendance_class.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_view_att(self):
        """Kiểm tra context của view view_att với thống kê"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            attendanceclass=attendance_class,
            date=date.today(),
            status=True
        )
        student2 = Student.objects.create(
            USN='S002',
            class_id=self.class_obj,
            name='Test Student 2',
            sex='F',
            DOB='2000-01-01'
        )
        Attendance.objects.create(
            student=student2,
            subject=self.subject,
            attendanceclass=attendance_class,
            date=date.today(),
            status=False
        )
        response = self.client.get(
            reverse('view_att', args=(attendance_class.id,))
        )
        context = response.context
        self.assertEqual(context['total_students'], 2)
        self.assertEqual(context['present_students'], 1)
        self.assertEqual(context['absent_students'], 1)
        self.assertEqual(context['attendance_percentage'], 50.0)

    def test_view_att_no_attendance(self):
        """Kiểm tra view_att khi không có bản ghi điểm danh"""
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        response = self.client.get(
            reverse('view_att', args=(attendance_class.id,))
        )
        context = response.context
        self.assertEqual(context['total_students'], 0)
        self.assertEqual(context['present_students'], 0)
        self.assertEqual(context['absent_students'], 0)
        self.assertEqual(context['attendance_percentage'], 0.0)

    def test_view_att_unauthenticated(self):
        """Kiểm tra view_att khi chưa đăng nhập"""
        self.client.logout()
        attendance_class = AttendanceClass.objects.create(
            assign=self.assign,
            date=date.today(),
            status=DEFAULT_ATTENDANCE_STATUS
        )
        response = self.client.get(
            reverse('view_att', args=(attendance_class.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
