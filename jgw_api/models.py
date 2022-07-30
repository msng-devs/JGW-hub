# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Board(models.Model):
    board_id_pk = models.AutoField(db_column='BOARD_ID_PK', primary_key=True)  # Field name made lowercase.
    board_name = models.CharField(db_column='BOARD_NAME', unique=True, max_length=45)  # Field name made lowercase.
    board_read_level = models.IntegerField(db_column='BOARD_READ_LEVEL')  # Field name made lowercase.
    board_write_level = models.IntegerField(db_column='BOARD_WRITE_LEVEL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BOARD'


class Category(models.Model):
    category_id_pk = models.AutoField(db_column='CATEGORY_ID_PK', primary_key=True)  # Field name made lowercase.
    category_name = models.CharField(db_column='CATEGORY_NAME', unique=True, max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CATEGORY'


class Comment(models.Model):
    comment_id = models.AutoField(db_column='COMMENT_ID', primary_key=True)  # Field name made lowercase.
    comment_ref_id = models.IntegerField(db_column='COMMENT_REF_ID')  # Field name made lowercase.
    comment_depth = models.IntegerField(db_column='COMMENT_DEPTH')  # Field name made lowercase.
    comment_writer = models.CharField(db_column='COMMENT_WRITER', max_length=45)  # Field name made lowercase.
    comment_content = models.TextField(db_column='COMMENT_CONTENT')  # Field name made lowercase.
    comment_write_time = models.DateTimeField(db_column='COMMENT_WRITE_TIME')  # Field name made lowercase.
    comment_update_time = models.DateTimeField(db_column='COMMENT_UPDATE_TIME')  # Field name made lowercase.
    comment_post = models.ForeignKey('Post', models.DO_NOTHING, db_column='COMMENT_POST_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'COMMENT'


class Image(models.Model):
    image_id_pk = models.AutoField(db_column='IMAGE_ID_PK', primary_key=True)  # Field name made lowercase.
    image_url = models.CharField(db_column='IMAGE_URL', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'IMAGE'


class Post(models.Model):
    post_id_pk = models.AutoField(db_column='POST_ID_PK', primary_key=True)  # Field name made lowercase.
    post_title = models.CharField(db_column='POST_TITLE', max_length=100)  # Field name made lowercase.
    post_content = models.TextField(db_column='POST_CONTENT')  # Field name made lowercase.
    post_writer = models.CharField(db_column='POST_WRITER', max_length=45)  # Field name made lowercase.
    post_write_time = models.DateTimeField(db_column='POST_WRITE_TIME')  # Field name made lowercase.
    post_update_time = models.DateTimeField(db_column='POST_UPDATE_TIME')  # Field name made lowercase.
    post_category = models.ForeignKey(Category, models.DO_NOTHING, db_column='POST_CATEGORY_ID')  # Field name made lowercase.
    post_thumbnail = models.ForeignKey(Image, models.DO_NOTHING, db_column='POST_THUMBNAIL_ID')  # Field name made lowercase.
    post_board = models.ForeignKey(Board, models.DO_NOTHING, db_column='POST_BOARD_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'POST'


class PostHasTag(models.Model):
    post_post_id_pk = models.OneToOneField(Post, models.DO_NOTHING, db_column='POST_POST_ID_PK', primary_key=True)  # Field name made lowercase.
    tag_tag_id_pk = models.ForeignKey('Tag', models.DO_NOTHING, db_column='TAG_TAG_ID_PK')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'POST_has_TAG'
        unique_together = (('post_post_id_pk', 'tag_tag_id_pk'),)


class Tag(models.Model):
    tag_id_pk = models.AutoField(db_column='TAG_ID_PK', primary_key=True)  # Field name made lowercase.
    tag_name = models.CharField(db_column='TAG_NAME', unique=True, max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TAG'
