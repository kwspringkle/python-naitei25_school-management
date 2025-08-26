from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase
from teachers.models import Teacher
from admins.models import User


class TeacherManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý giáo viên"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
    
    def test_add_teacher_success(self):
        """Kiểm tra thêm giáo viên thành công"""
        data = {
            'username': 'newteacher01',
            'email': 'teacher@test.com',
            'password': 'teacherpass123',
            'password_confirm': 'teacherpass123',
            'id': 'T002',
            'name': 'New Teacher',
            'sex': 'Female',
            'DOB': '1990-01-01',
            'address': '456 Teacher St',
            'phone': '0123456789',
            'dept': self.dept.id
        }
        
        response = self.client.post(reverse('add_teacher'), data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify teacher được tạo
        self.assertTrue(Teacher.objects.filter(id='T002').exists())
        self.assertTrue(User.objects.filter(username='newteacher01').exists())
    
    def test_add_teacher_form_display(self):
        """Kiểm tra hiển thị form thêm giáo viên"""
        response = self.client.get(reverse('add_teacher'))
        self.assertContains(response, 'form')
        