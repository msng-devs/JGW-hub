import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.conf import settings

from .models import (
    Category,
    Board,
    Post
)
from .serializers import (
    CategorySerializer,
    BoardSerializer,
    BoardWriteSerializer,
    PostSerializer,
    ImageSerializer,
    PostGetSerializer
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

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostGetSerializer
    queryset = Post.objects.all()
    pagination_class = PostPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        queryset = Post.objects.all()

        print(request.query_params)

        start_date = datetime.datetime.min
        end_date = datetime.datetime.max
        time_query = '%Y-%m-%dT%H:%M:%S'
        if 'start_date' in request.query_params:
            start_date = datetime.datetime.strptime(request.query_params['start_date'], time_query)
        if 'end_date' in request.query_params:
            end_date = datetime.datetime.strptime(request.query_params['end_date'], time_query)
        queryset = queryset.filter(post_write_time__range=(start_date, end_date))

        if 'writer_uid' in request.query_params:
            queryset = queryset.filter(member_member_pk=request.query_params['writer_uid'])

        if 'writer_name' in request.query_params:
            queryset = queryset.filter(member_member_pk__member_nm__contains=request.query_params['writer_name'])

        if 'category' in request.query_params:
            queryset = queryset.filter(category_category_id_pk=request.query_params['category'])

        if 'board' in request.query_params:
            queryset = queryset.filter(board_boadr_id_pk=request.query_params['board'])

        if 'title' in request.query_params:
            queryset = queryset.filter(post_title__icontains=request.query_params['title'])

        if 'order' in request.query_params:
            if 'desc' in request.query_params and request.query_params['desc']:
                queryset = queryset.order_by('-' + request.query_params['order'])
            else:
                queryset = queryset.order_by(request.query_params['order'])

        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'count': Post.objects.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
            return Response(response_data)

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
