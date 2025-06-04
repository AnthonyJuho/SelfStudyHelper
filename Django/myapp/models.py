# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CheckList(models.Model):
    grade = models.IntegerField()
    id = models.CharField(max_length=10)
    name = models.CharField(primary_key=True, max_length=100)
    content = models.CharField(max_length=100)
    check_date = models.DateField()
    # check_time = models.TimeField()
    class_field = models.CharField(db_column='class', max_length=30)  # Field renamed because it was a Python reserved word.
    class_teacher = models.CharField(max_length=100)
    message = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'check_list'
        unique_together = (('name', 'check_date'),)



class LeaveList(models.Model):
    num = models.IntegerField()
    aa_sabun = models.CharField(max_length=30)
    aa_kor_nm = models.CharField(max_length=100)
    reg_date = models.DateTimeField()
    ref_tea_sabun = models.CharField(max_length=30)
    gubun = models.IntegerField()
    hakbun = models.CharField(primary_key=True, max_length=10)
    kor_nm = models.CharField(max_length=100)
    gubun_nm = models.CharField(max_length=30)
    symptom = models.CharField(max_length=100, blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    approval_id = models.CharField(max_length=100)
    approval_nm = models.CharField(max_length=100)
    status = models.IntegerField()
    status_style = models.CharField(max_length=100)
    status_nm = models.CharField(max_length=100)
    ref_kor_nm = models.CharField(max_length=100)
    buseo = models.CharField(max_length=30)
    all_check = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'leave_list'


class NightClass(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    class_field = models.CharField(db_column='class', max_length=30)  # Field renamed because it was a Python reserved word.
    class_day = models.CharField(max_length=10)
    class_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'night_class'
        unique_together = (('id', 'class_day', 'class_time'),)


class Students(models.Model):
    grade = models.IntegerField()
    classno = models.CharField(db_column='classNo', max_length=10)  # Field name made lowercase.
    num = models.IntegerField()
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    room = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'students'


class Teacher(models.Model):
    class_year = models.IntegerField(primary_key=True)
    class_field = models.CharField(db_column='class', max_length=10)  # Field renamed because it was a Python reserved word.
    teacher_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'teacher'
        unique_together = (('class_year', 'class_field'),)

class Room(models.Model):
    room_name = models.CharField(primary_key=True, max_length=30)
    room_row = models.IntegerField()
    room_column = models.IntegerField()
    seat = models.CharField(max_length=100)
    id = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'room'
        unique_together = (('room_name', 'room_row', 'room_column'),)

