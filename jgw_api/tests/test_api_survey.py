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
    Image,
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

import pymongo
from secrets_content.files.secret_key import *
import os

class SurveyApiTestOK(APITestCase):
    now = datetime.datetime.now()

    def setUp(self):
        self.url = '/hub/api/v1/survey/'

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

        Member.objects.create(
            member_pk=get_random_string(length=24),
            member_nm=get_random_string(length=44),
            member_created_dttm=now,
            member_modified_dttm=now,
            member_email=f'test@test.com',
            member_cell_phone_number='01000000000',
            member_student_id=get_random_string(length=9, allowed_chars='0123456789'),
            member_year=38,
            role_role_pk=Role.objects.get(role_nm='ROLE_USER1'),
            rank_rank_pk=Rank.objects.get(rank_nm='정회원'),
            major_major_pk=Major.objects.get(major_nm='인공지능학과'),
            member_leave_absence=0,
            member_created_by='system',
            member_modified_by='system',
            member_dateofbirth=now,
        )
        Member.objects.create(
            member_pk=get_random_string(length=24),
            member_nm=get_random_string(length=44),
            member_created_dttm=now,
            member_modified_dttm=now,
            member_email=f'testddd@test.com',
            member_cell_phone_number='01000000000',
            member_student_id=get_random_string(length=9, allowed_chars='0123456789'),
            member_year=38,
            role_role_pk=Role.objects.get(role_nm='ROLE_DEV'),
            rank_rank_pk=Rank.objects.get(rank_nm='정회원'),
            major_major_pk=Major.objects.get(major_nm='인공지능학과'),
            member_leave_absence=0,
            member_created_by='system',
            member_modified_by='system',
            member_dateofbirth=now,
        )

    def __get_header(self, member_instance):
        return {
            'HTTP_USER_PK': member_instance.member_pk,
            'HTTP_ROLE_PK': member_instance.role_role_pk.role_pk
        }

    def test_survey_post_post(self):
        print("Survey post Api POST Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))
        insert_data = {
            'title': 'title',
            'description': 'desriptiopnmdsad',
            'writer': member_instance.member_pk,
            'allow_multiple': True,
            'role_answer': 100,
        }

        # when
        respons: Response = self.client.post(self.url, data=insert_data, **self.__get_header(member_instance))
        print(respons.content)

        # then
        responses_data = {
            'title': 'title',
            'description': 'desriptiopnmdsad',
            'writer': member_instance.member_pk,
            'allow_multiple': True,
            'role_answer': 100,
            "question": [],
            "answer": [],
            "_id": respons.content[-26:-2].decode('utf-8')
        }
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(respons.content, responses_data)