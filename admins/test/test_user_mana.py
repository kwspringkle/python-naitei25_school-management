from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from .test_base import AdminViewsBaseTestCase
from admins.models import User

class UserManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý người dùng"""

    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
        self.admin_user.user_permissions.set(Permission.objects.all())
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regularuser@test.com',
            password='regularpass123'
        )

    def test_user_list_view(self):
        """Kiểm tra hiển thị danh sách người dùng"""
        response = self.client.get(reverse('user_list'))
        self.assertContains(response, 'regularuser')

    def test_search_user_by_username(self):
        """Kiểm tra tìm kiếm người dùng theo username"""
        response = self.client.get(reverse('user_list'), {'q': 'regularuser'})
        self.assertContains(response, 'regularuser')

    def test_filter_user_by_is_active(self):
        """Kiểm tra lọc người dùng theo trạng thái is_active"""
        self.regular_user.is_active = False
        self.regular_user.save()
        response = self.client.get(reverse('user_list'), {'is_active': 'False'})
        self.assertContains(response, 'regularuser')

    def test_add_user_success(self):
        """Kiểm tra thêm người dùng mới thành công"""
        data = {
            'username': 'newuser', 'email': 'newuser@example.com', 'password': 'testpass123',
            'first_name': 'New', 'last_name': 'User', 'is_superuser': False, 'is_active': True
        }
        response = self.client.post(reverse('add_user'), data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_add_user_invalid_form(self):
        """Kiểm tra thêm người dùng với form không hợp lệ"""
        data = {'username': '', 'email': 'invalid@example.com'}
        response = self.client.post(reverse('add_user'), data)
        self.assertContains(response, 'This field is required')

    def test_edit_user(self):
        """Kiểm tra chỉnh sửa thông tin người dùng"""
        data = {
            'username': 'regularuser', 'email': 'updated@example.com', 'first_name': 'Updated',
            'last_name': 'Name', 'password': '', 'is_active': True, 'is_superuser': False
        }
        response = self.client.post(reverse('edit_user', args=[self.regular_user.id]), data)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, 'updated@example.com')

    def test_edit_user_password_change(self):
        """Kiểm tra thay đổi mật khẩu người dùng"""
        data = {
            'username': 'regularuser', 'email': 'john@example.com', 'first_name': 'John',
            'last_name': 'Doe', 'password': 'newsecurepass', 'is_superuser': False, 'is_active': True
        }
        response = self.client.post(reverse('edit_user', args=[self.regular_user.id]), data)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password('newsecurepass'))

    def test_toggle_user_status(self):
        """Kiểm tra bật/tắt trạng thái người dùng"""
        response = self.client.get(reverse('toggle_user_status', args=[self.regular_user.id]))
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

    def test_toggle_own_user_status(self):
        """Kiểm tra không thể tắt trạng thái tài khoản của chính mình"""
        response = self.client.get(reverse('toggle_user_status', args=[self.admin_user.id]))
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'You cannot deactivate your own account!')