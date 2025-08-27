from django.test import TestCase, Client
from django.urls import reverse
from .test_base import AdminViewsBaseTestCase
from teachers.models import Assign
from admins.models import Subject


class TeachingAssignmentTests(AdminViewsBaseTestCase):
    """Tests cho quản lý phân công giảng dạy"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
        # Tạo assignment cho test
        self.assignment = Assign.objects.create(
            class_id=self.test_class,
            subject=self.subject,
            teacher=self.teacher
        )
    
    def test_teaching_assignments_list(self):
        """Test danh sách phân công giảng dạy"""
        response = self.client.get(reverse('teaching_assignments'))
        self.assertIn('assignments', response.context)
        self.assertIn('filter_form', response.context)
    
    def test_add_teaching_assignment_success(self):
        """Test thêm phân công giảng dạy thành công"""
        # Tạo subject mới để test
        subject2 = Subject.objects.create(
            id='CS102', name='Data Structure', dept=self.dept
        )
        
        data = {
            'class_id': self.test_class.id,
            'subject': subject2.id,
            'teacher': self.teacher.id
        }
        
        response = self.client.post(reverse('add_teaching_assignment'), data)
        self.assertRedirects(response, reverse('teaching_assignments'))
        
        # Verify assignment được tạo
        self.assertTrue(Assign.objects.filter(
            class_id=self.test_class, subject=subject2, teacher=self.teacher
        ).exists())
    
    def test_edit_teaching_assignment(self):
        """Test chỉnh sửa phân công giảng dạy"""
        response = self.client.get(
            reverse('edit_teaching_assignment', args=[self.assignment.id])
        )
        self.assertIn('form', response.context)
        self.assertIn('assignment', response.context)
    
    def test_delete_teaching_assignment(self):
        """Test xóa phân công giảng dạy"""
        assignment_id = self.assignment.id
        response = self.client.post(
            reverse('delete_teaching_assignment', args=[assignment_id])
        )
        self.assertRedirects(response, reverse('teaching_assignments'))
        
        # Verify assignment bị xóa
        self.assertFalse(Assign.objects.filter(id=assignment_id).exists())
        