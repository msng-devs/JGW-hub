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
    '''
    image serializer
    '''

    class Meta:
        model = Image
        fields = '__all__'

    def validate(self, data):
        image_url = Image.objects.get(image_url=data['image_url'])
        if image_url.exists():
            raise serializers.ValidationError("image_url already exists")
        return data


class ImageNestedPostSerializer(serializers.ModelSerializer):
    '''
    image nested serializer. 다른 serializer에서 모든 이미지 필드가 필요 없을때 사용.
    '''

    class Meta:
        model = Image
        fields = ['image_id_pk', 'image_name', 'image_url']


class MemberSerializer(serializers.ModelSerializer):
    '''
    member serializer
    '''

    class Meta:
        model = Member
        fields = '__all__'


class MemberNestedSerializer(serializers.ModelSerializer):
    '''
    member nested serializer. 다른 serializer에서 모든 멤버 필드가 필요 없을때 사용.
    '''

    class Meta:
        model = Member
        fields = ['member_pk', 'member_nm']


class BoardWriteSerializer(serializers.ModelSerializer):
    '''
    board serializer. post method에 사용하는 serializer.
    '''

    class Meta:
        model = Board
        fields = '__all__'



class BoardGetSerializer(serializers.ModelSerializer):
    '''
    board serializer. get method에 사용하는 serializer.
    '''
    role_role_pk_write_level = RoleNestedSerializer(read_only=True)
    role_role_pk_read_level = RoleNestedSerializer(read_only=True)
    role_role_pk_comment_write_level = RoleNestedSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ['board_id_pk', 'board_name', 'board_layout', 'role_role_pk_write_level',
                  'role_role_pk_read_level', 'role_role_pk_comment_write_level']


class PostWriteSerializer(serializers.ModelSerializer):
    '''
    post serializer. post method에 사용하는 serializer.
    '''

    class Meta:
        model = Post
        fields = '__all__'


class PostGetSerializer(serializers.ModelSerializer):
    '''
    post serializer. get method에 사용하는 serializer.
    '''
    board_boadr_id_pk = BoardWriteSerializer(read_only=True)

    member_member_pk = MemberNestedSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['post_id_pk', 'post_title', 'post_content', 'post_write_time', 'post_update_time',
                  'thumbnail_id_pk', 'board_boadr_id_pk', 'member_member_pk']


class PostPatchSerializer(serializers.ModelSerializer):
    '''
    post serializer. patch method에 사용하는 serializer.
    '''

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('post_write_time', 'member_member_pk')


class CommentGetSerializer(serializers.ModelSerializer):
    '''
    comment serializer. get method에 사용하는 serializer.
    '''
    member_member_pk = MemberNestedSerializer(read_only=True)
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
    '''
    comment serializer. post method에 사용하는 serializer.
    '''

    class Meta:
        model = Comment

        fields = '__all__'



class CommentWriteResultSerializer(serializers.ModelSerializer):
    '''
    comment serializer. post method에 결과값 리턴을 위해 사용하는 serializer.
    '''
    member_member_pk = MemberNestedSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['comment_id', 'comment_depth', 'comment_content', 'comment_write_time', 'comment_update_time',
                  'comment_delete', 'post_post_id_pk', 'member_member_pk', 'comment_comment_id_ref']
