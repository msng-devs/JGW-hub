from rest_framework import serializers

from .models import (
    Category,
    Board,
    Role,
    Image,
    Post,
    Member,

)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class MemberNestedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['member_pk', 'member_nm']

class BoardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'

class BoardSerializer(serializers.ModelSerializer):
    role_role_pk_write_level = RoleSerializer(read_only=True)
    role_role_pk_read_level = RoleSerializer(read_only=True)
    role_role_pk_comment_write_level = RoleSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ['board_id_pk', 'board_name', 'board_layout', 'role_role_pk_write_level',
                  'role_role_pk_read_level', 'role_role_pk_comment_write_level']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostGetSerializer(serializers.ModelSerializer):
    category_category_id_pk = CategorySerializer(read_only=True)
    board_boadr_id_pk = BoardWriteSerializer(read_only=True)
    member_member_pk = MemberNestedPostSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['post_id_pk', 'post_title', 'post_content', 'post_write_time', 'post_update_time',
                  'category_category_id_pk', 'image_image_id_pk', 'board_boadr_id_pk', 'member_member_pk', 'images']
