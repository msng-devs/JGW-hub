from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from jgw_api.models import (
    Category,
    Board,
    Role,
    Member,
    Rank,
    Post,
    Major,
    Image
)

from django.utils.crypto import get_random_string

from jgw_api.views import post_get_all_query

import os
import base64
import random
import datetime
import traceback

class PostApiTestOK(APITestCase):
    now = datetime.datetime.now()

    def setUp(self):
        self.url = '/hubapi/post/'
        # self.now = datetime.datetime.now()

    @classmethod
    def setUpTestData(cls):
        now = cls.now

        Role.objects.create(role_nm='ROLE_GUEST')
        Role.objects.create(role_nm='ROLE_USER0')
        Role.objects.create(role_nm='ROLE_USER1')
        Role.objects.create(role_nm='ROLE_ADMIN')
        Role.objects.create(role_nm='ROLE_DEV')

        Major.objects.create(major_nm='인공지능학과')

        Rank.objects.create(rank_nm='none')
        Rank.objects.create(rank_nm='수습회원')
        Rank.objects.create(rank_nm='정회원')
        Rank.objects.create(rank_nm='준OB')
        Rank.objects.create(rank_nm='OB')

        for i in range(10):
            Category.objects.create(category_name=get_random_string(length=random.randint(1, 10)) + str(i))

        for i in range(5):
            Board.objects.create(
                board_name=get_random_string(length=random.randint(1, 5)) + str(i),
                board_layout=random.randint(1, 3),
                role_role_pk_write_level=Role.objects.get(role_nm='ROLE_USER1'),
                role_role_pk_read_level=Role.objects.get(role_nm='ROLE_USER1'),
                role_role_pk_comment_write_level=Role.objects.get(role_nm='ROLE_USER1')
            )

        for i in range(10):
            Member.objects.create(
                member_pk=get_random_string(length=29) + str(i),
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
                member_status=1
            )

        for i in range(50):
            now += datetime.timedelta(days=1)
            category_instance = random.choice(Category.objects.all())
            board_instance = random.choice(Board.objects.all())
            member_instance = random.choice(Member.objects.all())
            Post.objects.create(
                post_title=get_random_string(length=25) + str(i),
                post_content=get_random_string(length=500) + str(i),
                post_write_time=now,
                post_update_time=now,
                category_category_id_pk=category_instance,
                board_boadr_id_pk=board_instance,
                member_member_pk=member_instance
            )

    def __get_responses_data(self, instance):
        return_data = {
            'count': instance.count(),
            'next': None,
            'previous': None,
            'results': [
                {
                    'post_id_pk': i.post_id_pk,
                    'post_title': i.post_title,
                    'post_content': i.post_content,
                    'post_write_time': i.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                    'post_update_time': i.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                    'category_category_id_pk': {
                        'category_id_pk': i.category_category_id_pk.category_id_pk,
                        'category_name': i.category_category_id_pk.category_name
                    },
                    "image_image_id_pk": i.image_image_id_pk,
                    'board_boadr_id_pk': {
                        'board_id_pk': i.board_boadr_id_pk.board_id_pk,
                        'board_name': i.board_boadr_id_pk.board_name,
                        'board_layout': i.board_boadr_id_pk.board_layout,
                        'role_role_pk_write_level': i.board_boadr_id_pk.role_role_pk_write_level.role_pk,
                        'role_role_pk_read_level': i.board_boadr_id_pk.role_role_pk_read_level.role_pk,
                        'role_role_pk_comment_write_level': i.board_boadr_id_pk.role_role_pk_comment_write_level.role_pk,
                    },
                    'member_member_pk': {
                        'member_pk': i.member_member_pk.member_pk,
                        'member_nm': i.member_member_pk.member_nm
                    }
                } for i in instance]
        }

        return return_data

    def post_get_all(self):
        print("Post Api GET ALL Running...")

        try:
            for _ in range(500):
                now = self.now
                start = now + datetime.timedelta(days=random.randint(0, 10))
                end = start + datetime.timedelta(days=random.randint(0, 10))
                page = random.randint(1, 5)

                member = random.choice(Member.objects.all())
                category = random.choice(Category.objects.all())
                board = random.choice(Board.objects.all())
                post = random.choice(Post.objects.all())

                # given
                query_parameters = {
                    'start_date': start.strftime('%Y-%m-%dT%H-%M-%S'),
                    'end_date': end.strftime('%Y-%m-%dT%H-%M-%S'),
                    'writer_uid': member.member_pk,
                    'writer_name': member.member_nm,
                    'category': category.category_id_pk,
                    'board': board.board_id_pk,
                    'title': post.post_title,
                    'order': random.choice(post._meta.fields).name,
                    'desc': random.randint(0, 1),
                    'page': page,
                }

                query_data = dict()
                for key, value in random.sample(query_parameters.items(), k=random.randint(0, 3)):
                    query_data[key] = value

                instance = post_get_all_query(query_data, Post.objects.all())
                page_size = 15
                count_all = instance.count()
                if 'page' in query_data:
                    if count_all > page_size:
                        page_size = count_all // page
                        query_data['page_size'] = page_size
                        instance = instance[page_size * (page - 1):page_size * page]
                    else:
                        del query_data['page']

                # when
                respons: Response = self.client.get(self.url, data=query_data)

                page_exist = 'page' in query_data
                query_data = sorted(query_data.items(), key=lambda x: x[0])

                # then
                return_data = {
                    'count': instance.count(),
                    'next': "http://testserver/hubapi/post/?" +
                            '&'.join([f'{k}={v + 1 if k == "page" else v}' for k, v in query_data])
                    if page_size * page < count_all and page_exist and count_all else None,
                    'previous': "http://testserver/hubapi/post/?" +
                                '&'.join([f'{k}={v - 1 if k == "page" else v}' for k, v in query_data])
                    if page > 1 and page_exist and count_all else None,
                    'results': [
                        {
                            'post_id_pk': i.post_id_pk,
                            'post_title': i.post_title,
                            'post_content': i.post_content,
                            'post_write_time': i.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                            'post_update_time': i.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                            'category_category_id_pk': {
                                'category_id_pk': i.category_category_id_pk.category_id_pk,
                                'category_name': i.category_category_id_pk.category_name
                            },
                            "image_image_id_pk": i.image_image_id_pk,
                            'board_boadr_id_pk': {
                                'board_id_pk': i.board_boadr_id_pk.board_id_pk,
                                'board_name': i.board_boadr_id_pk.board_name,
                                'board_layout': i.board_boadr_id_pk.board_layout,
                                'role_role_pk_write_level': i.board_boadr_id_pk.role_role_pk_write_level.role_pk,
                                'role_role_pk_read_level': i.board_boadr_id_pk.role_role_pk_read_level.role_pk,
                                'role_role_pk_comment_write_level': i.board_boadr_id_pk.role_role_pk_comment_write_level.role_pk,
                            },
                            'member_member_pk': {
                                'member_pk': i.member_member_pk.member_pk,
                                'member_nm': i.member_member_pk.member_nm
                            }
                        } for i in instance]
                }

                # print(query_data)
                # print(respons.content.decode('utf-8'))
                # print(return_data)
                # print()

                self.assertEqual(respons.status_code, status.HTTP_200_OK)
                self.assertJSONEqual(respons.content, return_data)
        except:
            print(traceback.format_exc())
            self.assert_(False, 'error')

    def test_post_get_all_category(self):
        print("Post Api GET ALL CATEGORY Running...")

        post = random.choice(Post.objects.all())
        category = random.choice(Category.objects.all())

        # given
        query_parameters = {
            'category': category.category_id_pk,
            'order': random.choice(post._meta.fields).name,
            'desc': random.randint(0, 1),
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = post_get_all_query(query_parameters, Post.objects.all())

        return_data = self.__get_responses_data(instance)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_get_all_name(self):
        print("Post Api GET ALL NAME Running...")

        post = random.choice(Post.objects.all())

        # given
        query_parameters = {
            'writer_name': get_random_string(
                length=1,
                allowed_chars=''.join([chr(i) for i in range(ord('A'), ord('z') + 1) if not (ord('Z') < i < ord('a'))])
            ),
            'order': random.choice(post._meta.fields).name,
            'desc': random.randint(0, 1),
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = post_get_all_query(query_parameters, Post.objects.all())

        return_data = self.__get_responses_data(instance)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_get_all_uid(self):
        print("Post Api GET ALL UID Running...")

        member = random.choice(Member.objects.all())
        post = random.choice(Post.objects.all())

        # given
        query_parameters = {
            'writer_uid': member.member_pk,
            'order': random.choice(post._meta.fields).name,
            'desc': random.randint(0, 1),
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = post_get_all_query(query_parameters, Post.objects.all())

        return_data = self.__get_responses_data(instance)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_get_all_date(self):
        print("Post Api GET ALL DATE Running...")

        now = self.now
        start = now + datetime.timedelta(days=random.randint(0, 10))
        end = start + datetime.timedelta(days=random.randint(0, 10))

        post = random.choice(Post.objects.all())

        # given
        query_parameters = {
            'start_date': start.strftime('%Y-%m-%dT%H-%M-%S'),
            'end_date': end.strftime('%Y-%m-%dT%H-%M-%S'),
            'order': random.choice(post._meta.fields).name,
            'desc': random.randint(0, 1),
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = post_get_all_query(query_parameters, Post.objects.all())

        return_data = self.__get_responses_data(instance)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_post_with_img(self):
        print("Post with Images Api POST Running...")

        test_files_root_url = './test/file_upload_test'
        # given
        with open(os.path.join(test_files_root_url, 'test.html'), 'r', encoding='utf-8') as f:
            content_data = f.readlines()
            content_data = ''.join([content.rstrip() for content in content_data])
        imgs = []
        for i in os.listdir(os.path.join(test_files_root_url, 'img')):
            with open(os.path.join(test_files_root_url, 'img', i), 'rb') as f:
                encoded_img = base64.b64encode(f.read())
            imgs.append({'name': i, 'data': encoded_img})

        now = datetime.datetime.now()
        category_instance = Category.objects.all()[random.randint(0, Category.objects.count() - 1)]
        board_instance = Board.objects.all()[random.randint(0, Board.objects.count() - 1)]
        member_instance = Member.objects.all()[random.randint(0, Member.objects.count() - 1)]

        data = {
            'post_title': 'B-tree 구현하기',
            'post_content': content_data,
            'post_write_time': now,
            'post_update_time': now,
            'category_category_id_pk': category_instance.category_id_pk,
            'board_boadr_id_pk': board_instance.board_id_pk,
            'member_member_pk': member_instance.member_pk,
            'images': imgs
        }

        # when
        response: Response = self.client.post(self.url, data=data)

        # then
        post_instance = Post.objects.get(post_title='B-tree 구현하기')
        responses_data = {
            'post_id_pk': post_instance.post_id_pk,
            'post_title': post_instance.post_title,
            'post_content': post_instance.post_content,
            'post_write_time': post_instance.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'post_update_time': post_instance.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'category_category_id_pk': {
                'category_id_pk': category_instance.category_id_pk,
                'category_name': category_instance.category_name
            },
            "image_image_id_pk": {
                'image_id_pk': post_instance.image_image_id_pk.image_id_pk,
                'image_name': post_instance.image_image_id_pk.image_name,
                'image_url': post_instance.image_image_id_pk.image_url,
            },
            'board_boadr_id_pk': {
                'board_id_pk': board_instance.board_id_pk,
                'board_name': board_instance.board_name,
                'board_layout': board_instance.board_layout,
                'role_role_pk_write_level': board_instance.role_role_pk_write_level.role_pk,
                'role_role_pk_read_level': board_instance.role_role_pk_read_level.role_pk,
                'role_role_pk_comment_write_level': board_instance.role_role_pk_comment_write_level.role_pk,
            },
            'member_member_pk': {
                'member_pk': member_instance.member_pk,
                'member_nm': member_instance.member_nm
            },
            'images': [{
                "image_id_pk": i.image_id_pk,
                "image_name": i.image_name,
                "image_url": i.image_url,
                "post_post_id_pk": i.post_post_id_pk.post_id_pk
            } for i in Image.objects.all().order_by('image_id_pk')]
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(response.content, responses_data)

    def test_post_post_no_img(self):
        print("Post no Images Api POST Running...")

        # given
        content_data = '<!DOCTYPE html><html><head></head><body><h1>TEST</h1></body></html>'

        now = datetime.datetime.now()
        category_instance = Category.objects.all()[random.randint(0, Category.objects.count() - 1)]
        board_instance = Board.objects.all()[random.randint(0, Board.objects.count() - 1)]
        member_instance = Member.objects.all()[random.randint(0, Member.objects.count() - 1)]

        data = {
            'post_title': 'html test',
            'post_content': content_data,
            'post_write_time': now,
            'post_update_time': now,
            'category_category_id_pk': category_instance.category_id_pk,
            'board_boadr_id_pk': board_instance.board_id_pk,
            'member_member_pk': member_instance.member_pk,
            'images': []
        }

        # when
        response: Response = self.client.post(self.url, data=data)

        post_instance = Post.objects.get(post_title='html test')
        # then
        responses_data = {
            'post_id_pk': post_instance.post_id_pk,
            'post_title': post_instance.post_title,
            'post_content': post_instance.post_content,
            'post_write_time': post_instance.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'post_update_time': post_instance.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'category_category_id_pk': {
                'category_id_pk': category_instance.category_id_pk,
                'category_name': category_instance.category_name
            },
            "image_image_id_pk": post_instance.image_image_id_pk,
            'board_boadr_id_pk': {
                'board_id_pk': board_instance.board_id_pk,
                'board_name': board_instance.board_name,
                'board_layout': board_instance.board_layout,
                'role_role_pk_write_level': board_instance.role_role_pk_write_level.role_pk,
                'role_role_pk_read_level': board_instance.role_role_pk_read_level.role_pk,
                'role_role_pk_comment_write_level': board_instance.role_role_pk_comment_write_level.role_pk,
            },
            'member_member_pk': {
                'member_pk': member_instance.member_pk,
                'member_nm': member_instance.member_nm
            },
            'images': []
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(response.content, responses_data)
