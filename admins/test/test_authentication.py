from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase


class AdminAuthenticationTests(AdminViewsBaseTestCase):
    """Tests cho authentication flow"""
    
    def test_admin_login_success(self):
        """Test đăng nhập admin thành công"""
        response = self.client.post(reverse('admin_login'), {
            'username': 'adminuser',
            'password': 'adminpass123'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
    
    def test_admin_login_failure(self):
        """Test đăng nhập admin thất bại"""
        response = self.client.post(reverse('admin_login'), {
            'username': 'adminuser',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
    
    def test_admin_dashboard_access(self):
        """Test truy cập dashboard"""
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_students', response.context)
        self.assertIn('total_teachers', response.context)
    
    def test_admin_logout(self):
        """Test đăng xuất"""
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(reverse('admin_logout'))
        self.assertRedirects(response, reverse('admin_login'))
        