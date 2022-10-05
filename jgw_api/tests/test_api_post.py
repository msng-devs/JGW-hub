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

class PostApiTestOK(APITestCase):
    now = datetime.datetime.now()
    post_count = 100

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

        Config.objects.create(config_nm='admin_role_pk', config_val='4')

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

        for i in range(cls.post_count):
            now += datetime.timedelta(days=1)
            category_instance = random.choice(Category.objects.all())
            board_instance = random.choice(Board.objects.all())
            member_instance = random.choice(Member.objects.all())
            Post.objects.create(
                post_title=get_random_string(length=98) + str(i),
                post_content=get_random_string(length=500) + str(i),
                post_write_time=now,
                post_update_time=now,
                category_category_id_pk=category_instance,
                board_boadr_id_pk=board_instance,
                member_member_pk=member_instance
            )

    def __get_responses_data_pagenation(self, instance, query_parameters):
        next = previous = None
        if 'page' in query_parameters:
            page = query_parameters['page']
            query = sorted(query_parameters.items(), key=lambda x: x[0])
            if page != 1:
                previous = 'http://testserver/hubapi/post/?' +\
                           '&'.join([f'{i[0]}={i[1] - 1 if i[0] == "page" else i[1]}' for i in query])
            if page != self.post_count / query_parameters['page_size']:
                next = 'http://testserver/hubapi/post/?' +\
                           '&'.join([f'{i[0]}={i[1] + 1 if i[0] == "page" else i[1]}' for i in query])
        return_data = {
            'count': instance.count(),
            'next': next,
            'previous': previous,
            'results': [self.__get_response_data(i) for i in instance]
        }
        return return_data

    def __get_response_data(self, instance):
        responses_data = {
            'post_id_pk': instance.post_id_pk,
            'post_title': instance.post_title,
            'post_content': instance.post_content,
            'post_write_time': instance.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'post_update_time': instance.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'category_category_id_pk': {
                'category_id_pk': instance.category_category_id_pk.category_id_pk,
                'category_name': instance.category_category_id_pk.category_name
            },
            "image_image_id_pk": instance.image_image_id_pk,
            'board_boadr_id_pk': {
                'board_id_pk': instance.board_boadr_id_pk.board_id_pk,
                'board_name': instance.board_boadr_id_pk.board_name,
                'board_layout': instance.board_boadr_id_pk.board_layout,
                'role_role_pk_write_level': instance.board_boadr_id_pk.role_role_pk_write_level.role_pk,
                'role_role_pk_read_level': instance.board_boadr_id_pk.role_role_pk_read_level.role_pk,
                'role_role_pk_comment_write_level': instance.board_boadr_id_pk.role_role_pk_comment_write_level.role_pk,
            },
            'member_member_pk': {
                'member_pk': instance.member_member_pk.member_pk,
                'member_nm': instance.member_member_pk.member_nm
            }
        }
        return responses_data

    def test_post_get_all_page(self):
        print("Post Api GET ALL PAGE Running...")

        post = random.choice(Post.objects.all())
        page_size = random.choice([10, 25, 50])
        page = random.randint(1, self.post_count // page_size)

        # given
        query_parameters = {
            'page': page,
            'page_size': page_size,
            'order': random.choice(post._meta.fields).name,
            'desc': random.randint(0, 1),
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = post_get_all_query(query_parameters, Post.objects.all())
        instance = instance[page_size * (page - 1):page_size * page]

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

        # print(respons.content.decode('utf-8'))
        # print(return_data)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_get_all_title(self):
        print("Post Api GET ALL TITLE Running...")

        post = random.choice(Post.objects.all())

        # given
        query_parameters = {
            'title': get_random_string(
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

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_get_all_board(self):
        print("Post Api GET ALL BOARD Running...")

        post = random.choice(Post.objects.all())
        board = random.choice(Board.objects.all())

        # given
        query_parameters = {
            'board': board.board_id_pk,
            'order': random.choice(post._meta.fields).name,
            'desc': random.randint(0, 1),
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = post_get_all_query(query_parameters, Post.objects.all())

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

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

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

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

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

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

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_get_all_date(self):
        print("Post Api GET ALL DATE Running...")

        now = self.now
        start = now + datetime.timedelta(days=random.randint(0, 30))
        end = start + datetime.timedelta(days=random.randint(0, 70))

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

        return_data = self.__get_responses_data_pagenation(instance, query_parameters)

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    # def test_post_post_with_img(self):
    #     print("Post with Images Api POST Running...")
    #
    #     test_files_root_url = './test/file_upload_test'
    #     # given
    #     with open(os.path.join(test_files_root_url, 'test.html'), 'r', encoding='utf-8') as f:
    #         content_data = f.readlines()
    #         content_data = ''.join([content.rstrip() for content in content_data])
    #     imgs = []
    #     for i in os.listdir(os.path.join(test_files_root_url, 'img')):
    #         with open(os.path.join(test_files_root_url, 'img', i), 'rb') as f:
    #             encoded_img = base64.b64encode(f.read())
    #         imgs.append({'name': i, 'data': encoded_img})
    #
    #     now = datetime.datetime.now()
    #     category_instance = Category.objects.all()[random.randint(0, Category.objects.count() - 1)]
    #     board_instance = Board.objects.all()[random.randint(0, Board.objects.count() - 1)]
    #     member_instance = Member.objects.all()[random.randint(0, Member.objects.count() - 1)]
    #
    #     data = {
    #         'post_title': 'B-tree 구현하기',
    #         'post_content': content_data,
    #         'post_write_time': now,
    #         'post_update_time': now,
    #         'category_category_id_pk': category_instance.category_id_pk,
    #         'board_boadr_id_pk': board_instance.board_id_pk,
    #         'member_member_pk': member_instance.member_pk,
    #         'images': imgs
    #     }
    #
    #     # when
    #     response: Response = self.client.post(self.url, data=data)
    #
    #     # then
    #     post_instance = Post.objects.get(post_title='B-tree 구현하기')
    #     responses_data = {
    #         'post_id_pk': post_instance.post_id_pk,
    #         'post_title': post_instance.post_title,
    #         'post_content': post_instance.post_content,
    #         'post_write_time': post_instance.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
    #         'post_update_time': post_instance.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
    #         'category_category_id_pk': {
    #             'category_id_pk': category_instance.category_id_pk,
    #             'category_name': category_instance.category_name
    #         },
    #         "image_image_id_pk": {
    #             'image_id_pk': post_instance.image_image_id_pk.image_id_pk,
    #             'image_name': post_instance.image_image_id_pk.image_name,
    #             'image_url': post_instance.image_image_id_pk.image_url,
    #         },
    #         'board_boadr_id_pk': {
    #             'board_id_pk': board_instance.board_id_pk,
    #             'board_name': board_instance.board_name,
    #             'board_layout': board_instance.board_layout,
    #             'role_role_pk_write_level': board_instance.role_role_pk_write_level.role_pk,
    #             'role_role_pk_read_level': board_instance.role_role_pk_read_level.role_pk,
    #             'role_role_pk_comment_write_level': board_instance.role_role_pk_comment_write_level.role_pk,
    #         },
    #         'member_member_pk': {
    #             'member_pk': member_instance.member_pk,
    #             'member_nm': member_instance.member_nm
    #         },
    #         'images': [{
    #             "image_id_pk": i.image_id_pk,
    #             "image_name": i.image_name,
    #             "image_url": i.image_url,
    #             "post_post_id_pk": i.post_post_id_pk.post_id_pk
    #         } for i in Image.objects.all().order_by('image_id_pk')]
    #     }
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertJSONEqual(response.content, responses_data)

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
            'member_member_pk': member_instance.member_pk
        }

        # when
        header_data = {
            'user_pk': member_instance.member_pk,
            'user_role_pk': member_instance.role_role_pk.role_pk
        }
        response: Response = self.client.post(self.url, data=data, **header_data)

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
            }
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(response.content, responses_data)

    def test_post_get_by_id(self):
        print("Post Api GET BY ID Running...")

        # given

        # when
        post_instance = Post.objects.all()[random.randint(0, self.post_count - 1)]
        key = post_instance.post_id_pk

        header_data = {
            'user_pk': post_instance.member_member_pk.member_pk,
            'user_role_pk': post_instance.member_member_pk.role_role_pk.role_pk
        }
        respons: Response = self.client.get(f"{self.url}{key}/", **header_data)

        thumbnail_image = post_instance.image_image_id_pk

        # then
        responses_data = {
            'post_id_pk': post_instance.post_id_pk,
            'post_title': post_instance.post_title,
            'post_content': post_instance.post_content,
            'post_write_time': post_instance.post_write_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'post_update_time': post_instance.post_update_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'category_category_id_pk': {
                'category_id_pk': post_instance.category_category_id_pk.category_id_pk,
                'category_name': post_instance.category_category_id_pk.category_name
            },
            "image_image_id_pk":
                None if thumbnail_image is None else {
                'image_id_pk': thumbnail_image.image_id_pk,
                'image_name': thumbnail_image.image_name,
                'image_url': thumbnail_image.image_url,
            },
            'board_boadr_id_pk': {
                'board_id_pk': post_instance.board_boadr_id_pk.board_id_pk,
                'board_name': post_instance.board_boadr_id_pk.board_name,
                'board_layout': post_instance.board_boadr_id_pk.board_layout,
                'role_role_pk_write_level': post_instance.board_boadr_id_pk.role_role_pk_write_level.role_pk,
                'role_role_pk_read_level': post_instance.board_boadr_id_pk.role_role_pk_read_level.role_pk,
                'role_role_pk_comment_write_level': post_instance.board_boadr_id_pk.role_role_pk_comment_write_level.role_pk,
            },
            'member_member_pk': {
                'member_pk': post_instance.member_member_pk.member_pk,
                'member_nm': post_instance.member_member_pk.member_nm
            }
        }

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, responses_data)

    def test_post_patch_by_id(self):
        print("Post Api PATCH BY ID Running...")
        # given
        target = Post.objects.all().order_by('post_id_pk')[self.post_count - 1]
        key = target.post_id_pk

        patch_data = {
            "post_title": "Test" * 10
        }
        header_data = {
            'user_pk': target.member_member_pk.member_pk,
            'user_role_pk': target.member_member_pk.role_role_pk.role_pk
        }

        # when
        respons: Response = self.client.patch(f"{self.url}{key}/", data=patch_data, **header_data)

        # then
        target = Post.objects.all().order_by('post_id_pk').filter(post_id_pk=key)[0]
        return_data = self.__get_response_data(target)
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_post_delete_by_id(self):
        print("Post Api DELETE BY ID Running...")
        # given

        # when
        target = Post.objects.all().order_by('post_id_pk')[self.post_count - 1]
        key = target.post_id_pk
        header_data = {
            'user_pk': target.member_member_pk.member_pk,
            'user_role_pk': target.member_member_pk.role_role_pk.role_pk
        }
        respons: Response = self.client.delete(f"{self.url}{key}/", **header_data)

        # then
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)