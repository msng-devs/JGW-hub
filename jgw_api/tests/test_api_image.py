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
    Image,
    Config
)

from django.utils.crypto import get_random_string

from jgw_api.views import save_images_storge

import os
import base64
import random
import datetime
import traceback

class ImageApiTestOK(APITestCase):
    test_files_root_url = './test/file_upload_test'

    def setUp(self):
        self.url = '/hubapi/image/'

    @classmethod
    def setUpTestData(cls):
        imgs = []
        image_files = os.listdir(os.path.join(cls.test_files_root_url, 'img'))
        for i in image_files[:5]:
            with open(os.path.join(cls.test_files_root_url, 'img', i), 'rb') as f:
                encoded_img = base64.b64encode(f.read())
            imgs.append({'image_name': i, 'image_data': encoded_img, 'post_post_id_pk': 10001})
        save_images_storge(imgs)

        for i in image_files[5:10]:
            with open(os.path.join(cls.test_files_root_url, 'img', i), 'rb') as f:
                encoded_img = base64.b64encode(f.read())
            imgs.append({'image_name': i, 'image_data': encoded_img, 'post_post_id_pk': 10002})
        save_images_storge(imgs)

    def test_image_get_all_page(self):
        print("Image Api GET ALL PAGE Running...")

        # given
        query_parameters = {
            'post_id': 10001,
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = Image.objects.all().filter(post_post_id_pk=10001).order_by('image_id_pk')

        return_data = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': [{
                'image_id_pk': i.image_id_pk,
                'image_name': i.image_name,
                'image_url': i.image_url,
                'post_post_id_pk': i.post_post_id_pk
            } for i in instance]
        }

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)
