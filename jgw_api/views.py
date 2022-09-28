import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.conf import settings

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

def get_user_header(request):
    user_uid = request.META.get('user_pk', None)
    user_role_id = request.META.get('user_role_pk')
    if user_uid is None or user_role_id is None:
        return None
    else:
        return user_uid, user_role_id

def get_admin_role_pk():
    config_admin_role = Config.objects.filter(config_nm='admin_role_pk')
    if config_admin_role:
        return int(config_admin_role[0].config_val)
    else:
        return None

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
        post_serializer = self.get_serializer(instance)

        post_pk = post_serializer.data['post_id_pk']

        response_data = post_serializer.data

        img_instance = Image.objects.all().filter(post_post_id_pk=post_pk).order_by('image_id_pk')
        if img_instance.count():
            image_serializer = ImageSerializer(img_instance)
            response_data['images'] = image_serializer.data
        else:
            response_data['images'] = []

        return Response(response_data)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user_header = get_user_header(request)
        if user_header is None:
            responses_data = {
                'detail': 'User Header not Exist.'
            }
            return Response(responses_data, status=status.HTTP_400_BAD_REQUEST)
        admin_role_pk = get_admin_role_pk()
        if admin_role_pk is None:
            responses_data = {
                'detail': 'Admin Role not Exist.'
            }
            return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            serializer = PostPatchSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            user_uid, user_role_id = user_header
            if admin_role_pk <= user_role_id or user_uid == instance.member_member_pk.member_pk:
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

    def __save_images_storge(self, images_data, folder_pk):
        if settings.TESTING:
            img_path = os.path.join(settings.MEDIA_ROOT, 'test', 'imgs', str(folder_pk))
            if os.path.exists(img_path):
                shutil.rmtree(img_path)
            os.makedirs(img_path, exist_ok=True)
        else:
            img_path = os.path.join(settings.MEDIA_ROOT, 'imgs', str(folder_pk))
        img_urls = []
        for img in images_data:
            img = ast.literal_eval(img)
            name = img['name']
            data = img['data']

            # name = parse.quote(name)
            decoded_data = base64.b64decode(data)
            with open(os.path.join(img_path, name), 'wb') as f:
                f.write(decoded_data)
            url = os.path.join(img_path, name).replace('\\', '/').split(settings.MEDIA_URL)[1]
            img_urls.append({
                'image_name': name,
                'image_url': 'uploaded/' + url,
                'post_post_id_pk': folder_pk
            })
        return img_urls

    # post
    def create(self, request, *args, **kwargs):
        try:
            request.data._mutable = True
            if 'images' in request.data:
                images_data = request.data.pop('images')
            else:
                images_data = []
            post_data = request.data

            # post save
            post_serializer = PostSerializer(data=post_data)
            post_serializer.is_valid(raise_exception=True)
            self.perform_create(post_serializer)
            post_pk = post_serializer.data['post_id_pk']

            # img save
            img_urls = self.__save_images_storge(images_data, post_pk)
            img_serializer = ImageSerializer(data=img_urls, many=True)
            img_serializer.is_valid(raise_exception=True)
            self.perform_create(img_serializer)

            if img_urls:
                thumbnail_pk = img_serializer.data[0]['image_id_pk']
                thumbnail_data = {'image_image_id_pk': thumbnail_pk}
                thumbnail_serializer = PostSerializer(Post.objects.get(post_id_pk=post_pk), data=thumbnail_data, partial=True)
                thumbnail_serializer.is_valid(raise_exception=True)
                self.perform_update(thumbnail_serializer)

            get_serializer = self.get_serializer(Post.objects.get(post_id_pk=post_pk))
            response_data = get_serializer.data
            response_data['images'] = img_serializer.data

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as err:
            print(traceback.format_exc())
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

class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    http_method_names = ['get', 'post', 'head', 'delete']
