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

class BoardPageNumberPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        previous = self.get_previous_link()
        if previous is not None and previous.endswith('board/'):
            previous += '?page=1'
        return Response(OrderedDict([
            ('count', len(data)),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))

class PostPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 150

    def get_paginated_response(self, data):
        previous = self.get_previous_link()
        if previous is not None:
            query = {k: v for k, v in list(map(lambda x: x.split('='), previous.split('?')[1].split('&')))}
            print(query)
            if 'page' not in query:
                query['page'] = '1'
                query = sorted(query.items(), key=lambda x: x[0])
                previous = previous.split('?')[0] + '?' + '&'.join([f'{i[0]}={i[1]}' for i in query])
        return Response(OrderedDict([
            ('count', len(data)),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))
