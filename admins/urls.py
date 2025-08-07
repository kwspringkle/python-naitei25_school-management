from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),

    # Teaching Assignment URLs
    path('teaching-assignments/', views.teaching_assignments, name='teaching_assignments'),
    path('teaching-assignments/add/', views.add_teaching_assignment, name='add_teaching_assignment'),
    path('teaching-assignments/<int:assignment_id>/edit/', views.edit_teaching_assignment, name='edit_teaching_assignment'),
    path('teaching-assignments/<int:assignment_id>/delete/', views.delete_teaching_assignment, name='delete_teaching_assignment'),
    
    # Timetable URLs
    path('timetable/', views.timetable, name='timetable'),
    path('timetable/add/', views.add_timetable_entry, name='add_timetable_entry'),
    path('timetable/<int:entry_id>/edit/', views.edit_timetable_entry, name='edit_timetable_entry'),
    path('timetable/<int:entry_id>/delete/', views.delete_timetable_entry, name='delete_timetable_entry'),
    
    # Redirect to login by default
    path('', views.admin_login, name='admin_home'),
    # Class URLs
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.add_class, name='add_class'),
    path('classes/<str:class_id>/edit/', views.edit_class, name='edit_class'),
    path('classes/<str:class_id>/delete/', views.delete_class, name='delete_class'),
]
