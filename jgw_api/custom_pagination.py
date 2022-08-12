from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict

from rest_framework.response import Response


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