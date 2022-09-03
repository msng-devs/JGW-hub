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
    BoardSerializerWrite,
    PostSerializer,
    ImageSerializer
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
            serializer = BoardSerializerWrite(data=request.data, many=isinstance(request.data, list))
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
            serializer = BoardSerializerWrite(instance, data=request.data, partial=True)
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
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    pagination_class = PostPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

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
            decoded_data = base64.b64decode(data)
            with open(os.path.join(img_path, name), 'wb') as f:
                f.write(decoded_data)
            url = os.path.join(img_path, name).replace('\\', '/').split(settings.MEDIA_URL)[1]
            img_urls.append({'url': 'uploaded/' + url})
        return img_urls

    # post
    def create(self, request, *args, **kwargs):
        try:
            request.data._mutable = True
            images_data = request.data.pop('images')
            post_data = request.data

            # post save
            post_serializer = PostSerializer(data=post_data)
            post_serializer.is_valid(raise_exception=True)
            self.perform_create(post_serializer)
            post_pk = post_serializer.data['post_id_pk']

            img_urls = self.__save_images_storge(images_data, post_pk)
            print(img_urls)
            assert False

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as err:
            print(traceback.format_exc())
            error_responses_data = {
                'detail': 'board with this board name already exists.'
            }
            return Response(error_responses_data, status=status.HTTP_400_BAD_REQUEST)
