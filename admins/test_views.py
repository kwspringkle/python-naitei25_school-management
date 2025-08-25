
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from datetime import date

from admins.models import User, Dept, Subject, Class
from students.models import Student
from teachers.models import Teacher, Assign, AssignTime


class AdminViewsBaseTestCase(TestCase):
    """Base test case với setup dữ liệu chung"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Tạo department
        self.dept = Dept.objects.create(id='CS', name='Computer Science')
        
        # Tạo subject
        self.subject = Subject.objects.create(
            id='CS101', name='Programming', dept=self.dept
        )
        
        # Tạo class
        self.test_class = Class.objects.create(
            id='CS-1A', dept=self.dept, section='A', sem=1
        )
        
        # Tạo admin user (username >= 8 chars theo validation rule)
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@test.com', 
            password='adminpass123',
            is_superuser=True,
            is_staff=True
        )
        
        # Tạo teacher
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='teacherpass123'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            id='T001',
            name='Test Teacher',
            sex='M',
            DOB=date(1985, 1, 1),
            address='123 Test St',
            phone='1234567890',
            dept=self.dept
        )


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
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')


class TeacherManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý giáo viên"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
    
    def test_add_teacher_success(self):
        """Test thêm giáo viên thành công"""
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
        """Test hiển thị form thêm giáo viên"""
        response = self.client.get(reverse('add_teacher'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')


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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
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


class ClassManagementTests(AdminViewsBaseTestCase):
    """Tests cho quản lý lớp học"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
    
    def test_class_list(self):
        """Test danh sách lớp học"""
        response = self.client.get(reverse('class_list'))
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
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


class AdminViewsIntegrationTests(AdminViewsBaseTestCase):
    """Integration tests cho workflow chính"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='adminuser', password='adminpass123')
    
    def test_complete_class_workflow(self):
        """Test workflow hoàn chỉnh: tạo class -> thêm assignment -> thêm timetable"""
        # 1. Tạo class mới
        class_data = {
            'id': 'EE-1A',
            'dept': self.dept.id,
            'section': 'A',
            'sem': 1
        }
        response = self.client.post(reverse('add_class'), class_data)
        self.assertRedirects(response, reverse('class_list'))
        new_class = Class.objects.get(id='EE-1A')
        
        # 2. Thêm teaching assignment
        assignment_data = {
            'class_id': new_class.id,
            'subject': self.subject.id,
            'teacher': self.teacher.id
        }
        response = self.client.post(reverse('add_teaching_assignment'), assignment_data)
        self.assertRedirects(response, reverse('teaching_assignments'))
        new_assignment = Assign.objects.get(class_id=new_class, subject=self.subject)
        
        # 3. Thêm timetable entry
        timetable_data = {
            'assign': new_assignment.id,
            'day': 'Friday',
            'period': '2:30 - 3:30'
        }
        response = self.client.post(reverse('add_timetable_entry'), timetable_data)
        self.assertRedirects(response, reverse('timetable'))
        
        # 4. Verify toàn bộ workflow
        self.assertTrue(Class.objects.filter(id='EE-1A').exists())
        self.assertTrue(Assign.objects.filter(
            class_id=new_class, subject=self.subject, teacher=self.teacher
        ).exists())
        self.assertTrue(AssignTime.objects.filter(
            assign=new_assignment, day='Friday', period='2:30 - 3:30'
        ).exists())
    
    def test_student_teacher_creation_workflow(self):
        """Test workflow tạo teacher và student"""
        # 1. Thêm teacher
        teacher_data = {
            'username': 'teacher02user',
            'email': 'teacher2@test.com',
            'password': 'teacherpass123',
            'password_confirm': 'teacherpass123',
            'id': 'T002',
            'name': 'Teacher Two',
            'sex': 'Female',
            'DOB': '1990-01-01',
            'address': '456 Teacher St',
            'phone': '0123456789',
            'dept': self.dept.id
        }
        response = self.client.post(reverse('add_teacher'), teacher_data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # 2. Thêm student
        student_data = {
            'username': 'student01user',
            'email': 'student1@test.com',
            'password': 'studentpass123',
            'password_confirm': 'studentpass123',
            'USN': '1CS20CS001',
            'name': 'Student One',
            'sex': 'Male',
            'DOB': '2000-01-01',
            'address': '123 Student St',
            'phone': '0987654321',
            'class_id': self.test_class.id
        }
        response = self.client.post(reverse('add_student'), student_data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # 3. Verify cả hai được tạo
        self.assertTrue(Teacher.objects.filter(id='T002').exists())
        self.assertTrue(Student.objects.filter(USN='1CS20CS001').exists())
        self.assertTrue(User.objects.filter(username='teacher02user').exists())
        self.assertTrue(User.objects.filter(username='student01user').exists())