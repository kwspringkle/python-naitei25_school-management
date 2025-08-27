from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase
from admins.models import Dept


class DepartmentManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý khoa"""

    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')

    def test_department_list(self):
        """Kiểm tra hiển thị danh sách các khoa"""
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('departments', response.context)
        self.assertContains(response, self.dept.name)

    def test_add_department_success(self):
        """Kiểm tra thêm khoa mới thành công"""
        form_data = {'id': 'IT', 'name': 'Information Technology'}
        response = self.client.post(reverse('add_department'), form_data)
        self.assertRedirects(response, reverse('department_list'))
        self.assertTrue(Dept.objects.filter(id='IT').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Department has been added successfully!')

    def test_edit_department_success(self):
        """Kiểm tra chỉnh sửa khoa thành công"""
        form_data = {'id': 'CS', 'name': 'Updated Computer Science'}
        response = self.client.post(reverse('edit_department', args=['CS']), form_data)
        self.assertRedirects(response, reverse('department_list'))
        dept = Dept.objects.get(id='CS')
        self.assertEqual(dept.name, 'Updated Computer Science')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Department has been updated successfully!')

    def test_delete_department_success(self):
        """Kiểm tra xóa khoa không có dữ liệu liên quan"""
        dept = Dept.objects.create(id='IT', name='Information Technology')
        response = self.client.post(reverse('delete_department', args=['IT']))
        self.assertRedirects(response, reverse('department_list'))
        self.assertFalse(Dept.objects.filter(id='IT').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Department has been deleted successfully!')

    def test_delete_department_with_relations(self):
        """Kiểm tra xóa khoa có dữ liệu liên quan (không cho xóa)"""
        response = self.client.post(reverse('delete_department', args=['CS']))
        self.assertRedirects(response, reverse('department_list'))
        self.assertTrue(Dept.objects.filter(id='CS').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cannot delete department because it has related teachers, subjects, or classes.')
        