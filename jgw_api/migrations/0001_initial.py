# Generated by Django 4.0.6 on 2022-10-09 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceType',
            fields=[
                ('attendance_type_pk', models.IntegerField(db_column='ATTENDANCE_TYPE_PK', primary_key=True, serialize=False)),
                ('attendance_type_name', models.CharField(db_column='ATTENDANCE_TYPE_NAME', max_length=45)),
            ],
            options={
                'db_table': 'ATTENDANCE_TYPE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('board_id_pk', models.AutoField(db_column='BOARD_ID_PK', primary_key=True, serialize=False)),
                ('board_name', models.CharField(db_column='BOARD_NAME', max_length=45, unique=True)),
                ('board_layout', models.IntegerField(db_column='BOARD_LAYOUT')),
            ],
            options={
                'db_table': 'BOARD',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('config_pk', models.IntegerField(db_column='CONFIG_PK', primary_key=True, serialize=False)),
                ('config_nm', models.CharField(db_column='CONFIG_NM', max_length=50)),
                ('config_val', models.CharField(db_column='CONFIG_VAL', max_length=50)),
            ],
            options={
                'db_table': 'CONFIG',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('error_pk', models.IntegerField(db_column='ERROR_PK', primary_key=True, serialize=False)),
                ('error_nm', models.CharField(db_column='ERROR_NM', max_length=50)),
                ('error_title', models.CharField(blank=True, db_column='ERROR_TITLE', max_length=50, null=True)),
                ('error_http_code', models.CharField(blank=True, db_column='ERROR_HTTP_CODE', max_length=3, null=True)),
                ('error_index', models.TextField(blank=True, db_column='ERROR_INDEX', null=True)),
            ],
            options={
                'db_table': 'ERROR',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_pk', models.IntegerField(db_column='EVENT_PK', primary_key=True, serialize=False)),
                ('event_nm', models.CharField(db_column='EVENT_NM', max_length=50)),
                ('event_index', models.TextField(blank=True, db_column='EVENT_INDEX', null=True)),
                ('event_start_dttm', models.DateTimeField(db_column='EVENT_START_DTTM')),
                ('event_end_dttm', models.DateTimeField(db_column='EVENT_END_DTTM')),
                ('event_created_by', models.CharField(db_column='EVENT_CREATED_BY', max_length=30)),
                ('event_modified_by', models.CharField(db_column='EVENT_MODIFIED_BY', max_length=30)),
                ('event_modified_dttm', models.DateTimeField(db_column='EVENT_MODIFIED_DTTM')),
                ('event_created_dttm', models.DateTimeField(db_column='EVENT_CREATED_DTTM')),
            ],
            options={
                'db_table': 'EVENT',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('image_id_pk', models.AutoField(db_column='IMAGE_ID_PK', primary_key=True, serialize=False)),
                ('image_name', models.CharField(db_column='IMAGE_NAME', max_length=45)),
                ('image_url', models.CharField(db_column='IMAGE_URL', max_length=45)),
            ],
            options={
                'db_table': 'IMAGE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Major',
            fields=[
                ('major_pk', models.IntegerField(db_column='MAJOR_PK', primary_key=True, serialize=False)),
                ('major_nm', models.CharField(db_column='MAJOR_NM', max_length=45, unique=True)),
            ],
            options={
                'db_table': 'MAJOR',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('member_pk', models.CharField(db_column='MEMBER_PK', max_length=25, primary_key=True, serialize=False)),
                ('member_nm', models.CharField(db_column='MEMBER_NM', max_length=45)),
                ('member_email', models.CharField(db_column='MEMBER_EMAIL', max_length=255, unique=True)),
                ('member_cell_phone_number', models.CharField(blank=True, db_column='MEMBER_CELL_PHONE_NUMBER', max_length=15, null=True)),
                ('member_student_id', models.CharField(db_column='MEMBER_STUDENT_ID', max_length=45, unique=True)),
                ('member_year', models.SmallIntegerField(db_column='MEMBER_YEAR')),
                ('member_modified_dttm', models.DateTimeField(db_column='MEMBER_MODIFIED_DTTM')),
                ('member_created_dttm', models.DateTimeField(db_column='MEMBER_CREATED_DTTM')),
                ('member_leave_absence', models.IntegerField(db_column='MEMBER_LEAVE_ABSENCE')),
                ('member_modified_by', models.CharField(db_column='MEMBER_MODIFIED_BY', max_length=30)),
                ('member_created_by', models.CharField(db_column='MEMBER_CREATED_BY', max_length=30)),
                ('member_dateofbirth', models.DateField(db_column='MEMBER_DATEOFBIRTH')),
                ('major_major_pk', models.ForeignKey(db_column='MAJOR_MAJOR_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.major')),
            ],
            options={
                'db_table': 'MEMBER',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('method_pk', models.IntegerField(db_column='METHOD_PK', primary_key=True, serialize=False)),
                ('method_nm', models.CharField(db_column='METHOD_NM', max_length=45, unique=True)),
            ],
            options={
                'db_table': 'METHOD',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('rank_pk', models.IntegerField(db_column='RANK_PK', primary_key=True, serialize=False)),
                ('rank_nm', models.CharField(db_column='RANK_NM', max_length=45, unique=True)),
            ],
            options={
                'db_table': 'RANK',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('role_pk', models.IntegerField(db_column='ROLE_PK', primary_key=True, serialize=False)),
                ('role_nm', models.CharField(db_column='ROLE_NM', max_length=45, unique=True)),
            ],
            options={
                'db_table': 'ROLE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('service_pk', models.IntegerField(db_column='SERVICE_PK', primary_key=True, serialize=False)),
                ('service_nm', models.CharField(db_column='SERVICE_NM', max_length=45, unique=True)),
                ('service_domain', models.CharField(db_column='SERVICE_DOMAIN', max_length=45, unique=True)),
                ('service_domain_index', models.TextField(blank=True, db_column='SERVICE_DOMAIN_INDEX', null=True)),
            ],
            options={
                'db_table': 'SERVICE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_id_pk', models.AutoField(db_column='POST_ID_PK', primary_key=True, serialize=False)),
                ('post_title', models.CharField(db_column='POST_TITLE', max_length=100)),
                ('post_content', models.TextField(db_column='POST_CONTENT')),
                ('post_write_time', models.DateTimeField(db_column='POST_WRITE_TIME')),
                ('post_update_time', models.DateTimeField(db_column='POST_UPDATE_TIME')),
                ('board_boadr_id_pk', models.ForeignKey(db_column='BOARD_BOADR_ID_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.board')),
                ('image_image_id_pk', models.ForeignKey(blank=True, db_column='IMAGE_IMAGE_ID_PK', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.image')),
                ('member_member_pk', models.ForeignKey(blank=True, db_column='MEMBER_MEMBER_PK', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.member')),
            ],
            options={
                'db_table': 'POST',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('penalty_pk', models.IntegerField(db_column='PENALTY_PK', primary_key=True, serialize=False)),
                ('penalty_modified_dttm', models.DateTimeField(db_column='PENALTY_MODIFIED_DTTM')),
                ('penalty_created_dttm', models.DateTimeField(db_column='PENALTY_CREATED_DTTM')),
                ('penalty_type', models.IntegerField(db_column='PENALTY_TYPE')),
                ('penalty_reason', models.TextField(db_column='PENALTY_REASON')),
                ('penalty_created_by', models.CharField(db_column='PENALTY_CREATED_BY', max_length=30)),
                ('penalty_modified_by', models.CharField(db_column='PENALTY_MODIFIED_BY', max_length=30)),
                ('member_member_pk', models.ForeignKey(db_column='MEMBER_MEMBER_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.member')),
            ],
            options={
                'db_table': 'PENALTY',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='member',
            name='rank_rank_pk',
            field=models.ForeignKey(db_column='RANK_RANK_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.rank'),
        ),
        migrations.AddField(
            model_name='member',
            name='role_role_pk',
            field=models.ForeignKey(db_column='ROLE_ROLE_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.role'),
        ),
        migrations.AddField(
            model_name='image',
            name='member_member_pk',
            field=models.ForeignKey(blank=True, db_column='MEMBER_MEMBER_PK', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.member'),
        ),
        migrations.AddField(
            model_name='image',
            name='post_post_id_pk',
            field=models.ForeignKey(blank=True, db_column='POST_POST_ID_PK', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.post'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.AutoField(db_column='COMMENT_ID', primary_key=True, serialize=False)),
                ('comment_ref_id', models.IntegerField(db_column='COMMENT_REF_ID')),
                ('comment_depth', models.IntegerField(db_column='COMMENT_DEPTH')),
                ('comment_content', models.TextField(db_column='COMMENT_CONTENT')),
                ('comment_write_time', models.DateTimeField(db_column='COMMENT_WRITE_TIME')),
                ('comment_update_time', models.DateTimeField(db_column='COMMENT_UPDATE_TIME')),
                ('comment_delete', models.CharField(db_column='COMMENT_DELETE', max_length=1)),
                ('comment_comment_id_ref', models.ForeignKey(blank=True, db_column='COMMENT_COMMENT_ID_REF', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.comment')),
                ('member_member_pk', models.ForeignKey(blank=True, db_column='MEMBER_MEMBER_PK', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.member')),
                ('post_post_id_pk', models.ForeignKey(db_column='POST_POST_ID_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.post')),
            ],
            options={
                'db_table': 'COMMENT',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='board',
            name='role_role_pk_comment_write_level',
            field=models.ForeignKey(db_column='ROLE_ROLE_PK_COMMENT_WRITE_LEVEL', on_delete=django.db.models.deletion.DO_NOTHING, related_name='board_comment_write_level', to='jgw_api.role'),
        ),
        migrations.AddField(
            model_name='board',
            name='role_role_pk_read_level',
            field=models.ForeignKey(db_column='ROLE_ROLE_PK_READ_LEVEL', on_delete=django.db.models.deletion.DO_NOTHING, related_name='board_read_level', to='jgw_api.role'),
        ),
        migrations.AddField(
            model_name='board',
            name='role_role_pk_write_level',
            field=models.ForeignKey(db_column='ROLE_ROLE_PK_WRITE_LEVEL', on_delete=django.db.models.deletion.DO_NOTHING, related_name='board_write_level', to='jgw_api.role'),
        ),
        migrations.CreateModel(
            name='ApiRoute',
            fields=[
                ('api_route_pk', models.IntegerField(db_column='API_ROUTE_PK', primary_key=True, serialize=False)),
                ('api_route_path', models.CharField(db_column='API_ROUTE_PATH', max_length=45, unique=True)),
                ('api_route_gateway_refresh', models.IntegerField(blank=True, db_column='API_ROUTE_GATEWAY_REFRESH', null=True)),
                ('api_route_only_token', models.IntegerField(blank=True, db_column='API_ROUTE_ONLY_TOKEN', null=True)),
                ('api_route_optional', models.IntegerField(blank=True, db_column='API_ROUTE_OPTIONAL', null=True)),
                ('method_method_pk', models.ForeignKey(db_column='METHOD_METHOD_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.method')),
                ('role_role_pk', models.ForeignKey(db_column='ROLE_ROLE_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.role')),
                ('service_service_pk', models.ForeignKey(db_column='SERVICE_SERVICE_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.service')),
            ],
            options={
                'db_table': 'API_ROUTE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('timetable_pk', models.IntegerField(db_column='TIMETABLE_PK', primary_key=True, serialize=False)),
                ('timetable_start_dttm', models.DateTimeField(db_column='TIMETABLE_START_DTTM')),
                ('timetable_end_dttm', models.DateTimeField(db_column='TIMETABLE_END_DTTM')),
                ('timetable_nm', models.CharField(db_column='TIMETABLE_NM', max_length=50)),
                ('timetable_created_by', models.CharField(db_column='TIMETABLE_CREATED_BY', max_length=30)),
                ('timetable_modified_by', models.CharField(db_column='TIMETABLE_MODIFIED_BY', max_length=30)),
                ('timetable_created_dttm', models.DateTimeField(db_column='TIMETABLE_CREATED_DTTM')),
                ('timetable_modified_dttm', models.DateTimeField(db_column='TIMETABLE_MODIFIED_DTTM')),
                ('event_event_pk', models.ForeignKey(db_column='EVENT_EVENT_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.event')),
            ],
            options={
                'db_table': 'TIMETABLE',
                'managed': True,
                'unique_together': {('timetable_pk', 'event_event_pk')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('member_member_pk', models.OneToOneField(db_column='MEMBER_MEMBER_PK', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='jgw_api.member')),
                ('attendance_modified_dttm', models.DateTimeField(db_column='ATTENDANCE_MODIFIED_DTTM')),
                ('attendance_created_dttm', models.CharField(db_column='ATTENDANCE_CREATED_DTTM', max_length=45)),
                ('attendance_index', models.TextField(blank=True, db_column='ATTENDANCE_INDEX', null=True)),
                ('attendance_created_by', models.CharField(db_column='ATTENDANCE_CREATED_BY', max_length=30)),
                ('attendance_modified_by', models.CharField(db_column='ATTENDANCE_MODIFIED_BY', max_length=30)),
                ('attendance_type_attendance_type_pk', models.ForeignKey(db_column='ATTENDANCE_TYPE_ATTENDANCE_TYPE_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.attendancetype')),
                ('timetable_timetable_pk', models.ForeignKey(db_column='TIMETABLE_TIMETABLE_PK', on_delete=django.db.models.deletion.DO_NOTHING, to='jgw_api.timetable')),
            ],
            options={
                'db_table': 'ATTENDANCE',
                'managed': True,
                'unique_together': {('member_member_pk', 'timetable_timetable_pk')},
            },
        ),
    ]
