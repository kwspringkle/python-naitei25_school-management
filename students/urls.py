from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student index/homepage
    path('', views.index, name='index'),
    
    # Student dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Student logout
    path('logout/', views.student_logout, name='student_logout'),
    
    # Student attendance
    path('<str:student_usn>/attendance/', views.student_attendance, name='attendance'),
    
    # Student marks
    path('<str:student_usn>/marks/', views.student_marks_list, name='marks_list'),
    
    # Student timetable
    path('timetable/<str:class_id>/', views.student_timetable, name='timetable'),
]