import random

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.conf import settings
from django.utils.crypto import get_random_string

from typing import List

from ..models import (
    Image,
)
from ..serializers import (
    ImageSerializer,
)
from ..custom_pagination import (
    ImagePageNumberPagination,
)

import jgw_api.constant as constant

import base64
import shutil
import ast

from typing import Dict
from secrets_content.files.secret_key import *

from .view_check import (
    get_logger,
    request_check_admin_role,
    request_check_admin_upload_role
)

logger = get_logger()

def save_images_storge(
        images_data: List[str],
        member_pk: str) -> List[Dict[str, str]]:
    '''
    base64로 인코딩된 이미지 데이터를 실제 서버에 저장하는 함수

    :param images_data: 이미지 정보가 담겨있는 리스트. image_name, image_data, post_post_id_pk
    :param member_pk: 이미지를 추가한 유저의 pk
    :return: 실제 서버에 추가된 이미지의 정보 리스트. image_name, image_url, post_post_id_pk, member_member_pk
    '''
    if settings.TESTING:
        # unittest시 이전 테스트 기록 지우기
        logger.debug("recent image upload test file deleted")
        img_path = os.path.join(settings.MEDIA_ROOT, 'test', 'imgs')
        if os.path.exists(img_path):
            shutil.rmtree(img_path)
        os.makedirs(img_path, exist_ok=True)
    img_urls = []
    for img in images_data:
        # image 목록 순차적으로 가져와 저장 후 저장 정보 리턴
        img = ast.literal_eval(str(img))
        name = img['image_name']
        data = img['image_data']
        folder_pk = img['post_post_id_pk']

        # base64 -> byte 이미지 디코딩
        decoded_data = base64.b64decode(data)
        if settings.TESTING:
            # unittest시 test path에 저장
            img_path = os.path.join(
                settings.MEDIA_ROOT, 'test', 'imgs',
                str(folder_pk) if folder_pk is not None else 'common')
            # if os.path.exists(img_path):
            #     shutil.rmtree(img_path)
        else:
            img_path = os.path.join(
                settings.MEDIA_ROOT, 'imgs',
                str(folder_pk) if folder_pk is not None else 'common')
        os.makedirs(img_path, exist_ok=True)
        save_name = get_random_string(length=random.randint(10, 15), allowed_chars=constant.RANDOM_STRING_CHARS)
        while os.path.isfile(os.path.join(img_path, save_name)):
            save_name = get_random_string(length=random.randint(10, 15), allowed_chars=constant.RANDOM_STRING_CHARS)
        with open(os.path.join(img_path, save_name), 'wb') as f:
            f.write(decoded_data)
        url = os.path.join(img_path, save_name).replace('\\', '/').split(settings.MEDIA_URL)[1]
        img_urls.append({
            'image_name': name,
            'image_url': 'uploaded/' + url,
            'post_post_id_pk': folder_pk,
            'member_member_pk': member_pk
        })
    logger.info(f"saved image count: {len(img_urls)}")
    return img_urls

class ImageViewSet(viewsets.ModelViewSet):
    '''
    이미지 api를 담당하는 클래스
    '''
    serializer_class = ImageSerializer
    queryset = Image.objects.prefetch_related('post_post_id_pk', 'member_member_pk').all()
    http_method_names = ['get', 'post', 'delete']
    pagination_class = ImagePageNumberPagination

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_upload_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role, 최소 업로드 가능 role 중 하나라도 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk, min_upload_role_pk = checked

        if user_role_id >= admin_role_pk or user_role_id >= min_upload_role_pk:
            # 요청한 유저가 admin or 최소 업로드 가능 role 보다 높으면 승인
            logger.debug(f'{user_uid} Image post approved')
            data = request.data
            data = save_images_storge(data, user_uid)
            img_serializer = ImageSerializer(data=data, many=True)
            img_serializer.is_valid()
            logger.debug(f'{user_uid} Image data verified')

            self.perform_create(img_serializer)

            responses_data = img_serializer.data
            update_log = f'{user_uid} Image data created' \
                         f'\t{len(responses_data)} images created'
            logger.info(update_log)

            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Image create denied")
            detail = {
                'detail': 'Image upload not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Image get request")
        queryset = Image.objects.prefetch_related('post_post_id_pk', 'member_member_pk').all()
        if 'post_id' in request.query_params:
            # query parameter에 post_id가 있으면 해당 게시글에 포함된 이미지만 가져옴
            queryset = queryset.filter(post_post_id_pk=int(request.query_params['post_id']))
        if 'image_name' in request.query_params:
            queryset = queryset.get(image_name=request.query_params['image_name'])
        queryset = queryset.order_by('image_id_pk')

        request.query_params._mutable = True
        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # 'page size'를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.IMAGE_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.IMAGE_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.IMAGE_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.IMAGE_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        key, name = instance.image_id_pk, instance.image_name
        logger.debug(f'Image data get retrieve\tkey: {key}\tname: {name}')
        return Response(serializer.data)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        instance = self.get_object()
        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            # 요청한 유저가 admin or 사진을 업로드한 본인이면 승인
            logger.debug(f'{user_uid} Image delete approved')
            key, name = instance.image_id_pk, instance.image_name
            self.perform_destroy(instance)
            logger.debug(f'{user_uid} Image data deleted\tkey: {key}\ttitle: {name}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.info(f"{user_uid} Image delete denied")
            detail = {
                'detail': 'Image delete not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
