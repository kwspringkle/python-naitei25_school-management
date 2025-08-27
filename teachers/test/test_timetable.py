from django.test import TestCase, Client
from django.urls import reverse
from django.http import Http404
from admins.models import User, Dept, Subject, Class
from teachers.models import Teacher, Assign, AssignTime
import uuid
from django.test.utils import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class TimetableViewsTestCase(TestCase):
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
        self.client.login(username='testteacher', password='testpass123')

    def test_t_timetable(self):
        """Kiểm tra ma trận thời khóa biểu trong view t_timetable"""
        assign_time = AssignTime.objects.create(
            assign=self.assign,
            period='09:00-10:00',
            day='Monday'
        )
        response = self.client.get(
            reverse('t_timetable', args=(self.teacher.id,))
        )
        class_matrix = response.context['class_matrix']
        # Kiểm tra slot Monday, 09:00-10:00 có lịch dạy (True)
        self.assertTrue(class_matrix[0][1])  # View trả về True thay vì đối tượng AssignTime

    def test_t_timetable_unauthenticated(self):
        """Kiểm tra t_timetable khi chưa đăng nhập"""
        self.client.logout()
        response = self.client.get(
            reverse('t_timetable', args=(self.teacher.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_t_timetable_invalid_teacher(self):
        """Kiểm tra t_timetable với teacher ID không tồn tại"""
        invalid_teacher_id = 'T999'
        with self.assertRaises(Http404):
            self.client.get(
                reverse('t_timetable', args=(invalid_teacher_id,))
            )

    def test_free_teachers(self):
        """Kiểm tra view free_teachers hiển thị giáo viên rảnh"""
        assign_time = AssignTime.objects.create(
            assign=self.assign,
            period='09:00-10:00',
            day='Monday'
        )
        response = self.client.get(
            reverse('free_teachers', args=(assign_time.id,))
        )
        context = response.context
        self.assertEqual(len(context['ft_list']), 0)
        self.assertEqual(context['required_subject'], self.subject)
        self.assertEqual(context['assignment_time'], assign_time)

    def test_free_teachers_no_teachers(self):
        """Kiểm tra free_teachers khi không có giáo viên rảnh"""
        assign_time = AssignTime.objects.create(
            assign=self.assign,
            period='09:00-10:00',
            day='Monday'
        )
        response = self.client.get(
            reverse('free_teachers', args=(assign_time.id,))
        )
        context = response.context
        self.assertEqual(len(context['ft_list']), 0)

    def test_free_teachers_unauthenticated(self):
        """Kiểm tra free_teachers khi chưa đăng nhập"""
        self.client.logout()
        assign_time = AssignTime.objects.create(
            assign=self.assign,
            period='09:00-10:00',
            day='Monday'
        )
        response = self.client.get(
            reverse('free_teachers', args=(assign_time.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_free_teachers_invalid_id(self):
        """Kiểm tra free_teachers với AssignTime ID không tồn tại"""
        invalid_id = 999
        with self.assertRaises(Http404):
            self.client.get(
                reverse('free_teachers', args=(invalid_id,))
            )
            