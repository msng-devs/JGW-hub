from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.request import Request
from django.http import HttpRequest
from secret_key import TEST_JSON

class UserHeaderTestCase(APITestCase):
    def setUp(self):
        self.url = '/jgwapi/test/'
        self.url2 = '/jgwapi/testclass/'
        self.data = TEST_JSON

    def test_get_user_tocken(self):
        request = HttpRequest()
        request.method = 'GET'
        request._body = self.data
        response = self.client.generic('GET', self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_class_get_user_tocken(self):
    #     response = self.client.get(self.url2, data=self.data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
