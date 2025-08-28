from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.constant import (
    # Choices
    SEX_CHOICES,
    # Field Lengths
    STUDENT_USN_MAX_LENGTH, USER_NAME_MAX_LENGTH, USER_SEX_MAX_LENGTH,
    USER_ADDRESS_MAX_LENGTH, USER_PHONE_MAX_LENGTH,
    # Default Values
    DEFAULT_SEX, DEFAULT_EMPTY_STRING, DEFAULT_DEPT_ID, DEFAULT_STATUS_TRUE,
    # Business Logic Constants
    ATTENDANCE_MIN_PERCENTAGE, ATTENDANCE_CALCULATION_BASE, PERCENTAGE_MULTIPLIER,
    ATTENDANCE_ZERO_THRESHOLD, CIE_CALCULATION_LIMIT, CIE_DIVISOR, STATUS_TRUE_STRING,
    PERCENTAGE_DECIMAL_PLACES, STUDENT_ATTRIBUTE, ADMINS_USER_MODEL, ADMINS_CLASS_MODEL,
    ADMINS_SUBJECT_MODEL, TEACHERS_ATTENDANCE_CLASS_MODEL,
    # Verbose Names
    MARKS_VERBOSE_NAME_PLURAL
)


class Student(models.Model):
    user = models.OneToOneField(
        ADMINS_USER_MODEL, on_delete=models.RESTRICT, null=True)
    class_id = models.ForeignKey(
        ADMINS_CLASS_MODEL, on_delete=models.RESTRICT, default=DEFAULT_DEPT_ID)
    USN = models.CharField(primary_key=True, max_length=STUDENT_USN_MAX_LENGTH)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    sex = models.CharField(max_length=USER_SEX_MAX_LENGTH, choices=SEX_CHOICES, default=DEFAULT_SEX)
    DOB = models.DateField(default=DEFAULT_EMPTY_STRING)
    address = models.TextField(max_length=USER_ADDRESS_MAX_LENGTH, default=DEFAULT_EMPTY_STRING)
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, default=DEFAULT_EMPTY_STRING)

    def __str__(self):
        return self.name


class StudentSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    subject = models.ForeignKey(ADMINS_SUBJECT_MODEL, on_delete=models.RESTRICT)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = (('student', 'subject'),)
        verbose_name_plural = MARKS_VERBOSE_NAME_PLURAL

    def __str__(self):
        student_name = Student.objects.get(name=self.student)
        subject_name = self.subject
        return '%s : %s' % (student_name.name, subject_name.shortname)

    def get_cie(self):
        marks_list = self.marks_set.all()
        m = []
        for mk in marks_list:
            m.append(mk.marks1)
        cie = math.ceil(sum(m[:CIE_CALCULATION_LIMIT]) / CIE_DIVISOR)
        return cie

    def get_attendance(self):
        try:
            # Try to get from AttendanceTotal first
            a = AttendanceTotal.objects.get(
                student=self.student, subject=self.subject)
            return a.attendance
        except AttendanceTotal.DoesNotExist:
            # If AttendanceTotal doesn't exist, calculate directly from Attendance
            total_class = Attendance.objects.filter(
                subject=self.subject, student=self.student).count()
            att_class = Attendance.objects.filter(
                subject=self.subject, student=self.student, status=True).count()
            
            if total_class == 0:
                return 0
            else:
                attendance = round(att_class / total_class * 100, 2)
                return attendance


class Attendance(models.Model):
    subject = models.ForeignKey(ADMINS_SUBJECT_MODEL, on_delete=models.RESTRICT)
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    attendanceclass = models.ForeignKey(
        TEACHERS_ATTENDANCE_CLASS_MODEL, on_delete=models.RESTRICT, default=DEFAULT_DEPT_ID)
    date = models.DateField(default=DEFAULT_EMPTY_STRING)
    status = models.BooleanField(default=DEFAULT_STATUS_TRUE)

    def __str__(self):
        student_name = Student.objects.get(name=self.student)
        subject_name = self.subject
        return '%s : %s' % (student_name.name, subject_name.shortname)


class AttendanceTotal(models.Model):
    subject = models.ForeignKey(ADMINS_SUBJECT_MODEL, on_delete=models.RESTRICT)
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)

    class Meta:
        unique_together = (('student', 'subject'),)

    @property
    def att_class(self):
        stud = Student.objects.get(name=self.student)
        sname = self.subject
        att_class = Attendance.objects.filter(
            subject=sname, student=stud, status=STATUS_TRUE_STRING).count()
        return att_class

    @property
    def total_class(self):
        stud = Student.objects.get(name=self.student)
        sname = self.subject
        total_class = Attendance.objects.filter(
            subject=sname, student=stud).count()
        return total_class

    @property
    def attendance(self):
        stud = Student.objects.get(name=self.student)
        sname = self.subject
        total_class = Attendance.objects.filter(
            subject=sname, student=stud).count()
        att_class = Attendance.objects.filter(
            subject=sname, student=stud, status=STATUS_TRUE_STRING).count()
        if total_class == ATTENDANCE_ZERO_THRESHOLD:
            attendance = ATTENDANCE_ZERO_THRESHOLD
        else:
            attendance = round(att_class / total_class * PERCENTAGE_MULTIPLIER, PERCENTAGE_DECIMAL_PLACES)
        return attendance

    @property
    def classes_to_attend(self):
        stud = Student.objects.get(name=self.student)
        subj = self.subject
        total_class = Attendance.objects.filter(
            subject=subj, student=stud).count()
        att_class = Attendance.objects.filter(
            subject=subj, student=stud, status=STATUS_TRUE_STRING).count()
        cta = math.ceil((ATTENDANCE_MIN_PERCENTAGE * total_class - att_class) / ATTENDANCE_CALCULATION_BASE)
        if cta < ATTENDANCE_ZERO_THRESHOLD:
            return ATTENDANCE_ZERO_THRESHOLD
        return cta
