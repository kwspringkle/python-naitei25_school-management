from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Dept, Subject, Class, AttendanceRange


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(Dept)
class DeptAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['id', 'name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'shortname', 'dept']
    list_filter = ['dept']
    search_fields = ['id', 'name', 'shortname']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'dept', 'section', 'sem']
    list_filter = ['dept', 'sem']
    search_fields = ['id', 'section']


@admin.register(AttendanceRange)
class AttendanceRangeAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date']
    date_hierarchy = 'start_date'
