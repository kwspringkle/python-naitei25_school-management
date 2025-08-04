from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Student logout
    path('logout/', views.student_logout, name='student_logout'),
]