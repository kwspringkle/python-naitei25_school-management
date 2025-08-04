# School Management System Constants

# =============================================================================
# FIELD LENGTH CONSTANTS
# =============================================================================
DEPT_ID_MAX_LENGTH = 100
DEPT_NAME_MAX_LENGTH = 200

SUBJECT_ID_MAX_LENGTH = 50
SUBJECT_NAME_MAX_LENGTH = 50
SUBJECT_SHORTNAME_MAX_LENGTH = 50

CLASS_ID_MAX_LENGTH = 100
CLASS_SECTION_MAX_LENGTH = 100

USER_NAME_MAX_LENGTH = 100
USER_ADDRESS_MAX_LENGTH = 200
USER_PHONE_MAX_LENGTH = 15
USER_SEX_MAX_LENGTH = 50

STUDENT_USN_MAX_LENGTH = 100

TEACHER_ID_MAX_LENGTH = 100

ASSIGN_TIME_PERIOD_MAX_LENGTH = 50
ASSIGN_TIME_DAY_MAX_LENGTH = 15

TEST_NAME_MAX_LENGTH = 50

# =============================================================================
# DEFAULT VALUES
# =============================================================================
DEFAULT_SEX = 'Male'
DEFAULT_SUBJECT_SHORTNAME = 'X'
DEFAULT_EMPTY_STRING = ''
DEFAULT_DEPT_ID = 1
DEFAULT_STATUS_FALSE = False
DEFAULT_STATUS_TRUE = True
DEFAULT_ATTENDANCE_STATUS = 0
DEFAULT_MARKS_VALUE = 0

# =============================================================================
# CHOICES CONSTANTS
# =============================================================================

# Gender choices
SEX_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

# Time slot choices
TIME_SLOTS = (
    ('7:30 - 8:30', '7:30 - 8:30'),
    ('8:30 - 9:30', '8:30 - 9:30'),
    ('9:30 - 10:30', '9:30 - 10:30'),
    ('11:00 - 11:50', '11:00 - 11:50'),
    ('11:50 - 12:40', '11:50 - 12:40'),
    ('12:40 - 1:30', '12:40 - 1:30'),
    ('2:30 - 3:30', '2:30 - 3:30'),
    ('3:30 - 4:30', '3:30 - 4:30'),
    ('4:30 - 5:30', '4:30 - 5:30'),
)

# Days of week choices
DAYS_OF_WEEK = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)

# Test name choices
TEST_NAME_CHOICES = (
    ('Internal test 1', 'Internal test 1'),
    ('Internal test 2', 'Internal test 2'),
    ('Internal test 3', 'Internal test 3'),
    ('Event 1', 'Event 1'),
    ('Event 2', 'Event 2'),
    ('Semester End Exam', 'Semester End Exam'),
)

# =============================================================================
# VERBOSE NAMES
# =============================================================================
ATTENDANCE_RANGE_VERBOSE_NAME = "Attendance Range"
ATTENDANCE_RANGE_VERBOSE_NAME_PLURAL = "Attendance Ranges"
CLASSES_VERBOSE_NAME_PLURAL = 'classes'
MARKS_VERBOSE_NAME_PLURAL = 'Marks'
ATTENDANCE_VERBOSE_NAME = 'Attendance'
ATTENDANCE_VERBOSE_NAME_PLURAL = 'Attendance'

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================
MIN_MARKS_VALUE = 0
MAX_MARKS_VALUE = 100

# =============================================================================
# BUSINESS LOGIC CONSTANTS
# =============================================================================

# Attendance calculation constants
ATTENDANCE_MIN_PERCENTAGE = 0.75  # 75% minimum attendance required
ATTENDANCE_CALCULATION_BASE = 0.25  # Base for attendance calculation
PERCENTAGE_MULTIPLIER = 100  # For percentage calculation
ATTENDANCE_ZERO_THRESHOLD = 0  # When total class is 0

# Marks calculation constants
CIE_CALCULATION_LIMIT = 5  # Take first 5 marks for CIE calculation
CIE_DIVISOR = 2  # Divide by 2 for CIE calculation

# Exam marks constants
SEMESTER_END_EXAM_TOTAL_MARKS = 100  # Total marks for semester end exam
OTHER_EXAM_TOTAL_MARKS = 20  # Total marks for other exams

# Filter status values (as strings for query compatibility)
STATUS_TRUE_STRING = 'True'  # String value for True status in filters
STATUS_FALSE_STRING = 'False'  # String value for False status in filters

# Exam type names
SEMESTER_END_EXAM_NAME = 'Semester End Exam'  # Name for semester end exam

# Precision constants
PERCENTAGE_DECIMAL_PLACES = 2  # Number of decimal places for percentage calculations

# Model attribute names for hasattr checks
STUDENT_ATTRIBUTE = 'student'  # Attribute name for student check
TEACHER_ATTRIBUTE = 'teacher'  # Attribute name for teacher check

# Django model string references
ADMINS_USER_MODEL = 'admins.User'  # Reference to User model
ADMINS_CLASS_MODEL = 'admins.Class'  # Reference to Class model  
ADMINS_DEPT_MODEL = 'admins.Dept'  # Reference to Dept model
ADMINS_SUBJECT_MODEL = 'admins.Subject'  # Reference to Subject model
STUDENTS_STUDENT_SUBJECT_MODEL = 'students.StudentSubject'  # Reference to StudentSubject model
TEACHERS_ATTENDANCE_CLASS_MODEL = 'teachers.AttendanceClass'  # Reference to AttendanceClass model

# Choice index constants
FIRST_CHOICE_INDEX = 0  # Index for first choice in choices tuple

# Legacy/Comment constants  
DEFAULT_MANY_TO_MANY_ID = 1  # Default ID for ManyToManyField (legacy comment)

# =============================================================================
# DATE FORMAT CONSTANTS
# =============================================================================
ADMIN_DATETIME_FORMAT = "d/m/Y H:i"  # Format for displaying dates in admin interface
ADMIN_DATE_FORMAT = "d/m/Y"  # Format for displaying dates only
ADMIN_TIME_FORMAT = "H:i"  # Format for displaying time only

# =============================================================================
# ADMIN FORMS CONSTANTS
# =============================================================================

# Form field length constants
ADMIN_USERNAME_MAX_LENGTH = 150
ADMIN_USERNAME_MIN_LENGTH = 8
ADMIN_PASSWORD_MIN_LENGTH = 8

# Form field CSS classes
FORM_CONTROL_CLASS = 'form-control'

# Form field IDs
USERNAME_FIELD_ID = 'username'
PASSWORD_FIELD_ID = 'password'

# Form field HTML attributes
REQUIRED_ATTRIBUTE = True

# Form validation error messages
ADMIN_USERNAME_MIN_LENGTH_ERROR = 'Username must be at least {} characters long.'
ADMIN_PASSWORD_MIN_LENGTH_ERROR = 'Password must be at least {} characters long.'
ADMIN_INVALID_CREDENTIALS_ERROR = 'Invalid username or password.'
ADMIN_INACTIVE_ACCOUNT_ERROR = 'This account is inactive.'
ADMIN_NO_PERMISSION_ERROR = 'You do not have permission to access the admin area.'

# Form field placeholders (translation keys)
USERNAME_PLACEHOLDER = 'Username'
PASSWORD_PLACEHOLDER = 'Password'

# Form field labels (translation keys)
USERNAME_LABEL = 'Username'
PASSWORD_LABEL = 'Password'

# Success/Info messages
ADMIN_WELCOME_MESSAGE = 'Welcome %(name)s!'
ADMIN_LOGOUT_SUCCESS_MESSAGE = 'You have been logged out successfully.'

# Admin middleware messages
ADMIN_LOGIN_REQUIRED_MESSAGE = 'Please login to access the admin area.'
ADMIN_PERMISSION_REQUIRED_MESSAGE = 'You do not have permission to access the admin area.'

# Admin path constants
ADMIN_BASE_PATH = '/admin/'
ADMIN_URL_PATTERN_TEMPLATE = r'^(/({lang_pattern}))?/admin/'

# Exempt URL patterns for admin middleware
ADMIN_EXEMPT_URL_PATTERNS = [
    '/i18n/',  # Django i18n URLs
    '/django-admin/',  # Django default admin
    '/static/',  # Static files
    '/media/',  # Media files
]

# Default language if settings.LANGUAGES is not configured
DEFAULT_LANGUAGE_CODE = 'en'
DEFAULT_LANGUAGE_NAME = 'English'

# =============================================================================
# UNIFIED AUTHENTICATION CONSTANTS
# =============================================================================

# URL names for redirects
ADMIN_DASHBOARD_URL = 'admin_dashboard'
TEACHER_DASHBOARD_URL = 'teacher_dashboard'
STUDENT_DASHBOARD_URL = 'student_dashboard'
UNIFIED_LOGIN_URL = 'unified_login'

# Template paths
UNIFIED_LOGIN_TEMPLATE = 'common/login.html'

# User attribute names
IS_TEACHER_ATTRIBUTE = 'is_teacher'
IS_STUDENT_ATTRIBUTE = 'is_student'

# Welcome message templates
ADMIN_WELCOME_MSG_TEMPLATE = 'Welcome {}! (Administrator)'
TEACHER_WELCOME_MSG_TEMPLATE = 'Welcome {}! (Teacher)'
STUDENT_WELCOME_MSG_TEMPLATE = 'Welcome {}! (Student)'

# Error messages
UNIFIED_NO_PERMISSION_ERROR = 'Your account does not have permission to access this system.'
UNIFIED_INVALID_ROLE_ERROR = 'Invalid user role'
UNIFIED_FORM_ERRORS_MESSAGE = 'Please correct the errors below.'

# Success messages
UNIFIED_LOGOUT_SUCCESS_MSG_TEMPLATE = 'Goodbye {}! You have been logged out successfully.'
UNIFIED_LOGOUT_SUCCESS_MSG_ANONYMOUS = 'You have been logged out successfully.'

# Form context keys
FORM_CONTEXT_KEY = 'form'
TITLE_CONTEXT_KEY = 'title'
LOGIN_TITLE = 'Login'

# =============================================================================
# STUDENTS FORM CONSTANTS
# =============================================================================

# Field length constants
STUDENT_USERNAME_MAX_LENGTH = 254

# Student validation error messages
STUDENT_INVALID_CREDENTIALS_ERROR = 'Invalid student credentials'

# Student attribute names  
STUDENT_IS_STUDENT_ATTRIBUTE = 'is_student'

# =============================================================================
# TEACHERS FORM CONSTANTS
# =============================================================================

# Field length constants
TEACHER_USERNAME_MAX_LENGTH = 254

# Teacher validation error messages
TEACHER_INVALID_CREDENTIALS_ERROR = 'Invalid teacher credentials'

# Teacher attribute names
TEACHER_IS_TEACHER_ATTRIBUTE = 'is_teacher'

# =============================================================================
# DATABASE CONSTRAINTS
# =============================================================================
# Note: ON_DELETE_RESTRICT will be imported from django.db.models.RESTRICT
# in each model file to maintain proper Django constraint behavior
