from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('<slug:teacher_id>/<int:choice>/Classes/',
         views.t_clas, name='t_clas'),
    path('<int:assign_id>/marks_list/',
         views.t_marks_list, name='t_marks_list'),
    path('<int:marks_c_id>/marks_entry/',
         views.t_marks_entry, name='t_marks_entry'),
    path('<int:marks_c_id>/marks_entry/confirm/',
         views.marks_confirm, name='marks_confirm'),
    path('<int:marks_c_id>/Edit_marks/',
         views.edit_marks, name='edit_marks'),
    path('<slug:teacher_id>/t_timetable/',
         views.t_timetable, name='t_timetable'),
    path('<int:ass_c_id>/attendance/',
         views.t_attendance, name='t_attendance'),
    path('<int:ass_c_id>/attendance/confirm/',
         views.confirm, name='att_confirm'),
    path('<int:assign_id>/ClassDates/',
         views.t_class_date, name='t_class_date'),
    path('<int:ass_c_id>/edit_att/', views.edit_att, name='edit_att'),
    path('<int:ass_c_id>/view_att/', views.view_att, name='view_att'),
    path('<int:asst_id>/Free_teachers/',
         views.free_teachers, name='free_teachers'),
]
