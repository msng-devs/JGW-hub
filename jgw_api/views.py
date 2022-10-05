import datetime
import random

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.conf import settings
from django.utils.crypto import get_random_string

from .models import (
    Category,
    Board,
    Post,
    Image,
    Config
)
from .serializers import (
    CategorySerializer,
    BoardSerializer,
    BoardWriteSerializer,
    PostSerializer,
    ImageSerializer,
    PostGetSerializer,
    PostPatchSerializer
)
from .custom_pagination import (
    CategoryPageNumberPagination,
    BoardPageNumberPagination,
    PostPageNumberPagination
)

import base64
import os
import shutil
import traceback
import ast
from urllib import parse

RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def get_user_header(request):
    user_uid = request.META.get('user_pk', None)
    user_role_id = request.META.get('user_role_pk')
    if user_uid is None or user_role_id is None:
        responses_data = {
            'detail': 'Header Required.'
        }
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return user_uid, user_role_id

def get_admin_role_pk():
    config_admin_role = Config.objects.filter(config_nm='admin_role_pk')
    if config_admin_role:
        return int(config_admin_role[0].config_val)
    else:
        responses_data = {
            'detail': 'Admin Role not Exist.'
        }
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_min_upload_role_pk():
    config_admin_role = Config.objects.filter(config_nm='min_upload_role_pk')
    if config_admin_role:
        return int(config_admin_role[0].config_val)
    else:
        responses_data = {
            'detail': 'Minimum upload role not exist.'
        }
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def request_check(request):
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        return header_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id

def request_check_admin_role(request):
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
        return admin_role_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id, admin_role_checked

def request_check_admin_upload_role(request):
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

def save_images_storge(images_data, member_pk):
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
        save_name = get_random_string(length=random.randint(10, 15), allowed_chars=RANDOM_STRING_CHARS)
        while os.path.isfile(os.path.join(img_path, save_name)):
            save_name = get_random_string(length=random.randint(10, 15), allowed_chars=RANDOM_STRING_CHARS)
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

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('category_id_pk')
    pagination_class = CategoryPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'count': Category.objects.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
            return Response(response_data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            error_responses_data = {
                'detail': 'category with this category name already exists.'
            }
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)

    # put
    def update(self, request, *args, **kwargs):
        response_data = {
            "detail": "Use patch."
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        except:
            error_responses_data = {
                'detail': 'category with this category name already exists.'
            }
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)

class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all().order_by('board_id_pk')
    pagination_class = BoardPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'count': Board.objects.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
            return Response(response_data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        try:
            serializer = BoardWriteSerializer(data=request.data, many=isinstance(request.data, list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as err:
            error_responses_data = {
                'detail': 'board with this board name already exists.'
            }
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)

    # patch
    def partial_update(self, request, *args, **kwargs):
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

    # put
    def update(self, request, *args, **kwargs):
        response_data = {
            "detail": "Use patch."
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

def post_get_all_query(query_params, queryset):
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

    if 'category' in query_params:
        queryset = queryset.filter(category_category_id_pk=query_params['category'])

    if 'board' in query_params:
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
    serializer_class = PostGetSerializer
    queryset = Post.objects.all()
    pagination_class = PostPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        queryset = Post.objects.all()
        queryset = post_get_all_query(request.query_params, queryset)

        if 'page' in request.query_params and queryset.count():
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
            return Response(response_data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        if user_role_id >= admin_role_pk or user_role_id >= instance.board_boadr_id_pk.role_role_pk_read_level.role_pk:
            post_serializer = self.get_serializer(instance)
            response_data = post_serializer.data
            return Response(response_data)
        else:
            detail = {
                'detail': 'read post not allowed.'
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
            serializer = PostPatchSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if user_uid == instance.member_member_pk.member_pk:
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
                'detail': 'Test'
            }
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)

    # post
    def create(self, request, *args, **kwargs):
        post_serializer = PostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk = checked
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
                    'detail': 'board with this board name already exists.'
                }
                return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            responses_data = {
                'detail': 'Not Allowed.'
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # put
    def update(self, request, *args, **kwargs):
        response_data = {
            "detail": "Use patch."
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

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
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    http_method_names = ['get', 'post', 'head', 'delete']

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
                detail = {
                    'detail': 'Error uploading image.'
                }
                return Response(detail, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            detail = {
                'detail': 'Image upload not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        queryset = Image.objects.all()
        if 'post_id' in request.query_params:
            queryset = queryset.filter(post_post_id_pk=int(request.query_params['post_id']))
        else:
            error_responses = {
                'detail': "post_id required."
            }
            return Response(error_responses, status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.order_by('image_id_pk')

        if 'page' in request.query_params and queryset.count():
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
            return Response(response_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_upload_role(request)
        if isinstance(checked, Response):
            return checked
        user_uid, user_role_id, admin_role_pk, min_upload_role_pk = checked

        instance = self.get_object()

        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            detail = {
                'detail': 'Image delete not allowed.'
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
