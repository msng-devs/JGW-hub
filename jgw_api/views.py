import datetime
import random

from rest_framework import viewsets, status, renderers, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.conf import settings
from django.db import connection
from django.utils.crypto import get_random_string
from django.db import models
from django.http import QueryDict

from typing import List, Dict

from .models import (
    Board,
    Post,
    Image,
    Config,
    Comment,
    Member,
)
from .serializers import (
    BoardGetSerializer,
    BoardWriteSerializer,
    PostWriteSerializer,
    ImageSerializer,
    PostGetSerializer,
    PostPatchSerializer,
    CommentGetSerializer,
    CommentWriteSerializer,
    CommentWriteResultSerializer
)
from .custom_pagination import (
    BoardPageNumberPagination,
    PostPageNumberPagination,
    ImagePageNumberPagination,
    CommentPageNumberPagination
)

import jgw_api.constant as constant

import base64
import os
import shutil
import traceback
import ast
import logging

from typing import Union, Tuple, Dict
import rest_framework
import django
from secrets_content.files.secret_key import *
import pymongo

# 자람 허브 로거
# logger = logging.getLogger('hub')
logger = logging.getLogger('hub_error')

def get_user_header(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int]]:
    '''
    전달받은 request에서 user header를 가져오는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header가 정상적으로 존재한다면 user의 uid, role이 리턴.
        user header가 없다면 500 response 리턴
    '''
    # 헤더에서 유저 정보 가져오기
    user_uid = request.META.get('HTTP_USER_PK', None)
    user_role_id = request.META.get('HTTP_ROLE_PK', None)

    if user_uid is None or user_role_id is None:
        # 유저 정보가 정상적으로 없다면 500 response 리턴
        logger.error('get user information failed.')
        responses_data = {
            'detail': 'Header Required.'
        }
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # 유저 정보가 있다면 유저 정보 리턴
        user_role_id = int(user_role_id)
        logger.info(f'get user information success\tuser uid: {user_uid}\tuser role: {user_role_id}')
        return user_uid, user_role_id

def get_admin_role_pk() -> Union[rest_framework.response.Response, int]:
    '''
    Config 테이블에서 admin의 role이 몇 이상이지 가져오는 함수

    :return: admin의 최소 role 번호.
        최소 admin role의 정보가 없다면 500 response 리턴.
    '''
    try:
        # 어드민 롤을 정상적으로 가져오면 최소 어드민 롤 리턴
        config_admin_role = Config.objects.get(config_nm='admin_role_pk').config_val
        # logger.debug(f'get admin role success\tmin admin role: {config_admin_role}')
        return int(config_admin_role)
    except:
        # 최소 어드민 롤 정보가 없다면 500 response 리턴
        responses_data = {
            'detail': 'Admin Role not Exist.'
        }
        logger.error('min admin role not found')
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_min_upload_role_pk() -> Union[rest_framework.response.Response, int]:
    '''
    Config 테이블에서 서버에 콘텐츠(사진, 동영상 등)를 업로드 할 수 있는 role이 최소 몇 이상이지 가져오는 함수

    :return: 콘텐츠를 업로드 할 수 있는 최소 role 번호.
        최소 admin role의 정보가 없다면 500 response 리턴.
    '''
    config_admin_role = Config.objects.filter(config_nm='min_upload_role_pk')
    if config_admin_role:
        # 최소 업로드 롤을 정상적으로 가져오면 최소 업로드 롤 리턴
        return int(config_admin_role[0].config_val)
    else:
        # 최소 업로드 롤 정보가 없다면 500 response 리턴
        responses_data = {
            'detail': 'Minimum upload role not exist.'
        }
        logger.error('min upload role not found')
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def request_check(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int]]:
    '''
    user header가 정상적으로 리턴됐는지 확인하는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header가 정상적으로 존재한다면 user의 uid, role이 리턴.
        user header가 없다면 500 response 리턴
    '''
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        # get_user_header 에서 response 타입이 리턴됐다면 오류
        return header_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id

def request_check_admin_role(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int, int]]:
    '''
    user header, admin role 모두가 정상적으로 리턴됐는지 확인하는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header, admin role 모두가 정상적으로 존재한다면 user의 uid, role, admin role이 리턴.
        user header, admin role 중 하나라도 없다면 500 response 리턴
    '''
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        # get_user_header 에서 response 타입이 리턴됐다면 오류
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
        # get_admin_role_pk 에서 response 타입이 리턴됐다면 오류
        return admin_role_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id, admin_role_checked

def request_check_admin_upload_role(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int, int, int]]:
    '''
    user header, admin role, 최소 업로드 가능 role 모두가 정상적으로 리턴됐는지 확인하는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header, admin role, 최소 업로드 가능 role 모두가 정상적으로 존재한다면 user의 uid, role, admin role이 리턴.
        user header, admin role, 최소 업로드 가능 role 중 하나라도 없다면 500 response 리턴
    '''
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        # get_user_header 에서 response 타입이 리턴됐다면 오류
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
        # get_admin_role_pk 에서 response 타입이 리턴됐다면 오류
        return admin_role_checked
    min_upload_role_checked = get_min_upload_role_pk()
    if isinstance(min_upload_role_checked, Response):
        # get_min_upload_role_pk 에서 response 타입이 리턴됐다면 오류
        return min_upload_role_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id, admin_role_checked, min_upload_role_checked

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


@api_view(['GET'])
def ping_pong(request):
    # 서버 health check 용도
    return Response({
            'detail': 'pong'
        }, status.HTTP_200_OK)

class BoardViewSet(viewsets.ModelViewSet):
    '''
    게시판 api를 담당하는 클래스
    '''
    serializer_class = BoardGetSerializer
    queryset = Board.objects.all().order_by('board_id_pk')
    pagination_class = BoardPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Board get request")
        queryset = self.filter_queryset(self.get_queryset())
        request.query_params._mutable = True
        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.BOARD_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.BOARD_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.BOARD_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.BOARD_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        responses = self.get_paginated_response(serializer.data)
        return responses

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        key, name = instance.board_id_pk, instance.board_name
        logger.debug(f'Board data get retrieve\tkey: {key}\tname: {name}')
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        # 요청한 유저의 정보를 헤더로 확인
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            # 요청한 유저가 admin 이라면 승인
            logger.debug(f'{user_uid} Board create approved')
            serializer = BoardWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Board data verified')
            self.perform_create(serializer)
            responses_data = serializer.data

            update_log = f'{user_uid} Board data created' \
                         f'\tkey: {responses_data["board_id_pk"]} created log'
            for k in responses_data.keys():
                update_log += f'\n\t{k}: {responses_data[k]}'
            logger.info(update_log)

            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Board create denied")
            detail = {
                'detail': 'Not Allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        # 요청한 유저의 정보를 헤더로 확인
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            # 요청한 유저가 admin 이라면 승인
            logger.debug(f'{user_uid} Board patch approved')
            instance = self.get_object()
            request_data = request.data
            target_keys = list(request_data.dict().keys())
            before_change = dict()
            for k in target_keys:
                before_change[k] = getattr(instance, k)

            serializer = BoardWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Board data verified')
            self.perform_update(serializer)
            responses_data = serializer.data

            update_log = f'{user_uid} Board data patched' \
                         f'\tkey: {responses_data["board_id_pk"]} change log'
            for k in target_keys:
                update_log += f'\n\t{k}: {before_change[k]} -> {responses_data[k]}'
            logger.info(update_log)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(responses_data)
        else:
            logger.info(f"{user_uid} Board patch denied")
            detail = {
                'detail': 'Not Allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # delete
    def destroy(self, request, *args, **kwargs):
        # 요청한 유저의 정보를 헤더로 확인
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            # 요청한 유저가 admin 이라면 승인
            logger.debug(f'{user_uid} Board delete approved')
            instance = self.get_object()
            key, name = instance.board_id_pk, instance.board_name
            self.perform_destroy(instance)
            logger.debug(f'{user_uid} Board data deleted\tkey: {key}\tname: {name}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.info(f"{user_uid} Board delete denied")
            detail = {
                'detail': 'Not Allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)



def post_get_all_query(
        query_params: dict,
        queryset: django.db.models.query.QuerySet) -> django.db.models.query.QuerySet:
    '''
    post api 쿼리 파라미터를 추출하는 함수

    :param query_params: 필터에 적용시킬 쿼리 파라미터
    :param queryset: 쿼리 파라미터를 적용시킬 post instance
    :return: 쿼리 파라미터에 맞게 추출된 django orm instance 리턴
    '''
    start_date = datetime.datetime.min
    end_date = datetime.datetime.max
    time_query = '%Y-%m-%dT%H-%M-%S'
    if 'start_date' in query_params:
        start_date = datetime.datetime.strptime(query_params['start_date'], time_query)
    if 'end_date' in query_params:
        end_date = datetime.datetime.strptime(query_params['end_date'], time_query)
    queryset = queryset.filter(post_write_time__range=(start_date, end_date))

    if 'writer_uid' in query_params:
        queryset = queryset.filter(member_member_pk=query_params['writer_uid'])

    if 'writer_name' in query_params:
        queryset = queryset.filter(member_member_pk__member_nm__contains=query_params['writer_name'])

    if 'board' in query_params:
        # if is_admin:
        #     queryset = queryset.filter(board_boadr_id_pk=query_params['board'])
        # else:
        #     queryset = queryset.filter(
        #         board_boadr_id_pk=query_params['board'],
        #         board_boadr_id_pk__role_role_pk_read_level__role_pk__gte=user_role_id
        #     )
        queryset = queryset.filter(board_boadr_id_pk=query_params['board'])

    if 'title' in query_params:
        queryset = queryset.filter(post_title__icontains=query_params['title'])

    if 'order' in query_params:
        if 'desc' in query_params and int(query_params['desc']):
            queryset = queryset.order_by('-' + query_params['order'])
        else:
            queryset = queryset.order_by(query_params['order'])
    else:
        queryset = queryset.order_by('post_write_time')
    return queryset

class PostViewSet(viewsets.ModelViewSet):
    '''
    게시글 api를 담당하는 클래스
    '''
    serializer_class = PostGetSerializer
    queryset = Post.objects.all()
    pagination_class = PostPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Post get request")
        queryset = Post.objects.all()
        queryset = post_get_all_query(request.query_params, queryset)

        request.query_params._mutable = True
        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.POST_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.POST_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.POST_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.POST_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        data = serializer.data
        for i in data:
            if len(i['post_content']) > 500:
                i['post_content'] = i['post_content'][:500]
        return self.get_paginated_response(data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        checked = request_check(request)
        if isinstance(checked, Response):
            # user role이 없다면 최하위 권한 적용
            user_role_id = -1
            user_uid = None
        else:
            user_uid, user_role_id = checked
        admin_role_checked = get_admin_role_pk()
        if isinstance(admin_role_checked, Response):
            # admin role이 없다면 500 return
            return admin_role_checked

        instance = self.get_object()

        if user_role_id >= admin_role_checked or user_role_id >= instance.board_boadr_id_pk.role_role_pk_read_level.role_pk:
            # 요청한 유저가 admin or 해당 게시판 게시글 읽기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Post get retrieve approved')
            post_serializer = self.get_serializer(instance)
            response_data = post_serializer.data

            key, name = instance.post_id_pk, instance.post_title
            logger.debug(f'{user_uid} Post data get retrieve\tkey: {key}\ttitle: {name}')
            return Response(response_data)
        else:
            logger.info(f"{user_uid} Post get retrieve denied")
            detail = {
                'detail': 'Not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        if user_uid == instance.member_member_pk.member_pk and user_role_id >= instance.board_boadr_id_pk.role_role_pk_write_level.role_pk:
            # 요청한 유저가 글을 작성했던 본인이고, 해당 게시판 게시글 쓰기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Post patch approved')
            request_data = request.data
            target_keys = list(request_data.dict().keys())
            before_change = dict()
            for k in target_keys:
                before_change[k] = getattr(instance, k)

            if isinstance(request_data, QueryDict):
                request_data._mutable = True
            if 'board_boadr_id_pk' in request_data:
                # 변경하려는 데이터가 해당 게시글이 소속된 게시판이라면
                board_instance = Board.objects.get(board_id_pk=int(request_data['board_boadr_id_pk']))
                if board_instance.role_role_pk_write_level.role_pk > user_role_id:
                    # 변경하려는 게시판의 쓰기 레벨보다 요청한 유저의 권한이 낮다면 거부
                    logger.info(f"{user_uid} Post patch denied - request board not allowed")
                    responses_data = {
                        'detail': 'request board is not allowed.'
                    }
                    return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

            # if 'post_update_time' not in request_data:
            #     request_data['post_update_time'] = datetime.datetime.now()
            # if 'post_write_time' in request_data:
            #     del request_data['post_write_time']

            serializer = PostPatchSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Post data verified')
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            instance = Post.objects.get(post_id_pk=instance.post_id_pk)

            responses_serializer = self.get_serializer(instance)
            responses_data = responses_serializer.data
            update_log = f'{user_uid} Post data patched' \
                         f'\tkey: {responses_data["post_id_pk"]} change log'
            for k in target_keys:
                instance_data = getattr(instance, k)
                before_change_data = before_change[k]
                if k in ('post_content', 'post_title'):
                    instance_data = instance_data[:50]
                    before_change_data = before_change_data[:50]
                update_log += f'\n\t{k}: {before_change_data} -> {instance_data}'
            logger.info(update_log)

            return Response(responses_data)
        else:
            logger.info(f"{user_uid} Post patch denied")
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role 중 하나라도 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        request_data = request.data
        if isinstance(request_data, QueryDict):
            request_data._mutable = True
        # now = datetime.datetime.now()
        # request_data['post_write_time'] = now
        # request_data['post_update_time'] = now

        post_serializer = PostWriteSerializer(data=request_data)
        post_serializer.is_valid(raise_exception=True)
        logger.debug(f'{user_uid} Post data verified')

        board_instance = post_serializer.validated_data['board_boadr_id_pk']
        if user_role_id >= admin_role_pk or user_role_id >= board_instance.role_role_pk_write_level.role_pk:
            # 요청한 유저가 admin or 요청한 게시판 게시글 쓰기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Post post approved')
            self.perform_create(post_serializer)

            post_pk = post_serializer.data['post_id_pk']
            responses_instance = Post.objects.get(post_id_pk=post_pk)
            serializer = self.get_serializer(responses_instance)

            responses_data = serializer.data
            update_log = f'{user_uid} Post data created' \
                         f'\tkey: {responses_data["post_id_pk"]} created log'
            for k in responses_data.keys():
                instance_data = getattr(responses_instance, k)
                if k in ('post_content', 'post_title'):
                    instance_data = instance_data[:50]
                update_log += f'\n\t{k}: {instance_data}'
            logger.info(update_log)

            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Post create denied")
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk, = checked

        instance = self.get_object()

        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            # 요청한 유저가 admin or 글을 작성한 본인이면 승인
            logger.debug(f'{user_uid} Post delete approved')
            key, name = instance.post_id_pk, instance.post_title
            self.perform_destroy(instance)

            logger.debug(f'{user_uid} Post data deleted\tkey: {key}\ttitle: {name}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.info(f"{user_uid} Post delete denied")
            detail = {
                'detail': 'Image delete not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)



class ImageViewSet(viewsets.ModelViewSet):
    '''
    이미지 api를 담당하는 클래스
    '''
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
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
        queryset = Image.objects.all()
        if 'post_id' in request.query_params:
            # query parameter에 post_id가 있으면 해당 게시글에 포함된 이미지만 가져옴
            queryset = queryset.filter(post_post_id_pk=int(request.query_params['post_id']))

        queryset = queryset.order_by('image_id_pk')

        request.query_params._mutable = True
        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
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

class CommentViewSet(viewsets.ModelViewSet):
    '''
    댓글 api를 담당하는 클래스
    '''
    serializer_class = CommentGetSerializer
    queryset = Comment.objects.all().order_by('-comment_id')
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CommentPageNumberPagination

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Comment get request")
        request.query_params._mutable = True
        if 'post_id' not in request.query_params:
            # query parameter에 post_id가 없으면 400 return
            return Response(data={
                'detail': 'post_id request'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # query parameter에 post_id가 있으면 해당 게시글에 포함된 댓글만 가져옴
            queryset = self.get_queryset().filter(
                post_post_id_pk=int(request.query_params['post_id']),
                comment_comment_id_ref=None
            )

        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.COMMENT_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.COMMENT_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.COMMENT_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.COMMENT_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role 중 하나라도 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        request_data = request.data
        comment_serializer = CommentWriteSerializer(data=request_data)
        comment_serializer.is_valid(raise_exception=True)
        logger.debug(f'{user_uid} Comment data verified')

        post_instance = comment_serializer.validated_data['post_post_id_pk']
        board_instance = post_instance.board_boadr_id_pk
        if user_role_id >= admin_role_pk or user_role_id >= board_instance.role_role_pk_comment_write_level.role_pk:
            # 요청한 유저가 admin or 요청한 게시판 댓글 쓰기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Comment post approved')
            self.perform_create(comment_serializer)

            comment_pk = comment_serializer.data['comment_id']
            responses_instance = Comment.objects.get(comment_id=comment_pk)
            serializer = CommentWriteResultSerializer(responses_instance)

            responses_data = serializer.data
            update_log = f'{user_uid} Comment data created' \
                         f'\tkey: {responses_data["comment_id"]} created log'
            for k in responses_data.keys():
                instance_data = getattr(responses_instance, k)
                if k in ('comment_content',):
                    instance_data = instance_data[:50]
                update_log += f'\n\t{k}: {instance_data}'
            logger.info(update_log)

            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Comment create denied")
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        board_instance = instance.post_post_id_pk.board_boadr_id_pk
        user_instance = instance.member_member_pk
        if user_role_id >= board_instance.role_role_pk_comment_write_level.role_pk \
                and user_uid == user_instance.member_pk:
            # 요청한 유저의 role이 해당 게시판 댓글 쓰기 레벨 이상이고, 댓글을 작성했던 본인이면 승인
            logger.debug(f'{user_uid} Comment patch approved')
            request_data = request.data
            target_keys = list(request_data.dict().keys())
            before_change = dict()
            for k in target_keys:
                before_change[k] = getattr(instance, k)

            serializer = CommentWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Comment data verified')

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            responses_data = serializer.data
            update_log = f'{user_uid} Comment data patched' \
                         f'\tkey: {responses_data["comment_id"]} change log'
            for k in target_keys:
                instance_data = getattr(instance, k)
                before_change = before_change[k]
                if k in ('post_content', 'post_title'):
                    instance_data = instance_data[:50]
                    before_change = before_change[:50]
                update_log += f'\n\t{k}: {before_change} -> {instance_data}'
            logger.info(update_log)
            return Response(responses_data)
        else:
            logger.info(f"{user_uid} Comment patch denied")
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk, = checked

        instance = self.get_object()

        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            # 요청한 유저가 admin or 댓글을 업로드한 본인이면 승인
            logger.debug(f'{user_uid} Comment delete approved')
            request_data = {"comment_delete": 1}
            serializer = CommentWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            key, name = instance.comment_id, instance.comment_content
            logger.debug(f'{user_uid} Comment data deleted\tkey: {key}\ttitle: {name[:25]}')
            return Response(serializer.data)
        else:
            logger.info(f"{user_uid} Comment delete denied")
            detail = {
                'detail': 'Image delete not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)


# 설문조사

class SurveyViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        def __create_collection(db, name, validator):
            try:
                collection = db.create_collection(name)
                db.command({
                    'collMod': name,
                    'validator': validator,
                    'validationAction': 'error'
                })
            except:
                collection = db.get_collection(name)
            return collection

        self.client = pymongo.MongoClient(**SURVEY_DATABASES)

        if not settings.TESTING:
            self.db = self.client.get_database(constant.SURVEY_DB_NAME)
        else:
            self.db = pymongo.MongoClient(**SURVEY_DATABASES).get_database(os.environ.get("TEST_DB_NAME", 'test'))
            for i in self.db.list_collection_names():
                self.db.drop_collection(i)
        self.survey_post_collection = __create_collection(self.db, constant.SURVEY_POST_DB_NME, constant.SURVEY_POST_DB_VALIDATOR)
        self.text_question_collection = __create_collection(self.db, constant.SURVEY_TEXT_QUIZ, constant.SURVEY_TEXT_QUIZ_VALIDATOR)
        self.text_answer_collection = __create_collection(self.db, constant.SURVEY_TEXT_ANSWER, constant.SURVEY_TEXT_ANSWER_VALIDATOR)
        self.select_one_question_collection = __create_collection(self.db, constant.SURVEY_SELECT_ONE_QUIZ, constant.SURVEY_SELECT_ONE_QUIZ_VALIDATOR)
        self.select_one_answer_collection = __create_collection(self.db, constant.SURVEY_SELECT_ONE_ANSWER, constant.SURVEY_SELECT_ONE_ANSWER_VALIDATOR)

    def __make_question_data(self, data):
        type = int(data['type'])
        quiz_data = {
            'title': data['title'],
            'description': data['description'],
            'require': bool(data['require']),
            'answers': []
        }
        if type == 0: # text
            result = self.text_question_collection.insert_one(quiz_data)
        elif type == 1: # select one
            quiz_data['options'] = []
            for i in data['options']:
                quiz_data['options'].append({
                    'text': i['text']
                })
            result = self.select_one_question_collection.insert_one(quiz_data)
        else:
            return None
        return result

    def create(self, request):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            post_data = request.data

            try:
                new_data = {
                    'title': post_data['title'],
                    'description': post_data['description'],
                    'writer': user_uid,
                    'role': int(post_data['role']),
                    'quizzes': [],
                    'answers': []
                }

                try:
                    assert len(post_data['quizzes'])
                except:
                    detail = {
                        'detail': 'There must be at least 1 quiz.'
                    }
                    return Response(detail, status=status.HTTP_400_BAD_REQUEST)

                quizzes = []
                for quiz in post_data['quizzes']:
                    result = self.__make_question_data(quiz)
                    if result is not None:
                        quizzes.append(result)

                if not len(quizzes):
                    detail = {
                        'detail': 'There must be at least 1 quiz.'
                    }
                    return Response(detail, status=status.HTTP_400_BAD_REQUEST)

                post_result = self.survey_post_collection.insert_one(new_data)
                self.survey_post_collection.update_one(
                    {'_id': post_result.inserted_id},
                    {
                        '$push': {
                            'quizzes': {
                                '$each': [{'item': i.inserted_id} for i in quizzes]
                            }
                        }
                    }
                )

                return Response('{}', status=status.HTTP_201_CREATED)
            except Exception as e:
                traceback.print_exc()
                detail = {
                    'detail': 'Data is wrong.'
                }
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"{user_uid} Survey Post create denied")
            detail = {
                'detail': 'Not Allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
