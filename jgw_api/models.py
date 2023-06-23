# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApiRoute(models.Model):
    api_route_pk = models.AutoField(db_column='API_ROUTE_PK', primary_key=True)  # Field name made lowercase.
    api_route_path = models.CharField(db_column='API_ROUTE_PATH', max_length=45)  # Field name made lowercase.
    method_method_pk = models.ForeignKey('Method', models.DO_NOTHING, db_column='METHOD_METHOD_PK')  # Field name made lowercase.
    role_role_pk = models.ForeignKey('Role', models.DO_NOTHING, db_column='ROLE_ROLE_PK', blank=True, null=True)  # Field name made lowercase.
    service_service_pk = models.ForeignKey('Service', models.DO_NOTHING, db_column='SERVICE_SERVICE_PK')  # Field name made lowercase.
    route_option_route_option_pk = models.ForeignKey('RouteOption', models.DO_NOTHING, db_column='ROUTE_OPTION_ROUTE_OPTION_PK')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'API_ROUTE'


class Attendance(models.Model):
    attendance_pk = models.PositiveIntegerField(db_column='ATTENDANCE_PK', primary_key=True)  # Field name made lowercase.
    member_member_pk = models.ForeignKey('Member', models.DO_NOTHING, db_column='MEMBER_MEMBER_PK')  # Field name made lowercase.
    timetable_timetable_pk = models.ForeignKey('Timetable', models.DO_NOTHING, db_column='TIMETABLE_TIMETABLE_PK')  # Field name made lowercase.
    attendance_type_attendance_type_pk = models.ForeignKey('AttendanceType', models.DO_NOTHING, db_column='ATTENDANCE_TYPE_ATTENDANCE_TYPE_PK')  # Field name made lowercase.
    attendance_modified_dttm = models.DateTimeField(db_column='ATTENDANCE_MODIFIED_DTTM', blank=True, null=True)  # Field name made lowercase.
    attendance_created_dttm = models.CharField(db_column='ATTENDANCE_CREATED_DTTM', max_length=45, blank=True, null=True)  # Field name made lowercase.
    attendance_index = models.TextField(db_column='ATTENDANCE_INDEX', blank=True, null=True)  # Field name made lowercase.
    attendance_created_by = models.CharField(db_column='ATTENDANCE_CREATED_BY', max_length=30, blank=True, null=True)  # Field name made lowercase.
    attendance_modified_by = models.CharField(db_column='ATTENDANCE_MODIFIED_BY', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ATTENDANCE'
        unique_together = (('member_member_pk', 'timetable_timetable_pk'),)


class AttendanceType(models.Model):
    attendance_type_pk = models.IntegerField(db_column='ATTENDANCE_TYPE_PK', primary_key=True)  # Field name made lowercase.
    attendance_type_name = models.CharField(db_column='ATTENDANCE_TYPE_NAME', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ATTENDANCE_TYPE'


class Board(models.Model):
    board_id_pk = models.AutoField(db_column='BOARD_ID_PK', primary_key=True)  # Field name made lowercase.
    board_name = models.CharField(db_column='BOARD_NAME', unique=True, max_length=45)  # Field name made lowercase.
    role_role_pk_write_level = models.ForeignKey('Role', models.DO_NOTHING, db_column='ROLE_ROLE_PK_WRITE_LEVEL', related_name='board_write_level')  # Field name made lowercase.
    role_role_pk_read_level = models.ForeignKey('Role', models.DO_NOTHING, db_column='ROLE_ROLE_PK_READ_LEVEL', related_name='board_read_level')  # Field name made lowercase.
    role_role_pk_comment_write_level = models.ForeignKey('Role', models.DO_NOTHING, db_column='ROLE_ROLE_PK_COMMENT_WRITE_LEVEL', related_name='board_comment_write_level')  # Field name made lowercase.
    board_layout = models.IntegerField(db_column='BOARD_LAYOUT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'BOARD'


class Comment(models.Model):
    comment_id = models.AutoField(db_column='COMMENT_ID', primary_key=True)  # Field name made lowercase.
    comment_depth = models.IntegerField(db_column='COMMENT_DEPTH')  # Field name made lowercase.
    comment_content = models.TextField(db_column='COMMENT_CONTENT')  # Field name made lowercase.
    comment_write_time = models.DateTimeField(db_column='COMMENT_WRITE_TIME', auto_now_add=True)  # Field name made lowercase.
    comment_update_time = models.DateTimeField(db_column='COMMENT_UPDATE_TIME', auto_now=True)  # Field name made lowercase.
    comment_delete = models.IntegerField(db_column='COMMENT_DELETE')  # Field name made lowercase.
    post_post_id_pk = models.ForeignKey('Post', models.DO_NOTHING, db_column='POST_POST_ID_PK')  # Field name made lowercase.
    member_member_pk = models.ForeignKey('Member', models.DO_NOTHING, db_column='MEMBER_MEMBER_PK', blank=True, null=True)  # Field name made lowercase.
    comment_comment_id_ref = models.ForeignKey('self', models.DO_NOTHING, db_column='COMMENT_COMMENT_ID_REF', blank=True, null=True, related_name='reply')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'COMMENT'


class Config(models.Model):
    config_pk = models.AutoField(db_column='CONFIG_PK', primary_key=True)  # Field name made lowercase.
    config_nm = models.CharField(db_column='CONFIG_NM', max_length=50)  # Field name made lowercase.
    config_val = models.CharField(db_column='CONFIG_VAL', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'CONFIG'


class Error(models.Model):
    error_type = models.CharField(db_column='ERROR_TYPE', primary_key=True, max_length=50)  # Field name made lowercase.
    error_status = models.CharField(db_column='ERROR_STATUS', max_length=50)  # Field name made lowercase.
    error_title = models.CharField(db_column='ERROR_TITLE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    error_detail = models.CharField(db_column='ERROR_DETAIL', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ERROR'


class Event(models.Model):
    event_pk = models.IntegerField(db_column='EVENT_PK', primary_key=True)  # Field name made lowercase.
    event_nm = models.CharField(db_column='EVENT_NM', max_length=50)  # Field name made lowercase.
    event_index = models.TextField(db_column='EVENT_INDEX', blank=True, null=True)  # Field name made lowercase.
    event_start_dttm = models.DateTimeField(db_column='EVENT_START_DTTM')  # Field name made lowercase.
    event_end_dttm = models.DateTimeField(db_column='EVENT_END_DTTM')  # Field name made lowercase.
    event_created_by = models.CharField(db_column='EVENT_CREATED_BY', max_length=30)  # Field name made lowercase.
    event_modified_by = models.CharField(db_column='EVENT_MODIFIED_BY', max_length=30)  # Field name made lowercase.
    event_modified_dttm = models.DateTimeField(db_column='EVENT_MODIFIED_DTTM')  # Field name made lowercase.
    event_created_dttm = models.DateTimeField(db_column='EVENT_CREATED_DTTM')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'EVENT'


class GatewayManagementConfig(models.Model):
    gateway_management_config_nm = models.CharField(db_column='GATEWAY_MANAGEMENT_CONFIG_NM', primary_key=True, max_length=100)  # Field name made lowercase.
    gateway_management_config_val = models.CharField(db_column='GATEWAY_MANAGEMENT_CONFIG_VAL', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'GATEWAY_MANAGEMENT_CONFIG'


class Image(models.Model):
    image_id_pk = models.AutoField(db_column='IMAGE_ID_PK', primary_key=True)  # Field name made lowercase.
    image_name = models.CharField(db_column='IMAGE_NAME', max_length=45)  # Field name made lowercase.
    image_url = models.CharField(db_column='IMAGE_URL', max_length=45)  # Field name made lowercase.
    post_post_id_pk = models.ForeignKey('Post', models.DO_NOTHING, db_column='POST_POST_ID_PK', blank=True, null=True)  # Field name made lowercase.
    member_member_pk = models.ForeignKey('Member', models.DO_NOTHING, db_column='MEMBER_MEMBER_PK', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'IMAGE'


class Major(models.Model):
    major_pk = models.IntegerField(db_column='MAJOR_PK', primary_key=True)  # Field name made lowercase.
    major_nm = models.CharField(db_column='MAJOR_NM', unique=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'MAJOR'


class Member(models.Model):
    member_pk = models.CharField(db_column='MEMBER_PK', primary_key=True, max_length=28)  # Field name made lowercase.
    member_nm = models.CharField(db_column='MEMBER_NM', max_length=45)  # Field name made lowercase.
    member_email = models.CharField(db_column='MEMBER_EMAIL', unique=True, max_length=255)  # Field name made lowercase.
    role_role_pk = models.ForeignKey('Role', models.DO_NOTHING, db_column='ROLE_ROLE_PK')  # Field name made lowercase.
    member_status = models.PositiveIntegerField(db_column='MEMBER_STATUS')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'MEMBER'


class MemberInfo(models.Model):
    member_info_pk = models.AutoField(db_column='MEMBER_INFO_PK', primary_key=True)  # Field name made lowercase.
    member_member_pk = models.OneToOneField(Member, models.DO_NOTHING, db_column='MEMBER_MEMBER_PK')  # Field name made lowercase.
    member_info_cell_phone_number = models.CharField(db_column='MEMBER_INFO_CELL_PHONE_NUMBER', max_length=15, blank=True, null=True)  # Field name made lowercase.
    member_info_student_id = models.CharField(db_column='MEMBER_INFO_STUDENT_ID', unique=True, max_length=45)  # Field name made lowercase.
    member_info_year = models.SmallIntegerField(db_column='MEMBER_INFO_YEAR')  # Field name made lowercase.
    rank_rank_pk = models.ForeignKey('Rank', models.DO_NOTHING, db_column='RANK_RANK_PK')  # Field name made lowercase.
    major_major_pk = models.ForeignKey(Major, models.DO_NOTHING, db_column='MAJOR_MAJOR_PK')  # Field name made lowercase.
    member_info_dateofbirth = models.DateField(db_column='MEMBER_INFO_DATEOFBIRTH', blank=True, null=True)  # Field name made lowercase.
    member_info_modified_dttm = models.DateTimeField(db_column='MEMBER_INFO_MODIFIED_DTTM', blank=True, null=True)  # Field name made lowercase.
    member_info_created_dttm = models.DateTimeField(db_column='MEMBER_INFO_CREATED_DTTM', blank=True, null=True)  # Field name made lowercase.
    member_info_modified_by = models.CharField(db_column='MEMBER_INFO_MODIFIED_BY', max_length=30, blank=True, null=True)  # Field name made lowercase.
    member_info_created_by = models.CharField(db_column='MEMBER_INFO_CREATED_BY', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'MEMBER_INFO'


class MemberLeaveAbsence(models.Model):
    member_leave_absence_pk = models.AutoField(db_column='MEMBER_LEAVE_ABSENCE_PK', primary_key=True)  # Field name made lowercase.
    member_leave_absence_status = models.IntegerField(db_column='MEMBER_LEAVE_ABSENCE_STATUS')  # Field name made lowercase.
    member_leave_absence_expected_date_return_school = models.DateField(db_column='MEMBER_LEAVE_ABSENCE_EXPECTED_DATE_RETURN_SCHOOL', blank=True, null=True)  # Field name made lowercase.
    member_member_pk = models.OneToOneField(Member, models.DO_NOTHING, db_column='MEMBER_MEMBER_PK')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'MEMBER_LEAVE_ABSENCE'


class Method(models.Model):
    method_pk = models.IntegerField(db_column='METHOD_PK', primary_key=True)  # Field name made lowercase.
    method_nm = models.CharField(db_column='METHOD_NM', unique=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'METHOD'


class Penalty(models.Model):
    penalty_pk = models.PositiveBigIntegerField(db_column='PENALTY_PK', primary_key=True)  # Field name made lowercase.
    member_member_pk = models.ForeignKey(Member, models.DO_NOTHING, db_column='MEMBER_MEMBER_PK')  # Field name made lowercase.
    penalty_modified_dttm = models.DateTimeField(db_column='PENALTY_MODIFIED_DTTM', blank=True, null=True)  # Field name made lowercase.
    penalty_created_dttm = models.DateTimeField(db_column='PENALTY_CREATED_DTTM', blank=True, null=True)  # Field name made lowercase.
    penalty_type = models.IntegerField(db_column='PENALTY_TYPE')  # Field name made lowercase.
    penalty_reason = models.TextField(db_column='PENALTY_REASON')  # Field name made lowercase.
    penalty_created_by = models.CharField(db_column='PENALTY_CREATED_BY', max_length=30, blank=True, null=True)  # Field name made lowercase.
    penalty_modified_by = models.CharField(db_column='PENALTY_MODIFIED_BY', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'PENALTY'


class Post(models.Model):
    post_id_pk = models.AutoField(db_column='POST_ID_PK', primary_key=True)  # Field name made lowercase.
    post_title = models.CharField(db_column='POST_TITLE', max_length=100)  # Field name made lowercase.
    post_content = models.TextField(db_column='POST_CONTENT')  # Field name made lowercase.
    post_write_time = models.DateTimeField(db_column='POST_WRITE_TIME', auto_now_add=True)  # Field name made lowercase.
    post_update_time = models.DateTimeField(db_column='POST_UPDATE_TIME', auto_now=True)  # Field name made lowercase.
    image_image_id_pk = models.ForeignKey(Image, models.DO_NOTHING, db_column='IMAGE_IMAGE_ID_PK', blank=True, null=True)  # Field name made lowercase.
    board_boadr_id_pk = models.ForeignKey(Board, models.DO_NOTHING, db_column='BOARD_BOADR_ID_PK')  # Field name made lowercase.
    member_member_pk = models.ForeignKey(Member, models.DO_NOTHING, db_column='MEMBER_MEMBER_PK', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'POST'


class Rank(models.Model):
    rank_pk = models.IntegerField(db_column='RANK_PK', primary_key=True)  # Field name made lowercase.
    rank_nm = models.CharField(db_column='RANK_NM', unique=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'RANK'


class Role(models.Model):
    role_pk = models.IntegerField(db_column='ROLE_PK', primary_key=True)  # Field name made lowercase.
    role_nm = models.CharField(db_column='ROLE_NM', unique=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ROLE'


class RouteOption(models.Model):
    route_option_pk = models.AutoField(db_column='ROUTE_OPTION_PK', primary_key=True)  # Field name made lowercase.
    route_option_nm = models.CharField(db_column='ROUTE_OPTION_NM', unique=True, max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ROUTE_OPTION'


class Service(models.Model):
    service_pk = models.AutoField(db_column='SERVICE_PK', primary_key=True)  # Field name made lowercase.
    service_nm = models.CharField(db_column='SERVICE_NM', unique=True, max_length=45)  # Field name made lowercase.
    service_domain = models.CharField(db_column='SERVICE_DOMAIN', unique=True, max_length=45)  # Field name made lowercase.
    service_index = models.TextField(db_column='SERVICE_INDEX', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'SERVICE'


class Timetable(models.Model):
    timetable_pk = models.IntegerField(db_column='TIMETABLE_PK', primary_key=True)  # Field name made lowercase.
    timetable_start_dttm = models.DateTimeField(db_column='TIMETABLE_START_DTTM')  # Field name made lowercase.
    timetable_end_dttm = models.DateTimeField(db_column='TIMETABLE_END_DTTM')  # Field name made lowercase.
    event_event_pk = models.ForeignKey(Event, models.DO_NOTHING, db_column='EVENT_EVENT_PK')  # Field name made lowercase.
    timetable_nm = models.CharField(db_column='TIMETABLE_NM', max_length=50)  # Field name made lowercase.
    timetable_created_by = models.CharField(db_column='TIMETABLE_CREATED_BY', max_length=30)  # Field name made lowercase.
    timetable_modified_by = models.CharField(db_column='TIMETABLE_MODIFIED_BY', max_length=30)  # Field name made lowercase.
    timetable_created_dttm = models.DateTimeField(db_column='TIMETABLE_CREATED_DTTM')  # Field name made lowercase.
    timetable_modified_dttm = models.DateTimeField(db_column='TIMETABLE_MODIFIED_DTTM')  # Field name made lowercase.
    timetable_index = models.CharField(db_column='TIMETABLE_INDEX', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True

        db_table = 'TIMETABLE'

