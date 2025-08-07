# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext_lazy as _
from admins.models import User
from django.db import transaction
from django.core.paginator import Paginator

# Local application imports
from utils.constant import (
    ADMIN_DATETIME_FORMAT,
    ADMIN_WELCOME_MESSAGE,
    ADMIN_LOGOUT_SUCCESS_MESSAGE,
    PAGE_SIZE
)
from .forms import AdminLoginForm, AddStudentForm, AddTeacherForm, TeachingAssignmentForm, TeachingAssignmentFilterForm, TimetableFilterForm, TimetableForm, ClassForm

# Model imports
from students.models import Student
from teachers.models import Teacher, Assign, AssignTime
from admins.models import User, Dept, Subject, Class



@csrf_protect
def admin_login(request):
    """
    Custom admin login view with form validation and clean data
    """
    # Redirect authenticated admin users
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    # Initialize form
    form = AdminLoginForm(request=request)

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)

        if form.is_valid():
            # Get cleaned data and authenticated user
            user = form.get_user()

            # Login user
            login(request, user)
            messages.success(
                request,
                _(ADMIN_WELCOME_MESSAGE) % {
                    'name': user.get_full_name() or user.username}
            )
            return redirect('admin_dashboard')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    context = {
        'form': form
    }
    return render(request, 'admins/login.html', context)


def admin_dashboard(request):
    """
    Admin dashboard view
    Note: Admin permission check is handled by AdminPermissionMiddleware
    """
    # Basic statistics
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_departments': Dept.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classes': Class.objects.count(),
        'admin_user': request.user,
        'date_format': ADMIN_DATETIME_FORMAT,
    }

    return render(request, 'admins/dashboard.html', context)


def admin_logout(request):
    """
    Admin logout view
    Note: Admin permission check is handled by AdminPermissionMiddleware
    """
    if request.user.is_authenticated and request.user.is_superuser:
        messages.success(request, _(ADMIN_LOGOUT_SUCCESS_MESSAGE))
    logout(request)
    return redirect('admin_login')


def add_student(request):
    """
    Add new student view
    Note: Admin permission check is handled by AdminPermissionMiddleware
    """
    if request.method == 'POST':
        form = AddStudentForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user account
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['name'].split()[0],
                        last_name=' '.join(form.cleaned_data['name'].split()[1:]) if len(
                            form.cleaned_data['name'].split()) > 1 else ''
                    )

                    # Create student profile
                    student = Student.objects.create(
                        user=user,
                        USN=form.cleaned_data['USN'],
                        name=form.cleaned_data['name'],
                        sex=form.cleaned_data['sex'],
                        DOB=form.cleaned_data['DOB'],
                        address=form.cleaned_data['address'],
                        phone=form.cleaned_data['phone'],
                        class_id=form.cleaned_data['class_id']
                    )

                    messages.success(request, _(
                        'Student "{}" has been successfully added.').format(student.name))
                    return redirect('admin_dashboard')

            except Exception as e:
                messages.error(request, _(
                    'Error creating student: {}').format(str(e)))
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = AddStudentForm()

    context = {
        'form': form,
        'title': _('Add Student'),
        'submit_text': _('Add Student'),
        'admin_user': request.user,
    }
    return render(request, 'admins/add_student.html', context)


def add_teacher(request):
    """
    Add new teacher view
    Note: Admin permission check is handled by AdminPermissionMiddleware
    """
    if request.method == 'POST':
        form = AddTeacherForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user account
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['name'].split()[0],
                        last_name=' '.join(form.cleaned_data['name'].split()[1:]) if len(
                            form.cleaned_data['name'].split()) > 1 else ''
                    )

                    # Create teacher profile
                    teacher = Teacher.objects.create(
                        user=user,
                        id=form.cleaned_data['id'],
                        name=form.cleaned_data['name'],
                        sex=form.cleaned_data['sex'],
                        DOB=form.cleaned_data['DOB'],
                        address=form.cleaned_data['address'],
                        phone=form.cleaned_data['phone'],
                        dept=form.cleaned_data['dept']
                    )

                    messages.success(request, _(
                        'Teacher "{}" has been successfully added.').format(teacher.name))
                    return redirect('admin_dashboard')

            except Exception as e:
                messages.error(request, _(
                    'Error creating teacher: {}').format(str(e)))
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = AddTeacherForm()

    context = {
        'form': form,
        'title': _('Add Teacher'),
        'submit_text': _('Add Teacher'),
        'admin_user': request.user,
    }
    return render(request, 'admins/add_teacher.html', context)

@login_required
def teaching_assignments(request):
    """
    View for managing teaching assignments
    """
    # Handle filter form
    filter_form = TeachingAssignmentFilterForm(request.GET)
    assignments = Assign.objects.all()
    
    if filter_form.is_valid():
        teacher = filter_form.cleaned_data.get('teacher')
        subject = filter_form.cleaned_data.get('subject')
        class_id = filter_form.cleaned_data.get('class_id')
        
        if teacher:
            assignments = assignments.filter(teacher=teacher)
        if subject:
            assignments = assignments.filter(subject=subject)
        if class_id:
            assignments = assignments.filter(class_id=class_id)
    
    # Pagination
    paginator = Paginator(assignments, PAGE_SIZE)  # 10 entries per page
    page_number = request.GET.get('page')
    assignments = paginator.get_page(page_number)
    
    context = {
        'assignments': assignments,
        'filter_form': filter_form,
        'admin_user': request.user,
    }
    return render(request, 'admins/teaching_assignments.html', context)

@login_required
@permission_required('assign.add_assign', raise_exception=True)
def add_teaching_assignment(request):
    """
    View for adding a new teaching assignment
    """
    if request.method == 'POST':
        form = TeachingAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Teaching assignment has been added successfully!'))
            return redirect('teaching_assignments')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = TeachingAssignmentForm()
    
    context = {
        'form': form,
        'admin_user': request.user,
        'title': _('Add Teaching Assignment')
    }
    return render(request, 'admins/teaching_assignment_form.html', context)

@login_required
@permission_required('assign.change_assign', raise_exception=True)
def edit_teaching_assignment(request, assignment_id):
    """
    View for editing a teaching assignment
    """
    try:
        assignment = Assign.objects.get(id=assignment_id)
    except Assign.DoesNotExist:
        messages.error(request, _('The teaching assignment does not exist!'))
        return redirect('teaching_assignments')
    
    if request.method == 'POST':
        form = TeachingAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, _('Teaching assignment has been updated successfully!'))
            return redirect('teaching_assignments')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = TeachingAssignmentForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
        'admin_user': request.user,
        'title': _('Edit Teaching Assignment')
    }
    return render(request, 'admins/teaching_assignment_form.html', context)


@login_required
@permission_required('assign.delete_assign', raise_exception=True)
def delete_teaching_assignment(request, assignment_id):
    """
    View for deleting a teaching assignment
    """
    try:
        assignment = Assign.objects.get(id=assignment_id)
        assignment.delete()
        messages.success(request, _('Teaching assignment has been deleted successfully!'))
    except Assign.DoesNotExist:
        messages.error(request, _('The teaching assignment does not exist!'))
    
    return redirect('teaching_assignments')

@login_required
def timetable(request):
    """
    View for managing timetable
    """
    filter_form = TimetableFilterForm(request.GET)
    timetable_entries = AssignTime.objects.select_related(
        'assign__subject', 'assign__teacher', 'assign__class_id'
    )

    if filter_form.is_valid():
        class_id = filter_form.cleaned_data.get('class_id')
        teacher = filter_form.cleaned_data.get('teacher')
        day = filter_form.cleaned_data.get('day')

        if class_id:
            timetable_entries = timetable_entries.filter(assign__class_id=class_id)
        if teacher:
            timetable_entries = timetable_entries.filter(assign__teacher=teacher)
        if day:
            timetable_entries = timetable_entries.filter(day=day)

    context = {
        'timetable_entries': timetable_entries,
        'filter_form': filter_form,
        'admin_user': request.user,
    }
    return render(request, 'admins/timetable.html', context)


@login_required
@permission_required('assign.add_assigntime', raise_exception=True)
def add_timetable_entry(request):
    """
    View for adding new timetable entry
    """
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Timetable entry has been added successfully!'))
            return redirect('timetable')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(error))
    else:
        form = TimetableForm()

    context = {
        'form': form,
        'admin_user': request.user,
        'title': _('Add Timetable Entry')
    }
    return render(request, 'admins/timetable_form.html', context)


@login_required
@permission_required('assign.change_assigntime', raise_exception=True)
def edit_timetable_entry(request, entry_id):
    """
    View for editing timetable entry
    """
    try:
        entry = AssignTime.objects.get(id=entry_id)
    except AssignTime.DoesNotExist:
        messages.error(request, _('The timetable entry does not exist!'))
        return redirect('timetable')

    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, _('Timetable entry has been updated successfully!'))
            return redirect('timetable')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(error))
    else:
        form = TimetableForm(instance=entry)

    context = {
        'form': form,
        'entry': entry,
        'admin_user': request.user,
        'title': _('Edit Timetable Entry')
    }
    return render(request, 'admins/timetable_form.html', context)


@login_required
@permission_required('assign.delete_assigntime', raise_exception=True)
def delete_timetable_entry(request, entry_id):
    """
    View for deleting timetable entry
    """
    try:
        entry = AssignTime.objects.get(id=entry_id)
        entry.delete()
        messages.success(request, _('Timetable entry has been deleted successfully!'))
    except AssignTime.DoesNotExist:
        messages.error(request, _('The timetable entry does not exist!'))

    return redirect('timetable')

@login_required
def class_list(request):
    """
    View for listing all classes with pagination and filtering
    """
    # Handle filter form (optional, you can add a filter form later if needed)
    classes = Class.objects.all().order_by('id')
    
    # Pagination
    paginator = Paginator(classes, PAGE_SIZE)  # Use PAGE_SIZE from constants
    page_number = request.GET.get('page')
    classes_page = paginator.get_page(page_number)
    
    context = {
        'classes': classes_page,
        'admin_user': request.user,
        'title': _('Manage Classes'),
    }
    return render(request, 'admins/class_list.html', context)

@login_required
@permission_required('admins.add_class', raise_exception=True)
def add_class(request):
    """
    View for adding a new class
    """
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Class has been added successfully!'))
                return redirect('class_list')
            except Exception as e:
                messages.error(request, _('Error creating class: {}').format(str(e)))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ClassForm()
    
    context = {
        'form': form,
        'admin_user': request.user,
        'title': _('Add Class'),
        'submit_text': _('Add Class'),
    }
    return render(request, 'admins/class_form.html', context)

@login_required
@permission_required('admins.change_class', raise_exception=True)
def edit_class(request, class_id):
    """
    View for editing a class
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        messages.error(request, _('The class does not exist!'))
        return redirect('class_list')
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Class has been updated successfully!'))
                return redirect('class_list')
            except Exception as e:
                messages.error(request, _('Error updating class: {}').format(str(e)))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ClassForm(instance=class_obj)
    
    context = {
        'form': form,
        'class_obj': class_obj,
        'admin_user': request.user,
        'title': _('Edit Class'),
        'submit_text': _('Update Class'),
    }
    return render(request, 'admins/class_form.html', context)

@login_required
@permission_required('admins.delete_class', raise_exception=True)
def delete_class(request, class_id):
    """
    View for deleting a class
    """
    try:
        class_obj = Class.objects.get(id=class_id)
        class_obj.delete()
        messages.success(request, _('Class has been deleted successfully!'))
    except Class.DoesNotExist:
        messages.error(request, _('The class does not exist!'))
    
    return redirect('class_list')
