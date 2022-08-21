from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from jgw_api.models import (
    Category,
    Board,
    Role
)
import random

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
                role_role_pk_write_level=Role.objects.get(role_pk=random.randint(1, 5)),
                role_role_pk_read_level=Role.objects.get(role_pk=random.randint(1, 5))
            )

        # when
        respons: Response = self.client.get(self.url)

        # then
        return_data = {
                'count': Board.objects.count(),
                'next': None,
                'previous': None,
                'results': [{"board_id_pk": i.board_id_pk, "board_name": i.board_name,
                             "role_role_pk_write_level": {
                                 'role_pk': i.role_role_pk_write_level.role_pk,
                                 'role_nm': i.role_role_pk_write_level.role_nm
                             },
                             "role_role_pk_read_level": {
                                 'role_pk': i.role_role_pk_read_level.role_pk,
                                 'role_nm': i.role_role_pk_read_level.role_nm
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
                role_role_pk_write_level=Role.objects.get(role_pk=random.randint(1, 5)),
                role_role_pk_read_level=Role.objects.get(role_pk=random.randint(1, 5))
            )

        # when
        respons: Response = self.client.get(self.url, data={'page': 1})

        # then
        return_data = {
                'count': 10,
                'next': 'http://testserver/hubapi/board/?page=2',
                'previous': None,
                'results': [{"board_id_pk": i.board_id_pk, "board_name": i.board_name,
                             "role_role_pk_write_level": {
                                 'role_pk': i.role_role_pk_write_level.role_pk,
                                 'role_nm': i.role_role_pk_write_level.role_nm
                             },
                             "role_role_pk_read_level": {
                                 'role_pk': i.role_role_pk_read_level.role_pk,
                                 'role_nm': i.role_role_pk_read_level.role_nm
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
            role_role_pk_write_level=Role.objects.get(role_pk=1),
            role_role_pk_read_level=Role.objects.get(role_pk=1)
        )
        Board.objects.create(
            board_name='공지사항2',
            role_role_pk_write_level=Role.objects.get(role_pk=2),
            role_role_pk_read_level=Role.objects.get(role_pk=2)
        )

        # when
        target = '공지사항1'
        key = Board.objects.filter(board_name=target)[0].board_id_pk
        respons: Response = self.client.get(f"{self.url}{key}/")

        # then
        return_data = {
            "board_id_pk": key,
            "board_name": target,
            "role_role_pk_write_level": {
                'role_pk': 1,
                'role_nm': 'ROLE_GUEST'
            },
            "role_role_pk_read_level": {
                'role_pk': 1,
                'role_nm': 'ROLE_GUEST'
            }
        }
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_board_post(self):
        print("Board Api POST Running...")

        # given
        data = '[{"board_name": "test1", "role_role_pk_write_level": 1,"role_role_pk_read_level": 1},' \
               '{"board_name": "test2", "role_role_pk_write_level": 2,"role_role_pk_read_level": 1}]'

        # when
        respons: Response = self.client.post(self.url, data=data, content_type='application/json')

        # then
        responses_data = [{"board_id_pk": i.board_id_pk, "board_name": i.board_name,
                             "role_role_pk_write_level": i.role_role_pk_write_level.role_pk,
                             "role_role_pk_read_level": i.role_role_pk_read_level.role_pk}
                          for i in Board.objects.all().order_by('board_id_pk')]
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(respons.content, responses_data)
