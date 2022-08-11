from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpRequest
from secret_key import TEST_JSON
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
        return_data = [
            {
                "category_id_pk": 1,
                "category_name": "Java"
            },
            {
                "category_id_pk": 2,
                "category_name": "Python"
            },
            {
                "category_id_pk": 3,
                "category_name": "Rust"
            }
        ]
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
