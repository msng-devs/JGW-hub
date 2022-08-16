from rest_framework import serializers

from .models import (
    Category,
    Board,
    Role
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

    class Meta:
        model = Board
        fields = ['board_id_pk', 'board_name', 'role_role_pk_write_level', 'role_role_pk_read_level']
