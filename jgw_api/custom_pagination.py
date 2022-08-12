from rest_framework.pagination import PageNumberPagination

class CategoryPageNumberPagination(PageNumberPagination):
    page_size = 10