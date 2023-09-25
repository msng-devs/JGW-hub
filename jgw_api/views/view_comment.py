from rest_framework import viewsets, status
from rest_framework.response import Response

from ..models import (
    Comment,
    Member,
)
from ..serializers import (
    CommentGetSerializer,
    CommentWriteSerializer,
    CommentWriteResultSerializer
)
from ..custom_pagination import (
    CommentPageNumberPagination
)

import jgw_api.constant as constant

from .view_check import (
    get_logger,
    request_check_admin_role,
)
import datetime
logger = get_logger()

class CommentViewSet(viewsets.ModelViewSet):
    '''
    댓글 api를 담당하는 클래스
    '''
    serializer_class = CommentGetSerializer
    queryset = Comment.objects.all().order_by('-comment_id')
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CommentPageNumberPagination

    # get
    def list(self, request, *args, **kwargs):
        logger.debug(f"Comment get request")
        request.query_params._mutable = True
        if 'post_id' not in request.query_params:
            # query parameter에 post_id가 없으면 400 return
            
            return Response(data = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 400,

                "error": "Bad Request",

                "code": "JGW_hub-comment-001",

                "message": "post_id request",

                "path": "/hub/api/v1/comment/"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # query parameter에 post_id가 있으면 해당 게시글에 포함된 댓글만 가져옴
            queryset = self.get_queryset().filter(
                post_post_id_pk=int(request.query_params['post_id']),
                comment_comment_id_ref=None
            )

        if 'page' not in request.query_params:
            # page를 지정하지 않으면 1로 지정
            request.query_params['page'] = 1
        if 'page_size' in request.query_params:
            # page size를 최소~최대 범위 안에서 지정
            request.query_params['page_size'] = int(request.query_params['page_size'])
            if request.query_params['page_size'] < constant.COMMENT_MIN_PAGE_SIZE:
                request.query_params['page_size'] = constant.COMMENT_MIN_PAGE_SIZE
            elif request.query_params['page_size'] > constant.COMMENT_MAX_PAGE_SIZE:
                request.query_params['page_size'] = constant.COMMENT_MAX_PAGE_SIZE
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # post
    def create(self, request, *args, **kwargs):
        checked = request_check_admin_role(request)

        if isinstance(checked, Response):
                # user role, 최소 admin role 중 하나라도 없으면 500 return
            return checked

        user_uid, user_role_id, admin_role_pk = checked
        request_data = request.data
        comment_serializer = CommentWriteSerializer(data=request_data)

        comment_serializer.is_valid(raise_exception=True)
        logger.debug(f'{user_uid} Comment data verified')
        member_member_pk = user_uid
        logger.debug(f'{member_member_pk} found')
        comment = Comment(
            comment_depth=comment_serializer.validated_data['comment_depth'],
            comment_content=comment_serializer.validated_data['comment_content'],
            comment_delete=comment_serializer.validated_data['comment_delete'],
            post_post_id_pk=comment_serializer.validated_data['post_post_id_pk'],
            member_member_pk=member_member_pk,
            comment_comment_id_ref=comment_serializer.validated_data['comment_comment_id_ref']

        )
        logger.debug(f'{comment}')
        post_instance = comment.validated_data['post_post_id_pk']
        board_instance = post_instance.board_boadr_id_pk
        if user_role_id >= admin_role_pk or user_role_id >= board_instance.role_role_pk_comment_write_level.role_pk:
            logger.debug(f'{user_uid} Comment post approved\nrequest_body= {comment}')
            self.perform_create(comment)
            comment_pk = comment_serializer.data['comment_id']
            responses_instance = Comment.objects.get(comment_id=comment_pk)
            serializer = CommentWriteResultSerializer(responses_instance)
            responses_data = serializer.data
            update_log = f'{user_uid} Comment data created' \
                         f'\tkey: {responses_data["comment_id"]} created log'
            for k in responses_data.keys():
                instance_data = getattr(responses_instance, k)
                if k in ('comment_content',):
                    instance_data = instance_data[:50]
                update_log += f'\n\t{k}: {instance_data}'
            logger.info(update_log)

            return Response(responses_data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"{user_uid} Comment create denied")
            responses_data = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-comment-002",

                "message": "Comment create denied",

                "path": "/hub/api/v1/comment/"
            }
            return Response(responses_data, status=status.HTTP_403_FORBIDDEN)

    # patch
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # user role, 최소 admin role이 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_pk = checked

        board_instance = instance.post_post_id_pk.board_boadr_id_pk
        user_instance = instance.member_member_pk
        if user_role_id >= board_instance.role_role_pk_comment_write_level.role_pk \
                and user_uid == user_instance.member_pk:
            # 요청한 유저의 role이 해당 게시판 댓글 쓰기 레벨 이상이고, 댓글을 작성했던 본인이면 승인
            logger.debug(f'{user_uid} Comment patch approved')
            request_data = request.data
            target_keys = list(request_data.dict().keys())
            before_change = dict()
            for k in target_keys:
                before_change[k] = getattr(instance, k)

            serializer = CommentWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'{user_uid} Comment data verified')

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            responses_data = serializer.data
            update_log = f'{user_uid} Comment data patched' \
                         f'\tkey: {responses_data["comment_id"]} change log'
            for k in target_keys:
                instance_data = getattr(instance, k)
                before_change = before_change[k]
                if k in ('post_content', 'post_title'):
                    instance_data = instance_data[:50]
                    before_change = before_change[:50]
                update_log += f'\n\t{k}: {before_change} -> {instance_data}'
            logger.info(update_log)
            return Response(responses_data)
        else:
            logger.info(f"{user_uid} Comment patch denied")
            responses_data = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-comment-003",

                "message": "Comment patch denied",

                "path": "/hub/api/v1/comment/"
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
            # 요청한 유저가 admin or 댓글을 업로드한 본인이면 승인
            logger.debug(f'{user_uid} Comment delete approved')
            request_data = {"comment_delete": 1}
            serializer = CommentWriteSerializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            key, name = instance.comment_id, instance.comment_content
            logger.debug(f'{user_uid} Comment data deleted\tkey: {key}\ttitle: {name[:25]}')
            return Response(serializer.data)
        else:
            logger.info(f"{user_uid} Comment delete denied")
            detail = {
                "timestamp": datetime.datetime.now().isoformat(),

                "status": 403,

                "error": "Forbidden",

                "code": "JGW_hub-comment-004",

                "message": "Comment delete denied",

                "path": "/hub/api/v1/comment/"
            }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
