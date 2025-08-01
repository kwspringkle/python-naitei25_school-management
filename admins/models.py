from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from datetime import timedelta
from utils.constant import (
    # Choices
    SEX_CHOICES, TIME_SLOTS, DAYS_OF_WEEK, TEST_NAME_CHOICES,
    # Field Lengths
    DEPT_ID_MAX_LENGTH, DEPT_NAME_MAX_LENGTH,
    SUBJECT_ID_MAX_LENGTH, SUBJECT_NAME_MAX_LENGTH, SUBJECT_SHORTNAME_MAX_LENGTH,
    CLASS_ID_MAX_LENGTH, CLASS_SECTION_MAX_LENGTH,
    # Default Values
    DEFAULT_SUBJECT_SHORTNAME,
    # Verbose Names
    ATTENDANCE_RANGE_VERBOSE_NAME, ATTENDANCE_RANGE_VERBOSE_NAME_PLURAL,
    CLASSES_VERBOSE_NAME_PLURAL,
    # Model attribute names
    STUDENT_ATTRIBUTE, TEACHER_ATTRIBUTE,
    # Legacy constants
    DEFAULT_MANY_TO_MANY_ID
)


class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, STUDENT_ATTRIBUTE):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, TEACHER_ATTRIBUTE):
            return True
        return False


class Dept(models.Model):
    id = models.CharField(primary_key=True, max_length=DEPT_ID_MAX_LENGTH)
    name = models.CharField(max_length=DEPT_NAME_MAX_LENGTH)

    def __str__(self):
        return self.name


class Subject(models.Model):
    dept = models.ForeignKey(Dept, on_delete=models.RESTRICT)
    id = models.CharField(primary_key=True, max_length=SUBJECT_ID_MAX_LENGTH)
    name = models.CharField(max_length=SUBJECT_NAME_MAX_LENGTH)
    shortname = models.CharField(
        max_length=SUBJECT_SHORTNAME_MAX_LENGTH, default=DEFAULT_SUBJECT_SHORTNAME)

    def __str__(self):
        return self.name


class Class(models.Model):
    # subjects = models.ManyToManyField(Subject, default=DEFAULT_MANY_TO_MANY_ID)
    id = models.CharField(primary_key=True, max_length=CLASS_ID_MAX_LENGTH)
    dept = models.ForeignKey(Dept, on_delete=models.RESTRICT)
    section = models.CharField(max_length=CLASS_SECTION_MAX_LENGTH)
    sem = models.IntegerField()

    class Meta:
        verbose_name_plural = CLASSES_VERBOSE_NAME_PLURAL

    def __str__(self):
        d = Dept.objects.get(name=self.dept)
        return '%s : %d %s' % (d.name, self.sem, self.section)


class AttendanceRange(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.start_date} to {self.end_date}"

    class Meta:
        verbose_name = ATTENDANCE_RANGE_VERBOSE_NAME
        verbose_name_plural = ATTENDANCE_RANGE_VERBOSE_NAME_PLURAL
