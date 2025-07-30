from django.contrib import admin
from .models import Teacher, Assign, AssignTime, AttendanceClass, Marks, ExamSession


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sex', 'DOB', 'dept']
    list_filter = ['sex', 'dept', 'DOB']
    search_fields = ['id', 'name']
    date_hierarchy = 'DOB'


@admin.register(Assign)
class AssignAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'class_id']
    list_filter = ['teacher', 'subject', 'class_id']
    search_fields = ['teacher__name', 'subject__name']


@admin.register(AssignTime)
class AssignTimeAdmin(admin.ModelAdmin):
    list_display = ['assign', 'day', 'period']
    list_filter = ['day', 'period']
    search_fields = ['assign__teacher__name', 'assign__subject__name']


@admin.register(AttendanceClass)
class AttendanceClassAdmin(admin.ModelAdmin):
    list_display = ['assign', 'date', 'status']
    list_filter = ['date', 'status']
    search_fields = ['assign__teacher__name', 'assign__subject__name']
    date_hierarchy = 'date'


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ['student_subject', 'name', 'marks1', 'total_marks']
    list_filter = ['name']
    search_fields = ['student_subject__student__name',
                     'student_subject__subject__name']


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['assign', 'name', 'status', 'total_marks']
    list_filter = ['name', 'status']
    search_fields = ['assign__teacher__name', 'assign__subject__name']
