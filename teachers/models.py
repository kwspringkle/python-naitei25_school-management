from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.constant import (
    # Choices
    SEX_CHOICES, TIME_SLOTS, DAYS_OF_WEEK, TEST_NAME_CHOICES,
    # Field Lengths
    TEACHER_ID_MAX_LENGTH, USER_NAME_MAX_LENGTH, USER_SEX_MAX_LENGTH,
    USER_ADDRESS_MAX_LENGTH, USER_PHONE_MAX_LENGTH,
    ASSIGN_TIME_PERIOD_MAX_LENGTH, ASSIGN_TIME_DAY_MAX_LENGTH,
    TEST_NAME_MAX_LENGTH,
    # Default Values
    DEFAULT_SEX, DEFAULT_EMPTY_STRING, DEFAULT_DEPT_ID,
    DEFAULT_STATUS_FALSE, DEFAULT_ATTENDANCE_STATUS, DEFAULT_MARKS_VALUE,
    # Business Logic Constants
    SEMESTER_END_EXAM_TOTAL_MARKS, OTHER_EXAM_TOTAL_MARKS, SEMESTER_END_EXAM_NAME,
    FIRST_CHOICE_INDEX, TEACHER_ATTRIBUTE, ADMINS_USER_MODEL, ADMINS_DEPT_MODEL,
    ADMINS_CLASS_MODEL, ADMINS_SUBJECT_MODEL, STUDENTS_STUDENT_SUBJECT_MODEL,
    # Validation Constants
    MIN_MARKS_VALUE, MAX_MARKS_VALUE,
    # Verbose Names
    ATTENDANCE_VERBOSE_NAME, ATTENDANCE_VERBOSE_NAME_PLURAL
)


class Teacher(models.Model):
    user = models.OneToOneField(
        ADMINS_USER_MODEL, on_delete=models.RESTRICT, null=True)
    id = models.CharField(primary_key=True, max_length=TEACHER_ID_MAX_LENGTH)
    dept = models.ForeignKey(
        ADMINS_DEPT_MODEL, on_delete=models.RESTRICT, default=DEFAULT_DEPT_ID)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    sex = models.CharField(max_length=USER_SEX_MAX_LENGTH, choices=SEX_CHOICES, default=DEFAULT_SEX)
    DOB = models.DateField(default=DEFAULT_EMPTY_STRING)
    address = models.TextField(max_length=USER_ADDRESS_MAX_LENGTH, default=DEFAULT_EMPTY_STRING)
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, default=DEFAULT_EMPTY_STRING)

    def __str__(self):
        return self.name


class Assign(models.Model):
    class_id = models.ForeignKey(ADMINS_CLASS_MODEL, on_delete=models.RESTRICT)
    subject = models.ForeignKey(ADMINS_SUBJECT_MODEL, on_delete=models.RESTRICT)
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT)

    class Meta:
        unique_together = (('subject', 'class_id', 'teacher'),)

    def __str__(self):
        cl = self.class_id
        sname = self.subject
        te = self.teacher
        return '%s : %s : %s' % (te.name, sname.shortname, cl)


class AssignTime(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.RESTRICT)
    period = models.CharField(max_length=ASSIGN_TIME_PERIOD_MAX_LENGTH, choices=TIME_SLOTS, default=DEFAULT_EMPTY_STRING)
    day = models.CharField(max_length=ASSIGN_TIME_DAY_MAX_LENGTH, choices=DAYS_OF_WEEK)

    def __str__(self):
        return f"{self.assign} - {self.day} {self.period}"


class AttendanceClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.RESTRICT)
    date = models.DateField()
    status = models.IntegerField(default=DEFAULT_ATTENDANCE_STATUS)

    class Meta:
        verbose_name = ATTENDANCE_VERBOSE_NAME
        verbose_name_plural = ATTENDANCE_VERBOSE_NAME_PLURAL

    def __str__(self):
        return f"{self.assign} - {self.date}"


class Marks(models.Model):
    student_subject = models.ForeignKey(
        STUDENTS_STUDENT_SUBJECT_MODEL, on_delete=models.RESTRICT)
    name = models.CharField(
        max_length=TEST_NAME_MAX_LENGTH, choices=TEST_NAME_CHOICES, default=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][FIRST_CHOICE_INDEX])
    marks1 = models.IntegerField(default=DEFAULT_MARKS_VALUE, validators=[
                                 MinValueValidator(MIN_MARKS_VALUE), MaxValueValidator(MAX_MARKS_VALUE)])

    class Meta:
        unique_together = (('student_subject', 'name'),)

    @property
    def total_marks(self):
        if self.name == SEMESTER_END_EXAM_NAME:
            return SEMESTER_END_EXAM_TOTAL_MARKS
        return OTHER_EXAM_TOTAL_MARKS

    def __str__(self):
        return f"{self.student_subject} - {self.name}: {self.marks1}"


class ExamSession(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.RESTRICT)
    name = models.CharField(
        max_length=TEST_NAME_MAX_LENGTH, choices=TEST_NAME_CHOICES, default=TEST_NAME_CHOICES[FIRST_CHOICE_INDEX][FIRST_CHOICE_INDEX])
    status = models.BooleanField(default=DEFAULT_STATUS_FALSE)

    class Meta:
        unique_together = (('assign', 'name'),)

    @property
    def total_marks(self):
        if self.name == SEMESTER_END_EXAM_NAME:
            return SEMESTER_END_EXAM_TOTAL_MARKS
        return OTHER_EXAM_TOTAL_MARKS

    def __str__(self):
        return f"{self.assign} - {self.name}"
