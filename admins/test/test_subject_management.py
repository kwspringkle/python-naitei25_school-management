from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase
from admins.models import Subject
from teachers.models import Assign


class SubjectManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý môn học"""

    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')

    def test_subject_list(self):
        """Kiểm tra hiển thị danh sách môn học"""
        response = self.client.get(reverse('subject_list'))
        self.assertIn('subjects', response.context)
        self.assertContains(response, self.subject.name)

    def test_add_subject_success(self):
        """Kiểm tra thêm môn học mới thành công"""
        form_data = {'id': 'CS102', 'name': 'Database', 'dept': self.dept.id, 'shortname': 'DB'}
        response = self.client.post(reverse('add_subject'), form_data)
        self.assertRedirects(response, reverse('subject_list'))
        self.assertTrue(Subject.objects.filter(id='CS102').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Subject has been added successfully!')

    def test_edit_subject_success(self):
        """Kiểm tra chỉnh sửa môn học thành công"""
        form_data = {'id': 'CS101', 'name': 'Advanced Programming', 'dept': self.dept.id, 'shortname': 'ADVPROG'}
        response = self.client.post(reverse('edit_subject', args=['CS101']), form_data)
        self.assertRedirects(response, reverse('subject_list'))
        subject = Subject.objects.get(id='CS101')
        self.assertEqual(subject.name, 'Advanced Programming')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Subject has been updated successfully!')

    def test_delete_subject_success(self):
        """Kiểm tra xóa môn học không có dữ liệu liên quan"""
        response = self.client.post(reverse('delete_subject', args=['CS101']))
        self.assertRedirects(response, reverse('subject_list'))
        self.assertFalse(Subject.objects.filter(id='CS101').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Subject has been deleted successfully!')

    def test_delete_subject_with_relations(self):
        """Kiểm tra xóa môn học có dữ liệu liên quan (không cho xóa)"""
        Assign.objects.create(class_id=self.test_class, subject=self.subject, teacher=self.teacher)
        response = self.client.post(reverse('delete_subject', args=['CS101']))
        self.assertRedirects(response, reverse('subject_list'))
        self.assertTrue(Subject.objects.filter(id='CS101').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cannot delete subject because it has related assignments or student records.')
        