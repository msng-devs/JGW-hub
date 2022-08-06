from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.request import Request
from django.http import HttpRequest
from secret_key import TEST_JSON
import requests

class UserHeaderTestCase(APITestCase):
    def setUp(self):
        self.url = 'http://localhost:8080/test/'
        self.url2 = '/jgwapi/testclass/'
        self.data = TEST_JSON

    def test_get_user_tocken(self):
        headers = {'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjA2M2E3Y2E0M2MzYzc2MDM2NzRlZGE0YmU5NzcyNWI3M2QwZGMwMWYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vamFyYW0tZ3JvdXAtd2FyZSIsImF1ZCI6ImphcmFtLWdyb3VwLXdhcmUiLCJhdXRoX3RpbWUiOjE2NTk3NTM3NTQsInVzZXJfaWQiOiJnOXhtZkp4b2dhUFV3N2hlUWFPQXBZOEdRSEEzIiwic3ViIjoiZzl4bWZKeG9nYVBVdzdoZVFhT0FwWThHUUhBMyIsImlhdCI6MTY1OTc1Mzc1NCwiZXhwIjoxNjU5NzU3MzU0LCJlbWFpbCI6InRlc3R1c2VyMEB0ZXN0LmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJ0ZXN0dXNlcjBAdGVzdC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.yhyCw1dQo9Y0hInC1vsy7moDhb6yNbDjFcahir9GHpwbbpH6CfgKyaSN3oK9OVMrZOka9xSkJtfUG_A30gBkBrDTLtFsYT1tBhdi9K7h-N3AXe1rJoWP-kl_F7GMfMsYPhQMPrg1VgnEJTVDeX-JH71fO5S2N8Jh0sFH9fDLg5_apaCXpwMx_IGSjDfd9UbyDvQ-ueqyBzl8hVUVrDbFRKuzY5YbQwAaZHorSOQF2lh6w-S3_52Gs4_zUqyAHWIfbnBYQw_BXt3P8PcrKHynhyo0iQ-6JDoO3VqhCT6XsGCALjSAynQocf3yiCfDUPkg_eiLLTFf21DJjPd4-STyPg'}
        response = requests.get(self.url, headers=headers)
        self.assertEqual(response.status_code, 200)

    # def test_class_get_user_tocken(self):
    #     response = self.client.get(self.url2, data=self.data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
