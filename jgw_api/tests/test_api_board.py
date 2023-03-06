from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from jgw_api.models import (
    Board,
    Role,
    Config
)
import random

class BoardApiTestOK(APITestCase):
    databases = '__all__'
    def setUp(self):
        self.url = '/hub/api/v1/board/'

    @classmethod
    def setUpTestData(cls):
        Role.objects.create(role_pk=0, role_nm='ROLE_GUEST')
        Role.objects.create(role_pk=100, role_nm='ROLE_USER0')
        Role.objects.create(role_pk=101, role_nm='ROLE_USER1')
        Role.objects.create(role_pk=500, role_nm='ROLE_ADMIN')
        Role.objects.create(role_pk=501, role_nm='ROLE_DEV')

        Config.objects.create(config_nm='admin_role_pk', config_val='500', config_pk=500)

    def __make_header(self):
        header_data = {
            'HTTP_USER_PK': 'pkpkpkpkpkpkpkpkpkpkpk',
            'HTTP_ROLE_PK': 500
        }
        return header_data

    def test_board_get(self):
        print("Board Api GET ALL Pagination Running...")

        # given
        for i in range(20):
            Board.objects.create(
                board_name=f'공지사항{i}',
                board_layout=0,
                role_role_pk_write_level=Role.objects.get(role_pk=random.choice([0, 100, 101, 500, 501])),
                role_role_pk_read_level=Role.objects.get(role_pk=random.choice([0, 100, 101, 500, 501])),
                role_role_pk_comment_write_level=Role.objects.get(role_pk=random.choice([0, 100, 101, 500, 501]))
            )

        # when
        respons: Response = self.client.get(self.url, data={'page': 1}, **self.__make_header())

        # then
        total_count = Board.objects.count()
        return_data = {
                'count': 10,
                'total_pages': total_count // 10 + (1 if total_count % 2 else 0),
                'next': 'http://testserver/hub/api/v1/board/?page=2',
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
            role_role_pk_write_level=Role.objects.get(role_pk=0),
            role_role_pk_read_level=Role.objects.get(role_pk=0),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=0)
        )
        Board.objects.create(
            board_name='공지사항2',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=0),
            role_role_pk_read_level=Role.objects.get(role_pk=0),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=0)
        )

        # when
        target = '공지사항1'
        ins = Board.objects.filter(board_name=target)[0]
        respons: Response = self.client.get(f"{self.url}{ins.board_id_pk}/", **self.__make_header())

        # then
        return_data = {
            "board_id_pk": ins.board_id_pk,
            "board_name": ins.board_name,
            'board_layout': ins.board_layout,
            "role_role_pk_write_level": {
                'role_pk': 0,
                'role_nm': 'ROLE_GUEST'
            },
            "role_role_pk_read_level": {
                'role_pk': 0,
                'role_nm': 'ROLE_GUEST'
            },
            "role_role_pk_comment_write_level": {
                'role_pk': 0,
                'role_nm': 'ROLE_GUEST'
            }
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_post(self):
        print("Board Api POST Running...")

        # given
        data = {
                   "board_name": "test1",
                   "board_layout": 0,
                   "role_role_pk_write_level": 100,
                   "role_role_pk_read_level": 100,
                   "role_role_pk_comment_write_level": 100
               }

        # when
        respons: Response = self.client.post(self.url, data=data, **self.__make_header())

        # then
        i = Board.objects.get(board_name='test1')
        responses_data = {
            "board_id_pk": i.board_id_pk,
            "board_name": i.board_name,
            'board_layout': i.board_layout,
            "role_role_pk_write_level": i.role_role_pk_write_level.role_pk,
            "role_role_pk_read_level": i.role_role_pk_read_level.role_pk,
            'role_role_pk_comment_write_level': i.role_role_pk_comment_write_level.role_pk
        }
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(respons.content, responses_data)

    def test_board_patch_by_id(self):
        print("Board Api PATCH BY ID Running...")
        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=0),
            role_role_pk_read_level=Role.objects.get(role_pk=0),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=0)
        )
        Board.objects.create(
            board_name='공지사항2',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=0),
            role_role_pk_read_level=Role.objects.get(role_pk=0),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=0)
        )
        patch_data = {
            "board_name": "자유게시판",
            'role_role_pk_write_level': 100
        }

        # when
        target = '공지사항1'
        instance = Board.objects.filter(board_name=target)[0]
        key = instance.board_id_pk
        respons: Response = self.client.patch(f"{self.url}{key}/", data=patch_data, **self.__make_header())

        # then
        return_data = {
            "board_id_pk": key,
            "board_name": '자유게시판',
            'board_layout': 0,
            "role_role_pk_write_level": 100,
            "role_role_pk_read_level": 0,
            'role_role_pk_comment_write_level': 0
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_delete_by_id(self):
        print("Board Api DELETE BY ID Running...")
        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=100),
            role_role_pk_read_level=Role.objects.get(role_pk=101),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=101)
        )
        Board.objects.create(
            board_name='공지사항2',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=100),
            role_role_pk_read_level=Role.objects.get(role_pk=100),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=101)
        )

        # when
        target = '공지사항1'
        instance = Board.objects.filter(board_name=target)[0]
        key = instance.board_id_pk
        respons: Response = self.client.delete(f"{self.url}{key}/", **self.__make_header())

        # then
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)

class BoardApiError(APITestCase):
    databases = '__all__'
    def setUp(self):
        self.url = '/hub/api/v1/board/'

    @classmethod
    def setUpTestData(cls):
        Role.objects.create(role_pk=0, role_nm='ROLE_GUEST')
        Role.objects.create(role_pk=1, role_nm='ROLE_USER0')
        Role.objects.create(role_pk=2, role_nm='ROLE_USER1')
        Role.objects.create(role_pk=3, role_nm='ROLE_ADMIN')
        Role.objects.create(role_pk=4, role_nm='ROLE_DEV')

        Config.objects.create(config_nm='admin_role_pk', config_val='4')

    def __make_header(self):
        header_data = {
            'HTTP_USER_PK': 'pkpkpkpkpkpkpkpkpkpkpk',
            'HTTP_ROLE_PK': 5
        }
        return header_data

    def test_board_get_by_id_not_found(self):
        print("Board Api GET BY ID not found Running...")

        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=1),
            role_role_pk_read_level=Role.objects.get(role_pk=1),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=1)
        )

        # when
        respons: Response = self.client.get(f"{self.url}1000/", **self.__make_header())

        # then
        return_data = {
            'detail': 'Not found.'
        }
        self.assertEqual(respons.status_code, status.HTTP_404_NOT_FOUND)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_post_already_exist(self):
        print("Board Api POST already exist Running...")

        # given
        Board.objects.create(
            board_name='공지사항1',
            board_layout=0,
            role_role_pk_write_level=Role.objects.get(role_pk=0),
            role_role_pk_read_level=Role.objects.get(role_pk=0),
            role_role_pk_comment_write_level=Role.objects.get(role_pk=0)
        )

        data = {
            "board_name": "공지사항1",
            "board_layout": 0,
            "role_role_pk_write_level": 0,
            "role_role_pk_read_level": 20,
            "role_role_pk_comment_write_level": 0
        }

        # when
        respons: Response = self.client.post(self.url, data=data, **self.__make_header())

        # then
        responses_data = {
            "board_name":["board with this board name already exists."],
            "role_role_pk_read_level":["Invalid pk \"20\" - object does not exist."]
        }
        self.assertEqual(respons.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(respons.content, responses_data)

    def test_board_post_required(self):
        print("Board Api POST already exist not found Running...")

        # given

        data = {
            "board_name": "공지사항1",
            "board_layout": 0,
        }

        # when
        respons: Response = self.client.post(self.url, data=data, **self.__make_header())

        # then
        responses_data = {
            "role_role_pk_write_level":["This field is required."],
            "role_role_pk_read_level":["This field is required."],
            "role_role_pk_comment_write_level":["This field is required."]
        }
        self.assertEqual(respons.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(respons.content, responses_data)
