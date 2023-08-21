from rest_framework import viewsets, status
from rest_framework.response import Response
import datetime
from ..models import (
    Board,
)
from ..serializers import (
    BoardGetSerializer,
    BoardWriteSerializer,
)
from ..custom_pagination import (
    BoardPageNumberPagination,
)

import jgw_api.constant as constant

from .view_check import (
    get_logger,
    request_check_admin_role
)

logger = get_logger()

class BoardViewSet(viewsets.ModelViewSet):
    '''
    게시판 api를 담당하는 클래스
    '''
    serializer_class = BoardGetSerializer
    queryset = Board.objects.all().order_by('board_id_pk')
    pagination_class = BoardPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Board get request")
        queryset = self.filter_queryset(self.get_queryset())
        request.query_params._mutable = True
        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.BOARD_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.BOARD_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.BOARD_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.BOARD_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        responses = self.get_paginated_response(serializer.data)
        return responses

    # get by id
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        key, name = instance.board_id_pk, instance.board_name
        logger.debug(f'Board data get retrieve\tkey: {key}\tname: {name}')
        return Response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        # 요청한 유저의 정보를 헤더로 확인
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            # 요청한 유저가 admin 이라면 승인
            logger.debug(f'{user_uid} Board create approved')
            serializer = BoardWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Board data verified')
            self.perform_create(serializer)
            responses_data = serializer.data

            update_log = f'{user_uid} Board data created' \
                         f'\tkey: {responses_data["board_id_pk"]} created log'
            for k in responses_data.keys():
                update_log += f'\n\t{k}: {responses_data[k]}'
            logger.info(update_log)

            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Board create denied")

            detail = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-board-001",

                "message": "Board create denied",

                "path": "/hub/api/v1/board/"
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
    # patch
    def partial_update(self, request, *args, **kwargs):
        # 요청한 유저의 정보를 헤더로 확인
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            # 요청한 유저가 admin 이라면 승인
            logger.debug(f'{user_uid} Board patch approved')
            instance = self.get_object()
            request_data = request.data
            target_keys = list(request_data.dict().keys())
            before_change = dict()
            for k in target_keys:
                before_change[k] = getattr(instance, k)

            serializer = BoardWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Board data verified')
            self.perform_update(serializer)
            responses_data = serializer.data

            update_log = f'{user_uid} Board data patched' \
                         f'\tkey: {responses_data["board_id_pk"]} change log'
            for k in target_keys:
                update_log += f'\n\t{k}: {before_change[k]} -> {responses_data[k]}'
            logger.info(update_log)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(responses_data)
        else:
            logger.info(f"{user_uid} Board patch denied")
            detail = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-board-002",

                "message": "Board patch denied",

                "path": "/hub/api/v1/board/"
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
    # delete
    def destroy(self, request, *args, **kwargs):
        # 요청한 유저의 정보를 헤더로 확인
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            # 요청한 유저가 admin 이라면 승인
            logger.debug(f'{user_uid} Board delete approved')
            instance = self.get_object()
            key, name = instance.board_id_pk, instance.board_name
            self.perform_destroy(instance)
            logger.debug(f'{user_uid} Board data deleted\tkey: {key}\tname: {name}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.info(f"{user_uid} Board delete denied")
            detail = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-board-003",

                "message": "Board delete denied",

                "path": "/hub/api/v1/board/"
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
