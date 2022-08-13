from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Category
from .serializers import CategoryGetSerializer
from .custom_pagination import CategoryPageNumberPagination

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class CategoryViewSet(viewsets.ModelViewSet):
    '''
    카테고리 Api
    '''
    serializer_class = CategoryGetSerializer
    queryset = Category.objects.all().order_by('category_id_pk')
    pagination_class = CategoryPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            serializer = CategoryGetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = CategoryGetSerializer(queryset, many=True)
            response_data = {
                'count': Category.objects.count(),
                'results': serializer.data
            }
            return Response(response_data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryGetSerializer(instance)
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # put
    def update(self, request, *args, **kwargs):
        response_data = {
            "detail": "Use patch."
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        serializer = CategoryGetSerializer(instance)
        return Response(serializer.data)
