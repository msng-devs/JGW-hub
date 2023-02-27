import time

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
from bson.objectid import ObjectId
import itertools

class SurveyApiTestOK(APITestCase):
    databases = '__all__'

    now = datetime.datetime.now()
    collection_survey = None
    collection_quiz = None
    collection_answer = None
    survey_pks = []

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
            # member_created_dttm=now,
            # member_modified_dttm=now,
            member_email=f'test@test.com',
            # member_cell_phone_number='01000000000',
            # member_student_id=get_random_string(length=9, allowed_chars='0123456789'),
            # member_year=38,
            role_role_pk=Role.objects.get(role_nm='ROLE_USER1'),
            # rank_rank_pk=Rank.objects.get(rank_nm='정회원'),
            # major_major_pk=Major.objects.get(major_nm='인공지능학과'),
            # member_leave_absence=0,
            # member_created_by='system',
            # member_modified_by='system',
            # member_dateofbirth=now,
            member_status=1
        )
        Member.objects.create(
            member_pk=get_random_string(length=24),
            member_nm=get_random_string(length=44),
            # member_created_dttm=now,
            # member_modified_dttm=now,
            member_email=f'testddd@test.com',
            # member_cell_phone_number='01000000000',
            # member_student_id=get_random_string(length=9, allowed_chars='0123456789'),
            # member_year=38,
            role_role_pk=Role.objects.get(role_nm='ROLE_DEV'),
            # rank_rank_pk=Rank.objects.get(rank_nm='정회원'),
            # major_major_pk=Major.objects.get(major_nm='인공지능학과'),
            # member_leave_absence=0,
            # member_created_by='system',
            # member_modified_by='system',
            # member_dateofbirth=now,
            member_status=1
        )

        def __create_collection(db, name, validator):
            try:
                collection = db.create_collection(name)
                # db.command({
                #     'collMod': name,
                #     'validator': validator,
                #     'validationAction': 'error'
                # })
            except:
                collection = db.get_collection(name)
            return collection

        client = pymongo.MongoClient(SURVEY_DATABASES)
        db = client.get_database(os.environ.get("TEST_DB_NAME", 'test'))
        for i in db.list_collection_names():
            db.drop_collection(i)
        cls.collection_survey = __create_collection(db, constant.SURVEY_POST_DB_NME, None)
        cls.collection_quiz = __create_collection(db, constant.SURVEY_QUIZ, None)
        cls.collection_answer = __create_collection(db, constant.SURVEY_ANSWER, None)

        def __create_post(idx, is_random=0):
            survey_data = {
                '_id': ObjectId(),
                'title': f'title{idx}',
                'description': f'description{idx}',
                'role': 100,
                'activate': True if not is_random else bool(random.choice([0, 1])),
                'created_time': datetime.datetime.now()
            }

            quizzes = [
                {"type": 0, "title": get_random_string(length=random.randint(5, 20)), "description": get_random_string(length=random.randint(5, 20)), "require": True},
                {"type": 0, "title": get_random_string(length=random.randint(5, 20)), "description": get_random_string(length=random.randint(5, 20)), "require": False},
                {"type": 1, "title": get_random_string(length=random.randint(5, 20)), "description": get_random_string(length=random.randint(5, 20)), "require": True,
                 "options": [{"text": "옵션1"}, {"text": "옵션2"}, {"text": "옵션3"}, {"text": "옵션4"}]},
                {"type": 2, "title": get_random_string(length=random.randint(5, 20)), "description": get_random_string(length=random.randint(5, 20)), "require": True,
                 "options": [{"text": "옵션1"}, {"text": "옵션2"}, {"text": "옵션3"}, {"text": "옵션4"}]}
            ]

            quizzes_data = []
            for q in quizzes:
                type = int(q['type'])
                quiz_data = {
                    '_id': ObjectId(),
                    'parent_post': survey_data['_id'],
                    'title': q['title'],
                    'description': q['description'],
                    'require': q['require'],
                    'type': type
                }
                if type == constant.SURVEY_TEXT_CODE:  # text
                    pass
                elif type == constant.SURVEY_SELECT_ONE_CODE:  # select one
                    quiz_data['options'] = []
                    for i in q['options']:
                        quiz_data['options'].append({
                            'text': i['text']
                        })
                elif type == constant.SURVEY_SELECT_MULTIPLE_CODE:
                    quiz_data['options'] = []
                    for i in q['options']:
                        quiz_data['options'].append({
                            'text': i['text']
                        })
                quizzes_data.append(quiz_data)

            cls.collection_survey.insert_one(survey_data)
            cls.collection_quiz.insert_many(quizzes_data)
            if not is_random:
                cls.survey_pks.append(str(survey_data['_id']))

        for i in range(500):
            __create_post(i, 0)
        for i in range(153):
            __create_post(i, 1)

        for k in cls.survey_pks:
            quizzes = list(cls.collection_quiz.find({'parent_post': ObjectId(k)}))
            cls.collection_answer.insert_many([{
                    '_id': ObjectId(),
                    'parent_post': ObjectId(k),
                    'user': None,
                    'answers': [
                        {"parent_quiz": quizzes[0]['_id'], "text": get_random_string(length=random.randint(10, 100))},
                        {"parent_quiz": quizzes[1]['_id'], "text": get_random_string(length=random.randint(10, 100))},
                        {"parent_quiz": quizzes[2]['_id'], "selection": random.choice([0, 2, 3])},
                        {"parent_quiz": quizzes[3]['_id'], "selections": list(list(itertools.combinations([0, 1, 2, 3], random.randint(1, 4)))[0])}
                    ]
                } for _ in range(49)])

    def __get_header(self, member_instance):
        return {
            'HTTP_USER_PK': member_instance.member_pk,
            'HTTP_ROLE_PK': member_instance.role_role_pk.role_pk
        }

    def test_survey_post_post(self):
        print("Survey post Api POST Running...")
        now = datetime.datetime.now() + datetime.timedelta(days=10)
        now = now.strftime('%Y-%m-%dT%H-%M-%S')

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))
        insert_data = '{"title": "vgcfhvbjknbhgvcfhvbj",' \
                      '"description": "cfvgbhugyvftcdrftgvyhuj",' \
                      f'"writer": "{member_instance.member_pk}",' \
                      '"role": 100,' \
                      f'"to_time": "{now}",' \
                      f'"activate": "true",' \
                      '"quizzes": [' \
                      '{"type": 0, "title": "test1", "description": "test1", "require": true},' \
                      '{"type": 0, "title": "test2", "description": "test2", "require": false},' \
                      '{"type": 1, "title": "test3", "description": "test3", "require": true, "options": [' \
                        '{"text": "옵션1"}, {"text": "옵션2"}, {"text": "옵션3"}, {"text": "옵션4"}]},' \
                      '{"type": 2, "title": "test3", "description": "test3", "require": true, "options": [' \
                        '{"text": "옵션1"}, {"text": "옵션2"}, {"text": "옵션3"}, {"text": "옵션4"}]}]}'

        # when
        respons: Response = self.client.post(self.url, data=insert_data, content_type='application/json', **self.__get_header(member_instance))
        # print(respons.content)

    def test_answer_post(self):
        print("Answer post Api POST Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))
        insert_data = '{"answers": [' \
                      '{"text": "answer text 11122233 fjf!! ^&*(*&^%$%^&*(*&^%$", "type": 0},' \
                      '{"text": "mjknbdhvinbuvuyiwhyrehiwubeyihc ncfbuihjfiub cnuegyh", "type": 0},' \
                      '{"selection": 0, "type": 1},' \
                      '{"selections": [0 ,3], "type": 2}]}'
        # when
        respons: Response = self.client.post(self.url + f'{self.survey_pks[0]}/answer/', data=insert_data, content_type='application/json', **self.__get_header(member_instance))
        print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)

    def test_survey_list(self):
        print("Survey Post list Api GET Running...")

        # given

        # when
        respons: Response = self.client.get(self.url + '?page=0')
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_200_OK)

    def test_survey_get_by_id(self):
        print("Survey Api GET BY ID Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))

        # when
        respons: Response = self.client.get(self.url + f'{self.survey_pks[0]}/', **self.__get_header(member_instance))
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_200_OK)

    def test_answer_list(self):
        print("Answer Api GET Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))

        # when
        respons: Response = self.client.get(self.url + f'{self.survey_pks[1]}/answer/', **self.__get_header(member_instance))
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_200_OK)

    def test_survey_delete(self):
        print("Post Api DELETE Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))

        # when
        respons: Response = self.client.delete(self.url + f'{self.survey_pks[2]}/', **self.__get_header(member_instance))
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)

    def test_answer_analyze_text(self):
        print("Answer Analyze TEXT Api GET Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))
        answer = list(self.collection_quiz.find({'parent_post': ObjectId(self.survey_pks[1])}))[0]

        # when
        respons: Response = self.client.get(self.url + f'{self.survey_pks[1]}/answer/?analyze=1&answer_id={answer["_id"]}', **self.__get_header(member_instance))
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_200_OK)

    def test_answer_analyze_select_one(self):
        print("Answer Analyze SELECT ONE Api GET Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))
        answer = list(self.collection_quiz.find({'parent_post': ObjectId(self.survey_pks[1])}))[2]

        # when
        respons: Response = self.client.get(self.url + f'{self.survey_pks[1]}/answer/?analyze=1&answer_id={answer["_id"]}', **self.__get_header(member_instance))
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_200_OK)

    def test_answer_analyze_select_multiple(self):
        print("Answer Analyze SELECT MULTIPLE Api GET Running...")

        # given
        member_instance = Member.objects.get(role_role_pk=Role.objects.get(role_nm='ROLE_DEV'))
        answer = list(self.collection_quiz.find({'parent_post': ObjectId(self.survey_pks[1])}))[3]
        # print(list(self.collection_quiz.find({'parent_post': ObjectId(self.survey_pks[1])})))

        # when
        respons: Response = self.client.get(self.url + f'{self.survey_pks[1]}/answer/?analyze=1&answer_id={answer["_id"]}', **self.__get_header(member_instance))
        # print(respons.content)

        # then
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
