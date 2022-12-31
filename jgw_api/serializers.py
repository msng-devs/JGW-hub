from rest_framework import serializers

from .models import (
    Board,
    Role,
    Image,
    Post,
    Member,
    Comment
)

class RoleNestedSerializer(serializers.ModelSerializer):
    '''
    role nested serializer
    '''
    class Meta:
        model = Role
        fields = '__all__'



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ImageNestedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_id_pk', 'image_name', 'image_url']



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
    role_role_pk_write_level = RoleNestedSerializer(read_only=True)
    role_role_pk_read_level = RoleNestedSerializer(read_only=True)
    role_role_pk_comment_write_level = RoleNestedSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ['board_id_pk', 'board_name', 'board_layout', 'role_role_pk_write_level',
                  'role_role_pk_read_level', 'role_role_pk_comment_write_level']



class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostGetSerializer(serializers.ModelSerializer):
    board_boadr_id_pk = BoardWriteSerializer(read_only=True)
    member_member_pk = MemberNestedPostSerializer(read_only=True)
    image_image_id_pk = ImageNestedPostSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['post_id_pk', 'post_title', 'post_content', 'post_write_time', 'post_update_time',
                  'image_image_id_pk', 'board_boadr_id_pk', 'member_member_pk']

class PostPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('post_write_time', 'member_member_pk')



class CommentGetSerializer(serializers.ModelSerializer):
    member_member_pk = MemberNestedPostSerializer(read_only=True)
    reply = serializers.SerializerMethodField()

    def get_reply(self, instance):
        # recursive
        serializer = self.__class__(instance.reply, many=True)
        serializer.bind('', self)
        return serializer.data

    class Meta:
        model = Comment
        fields = ['comment_id', 'comment_depth', 'comment_content', 'comment_write_time', 'comment_update_time',
                  'comment_delete', 'post_post_id_pk', 'member_member_pk', 'reply']

class CommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentWriteResultSerializer(serializers.ModelSerializer):
    member_member_pk = MemberNestedPostSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['comment_id', 'comment_depth', 'comment_content', 'comment_write_time', 'comment_update_time',
                  'comment_delete', 'post_post_id_pk', 'member_member_pk', 'comment_comment_id_ref']
