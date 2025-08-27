from django.test import TestCase, Client
from django.urls import reverse
from .test_base import AdminViewsBaseTestCase
from teachers.models import Assign, AssignTime


class TimetableManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý thời khóa biểu"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
        # Tạo assignment và assign time cho test
        self.assignment = Assign.objects.create(
            class_id=self.test_class,
            subject=self.subject,
            teacher=self.teacher
        )
        self.assign_time = AssignTime.objects.create(
            assign=self.assignment,
            day='Monday',
            period='9:30 - 10:30'
        )
    
    def test_timetable_list(self):
        """Test danh sách thời khóa biểu"""
        response = self.client.get(reverse('timetable'))
        self.assertIn('timetable_entries', response.context)
        self.assertIn('filter_form', response.context)
    
    def test_add_timetable_entry_success(self):
        """Test thêm entry thời khóa biểu thành công"""
        data = {
            'assign': self.assignment.id,
            'day': 'Tuesday',
            'period': '10:30 - 11:30'
        }
        
        response = self.client.post(reverse('add_timetable_entry'), data)
        self.assertRedirects(response, reverse('timetable'))
        
        # Verify entry được tạo
        self.assertTrue(AssignTime.objects.filter(
            assign=self.assignment, day='Tuesday', period='10:30 - 11:30'
        ).exists())
    
    def test_edit_timetable_entry(self):
        """Test chỉnh sửa entry thời khóa biểu"""
        response = self.client.get(
            reverse('edit_timetable_entry', args=[self.assign_time.id])
        )
        self.assertIn('form', response.context)
        self.assertIn('entry', response.context)
    
    def test_delete_timetable_entry(self):
        """Test xóa entry thời khóa biểu"""
        entry_id = self.assign_time.id
        response = self.client.post(
            reverse('delete_timetable_entry', args=[entry_id])
        )
        self.assertRedirects(response, reverse('timetable'))
        
        # Verify entry bị xóa
        self.assertFalse(AssignTime.objects.filter(id=entry_id).exists())
        