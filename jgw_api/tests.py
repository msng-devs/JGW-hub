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

from .views import post_get_all_query

import os
import base64
import random
import datetime
import traceback

class CategoryApiTestOK(APITestCase):
    def setUp(self):
        self.url = '/hubapi/category/'

    def test_category_get_all(self):
        print("Category Api GET ALL Running...")

        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        Category.objects.create(category_name="Rust")

        # when
        respons: Response = self.client.get(self.url)

        # then
        return_data = {
                'count': Category.objects.count(),
                'next': None,
                'previous': None,
                'results': [{"category_id_pk": i.category_id_pk, "category_name": i.category_name}
                            for i in Category.objects.all().order_by('category_id_pk')]
            }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_get_pagination(self):
        print("Category Api GET ALL Pagination Running...")

        # given
        datas = ['Java', 'Python', 'ML', 'Back-end', 'Rust', 'Ruby', 'HTML', 'CSS',
                 'JS', 'C', 'C#', 'Brainfuck', 'tensorflow']
        for d in datas:
            Category.objects.create(category_name=d)

        # when
        respons: Response = self.client.get(self.url, data={'page': 1})

        # then
        return_data = {
            'count': 10,
            'next': 'http://testserver/hubapi/category/?page=2',
            'previous': None,
            'results': [{"category_id_pk": i.category_id_pk, "category_name": i.category_name}
                        for i in Category.objects.all().order_by('category_id_pk')[:10]]
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_post(self):
        print("Category Api POST Running...")

        # given
        data = '[{"category_name": "Python"},{"category_name": "Rust"}]'

        # when
        respons: Response = self.client.post(self.url, data=data, content_type='application/json')

        # then
        responses_data = [{"category_id_pk": i.category_id_pk, "category_name": i.category_name}
                        for i in Category.objects.all().order_by('category_id_pk')]
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(respons.content, responses_data)

    def test_category_get_by_id(self):
        print("Category Api GET BY ID Running...")

        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        Category.objects.create(category_name="Rust")


        # when
        target = 'Python'
        key = Category.objects.filter(category_name=target)[0].category_id_pk
        respons: Response = self.client.get(f"{self.url}{key}/")

        # then
        return_data = {
                "category_id_pk": key,
                "category_name": target
            }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_patch_by_id(self):
        print("Category Api PATCH BY ID Running...")
        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        Category.objects.create(category_name="Rust")
        patch_data = {
            "category_name": "JS"
        }

        # when
        target = 'Python'
        instance = Category.objects.filter(category_name=target)[0]
        key = instance.category_id_pk
        respons: Response = self.client.patch(f"{self.url}{key}/", data=patch_data)

        # then
        return_data = {
            "category_id_pk": key,
            "category_name": "JS"
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_delete_by_id(self):
        print("Category Api DELETE BY ID Running...")
        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        Category.objects.create(category_name="Rust")

        # when
        target = 'Python'
        instance = Category.objects.filter(category_name=target)[0]
        key = instance.category_id_pk
        respons: Response = self.client.delete(f"{self.url}{key}/")

        # then
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)

class CategoryApiTestError(APITestCase):
    def setUp(self):
        self.url = '/hubapi/category/'

    def test_category_get_by_id_not_exist(self):
        print("Category Api GET BY ID not exist Running...")

        # given

        # when
        respons: Response = self.client.get(f'{self.url}0/')

        # then
        return_data = {
            "detail": "Not found."
        }
        self.assertEqual(respons.status_code, status.HTTP_404_NOT_FOUND)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_get_pagination_out_of_idx(self):
        print("Category Api GET ALL Pagination out of idx Running...")

        # given

        # when
        respons: Response = self.client.get(self.url, data={'page': 3})

        # then
        return_data = {
            "detail": "Invalid page."
        }
        self.assertEqual(respons.status_code, status.HTTP_404_NOT_FOUND)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_put_405(self):
        print("Category Api PUT BY ID Running...")
        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        Category.objects.create(category_name="Rust")
        put_data = {
            "category_name": "JS"
        }

        # when
        target = 'Python'
        instance = Category.objects.filter(category_name=target)[0]
        key = instance.category_id_pk
        respons: Response = self.client.put(f"{self.url}{key}/", data=put_data)

        # then
        self.assertEqual(respons.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_category_post_already_exist(self):
        print("Category Api POST already exist Running...")

        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        data = '[{"category_name": "Java"},{"category_name": "Test"}]'

        # when
        respons: Response = self.client.post(self.url, data=data, content_type='application/json')

        # then
        responses_data = {"detail":"category with this category name already exists."}
        self.assertEqual(respons.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(respons.content, responses_data)

    def test_category_patch_already_exist(self):
        print("Category Api PATCH BY ID already exist Running...")
        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        patch_data = {
            "category_name": "Python"
        }

        # when
        target = 'Java'
        instance = Category.objects.filter(category_name=target)[0]
        key = instance.category_id_pk
        respons: Response = self.client.patch(f"{self.url}{key}/", data=patch_data)

        # then
        return_data = {"detail":"category with this category name already exists."}
        self.assertEqual(respons.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_patch_id_not_exist(self):
        print("Category Api PATCH BY ID not exist Running...")
        # given
        Category.objects.create(category_name="Java")
        Category.objects.create(category_name="Python")
        patch_data = {
            "category_name": "Python"
        }

        # when
        respons: Response = self.client.patch(f"{self.url}0/", data=patch_data)

        # then
        return_data = {'detail': 'Not found.'}
        self.assertEqual(respons.status_code, status.HTTP_404_NOT_FOUND)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_delete_by_id_not_exist(self):
        print("Category Api DELETE BY ID not exist Running...")
        # given
        Category.objects.create(category_name="Java")

        # when
        respons: Response = self.client.delete(f"{self.url}0/")

        # then
        return_data = {'detail': 'Not found.'}
        self.assertEqual(respons.status_code, status.HTTP_404_NOT_FOUND)
        self.assertJSONEqual(respons.content, return_data)

class BoardApiTestOK(APITestCase):
    def setUp(self):
        self.url = '/hubapi/board/'

    @classmethod
    def setUpTestData(cls):
        Role.objects.create(role_nm='ROLE_GUEST')
        Role.objects.create(role_nm='ROLE_USER0')
        Role.objects.create(role_nm='ROLE_USER1')
        Role.objects.create(role_nm='ROLE_ADMIN')
        Role.objects.create(role_nm='ROLE_DEV')

    def test_board_get_all(self):
        print("Board Api GET ALL Running...")

        # given
        for i in range(20):
            Board.objects.create(
                board_name=f'공지사항{i}',
                board_layout=0,
                role_role_pk_write_level=Role.objects.get(role_pk=random.randint(1, 5)),
                role_role_pk_read_level=Role.objects.get(role_pk=random.randint(1, 5)),
                role_role_pk_comment_write_level=Role.objects.get(role_pk=random.randint(1, 5))
            )

        # when
        respons: Response = self.client.get(self.url)

        # then
        return_data = {
                'count': Board.objects.count(),
                'next': None,
                'previous': None,
                'results': [{"board_id_pk": i.board_id_pk,
                             "board_name": i.board_name,
                             'board_layout': i.board_layout,
                             "role_role_pk_write_level": {
                                 'role_pk': i.role_role_pk_write_level.role_pk,
                                 'role_nm': i.role_role_pk_write_level.role_nm
                             },
                             "role_role_pk_read_level": {
                                 'role_pk': i.role_role_pk_read_level.role_pk,
                                 'role_nm': i.role_role_pk_read_level.role_nm
                             },
                             "role_role_pk_comment_write_level": {
                                 'role_pk': i.role_role_pk_comment_write_level.role_pk,
                                 'role_nm': i.role_role_pk_comment_write_level.role_nm
                             }}
                            for i in Board.objects.all().order_by('board_id_pk')]
            }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_get_pagination(self):
        print("Board Api GET ALL Pagination Running...")

        # given
        for i in range(20):
            Board.objects.create(
                board_name=f'공지사항{i}',
                board_layout=0,
                role_role_pk_write_level=Role.objects.get(role_pk=random.randint(1, 5)),
                role_role_pk_read_level=Role.objects.get(role_pk=random.randint(1, 5)),
                role_role_pk_comment_write_level=Role.objects.get(role_pk=random.randint(1, 5))
            )

        # when
        respons: Response = self.client.get(self.url, data={'page': 1})

        # then
        return_data = {
                'count': 10,
                'next': 'http://testserver/hubapi/board/?page=2',
                'previous': None,
                'results': [{"board_id_pk": i.board_id_pk,
                             "board_name": i.board_name,
                             'board_layout': i.board_layout,
                             "role_role_pk_write_level": {
                                 'role_pk': i.role_role_pk_write_level.role_pk,
                                 'role_nm': i.role_role_pk_write_level.role_nm
                             },
                             "role_role_pk_read_level": {
                                 'role_pk': i.role_role_pk_read_level.role_pk,
                                 'role_nm': i.role_role_pk_read_level.role_nm
                             },
                             "role_role_pk_comment_write_level": {
                                 'role_pk': i.role_role_pk_comment_write_level.role_pk,
                                 'role_nm': i.role_role_pk_comment_write_level.role_nm
                             }}
                            for i in Board.objects.all().order_by('board_id_pk')[:10]]
            }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_get_by_id(self):
        print("Board Api GET BY ID Running...")

        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=1),
            role_role_pk_read_level=Role.objects.get(role_pk=1),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=1)
        )
        Board.objects.create(
            board_name='공지사항2',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=2),
            role_role_pk_read_level=Role.objects.get(role_pk=2),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=2)
        )

        # when
        target = '공지사항1'
        ins = Board.objects.filter(board_name=target)[0]
        respons: Response = self.client.get(f"{self.url}{ins.board_id_pk}/")

        # then
        return_data = {
            "board_id_pk": ins.board_id_pk,
            "board_name": ins.board_name,
            'board_layout': ins.board_layout,
            "role_role_pk_write_level": {
                'role_pk': 1,
                'role_nm': 'ROLE_GUEST'
            },
            "role_role_pk_read_level": {
                'role_pk': 1,
                'role_nm': 'ROLE_GUEST'
            },
            "role_role_pk_comment_write_level": {
                'role_pk': 1,
                'role_nm': 'ROLE_GUEST'
            }
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_post(self):
        print("Board Api POST Running...")

        # given
        data = '[{"board_name": "test1", "board_layout": 0, "role_role_pk_write_level": 1,' \
               '"role_role_pk_read_level": 1, "role_role_pk_comment_write_level": 1},' \
               '{"board_name": "test2", "board_layout": 0, "role_role_pk_write_level": 2,' \
               '"role_role_pk_read_level": 1, "role_role_pk_comment_write_level": 2}]'

        # when
        respons: Response = self.client.post(self.url, data=data, content_type='application/json')

        # then
        responses_data = [{"board_id_pk": i.board_id_pk,
                           "board_name": i.board_name,
                            'board_layout': i.board_layout,
                            "role_role_pk_write_level": i.role_role_pk_write_level.role_pk,
                            "role_role_pk_read_level": i.role_role_pk_read_level.role_pk,
                           'role_role_pk_comment_write_level': i.role_role_pk_comment_write_level.role_pk}
                          for i in Board.objects.all().order_by('board_id_pk')]
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(respons.content, responses_data)

    def test_board_patch_by_id(self):
        print("Board Api PATCH BY ID Running...")
        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=1),
            role_role_pk_read_level=Role.objects.get(role_pk=3),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=3)
        )
        Board.objects.create(
            board_name='공지사항2',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=2),
            role_role_pk_read_level=Role.objects.get(role_pk=2),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=3)
        )
        patch_data = {
            "board_name": "자유게시판",
            'role_role_pk_write_level': 1
        }

        # when
        target = '공지사항1'
        instance = Board.objects.filter(board_name=target)[0]
        key = instance.board_id_pk
        respons: Response = self.client.patch(f"{self.url}{key}/", data=patch_data)

        # then
        return_data = {
            "board_id_pk": key,
            "board_name": '자유게시판',
            'board_layout': 0,
            "role_role_pk_write_level": 1,
            "role_role_pk_read_level": 3,
            'role_role_pk_comment_write_level': 3
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_delete_by_id(self):
        print("Board Api DELETE BY ID Running...")
        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=1),
            role_role_pk_read_level=Role.objects.get(role_pk=3),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=3)
        )
        Board.objects.create(
            board_name='공지사항2',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=2),
            role_role_pk_read_level=Role.objects.get(role_pk=2),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=3)
        )

        # when
        target = '공지사항1'
        instance = Board.objects.filter(board_name=target)[0]
        key = instance.board_id_pk
        respons: Response = self.client.delete(f"{self.url}{key}/")

        # then
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)

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
                member_nm=get_random_string(length=random.randint(1, 5)) + str(i),
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

    def test_post_get_all(self):
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
