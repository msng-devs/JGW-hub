import datetime

import django

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import QueryDict

from ..models import (
    Board,
    Post,
)
from ..serializers import (
    PostWriteSerializer,
    PostGetSerializer,
    PostPatchSerializer,
    PostIndexSerializer
)
from ..custom_pagination import (
    PostPageNumberPagination,
)

import jgw_api.constant as constant

from .view_check import (
    get_logger,
    request_check_admin_role,
    get_admin_role_pk,
    request_check,
)
import datetime

logger = get_logger()

import markdown


def post_get_all_query(
        query_params: dict,
        queryset: django.db.models.query.QuerySet) -> django.db.models.query.QuerySet:
    '''
    post api 쿼리 파라미터를 추출하는 함수

    :param query_params: 필터에 적용시킬 쿼리 파라미터
    :param queryset: 쿼리 파라미터를 적용시킬 post instance
    :return: 쿼리 파라미터에 맞게 추출된 django orm instance 리턴
    '''
    start_date = datetime.datetime.min
    end_date = datetime.datetime.max

    if 'start_date' in query_params:
        start_date = datetime.datetime.strptime(query_params['start_date'], constant.TIME_QUERY)
    if 'end_date' in query_params:
        end_date = datetime.datetime.strptime(query_params['end_date'], constant.TIME_QUERY)
    queryset = queryset.filter(post_write_time__range=(start_date, end_date))

    if 'writer_uid' in query_params:
        queryset = queryset.filter(member_member_pk=query_params['writer_uid'])

    if 'writer_name' in query_params:
        queryset = queryset.filter(member_member_pk__member_nm__contains=query_params['writer_name'])

    if 'board' in query_params:
        # if is_admin:
        #     queryset = queryset.filter(board_boadr_id_pk=query_params['board'])
        # else:
        #     queryset = queryset.filter(
        #         board_boadr_id_pk=query_params['board'],
        #         board_boadr_id_pk__role_role_pk_read_level__role_pk__gte=user_role_id
        #     )
        queryset = queryset.filter(board_boadr_id_pk=query_params['board'])

    if 'title' in query_params:
        queryset = queryset.filter(post_title__icontains=query_params['title'])

    if 'content' in query_params:
        queryset = queryset.filter(post_content__icontains=query_params['content'])


    if 'order' in query_params:
        if 'desc' in query_params and int(query_params['desc']):
            queryset = queryset.order_by('-' + query_params['order'])
        else:
            queryset = queryset.order_by(query_params['order'])
    else:
        queryset = queryset.order_by('post_write_time')
    return queryset


class PostViewSet(viewsets.ModelViewSet):
    '''
    게시글 api를 담당하는 클래스
    '''
    serializer_class = PostGetSerializer
    queryset = Post.objects.all()
    pagination_class = PostPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Post get request")
        queryset = Post.objects.all()
        queryset = post_get_all_query(request.query_params, queryset)
        logger.debug(f"[2]\nqueryset : {queryset}")
        request.query_params._mutable = True
        logger.debug(f"[3]")
        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1

        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.POST_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.POST_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.POST_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.POST_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        logger.debug("3")
        serializer = self.get_serializer(page, many=True)
        logger.debug("4")
        data = serializer.data
        logger.debug(f"[5]\n data : {data}")
        for i in data:
            if len(i['post_content']) > 500:
                i['post_content'] = i['post_content'][:500]
        logger.debug(f"[6] data : {data}")
        return self.get_paginated_response(data)

    # get by id
    def retrieve(self, request, *args, **kwargs):
        checked = request_check(request)
        if isinstance(checked, Response):
            # user role이 없다면 최하위 권한 적용
            user_role_id = -1
            user_uid = None
        else:
            user_uid, user_role_id = checked
        admin_role_checked = get_admin_role_pk()
        if isinstance(admin_role_checked, Response):
            # admin role이 없다면 500 return
            return admin_role_checked

        instance = self.get_object()

        if user_role_id >= admin_role_checked or user_role_id >= instance.board_boadr_id_pk.role_role_pk_read_level.role_pk:
            # 요청한 유저가 admin or 해당 게시판 게시글 읽기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Post get retrieve approved')
            post_serializer = self.get_serializer(instance)
            response_data = post_serializer.data

            key, name = instance.post_id_pk, instance.post_title
            logger.debug(f'{user_uid} Post data get retrieve\tkey: {key}\ttitle: {name}')
            return Response(response_data)
        else:
            logger.info(f"{user_uid} Post get retrieve denied")
            detail = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-post-001",

                "message": "Post retrieve denied",

                "path": "/hub/api/v1/post/"
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        if user_uid == instance.member_member_pk.member_pk and user_role_id >= instance.board_boadr_id_pk.role_role_pk_write_level.role_pk:
            # 요청한 유저가 글을 작성했던 본인이고, 해당 게시판 게시글 쓰기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Post patch approved')
            request_data = request.data
            target_keys = list(request_data.dict().keys())
            before_change = dict()
            for k in target_keys:
                before_change[k] = getattr(instance, k)

            if isinstance(request_data, QueryDict):
                request_data._mutable = True
            if 'board_boadr_id_pk' in request_data:
                # 변경하려는 데이터가 해당 게시글이 소속된 게시판이라면
                board_instance = Board.objects.get(board_id_pk=int(request_data['board_boadr_id_pk']))
                if board_instance.role_role_pk_write_level.role_pk > user_role_id:
                    # 변경하려는 게시판의 쓰기 레벨보다 요청한 유저의 권한이 낮다면 거부
                    logger.info(f"{user_uid} Post patch denied - request board not allowed")
                    responses_data = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 403,

                        "error": "Forbidden",

                        "code": "JGW_hub-post-002",

                        "message": "request board not allowed",

                        "path": "/hub/api/v1/post/"
                    }
                    return Response(responses_data, status=status.HTTP_403_FORBIDDEN)
            # if 'post_update_time' not in request_data:
            #     request_data['post_update_time'] = datetime.datetime.now()
            # if 'post_write_time' in request_data:
            #     del request_data['post_write_time']

            serializer = PostPatchSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Post data verified')
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            instance = Post.objects.get(post_id_pk=instance.post_id_pk)

            responses_serializer = self.get_serializer(instance)
            responses_data = responses_serializer.data
            update_log = f'{user_uid} Post data patched' \
                         f'\tkey: {responses_data["post_id_pk"]} change log'
            for k in target_keys:
                instance_data = getattr(instance, k)
                before_change_data = before_change[k]
                if k in ('post_content', 'post_title'):
                    instance_data = instance_data[:50]
                    before_change_data = before_change_data[:50]
                update_log += f'\n\t{k}: {before_change_data} -> {instance_data}'
            logger.info(update_log)

            return Response(responses_data)
        else:
            logger.info(f"{user_uid} Post patch denied")
            responses_data = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-post-003",

                "message": "Post patch denied",

                "path": "/hub/api/v1/post/"
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role 중 하나라도 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked
        index_content = request.data["post_content"]
        request_data = {
            "post_title": request.data["post_title"],
            "post_content": markdown.markdown(f'#{request.data["post_content"]}'),
            "post_write_time": request.data["post_write_time"],
            "post_update_time": request.data["post_update_time"],
            "thumbnail_id_pk": request.data["thumbnail_id_pk"],
            "board_boadr_id_pk": request.data["board_boadr_id_pk"],
            "member_member_pk": user_uid

        }

        if isinstance(request_data, QueryDict):
            request_data._mutable = True
        # now = datetime.datetime.now()
        # request_data['post_write_time'] = now
        # request_data['post_update_time'] = now

        post_serializer = PostWriteSerializer(data=request_data)

        post_serializer.is_valid(raise_exception=True)
        logger.debug(f'{user_uid} Post data verified')
        board_instance = post_serializer.validated_data['board_boadr_id_pk']
        if user_role_id >= admin_role_pk or user_role_id >= board_instance.role_role_pk_write_level.role_pk:
            # 요청한 유저가 admin or 요청한 게시판 게시글 쓰기 레벨 이상이면 승인
            logger.debug(f'{user_uid} Post post approved')
            self.perform_create(post_serializer)

            post_pk = post_serializer.data['post_id_pk']
            responses_instance = Post.objects.get(post_id_pk=post_pk)
            serializer = self.get_serializer(responses_instance)

            responses_data = serializer.data
            update_log = f'{user_uid} Post data created' \
                         f'\tkey: {responses_data["post_id_pk"]} created log'
            for k in responses_data.keys():
                instance_data = getattr(responses_instance, k)
                if k in ('post_content', 'post_title'):
                    instance_data = instance_data[:50]
                update_log += f'\n\t{k}: {instance_data}'
            logger.info(update_log)
            index_data = {
                "postindex_id" : post_pk,
                "postindex_content" : index_content
            }
            postindex_serailizer = PostIndexSerializer(data=index_data)
            postindex_serailizer.is_valid(raise_exception=True)
            logger.debug("postindex data verified")
            self.perform_create(postindex_serailizer)
            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Post create denied")
            responses_data = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-post-004",

                "message": "Post create not allowed",

                "path": "/hub/api/v1/post/"
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # delete
    def destroy(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk, = checked

        instance = self.get_object()

        if user_role_id >= admin_role_pk or user_uid == instance.member_member_pk.member_pk:
            # 요청한 유저가 admin or 글을 작성한 본인이면 승인

            logger.debug(f'{user_uid} Post delete approved')
            key, name = instance.post_id_pk, instance.post_title
            self.perform_destroy(instance)

            logger.debug(f'{user_uid} Post data deleted\tkey: {key}\ttitle: {name}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.info(f"{user_uid} Post delete denied")
            detail = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-post-005",

                "message": "Post delete not allowed",

                "path": "/hub/api/v1/post/"
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
