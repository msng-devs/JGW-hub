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

# 자람 허브 로거
# logger = logging.getLogger('hub')
logger = logging.getLogger('hub_error')

def get_user_header(
        request
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
        logger.debug(f'get user information success\tuser uid: {user_uid}\tuser role: {user_role_id}')
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
        logger.debug(f'get admin role success\tmin admin role: {config_admin_role}')
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
        return int(config_admin_role[0].config_val)
    else:
        responses_data = {
            'detail': 'Minimum upload role not exist.'
        }
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
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
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
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
        return admin_role_checked
    min_upload_role_checked = get_min_upload_role_pk()
    if isinstance(min_upload_role_checked, Response):
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
        img_path = os.path.join(settings.MEDIA_ROOT, 'test', 'imgs')
        if os.path.exists(img_path):
            shutil.rmtree(img_path)
        os.makedirs(img_path, exist_ok=True)
    img_urls = []
    for img in images_data:
        img = ast.literal_eval(str(img))
        name = img['image_name']
        data = img['image_data']
        folder_pk = img['post_post_id_pk']

        decoded_data = base64.b64decode(data)
        if settings.TESTING:
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
    return img_urls


@api_view(['GET'])
def ping_pong(request):
    msg = {
        'detail': 'pong'
    }
    return Response(msg, status.HTTP_200_OK)

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
        queryset = self.filter_queryset(self.get_queryset())
        request.query_params._mutable = True
        if 'page' not in request.query_params:
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.BOARD_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.BOARD_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.BOARD_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.BOARD_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            logger.debug(f'{user_uid} Board create approved')
            serializer = BoardWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Board data verified')
            self.perform_create(serializer)
            logger.debug(f'{user_uid} Board data created')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            detail = {
                'detail': 'Not Allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            instance = self.get_object()
            try:
                serializer = BoardWriteSerializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                return Response(serializer.data)
            except:
                error_responses_data = {
                    'detail': 'board with this board name already exists.'
                }
                return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            detail = {
                'detail': 'Not Allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
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
        queryset = Post.objects.all()
        queryset = post_get_all_query(request.query_params, queryset)

        request.query_params._mutable = True
        if 'page' not in request.query_params:
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
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
            user_role_id = -1
        else:
            user_uid, user_role_id = checked
        admin_role_checked = get_admin_role_pk()
        if isinstance(admin_role_checked, Response):
            return admin_role_checked

        instance = self.get_object()

        if user_role_id >= admin_role_checked or user_role_id >= instance.board_boadr_id_pk.role_role_pk_read_level.role_pk:
            post_serializer = self.get_serializer(instance)
            response_data = post_serializer.data
            return Response(response_data)
        else:
            detail = {
                'detail': 'Not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        try:
            if user_uid == instance.member_member_pk.member_pk and user_role_id >= instance.board_boadr_id_pk.role_role_pk_read_level.role_pk:
                request_data = request.data
                if isinstance(request_data, QueryDict):
                    request_data._mutable = True
                if 'board_boadr_id_pk' in request_data:
                    board_instance = Board.objects.get(board_id_pk=int(request_data['board_boadr_id_pk']))
                    if board_instance.role_role_pk_write_level.role_pk > user_role_id:
                        responses_data = {
                            'detail': 'This board is not allowed.'
                        }
                        return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

                if 'post_update_time' not in request_data:
                    request_data['post_update_time'] = datetime.datetime.now()
                if 'post_write_time' in request_data:
                    del request_data['post_write_time']

                serializer = PostPatchSerializer(instance, data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                instance = Post.objects.filter(post_id_pk=instance.post_id_pk)

                responses_serializer = self.get_serializer(instance[0])
                return Response(responses_serializer.data)
            else:
                responses_data = {
                    'detail': 'Not Allowed.'
                }
                return Response(responses_data, status=status.HTTP_403_FORBIDDEN)
        except:
            if settings.TESTING:
                traceback.print_exc()
            error_responses_data = {
                'detail': 'Error occurred while update post.'
            }
            logger.debug(traceback.print_exc())
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        request_data = request.data
        if isinstance(request_data, QueryDict):
            request_data._mutable = True
        now = datetime.datetime.now()
        request_data['post_write_time'] = now
        request_data['post_update_time'] = now

        post_serializer = PostWriteSerializer(data=request_data)
        post_serializer.is_valid(raise_exception=True)
        board_instance = post_serializer.validated_data['board_boadr_id_pk']
        if user_role_id >= admin_role_pk or user_role_id >= board_instance.role_role_pk_write_level.role_pk:
            try:
                self.perform_create(post_serializer)

                post_pk = post_serializer.data['post_id_pk']
                serializer = self.get_serializer(Post.objects.get(post_id_pk=post_pk))

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as err:
                traceback.print_exc()
                error_responses_data = {
                    'detail': 'Error occurred while make post.'
                }
                logger.debug(traceback.print_exc())
                return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk, = checked

        instance = self.get_object()

        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
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
            return checked
        user_uid, user_role_id, admin_role_pk, min_upload_role_pk = checked

        if user_role_id >= admin_role_pk or user_role_id >= min_upload_role_pk:
            try:
                data = request.data
                data = save_images_storge(data, user_uid)
                img_serializer = ImageSerializer(data=data, many=True)
                img_serializer.is_valid()
                self.perform_create(img_serializer)
                return Response(img_serializer.data, status=status.HTTP_201_CREATED)
            except:
                traceback.print_exc()
                detail = {
                    'detail': 'Error uploading image.'
                }
                return Response(detail, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            detail = {
                'detail': 'Image upload not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # get
    def list(self, request, *args, **kwargs):
        queryset = Image.objects.all()
        if 'post_id' in request.query_params:
            queryset = queryset.filter(post_post_id_pk=int(request.query_params['post_id']))

        queryset = queryset.order_by('image_id_pk')

        request.query_params._mutable = True
        if 'page' not in request.query_params:
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
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
        return Response(serializer.data)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        instance = self.get_object()
        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
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
        request.query_params._mutable = True
        if 'post_id' not in request.query_params:
            return Response(data={
                'detail': 'post_id request'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = self.get_queryset().filter(
                post_post_id_pk=int(request.query_params['post_id']),
                comment_comment_id_ref=None
            )

        if 'page' not in request.query_params:
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
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
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        request_data = request.data
        comment_serializer = CommentWriteSerializer(data=request_data)
        comment_serializer.is_valid(raise_exception=True)

        post_instance = comment_serializer.validated_data['post_post_id_pk']
        board_instance = post_instance.board_boadr_id_pk
        if user_role_id >= admin_role_pk or user_role_id >= board_instance.role_role_pk_comment_write_level.role_pk:
            try:
                self.perform_create(comment_serializer)

                comment_pk = comment_serializer.data['comment_id']
                serializer = CommentWriteResultSerializer(Comment.objects.get(comment_id=comment_pk))

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as err:
                traceback.print_exc()
                error_responses_data = {
                    'detail': 'Error occurred while make post.'
                }
                logger.debug(traceback.print_exc())
                return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        board_instance = instance.post_post_id_pk.board_boadr_id_pk
        user_instance = instance.member_member_pk
        try:
            if user_role_id >= board_instance.role_role_pk_comment_write_level.role_pk \
                    and user_uid == user_instance.member_pk:
                request_data = request.data
                serializer = CommentWriteSerializer(instance, data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                return Response(serializer.data)
            else:
                responses_data = {
                    'detail': 'Not Allowed.'
                }
                return Response(responses_data, status=status.HTTP_403_FORBIDDEN)
        except:
            if settings.TESTING:
                traceback.print_exc()
            error_responses_data = {
                'detail': 'Error occurred while update post.'
            }
            logger.debug(traceback.print_exc())
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk, = checked

        instance = self.get_object()

        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            request_data = {"comment_delete": 1}
            serializer = CommentWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)
        else:
            detail = {
                'detail': 'Image delete not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
