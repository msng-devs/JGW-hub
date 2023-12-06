from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict


from rest_framework.response import Response

import backups.constant as constant

class BoardPageNumberPagination(PageNumberPagination):
    page_size = constant.BOARD_DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = constant.BOARD_MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        previous = self.get_previous_link()
        if previous is not None and previous.endswith('board/'):
            previous += '?page=1'
        return Response(OrderedDict([
            ('count', len(data)),
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))

class PostPageNumberPagination(PageNumberPagination):
    page_size = constant.POST_DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = constant.POST_MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        previous = self.get_previous_link()
        if previous and '?' in previous:
            query_string = previous.split('?', 1)[1]
            query = {k: v for k, v in (param.split('=') for param in query_string.split('&'))}

            if 'page' not in query:
                query['page'] = '1'
                query = sorted(query.items())
                previous = previous.split('?', 1)[0] + '?' + '&'.join(f'{key}={value}' for key, value in query)

        return Response(OrderedDict([
            ('count', len(data)),
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))

class ImagePageNumberPagination(PageNumberPagination):
    page_size = constant.IMAGE_DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = constant.IMAGE_MAX_PAGE_SIZE

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
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))

class CommentPageNumberPagination(PageNumberPagination):
    page_size = constant.COMMENT_DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = constant.COMMENT_MAX_PAGE_SIZE

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
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', previous),
            ('results', data)
        ]))
