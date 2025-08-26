from django.test import TestCase, Client
from django.urls import reverse
from .test_base import AdminViewsBaseTestCase
from admins.models import User


class AdminViewsPermissionTests(AdminViewsBaseTestCase):
    """Tests cho permissions cơ bản"""
    
    def test_views_require_login(self):
        """Test các views yêu cầu login"""
        protected_urls = [
            reverse('teaching_assignments'),
            reverse('add_teaching_assignment'),
            reverse('timetable'),
            reverse('add_timetable_entry'),
            reverse('class_list'),
            reverse('add_class'),
            reverse('department_list'), reverse('add_department'),
            reverse('subject_list'), reverse('add_subject'),
            reverse('user_list'), reverse('add_user'),
            reverse('admin_reports')
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
    
    def test_admin_dashboard_requires_admin(self):
        """Test dashboard yêu cầu admin privileges"""
        # Test với user thường
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='regularpass123'
        )
        
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('admin_dashboard'))
        # Should be handled by middleware (redirect or 403)
        self.assertNotEqual(response.status_code, 200)
        