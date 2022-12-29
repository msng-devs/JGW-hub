from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from jgw_api.models import (
    Board,
    Role,
    Member,
    Rank,
    Post,
    Major,
    Comment,
    Config
)

from django.utils.crypto import get_random_string

from jgw_api.views import post_get_all_query

import os
import base64
import random
import datetime
import traceback

import jgw_api.constant as constant

class CommentApiTestOK(APITestCase):
    now = datetime.datetime.now()

    def setUp(self):
        self.url = '/hub/api/v1/comment/'
        self.now = datetime.datetime.now()

    @classmethod
    def setUpTestData(cls):
        now = cls.now

        Role.objects.create(role_pk=0, role_nm='ROLE_GUEST')
        Role.objects.create(role_pk=100, role_nm='ROLE_USER0')
        Role.objects.create(role_pk=101, role_nm='ROLE_USER1')
        Role.objects.create(role_pk=500, role_nm='ROLE_ADMIN')
        Role.objects.create(role_pk=501, role_nm='ROLE_DEV')

        Config.objects.create(config_nm='admin_role_pk', config_val='500', config_pk=500)

        Major.objects.create(major_nm='인공지능학과', major_pk=0)

        Rank.objects.create(rank_nm='none', rank_pk=0)
        Rank.objects.create(rank_nm='수습회원', rank_pk=1)
        Rank.objects.create(rank_nm='정회원', rank_pk=2)
        Rank.objects.create(rank_nm='준OB', rank_pk=3)
        Rank.objects.create(rank_nm='OB', rank_pk=4)

        Board.objects.create(
            board_name='test1',
            board_layout=1,
            role_role_pk_write_level=Role.objects.get(role_nm='ROLE_USER1'),
            role_role_pk_read_level=Role.objects.get(role_nm='ROLE_USER1'),
            role_role_pk_comment_write_level=Role.objects.get(role_nm='ROLE_USER1')
        )

        for i in range(2):
            Member.objects.create(
                member_pk=get_random_string(length=24) + str(i),
                member_nm=get_random_string(length=44) + str(i),
                member_created_dttm=now,
                member_modified_dttm=now,
                member_email=f'test{i}@test.com',
                member_cell_phone_number='01000000000',
                member_student_id=get_random_string(length=9, allowed_chars='0123456789') + str(i),
                member_year=38,
                role_role_pk=Role.objects.get(role_nm='ROLE_USER1'),
                rank_rank_pk=Rank.objects.get(rank_nm='정회원'),
                major_major_pk=Major.objects.get(major_nm='인공지능학과'),
                member_leave_absence=0,
                member_created_by='system',
                member_modified_by='system',
                member_dateofbirth=now,
            )

        for i in range(2):
            now += datetime.timedelta(days=1)
            board_instance = Board.objects.get(board_name='test1')
            member_instance = Member.objects.all()[i]
            Post.objects.create(
                post_title=get_random_string(length=98) + str(i),
                post_content=get_random_string(length=500) + str(i),
                post_write_time=now,
                post_update_time=now,
                board_boadr_id_pk=board_instance,
                member_member_pk=member_instance
            )

        for i in range(10):
            Comment.objects.create(
                comment_depth=0,
                comment_content='testetse',
                comment_write_time=now,
                comment_update_time=now,
                comment_delete=0,
                post_post_id_pk=Post.objects.all()[0 if i < 5 else 1],
                member_member_pk=random.choice(Member.objects.all()),
                comment_comment_id_ref=None
            )

        depth_1_count = [3,5,1,4,6,0,0,7,4,0]
        for i in range(10):
            for j in range(depth_1_count[i]):
                Comment.objects.create(
                    comment_depth=1,
                    comment_content='testetse',
                    comment_write_time=now,
                    comment_update_time=now,
                    comment_delete=0,
                    post_post_id_pk=Comment.objects.get(comment_id=i + 1).post_post_id_pk,
                    member_member_pk=Comment.objects.get(comment_id=i + 1).member_member_pk,
                    comment_comment_id_ref=Comment.objects.get(comment_id=i + 1)
                )

    def __comment_get(self, data):
        def comment_get_data(ref_comment):
            instance = Comment.objects.all().order_by(('-' if ref_comment is None else '') + 'comment_id').filter(
                post_post_id_pk=int(data['post_id']),
                comment_comment_id_ref=None if ref_comment is None else ref_comment.comment_id
            )

            if ref_comment is None:
                instance = instance[:3]

            return [{
                "comment_id": i.comment_id,
                "comment_depth": i.comment_depth,
                "comment_content": i.comment_content,
                "comment_write_time": i.comment_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "comment_update_time": i.comment_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "comment_delete": i.comment_delete,
                "post_post_id_pk": i.post_post_id_pk.post_id_pk,
                "member_member_pk": {
                    "member_pk": i.member_member_pk.member_pk,
                    "member_nm": i.member_member_pk.member_nm,
                },
                "reply": comment_get_data(i)
            } for i in instance]

        return {
            'count': 3,
            "next": "http://testserver/hub/api/v1/comment/?page=2&page_size=3&post_id=2",
            "previous": None,
            "results": comment_get_data(None)
        }

    def test_comment_get(self):
        print("Comment Api GET ALL Running...")

        # given
        data = {'post_id': 2, 'page': 1, 'page_size': 3}

        # when
        respons: Response = self.client.get(self.url, data=data)

        # # then
        return_data = self.__comment_get(data)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)
