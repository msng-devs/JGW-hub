from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from jgw_api.models import (
    Board,
    Role,
)
import random

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