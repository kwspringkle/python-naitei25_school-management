from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase
from students.models import Student
from admins.models import User


class StudentManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý sinh viên"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
    
    def test_add_student_success(self):
        """Test thêm sinh viên thành công"""
        data = {
            'username': 'newstudent01',
            'email': 'student@test.com',
            'password': 'studentpass123',
            'password_confirm': 'studentpass123',
            'USN': '1CS20CS001',
            'name': 'New Student',
            'sex': 'Male',
            'DOB': '2000-01-01',
            'address': '123 Student St',
            'phone': '0987654321',
            'class_id': self.test_class.id
        }
        
        response = self.client.post(reverse('add_student'), data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify student được tạo
        self.assertTrue(Student.objects.filter(USN='1CS20CS001').exists())
        self.assertTrue(User.objects.filter(username='newstudent01').exists())
    
    def test_add_student_form_display(self):
        """Test hiển thị form thêm sinh viên"""
        response = self.client.get(reverse('add_student'))
        self.assertContains(response, 'form')

    def test_add_student_to_class_success(self):
        """Kiểm tra thêm sinh viên vào lớp thành công"""
        form_data = {
            'username': 'newstudent02', 'email': 'newstudent02@example.com',
            'password': 'newpass123', 'name': 'Jane Doe', 'USN': '1CS20CS003',
            'sex': 'F', 'DOB': '2000-02-02', 'address': '456 Street',
            'phone': '0987654321'
        }
        response = self.client.post(reverse('add_student_to_class', args=[self.test_class.id]), form_data)
        self.assertRedirects(response, reverse('edit_class', args=[self.test_class.id]))
        self.assertTrue(Student.objects.filter(USN='1CS20CS003').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Student "Jane Doe" has been successfully added to class.')

    def test_add_student_to_class_invalid_form(self):
        """Kiểm tra thêm sinh viên vào lớp với form không hợp lệ"""
        form_data = {'username': ''}  # Form không hợp lệ
        response = self.client.post(reverse('add_student_to_class', args=[self.test_class.id]), form_data)
        self.assertTemplateUsed(response, 'admins/add_student_to_class.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('This field is required' in str(m) for m in messages))

    def test_add_student_to_class_not_found(self):
        """Kiểm tra thêm sinh viên vào lớp không tồn tại"""
        response = self.client.post(reverse('add_student_to_class', args=['NONEXISTENT']))
        self.assertRedirects(response, reverse('class_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'The class does not exist!')

    def test_edit_student_success(self):
        """Kiểm tra chỉnh sửa thông tin sinh viên thành công"""
        form_data = {
            'username': 'updatedstudent', 'email': 'updated@example.com',
            'name': 'Updated Student', 'USN': '1CS20CS001', 'sex': 'M',
            'DOB': '2000-01-01', 'address': '789 Street', 'phone': '1112223333'
        }
        response = self.client.post(reverse('edit_student', args=['1CS20CS001']), form_data)
        self.assertRedirects(response, reverse('edit_class', args=[self.test_class.id]))
        student = Student.objects.get(USN='1CS20CS001')
        self.assertEqual(student.user.username, 'updatedstudent')
        self.assertEqual(student.name, 'Updated Student')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Student "Test Student" has been updated successfully!')

    def test_edit_student_not_found(self):
        """Kiểm tra chỉnh sửa sinh viên không tồn tại"""
        response = self.client.post(reverse('edit_student', args=['NONEXISTENT']))
        self.assertRedirects(response, reverse('class_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'The student does not exist!')

    def test_delete_student_no_related_data(self):
        """Kiểm tra xóa sinh viên không có dữ liệu liên quan"""
        response = self.client.post(reverse('delete_student', args=['1CS20CS001']))
        self.assertRedirects(response, reverse('edit_class', args=[self.test_class.id]))
        self.assertFalse(Student.objects.filter(USN='1CS20CS001').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Student has been deleted successfully!')

    def test_delete_student_with_related_data(self):
        """Kiểm tra xóa sinh viên có dữ liệu liên quan (deactivate thay vì xóa)"""
        Student.objects.create(student=self.student, subject=self.subject)
        response = self.client.post(reverse('delete_student', args=['1CS20CS001']))
        self.assertRedirects(response, reverse('edit_class', args=[self.test_class.id]))
        student = Student.objects.get(USN='1CS20CS001')
        self.assertFalse(student.is_active)
        self.assertFalse(student.user.is_active)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Student has academic records and has been deactivated instead of deleted.')
        