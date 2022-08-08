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

    def category_get_api(self):
        print("Category GET ALL")
        response: Response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('GET data:', response.data)
        return response.data

    def category_post_api(self, content):
        print("Category POST")
        data = {
            "category_name": content
        }
        response: Response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def category_get_by_id(self, key):
        print("Category GET BY ID")
        url = self.url + str(key) + '/'
        response: Response = self.client.get(url)
        print("GET Rust:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def category_delete_by_id(self, key):
        print("Category DELETE BY ID")
        url = self.url + str(key) + '/'
        response: Response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_api_ok(self):
        self.category_post_api('Rust')
        self.category_post_api('Java')
        self.category_post_api('Python')
        data = self.category_get_api()
        for i in data:
            key = i['category_id_pk']
            if i['category_name'] == 'Rust':
                break
        self.category_get_by_id(key)
        self.category_delete_by_id(key)
