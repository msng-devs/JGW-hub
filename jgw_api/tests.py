from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpRequest
from secret_key import TEST_JSON

class CategoryApiTest(APITestCase):
    def setUp(self):
        self.url = '/hubapi/category/'

    def test_category_get_api(self):
        response: Response = self.client.get(self.url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_post_api(self):
        data = {
            "category_name": "Rust"
        }
        response: Response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response: Response = self.client.get(self.url)
        print(response.data)
