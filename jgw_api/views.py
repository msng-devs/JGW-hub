from rest_framework.decorators import api_view
from rest_framework import viewsets, status, views
from rest_framework.response import Response

from .models import Category
from .serializers import CategoryGetSerializer, CategoryEditSerializer

@api_view(['GET'])
def test_header(request):
    print(request.body)
    return Response(data={'test': 'test'}, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryEditSerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategoryGetSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CategoryEditSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TestHeader(views.APIView):
    def get(self, request):
        print('get')
        data = request.query_params['member']
        print(data)
        return Response(data={'test': 'test'}, status=status.HTTP_200_OK)
