from django.test import TestCase, Client
from django.urls import reverse
from django.http import Http404
from admins.models import User, Dept, Subject, Class
from teachers.models import Teacher, Assign, ExamSession, Marks
from students.models import Student, StudentSubject
from utils.constant import TEST_NAME_CHOICES, FIRST_CHOICE_INDEX, DEFAULT_STATUS_FALSE
import uuid
from django.test.utils import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class MarksViewsTestCase(TestCase):
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

    def test_t_marks_list_post_create_exam(self):
        """Kiểm tra tạo kỳ thi mới trong view t_marks_list"""
        post_data = {
            'create_exam': 'true',
            'exam_name': TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0]
        }
        response = self.client.post(
            reverse('t_marks_list', args=(self.assign.id,)),
            post_data
        )
        self.assertTrue(ExamSession.objects.filter(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0]
        ).exists())

    def test_t_marks_list_invalid_exam_name(self):
        """Kiểm tra t_marks_list khi gửi tên kỳ thi không hợp lệ"""
        post_data = {
            'create_exam': 'true',
            'exam_name': 'INVALID_EXAM'
        }
        response = self.client.post(
            reverse('t_marks_list', args=(self.assign.id,)),
            post_data
        )
        self.assertFalse(ExamSession.objects.filter(
            assign=self.assign,
            name='INVALID_EXAM'
        ).exists())
        self.assertEqual(response.status_code, 200)

    def test_t_marks_list_unauthenticated(self):
        """Kiểm tra t_marks_list khi chưa đăng nhập"""
        self.client.logout()
        response = self.client.get(
            reverse('t_marks_list', args=(self.assign.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_t_marks_list_invalid_assign(self):
        """Kiểm tra t_marks_list với assign ID không tồn tại"""
        invalid_assign_id = 9999
        with self.assertRaises(Http404):
            self.client.get(
                reverse('t_marks_list', args=(invalid_assign_id,))
            )

    def test_t_marks_entry(self):
        """Kiểm tra context của view t_marks_entry"""
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        response = self.client.get(
            reverse('t_marks_entry', args=(exam_session.id,))
        )
        context = response.context
        self.assertEqual(context['ass'], self.assign)
        self.assertEqual(context['c'], self.class_obj)
        self.assertEqual(context['mc'], exam_session)
        self.assertEqual(len(context['students_in_subject']), 1)
        self.assertEqual(context['students_in_subject'][0], self.student_subject)

    def test_t_marks_entry_unauthenticated(self):
        """Kiểm tra t_marks_entry khi chưa đăng nhập"""
        self.client.logout()
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        response = self.client.get(
            reverse('t_marks_entry', args=(exam_session.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_t_marks_entry_invalid_id(self):
        """Kiểm tra t_marks_entry với ExamSession ID không tồn tại"""
        invalid_id = 999
        with self.assertRaises(Http404):
            self.client.get(
                reverse('t_marks_entry', args=(invalid_id,))
            )

    def test_marks_confirm(self):
        """Kiểm tra view marks_confirm lưu điểm số đúng"""
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        post_data = {
            self.student.USN: '85'
        }
        response = self.client.post(
            reverse('marks_confirm', args=(exam_session.id,)),
            post_data
        )
        marks_instance = Marks.objects.get(
            student_subject=self.student_subject,
            name=exam_session.name
        )
        self.assertEqual(marks_instance.marks1, 85)
        exam_session.refresh_from_db()
        self.assertTrue(exam_session.status)

    def test_marks_confirm_invalid_marks(self):
        """Kiểm tra marks_confirm với điểm số không hợp lệ (âm)"""
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        post_data = {
            self.student.USN: '-10'
        }
        response = self.client.post(
            reverse('marks_confirm', args=(exam_session.id,)),
            post_data
        )
        marks_instance = Marks.objects.get(
            student_subject=self.student_subject,
            name=exam_session.name
        )
        self.assertEqual(marks_instance.marks1, 0)  # Giả định view xử lý điểm âm thành 0
        exam_session.refresh_from_db()
        self.assertTrue(exam_session.status)

    def test_marks_confirm_unauthenticated(self):
        """Kiểm tra marks_confirm khi chưa đăng nhập"""
        self.client.logout()
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        post_data = {
            self.student.USN: '85'
        }
        response = self.client.post(
            reverse('marks_confirm', args=(exam_session.id,)),
            post_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_marks_confirm_invalid_id(self):
        """Kiểm tra marks_confirm với ExamSession ID không tồn tại"""
        invalid_id = 999
        post_data = {
            self.student.USN: '85'
        }
        with self.assertRaises(Http404):
            self.client.post(
                reverse('marks_confirm', args=(invalid_id,))
            )

    def test_edit_marks(self):
        """Kiểm tra context của view edit_marks"""
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        Marks.objects.create(
            student_subject=self.student_subject,
            name=exam_session.name,
            marks1=90
        )
        response = self.client.get(
            reverse('edit_marks', args=(exam_session.id,))
        )
        context = response.context
        self.assertEqual(context['mc'], exam_session)
        self.assertEqual(len(context['m_list']), 1)
        self.assertEqual(context['m_list'][0].marks1, 90)

    def test_edit_marks_no_marks(self):
        """Kiểm tra edit_marks khi không có bản ghi điểm"""
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        response = self.client.get(
            reverse('edit_marks', args=(exam_session.id,))
        )
        context = response.context
        self.assertEqual(context['mc'], exam_session)
        self.assertEqual(len(context['m_list']), 0)

    def test_edit_marks_unauthenticated(self):
        """Kiểm tra edit_marks khi chưa đăng nhập"""
        self.client.logout()
        exam_session = ExamSession.objects.create(
            assign=self.assign,
            name=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][0],
            status=DEFAULT_STATUS_FALSE
        )
        response = self.client.get(
            reverse('edit_marks', args=(exam_session.id,))
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
