from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from datetime import date
from django.utils import timezone
from django.core.exceptions import PermissionDenied
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
        
        # Tạo student
        self.student_user = User.objects.create_user(
            username='student1', email='student1@test.com', password='studentpass123'
        )
        self.student = Student.objects.create(
            user=self.student_user, USN='1CS20CS001', name='Test Student', sex='M',
            DOB=date(2000, 1, 1), address='123 Student St', phone='0987654321',
            class_id=self.test_class
        )
        