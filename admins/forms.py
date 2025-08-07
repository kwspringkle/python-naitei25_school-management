from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Import constants
from utils.constant import (
    ADMIN_USERNAME_MAX_LENGTH,
    ADMIN_USERNAME_MIN_LENGTH,
    ADMIN_PASSWORD_MIN_LENGTH,
    FORM_CONTROL_CLASS,
    USERNAME_FIELD_ID,
    PASSWORD_FIELD_ID,
    REQUIRED_ATTRIBUTE,
    ADMIN_USERNAME_MIN_LENGTH_ERROR,
    ADMIN_PASSWORD_MIN_LENGTH_ERROR,
    ADMIN_INVALID_CREDENTIALS_ERROR,
    ADMIN_INACTIVE_ACCOUNT_ERROR,
    ADMIN_NO_PERMISSION_ERROR,
    USERNAME_PLACEHOLDER,
    PASSWORD_PLACEHOLDER,
    USERNAME_LABEL,
    PASSWORD_LABEL,
    # Form field constants
    STUDENT_USN_MAX_LENGTH, USER_NAME_MAX_LENGTH, USER_SEX_MAX_LENGTH,
    USER_ADDRESS_MAX_LENGTH, USER_PHONE_MAX_LENGTH, TEACHER_ID_MAX_LENGTH,
    SEX_CHOICES, DEFAULT_SEX,
    DAYS_OF_WEEK, TIME_SLOTS
)

# Import models
from students.models import Student
from teachers.models import Teacher, Assign, AssignTime
from admins.models import User, Dept, Class, Subject


class UnifiedLoginForm(forms.Form):
    """
    Unified login form for all user types (Admin, Teacher, Student)
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Username'),
            'required': True,
            'id': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Password'),
            'required': True,
            'id': 'password'
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        Initialize form with request object
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validate user credentials for any user type
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Authenticate user
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if self.user_cache is None:
                raise ValidationError(_(ADMIN_INVALID_CREDENTIALS_ERROR))

            if not self.user_cache.is_active:
                raise ValidationError(_(ADMIN_INACTIVE_ACCOUNT_ERROR))

        return cleaned_data

    def get_user(self):
        """
        Return authenticated user
        """
        return self.user_cache



class AdminLoginForm(forms.Form):
    """
    Custom admin login form with data validation and cleaning
    """
    username = forms.CharField(
        max_length=ADMIN_USERNAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'id': USERNAME_FIELD_ID,
            'placeholder': _(USERNAME_PLACEHOLDER),
            'required': REQUIRED_ATTRIBUTE
        }),
        label=_(USERNAME_LABEL)
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'id': PASSWORD_FIELD_ID,
            'placeholder': _(PASSWORD_PLACEHOLDER),
            'required': REQUIRED_ATTRIBUTE
        }),
        label=_(PASSWORD_LABEL)
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        Initialize form with request object for authentication
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_username(self):
        """
        Clean and validate username field
        """
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip().lower()
            if len(username) < ADMIN_USERNAME_MIN_LENGTH:
                raise ValidationError(
                    _(ADMIN_USERNAME_MIN_LENGTH_ERROR.format(ADMIN_USERNAME_MIN_LENGTH)))
        return username

    def clean_password(self):
        """
        Clean and validate password field
        """
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < ADMIN_PASSWORD_MIN_LENGTH:
                raise ValidationError(
                    _(ADMIN_PASSWORD_MIN_LENGTH_ERROR.format(ADMIN_PASSWORD_MIN_LENGTH)))
        return password

    def clean(self):
        """
        Validate the entire form and authenticate user
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Authenticate user
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if self.user_cache is None:
                raise ValidationError(_(ADMIN_INVALID_CREDENTIALS_ERROR))

            if not self.user_cache.is_active:
                raise ValidationError(_(ADMIN_INACTIVE_ACCOUNT_ERROR))

            if not self.user_cache.is_superuser:
                raise ValidationError(
                    _(ADMIN_NO_PERMISSION_ERROR))

        return cleaned_data

    def get_user(self):
        """
        Return authenticated user
        """
        return self.user_cache


class AddStudentForm(forms.ModelForm):
    """
    Form for adding new students
    """
    # User account fields
    username = forms.CharField(
        max_length=ADMIN_USERNAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter username'),
            'required': True
        }),
        label=_('Username')
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter email address'),
            'required': True
        }),
        label=_('Email')
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter password'),
            'required': True
        }),
        label=_('Password'),
        min_length=ADMIN_PASSWORD_MIN_LENGTH
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Confirm password'),
            'required': True
        }),
        label=_('Confirm Password')
    )

    # Student profile fields
    USN = forms.CharField(
        max_length=STUDENT_USN_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter USN'),
            'required': True
        }),
        label=_('USN')
    )

    name = forms.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter full name'),
            'required': True
        }),
        label=_('Full Name')
    )

    sex = forms.ChoiceField(
        choices=SEX_CHOICES,
        widget=forms.Select(attrs={
            'class': FORM_CONTROL_CLASS,
            'required': True
        }),
        label=_('Gender'),
        initial=DEFAULT_SEX
    )

    DOB = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'type': 'date',
            'required': True
        }),
        label=_('Date of Birth')
    )

    address = forms.CharField(
        max_length=USER_ADDRESS_MAX_LENGTH,
        widget=forms.Textarea(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter address'),
            'rows': 3
        }),
        label=_('Address'),
        required=False
    )

    phone = forms.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter phone number')
        }),
        label=_('Phone Number'),
        required=False
    )

    class_id = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': FORM_CONTROL_CLASS,
            'required': True
        }),
        label=_('Class'),
        empty_label=_('Select a class')
    )

    class Meta:
        model = Student
        fields = ['USN', 'name', 'sex', 'DOB', 'address', 'phone', 'class_id']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError(_('Passwords do not match'))
        return password_confirm

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Username already exists'))
        return username

    def clean_USN(self):
        usn = self.cleaned_data.get('USN')
        if Student.objects.filter(USN=usn).exists():
            raise ValidationError(_('USN already exists'))
        return usn

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Email already exists'))
        return email


class AddTeacherForm(forms.ModelForm):
    """
    Form for adding new teachers
    """
    # User account fields
    username = forms.CharField(
        max_length=ADMIN_USERNAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter username'),
            'required': True
        }),
        label=_('Username')
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter email address'),
            'required': True
        }),
        label=_('Email')
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter password'),
            'required': True
        }),
        label=_('Password'),
        min_length=ADMIN_PASSWORD_MIN_LENGTH
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Confirm password'),
            'required': True
        }),
        label=_('Confirm Password')
    )

    # Teacher profile fields
    id = forms.CharField(
        max_length=TEACHER_ID_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Auto-generated (e.g., T001)'),
            'readonly': True
        }),
        label=_('Teacher ID'),
        required=False
    )

    name = forms.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter full name'),
            'required': True
        }),
        label=_('Full Name')
    )

    sex = forms.ChoiceField(
        choices=SEX_CHOICES,
        widget=forms.Select(attrs={
            'class': FORM_CONTROL_CLASS,
            'required': True
        }),
        label=_('Gender'),
        initial=DEFAULT_SEX
    )

    DOB = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'type': 'date',
            'required': True
        }),
        label=_('Date of Birth')
    )

    address = forms.CharField(
        max_length=USER_ADDRESS_MAX_LENGTH,
        widget=forms.Textarea(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter address'),
            'rows': 3
        }),
        label=_('Address'),
        required=False
    )

    phone = forms.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _('Enter phone number')
        }),
        label=_('Phone Number'),
        required=False
    )

    dept = forms.ModelChoiceField(
        queryset=Dept.objects.all(),
        widget=forms.Select(attrs={
            'class': FORM_CONTROL_CLASS,
            'required': True
        }),
        label=_('Department'),
        empty_label=_('Select a department')
    )

    class Meta:
        model = Teacher
        fields = ['id', 'name', 'sex', 'DOB', 'address', 'phone', 'dept']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError(_('Passwords do not match'))
        return password_confirm

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Username already exists'))
        return username

    def clean_id(self):
        """Auto-generate Teacher ID if not provided"""
        teacher_id = self.cleaned_data.get('id')
        
        # If no ID provided, generate automatically
        if not teacher_id:
            # Find the highest existing teacher ID number
            last_teacher = Teacher.objects.filter(
                id__startswith='T'
            ).order_by('-id').first()
            
            if last_teacher:
                # Extract number from last ID (e.g., 'T003' -> 3)
                try:
                    last_number = int(last_teacher.id[1:])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            # Generate new ID with format T001, T002, etc.
            teacher_id = f'T{new_number:03d}'
        
        # Check if the generated/provided ID already exists
        if Teacher.objects.filter(id=teacher_id).exists():
            # If exists, find next available ID
            counter = 1
            while Teacher.objects.filter(id=f'T{counter:03d}').exists():
                counter += 1
            teacher_id = f'T{counter:03d}'
        
        return teacher_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Email already exists'))
        return email

class TeachingAssignmentForm(forms.ModelForm):
    """
    Form for managing teaching assignments
    """
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label=_('Teacher')
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label=_('Subject')
    )

    class_id = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label=_('Class')
    )

    class Meta:
        model = Assign
        fields = ['teacher', 'subject', 'class_id']
        labels = {
            'teacher': _('Teacher'),
            'subject': _('Subject'),
            'class_id': _('Class')
        }

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('teacher')
        subject = cleaned_data.get('subject')
        class_id = cleaned_data.get('class_id')

        if teacher and subject and class_id:
            if Assign.objects.filter(
                teacher=teacher,
                subject=subject,
                class_id=class_id
            ).exists():
                raise forms.ValidationError(
                    _('This assignment already exists!')
                )

        return cleaned_data


class TeachingAssignmentFilterForm(forms.Form):
    """
    Form for filtering teaching assignments
    """
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('Select teacher')
        }),
        label=_('Teacher')
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('Select subject')
        }),
        label=_('Subject')
    )

    class_id = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('Select class')
        }),
        label=_('Class')
    )

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['id', 'dept', 'section', 'sem', 'is_active']
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control'}),
            'dept': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'sem': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'id': 'Class ID',
            'dept': 'Department',
            'section': 'Section',
            'sem': 'Semester',
            'is_active': 'Active',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nếu đang update (tức là đã có instance tồn tại), khóa trường 'id'
        if self.instance and self.instance.pk:
            self.fields['id'].disabled = True
            
    def clean_sem(self):
        sem = self.cleaned_data['sem']
        if sem < 1 or sem > 8:
            raise forms.ValidationError("Semester must be between 1 and 8.")
        return sem



class TimetableForm(forms.ModelForm):
    """
    Form for managing timetable
    """
    assign = forms.ModelChoiceField(
        queryset=Assign.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label=_('Teaching Assignment')
    )
    
    period = forms.ChoiceField(
        choices=TIME_SLOTS,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label=_('Period')
    )
    
    day = forms.ChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label=_('Day of Week')
    )

    class Meta:
        model = AssignTime
        fields = ['assign', 'period', 'day']
        labels = {
            'assign': _('Teaching Assignment'),
            'period': _('Period'),
            'day': _('Day of Week')
        }

    def clean(self):
        cleaned_data = super().clean()
        assign = cleaned_data.get('assign')
        period = cleaned_data.get('period')
        day = cleaned_data.get('day')

        if assign and period and day:
            if AssignTime.objects.filter(
                assign=assign,
                period=period,
                day=day
            ).exists():
                raise forms.ValidationError(
                    _('This timetable entry already exists!')
                )

            if AssignTime.objects.filter(
                period=period,
                day=day
            ).exclude(assign=assign).exists():
                raise forms.ValidationError(
                    _('This time slot is already occupied by another assignment!')
                )

        return cleaned_data

class TimetableFilterForm(forms.Form):
    """
    Form for filtering timetable
    """
    class_id = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('Select class')
        }),
        label=_('Class')
    )

    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('Select teacher')
        }),
        label=_('Teacher')
    )

    day = forms.ChoiceField(
        choices=[('', _('All'))] + list(DAYS_OF_WEEK),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Day of Week')
    )
