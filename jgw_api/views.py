from rest_framework.decorators import api_view
from rest_framework import viewsets, status, views
from rest_framework.response import Response

from .models import Category
from .serializers import CategoryGetSerializer, CategoryEditSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryEditSerializer
    queryset = Category.objects.all()

    # get
    def list(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategoryGetSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryGetSerializer(instance)
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        serializer = CategoryEditSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # put
    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        serializer = CategoryGetSerializer(instance)
        return Response(serializer.data)
