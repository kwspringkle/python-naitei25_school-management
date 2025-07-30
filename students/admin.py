from django.contrib import admin
from .models import Student, StudentSubject, Attendance, AttendanceTotal


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['USN', 'name', 'sex', 'DOB', 'class_id']
    list_filter = ['sex', 'class_id', 'DOB']
    search_fields = ['USN', 'name']
    date_hierarchy = 'DOB'


@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'get_cie', 'get_attendance']
    list_filter = ['subject']
    search_fields = ['student__name', 'subject__name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status']
    list_filter = ['subject', 'status', 'date']
    search_fields = ['student__name', 'subject__name']
    date_hierarchy = 'date'


@admin.register(AttendanceTotal)
class AttendanceTotalAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject',
                    'attendance', 'att_class', 'total_class']
    list_filter = ['subject']
    search_fields = ['student__name', 'subject__name']
