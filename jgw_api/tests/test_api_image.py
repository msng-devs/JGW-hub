from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from jgw_api.models import (
    Board,
    Role,
    Member,
    Rank,
    Post,
    Major,
    Image,
    Config
)

from jgw_api.views import save_images_storge

import os
import base64
import random
import datetime
import traceback

class ImageApiTestOK(APITestCase):
    test_files_root_url = './test/file_upload_test'

    def setUp(self):
        self.url = '/hub/api/v1/image/'

    @classmethod
    def setUpTestData(cls):
        now = datetime.datetime.now()

        Role.objects.create(role_pk=0, role_nm='ROLE_GUEST')

        Config.objects.create(config_nm='admin_role_pk', config_val='500', config_pk=500)
        Config.objects.create(config_nm='min_upload_role_pk', config_val='0', config_pk=501)

        Major.objects.create(major_nm='인공지능학과', major_pk=0)

        Rank.objects.create(rank_nm='none', rank_pk=0)

        Board.objects.create(
            board_name='test',
            board_layout=random.randint(1, 3),
            role_role_pk_write_level=Role.objects.get(role_nm='ROLE_GUEST'),
            role_role_pk_read_level=Role.objects.get(role_nm='ROLE_GUEST'),
            role_role_pk_comment_write_level=Role.objects.get(role_nm='ROLE_GUEST')
        )

        Member.objects.create(
            member_pk='ksjd793JNSO918234OLAKWMD',
            member_nm='test1',
            # member_created_dttm=now,
            # member_modified_dttm=now,
            member_email=f'test@test.com',
            # member_cell_phone_number='01000000000',
            # member_student_id='012345678',
            # member_year=38,
            role_role_pk=Role.objects.get(role_nm='ROLE_GUEST'),
            # rank_rank_pk=Rank.objects.get(rank_nm='none'),
            # major_major_pk=Major.objects.get(major_nm='인공지능학과'),
            # member_leave_absence=0,
            # member_created_by='system',
            # member_modified_by='system',
            # member_dateofbirth=now,
            member_status=1
        )

        Post.objects.create(
            post_title='test',
            post_content='content',
            post_write_time=now,
            post_update_time=now,
            board_boadr_id_pk=Board.objects.get(board_name='test'),
            member_member_pk=Member.objects.get(member_nm='test1')
        )
        Post.objects.create(
            post_title='test',
            post_content='content',
            post_write_time=now,
            post_update_time=now,
            board_boadr_id_pk=Board.objects.get(board_name='test'),
            member_member_pk=Member.objects.get(member_nm='test1')
        )

        imgs = []
        image_files = os.listdir(os.path.join(cls.test_files_root_url, 'img'))
        post_post_id_pk = Post.objects.all()[0].post_id_pk
        for i in image_files[:10]:
            with open(os.path.join(cls.test_files_root_url, 'img', i), 'rb') as f:
                encoded_img = base64.b64encode(f.read())
            imgs.append({'image_name': i, 'image_data': encoded_img, 'post_post_id_pk': int(post_post_id_pk)})

        for i in save_images_storge(imgs, Member.objects.all()[0].member_pk):
            Image.objects.create(
                image_name=i['image_name'],
                image_url=i['image_url'],
                post_post_id_pk=Post.objects.get(post_id_pk=int(i['post_post_id_pk'])),
                member_member_pk=Member.objects.all()[0]
            )

        imgs = []
        for i in image_files[10:20]:
            with open(os.path.join(cls.test_files_root_url, 'img', i), 'rb') as f:
                encoded_img = base64.b64encode(f.read())
            imgs.append({'image_name': i, 'image_data': encoded_img, 'post_post_id_pk': None})

        for i in save_images_storge(imgs, None):
            Image.objects.create(
                image_name=i['image_name'],
                image_url=i['image_url'],
                post_post_id_pk=Post.objects.get(post_id_pk=int(i['post_post_id_pk']))
                    if i['post_post_id_pk'] is not None else None,
                member_member_pk=Member.objects.all()[0]
            )

    def test_image_get_all_page(self):
        print("Image Api GET ALL PAGE Running...")

        # given
        post_id = Post.objects.all()[0].post_id_pk
        query_parameters = {
            'post_id': post_id,
        }

        # when
        respons: Response = self.client.get(self.url, data=query_parameters)

        # then
        instance = Image.objects.all().filter(post_post_id_pk=post_id).order_by('image_id_pk')

        return_data = {
            'count': instance.count(),
            'next': None,
            'previous': None,
            'results': [{
                'image_id_pk': i.image_id_pk,
                'image_name': i.image_name,
                'image_url': i.image_url,
                'post_post_id_pk': i.post_post_id_pk.post_id_pk,
                'member_member_pk': i.member_member_pk.member_pk if i.member_member_pk else None
            } for i in instance]
        }

        self.assertEqual(respons.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(respons.content, return_data)

    def test_image_get_by_id(self):
        print("Image Api GET BY ID Running...")

        # given

        # when
        image_instance = Image.objects.all()[random.randint(0, 19)]
        key = image_instance.image_id_pk
        responses: Response = self.client.get(f"{self.url}{key}/")

        # then
        responses_data = {
            'image_id_pk': image_instance.image_id_pk,
            'image_name': image_instance.image_name,
            'image_url': image_instance.image_url,
            'post_post_id_pk': image_instance.post_post_id_pk.post_id_pk if image_instance.post_post_id_pk else None,
            'member_member_pk': image_instance.member_member_pk.member_pk if image_instance.member_member_pk else None
        }

        self.assertEqual(responses.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(responses.content, responses_data)

    def test_image_delete_by_id(self):
        print("Image Api DELETE BY ID Running...")
        # given

        # when
        target = Image.objects.all().order_by('image_id_pk')[Image.objects.count() - 1]
        key = target.image_id_pk
        header_data = {
            'HTTP_USER_PK': target.member_member_pk.member_pk,
            'HTTP_ROLE_PK': target.member_member_pk.role_role_pk.role_pk
        }
        respons: Response = self.client.delete(f"{self.url}{key}/", **header_data)

        # then
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)

    def test_image_post(self):
        print("Image Api POST Running...")

        test_files_root_url = './test/file_upload_test'
        # given
        target_member = Member.objects.all()[0]
        header_data = {
            'HTTP_USER_PK': target_member.member_pk,
            'HTTP_ROLE_PK': target_member.role_role_pk.role_pk
        }

        data = '['
        for idx, i in enumerate(os.listdir(os.path.join(test_files_root_url, 'img'))[25:]):
            with open(os.path.join(test_files_root_url, 'img', i), 'rb') as f:
                encoded_img = base64.b64encode(f.read())
            if idx:
                data += ','
            data += '{' + f'"image_name": "{i}", "image_data": "' + encoded_img.decode("utf-8") + '", "post_post_id_pk": null' + '}'
        data += ']'

        # when
        response: Response = self.client.post(self.url, data=data, content_type='application/json', **header_data)

        # then
        responses_data = [
            {
                'image_id_pk': i.image_id_pk,
                'image_name': i.image_name,
                'image_url': i.image_url,
                'member_member_pk': i.member_member_pk.member_pk if i.member_member_pk else None,
                'post_post_id_pk': i.post_post_id_pk.post_id_pk if i.post_post_id_pk else None
            } for i in Image.objects.all()[20:]
        ]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(response.content, responses_data)
