from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpRequest
from jgw_api.models import Category

class CategoryApiTest(APITestCase):
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
        return_data = [{"category_id_pk": i.category_id_pk, "category_name": i.category_name}
                       for i in Category.objects.all()]
        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_category_post(self):
        print("Category Api POST Running...")

        # given
        data = {
            "category_name": "Java"
        }

        # when
        respons: Response = self.client.post(self.url, data=data)

        # then
        self.assertEqual(respons.status_code, status.HTTP_201_CREATED)

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

    def test_category_put(self):
        print("Category Api PUT BY ID Running...")
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
        respons: Response = self.client.put(f"{self.url}{key}/", data=patch_data)

        # then
        self.assertEqual(respons.status_code, status.HTTP_403_FORBIDDEN)
