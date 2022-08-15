from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict

from rest_framework.response import Response

from drf_spectacular.openapi import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes
)


class CategoryPageNumberPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        previous = self.get_previous_link()
        if previous is not None and previous.endswith('category/'):
            previous += '?page=1'
        return Response(OrderedDict([
            ('count', len(data)),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                    'description': '가져온 카테고리의 개수'
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{page_query_param}=4'.format(
                        page_query_param=self.page_query_param),
                    'description': '다음 페이지 uri. 다음 페이지가 없으면 null'
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{page_query_param}=2'.format(
                        page_query_param=self.page_query_param),
                    'description': '이전 페이지 uri. 이전 페이지가 없으면 null'
                },
                'results': schema,
            },
        }
