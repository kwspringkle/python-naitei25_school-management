from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase
from admins.models import User, Class


class ClassManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý lớp học"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
    
    def test_class_list(self):
        """Test danh sách lớp học"""
        response = self.client.get(reverse('class_list'))
        self.assertIn('classes', response.context)
        
        # Verify class hiện tại có trong list
        classes = response.context['classes']
        self.assertTrue(self.test_class in classes)
    
    def test_add_class_success(self):
        """Test thêm lớp học thành công"""
        data = {
            'id': 'CS-2A',
            'dept': self.dept.id,
            'section': 'A',
            'sem': 2
        }
        
        response = self.client.post(reverse('add_class'), data)
        self.assertRedirects(response, reverse('class_list'))
        
        # Verify class được tạo
        self.assertTrue(Class.objects.filter(id='CS-2A').exists())
        new_class = Class.objects.get(id='CS-2A')
        self.assertEqual(new_class.dept, self.dept)
        self.assertEqual(new_class.section, 'A')
        self.assertEqual(new_class.sem, 2)
    
    def test_edit_class_display(self):
        """Test hiển thị form chỉnh sửa lớp học"""
        response = self.client.get(
            reverse('edit_class', args=[self.test_class.id])
        )
        self.assertIn('form', response.context)
        self.assertIn('class_obj', response.context)
        self.assertIn('students', response.context)
        self.assertIn('assignments', response.context)
        
        # Verify class object đúng
        self.assertEqual(response.context['class_obj'], self.test_class)
    
    def test_edit_class_success(self):
        """Test chỉnh sửa lớp học thành công"""
        data = {
            'id': self.test_class.id,
            'dept': self.dept.id,
            'section': 'B',  # Đổi section
            'sem': 2         # Đổi semester
        }
        
        response = self.client.post(
            reverse('edit_class', args=[self.test_class.id]), data
        )
        self.assertRedirects(response, reverse('class_list'))
        
        # Verify class được update
        updated_class = Class.objects.get(id=self.test_class.id)
        self.assertEqual(updated_class.section, 'B')
        self.assertEqual(updated_class.sem, 2)

    def test_delete_class_success(self):
        """Testcase: xóa lớp học thành công"""
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.post(reverse('delete_class', args=[self.test_class.id]))
        self.assertRedirects(response, reverse('class_list'))
        self.assertFalse(Class.objects.filter(id=self.test_class.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Class has been deleted successfully!')

    def test_delete_class_with_students(self):
        """Testcase: xóa lớp học có học sinh"""
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.post(reverse('delete_class', args=[self.test_class.id]))
        self.assertRedirects(response, reverse('class_list'))
        self.assertTrue(Class.objects.filter(id=self.test_class.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cannot delete this class because it has 1 student(s).')

    def test_delete_class_not_found(self):
        """Testcase: xóa lớp học không tồn tại"""
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.post(reverse('delete_class', args=['NONEXISTENT']))
        self.assertRedirects(response, reverse('class_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'The class does not exist!')

    def test_delete_class_permission_denied(self):
        """Testcase: xóa lớp học, không đúng role"""
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='regularpass123'
        )
        self.client.login(username='regular', password='regularpass123')
        response = self.client.post(reverse('delete_class', args=[self.test_class.id]), follow=True)
    