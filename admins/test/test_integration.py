from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from datetime import date
from .test_base import AdminViewsBaseTestCase
from admins.models import User, Dept, Subject, Class
from students.models import Student
from teachers.models import Teacher, Assign


class AdminViewsIntegrationTests(AdminViewsBaseTestCase):
    """Integration tests cho các workflow chính"""

    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
        self.admin_user.user_permissions.set(Permission.objects.all())

    def test_class_management_workflow(self):
        """Kiểm tra toàn bộ flow quản lý lớp: tạo, chỉnh sửa, xóa lớp; quản lý sinh viên, môn học trong lớp"""
        # 1. Tạo lớp mới
        class_data = {
            'id': 'EE-1A', 'dept': self.dept.id, 'section': 'A', 'sem': 1
        }
        response = self.client.post(reverse('add_class'), class_data)
        self.assertRedirects(response, reverse('class_list'))
        new_class = Class.objects.get(id='EE-1A')

        # 2. Chỉnh sửa thông tin lớp
        edit_class_data = {
            'id': 'EE-1A', 'dept': self.dept.id, 'section': 'B', 'sem': 2
        }
        response = self.client.post(reverse('edit_class', args=['EE-1A']), edit_class_data)
        self.assertRedirects(response, reverse('class_list'))
        updated_class = Class.objects.get(id='EE-1A')
        self.assertEqual(updated_class.section, 'B')
        self.assertEqual(updated_class.sem, 2)

        # 3. Thêm sinh viên vào lớp
        student_data = {
            'username': 'newstudent02', 'email': 'newstudent02@example.com',
            'password': 'newpass123', 'name': 'Jane Doe', 'USN': '1EE20EE001',
            'sex': 'F', 'DOB': '2000-02-02', 'address': '456 Street',
            'phone': '0987654321'
        }
        response = self.client.post(reverse('add_student_to_class', args=['EE-1A']), student_data)
        self.assertRedirects(response, reverse('edit_class', args=['EE-1A']))
        self.assertTrue(Student.objects.filter(USN='1EE20EE001').exists())

        # 4. Chỉnh sửa thông tin sinh viên
        edit_student_data = {
            'username': 'updatedstudent', 'email': 'updated@example.com',
            'name': 'Jane Updated', 'USN': '1EE20EE001', 'sex': 'F',
            'DOB': '2000-02-02', 'address': '789 Street', 'phone': '1112223333'
        }
        response = self.client.post(reverse('edit_student', args=['1EE20EE001']), edit_student_data)
        self.assertRedirects(response, reverse('edit_class', args=['EE-1A']))
        student = Student.objects.get(USN='1EE20EE001')
        self.assertEqual(student.name, 'Jane Updated')

        # 5. Thêm môn học có sẵn vào lớp
        assign_data = {
            'subject': self.subject.id, 'teacher': self.teacher.id
        }
        response = self.client.post(reverse('add_subject_to_class', args=['EE-1A']), assign_data)
        self.assertRedirects(response, reverse('edit_class', args=['EE-1A']))
        self.assertTrue(Assign.objects.filter(class_id=new_class, subject=self.subject).exists())

        # 6. Thêm môn học mới vào lớp
        new_subject_data = {
            'id': 'CS103', 'name': 'Database Systems', 'dept': self.dept.id, 'shortname': 'DBS'
        }
        response = self.client.post(reverse('add_subject'), new_subject_data)
        self.assertRedirects(response, reverse('subject_list'))
        new_subject = Subject.objects.get(id='CS103')
        assign_data_new = {
            'subject': new_subject.id, 'teacher': self.teacher.id
        }
        response = self.client.post(reverse('add_subject_to_class', args=['EE-1A']), assign_data_new)
        self.assertRedirects(response, reverse('edit_class', args=['EE-1A']))
        self.assertTrue(Assign.objects.filter(class_id=new_class, subject=new_subject).exists())

        # 7. Chỉnh sửa phân công giảng dạy
        assignment = Assign.objects.get(class_id=new_class, subject=self.subject)
        new_teacher = Teacher.objects.create(
            user=User.objects.create_user(username='teacher2', email='teacher2@test.com', password='teacherpass123'),
            id='T002', name='New Teacher', sex='F', DOB=date(1990, 1, 1),
            address='456 Teacher St', phone='0123456789', dept=self.dept
        )
        edit_assign_data = {
            'class_id': new_class.id, 'subject': self.subject.id, 'teacher': new_teacher.id
        }
        response = self.client.post(reverse('edit_teaching_assignment', args=[assignment.id]), edit_assign_data)
        self.assertRedirects(response, reverse('teaching_assignments'))
        assignment.refresh_from_db()
        self.assertEqual(assignment.teacher, new_teacher)

        # 8. Xóa môn học khỏi lớp
        response = self.client.post(reverse('remove_subject_from_class', args=['EE-1A', assignment.id]))
        self.assertRedirects(response, reverse('edit_class', args=['EE-1A']))
        self.assertFalse(Assign.objects.filter(id=assignment.id).exists())

        # 9. Xóa sinh viên khỏi lớp
        response = self.client.post(reverse('delete_student', args=['1EE20EE001']))
        self.assertRedirects(response, reverse('edit_class', args=['EE-1A']))
        self.assertFalse(Student.objects.filter(USN='1EE20EE001').exists())

        # 10. Xóa lớp (sẽ thất bại vì có môn học)
        assign_data = {'subject': new_subject.id, 'teacher': self.teacher.id}
        self.client.post(reverse('add_subject_to_class', args=['EE-1A']), assign_data)
        response = self.client.post(reverse('delete_class', args=['EE-1A']))
        self.assertRedirects(response, reverse('class_list'))
        self.assertTrue(Class.objects.filter(id='EE-1A').exists())

        # 11. Xóa môn học và thử xóa lớp lại
        assignment = Assign.objects.get(class_id=new_class, subject=new_subject)
        self.client.post(reverse('remove_subject_from_class', args=['EE-1A', assignment.id]))
        response = self.client.post(reverse('delete_class', args=['EE-1A']))
        self.assertRedirects(response, reverse('class_list'))
        self.assertFalse(Class.objects.filter(id='EE-1A').exists())

    def test_department_management_workflow(self):
        """Kiểm tra flow quản lý khoa: tạo, chỉnh sửa, xóa khoa"""
        # 1. Tạo khoa mới
        dept_data = {'id': 'IT', 'name': 'Information Technology'}
        response = self.client.post(reverse('add_department'), dept_data)
        self.assertRedirects(response, reverse('department_list'))
        self.assertTrue(Dept.objects.filter(id='IT').exists())

        # 2. Chỉnh sửa khoa
        edit_dept_data = {'id': 'IT', 'name': 'Updated IT'}
        response = self.client.post(reverse('edit_department', args=['IT']), edit_dept_data)
        self.assertRedirects(response, reverse('department_list'))
        dept = Dept.objects.get(id='IT')
        self.assertEqual(dept.name, 'Updated IT')

        # 3. Xóa khoa (thành công vì không có dữ liệu liên quan)
        response = self.client.post(reverse('delete_department', args=['IT']))
        self.assertRedirects(response, reverse('department_list'))
        self.assertFalse(Dept.objects.filter(id='IT').exists())

        # 4. Thử xóa khoa có dữ liệu liên quan (thất bại)
        response = self.client.post(reverse('delete_department', args=['CS']))
        self.assertRedirects(response, reverse('department_list'))
        self.assertTrue(Dept.objects.filter(id='CS').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cannot delete department because it has related teachers, subjects, or classes.')

    def test_subject_management_workflow(self):
        """Kiểm tra flow quản lý môn học: tạo, chỉnh sửa, xóa môn học"""
        # 1. Tạo môn học mới
        subject_data = {'id': 'CS102', 'name': 'Database', 'dept': self.dept.id, 'shortname': 'DB'}
        response = self.client.post(reverse('add_subject'), subject_data)
        self.assertRedirects(response, reverse('subject_list'))
        self.assertTrue(Subject.objects.filter(id='CS102').exists())

        # 2. Chỉnh sửa môn học
        edit_subject_data = {'id': 'CS102', 'name': 'Advanced Database', 'dept': self.dept.id, 'shortname': 'ADB'}
        response = self.client.post(reverse('edit_subject', args=['CS102']), edit_subject_data)
        self.assertRedirects(response, reverse('subject_list'))
        subject = Subject.objects.get(id='CS102')
        self.assertEqual(subject.name, 'Advanced Database')

        # 3. Xóa môn học (thành công vì không có dữ liệu liên quan)
        response = self.client.post(reverse('delete_subject', args=['CS102']))
        self.assertRedirects(response, reverse('subject_list'))
        self.assertFalse(Subject.objects.filter(id='CS102').exists())

        # 4. Thử xóa môn học có dữ liệu liên quan (thất bại)
        Assign.objects.create(class_id=self.test_class, subject=self.subject, teacher=self.teacher)
        response = self.client.post(reverse('delete_subject', args=['CS101']))
        self.assertRedirects(response, reverse('subject_list'))
        self.assertTrue(Subject.objects.filter(id='CS101').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cannot delete subject because it has related assignments or student records.')

    def test_report_statistics_workflow(self):
        """Kiểm tra flow báo cáo thống kê: truy cập các loại báo cáo"""
        # 1. Kiểm tra báo cáo overview
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.context['report_type'], 'overview')
        self.assertEqual(response.context['system_stats']['total_students'], 1)

        # 2. Kiểm tra báo cáo performance
        response = self.client.get(reverse('admin_reports') + '?type=performance')
        self.assertEqual(response.context['report_type'], 'performance')

        # 3. Kiểm tra báo cáo attendance
        response = self.client.get(reverse('admin_reports') + '?type=attendance')
        self.assertEqual(response.context['report_type'], 'attendance')

        # 4. Kiểm tra báo cáo teaching
        response = self.client.get(reverse('admin_reports') + '?type=teaching')
        self.assertEqual(response.context['report_type'], 'teaching')

        # 5. Kiểm tra báo cáo data
        response = self.client.get(reverse('admin_reports') + '?type=data')
        self.assertEqual(response.context['report_type'], 'data')

        # 6. Kiểm tra báo cáo export
        response = self.client.get(reverse('admin_reports') + '?type=export')
        self.assertEqual(response.context['report_type'], 'export')

    def test_user_management_workflow(self):
        """Kiểm tra flow quản lý người dùng: tạo, chỉnh sửa, bật/tắt trạng thái"""
        # 1. Tạo người dùng mới
        user_data = {
            'username': 'newuser', 'email': 'newuser@example.com', 'password': 'testpass123',
            'first_name': 'New', 'last_name': 'User', 'is_superuser': False, 'is_active': True
        }
        response = self.client.post(reverse('add_user'), user_data)
        self.assertRedirects(response, reverse('user_list'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # 2. Chỉnh sửa người dùng
        new_user = User.objects.get(username='newuser')
        edit_user_data = {
            'username': 'newuser', 'email': 'updated@example.com', 'first_name': 'Updated',
            'last_name': 'Name', 'password': '', 'is_active': True, 'is_superuser': False
        }
        response = self.client.post(reverse('edit_user', args=[new_user.id]), edit_user_data)
        self.assertRedirects(response, reverse('user_list'))
        new_user.refresh_from_db()
        self.assertEqual(new_user.email, 'updated@example.com')

        # 3. Tắt trạng thái người dùng
        response = self.client.get(reverse('toggle_user_status', args=[new_user.id]))
        self.assertRedirects(response, reverse('user_list'))
        new_user.refresh_from_db()
        self.assertFalse(new_user.is_active)

        # 4. Bật lại trạng thái người dùng
        response = self.client.get(reverse('toggle_user_status', args=[new_user.id]))
        self.assertRedirects(response, reverse('user_list'))
        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)

        # 5. Thử tắt trạng thái tài khoản của chính admin
        response = self.client.get(reverse('toggle_user_status', args=[self.admin_user.id]))
        self.assertRedirects(response, reverse('user_list'))
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'You cannot deactivate your own account!')
        