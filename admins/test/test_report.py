from django.test import TestCase, Client
from django.urls import reverse
from .test_base import AdminViewsBaseTestCase


class ReportTests(AdminViewsBaseTestCase):
    """Tests cho báo cáo và thống kê"""

    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')

    def test_admin_reports_overview(self):
        """Kiểm tra báo cáo overview hiển thị đúng thống kê hệ thống"""
        response = self.client.get(reverse('admin_reports'))
        self.assertTemplateUsed(response, 'admins/admin_reports.html')
        self.assertEqual(response.context['report_type'], 'overview')
        self.assertEqual(response.context['system_stats']['total_students'], 1)
        self.assertEqual(response.context['system_stats']['total_classes'], 1)

    def test_admin_reports_performance(self):
        """Kiểm tra báo cáo performance hiển thị đúng"""
        response = self.client.get(reverse('admin_reports') + '?type=performance')
        self.assertTemplateUsed(response, 'admins/admin_reports.html')
        self.assertEqual(response.context['report_type'], 'performance')

    def test_admin_reports_unauthenticated(self):
        """Kiểm tra truy cập báo cáo khi chưa đăng nhập"""
        self.client.logout()
        response = self.client.get(reverse('admin_reports'))
        