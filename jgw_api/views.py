from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view
from rest_framework import viewsets, status, views
from rest_framework.response import Response
import json

__user_tocken = 'user_uid'

@api_view(['GET'])
def test_header(request):
    print(request.body)
    # data = json.loads(request.body)
    # print(data['member']['id'])
    return Response(data={'test': 'test'}, status=status.HTTP_200_OK)

class TestHeader(views.APIView):
    def get(self, request):
        print('get')
        data = request.query_params['member']
        print(data)
        return Response(data={'test': 'test'}, status=status.HTTP_200_OK)