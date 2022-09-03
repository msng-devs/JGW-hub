from rest_framework import serializers

from .models import (
    Category,
    Board,
    Role,
    Image,
    Post
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class BoardSerializer(serializers.ModelSerializer):
    role_role_pk_write_level = RoleSerializer(read_only=True)
    role_role_pk_read_level = RoleSerializer(read_only=True)
    role_role_pk_comment_write_level = RoleSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ['board_id_pk', 'board_name', 'board_layout', 'role_role_pk_write_level',
                  'role_role_pk_read_level', 'role_role_pk_comment_write_level']

class BoardSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
