from rest_framework import status
from rest_framework.response import Response

from ..models import (
    Config,
)

import logging

from typing import Union, Tuple
import rest_framework

from rest_framework.decorators import api_view

logger = logging.getLogger('hub_error')


def get_user_header(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int]]:

    '''
    전달받은 request에서 user header를 가져오는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header가 정상적으로 존재한다면 user의 uid, role이 리턴.
        user header가 없다면 500 response 리턴
    '''
    # 헤더에서 유저 정보 가져오기
    user_uid = request.META.get('HTTP_USER_PK', None)
    user_role_id = request.META.get('HTTP_ROLE_PK', None)

    if user_uid is None or user_role_id is None:
        # 유저 정보가 정상적으로 없다면 500 response 리턴
        logger.error('get user information failed.')
        responses_data = {
            'detail': 'Header Required.'
        }
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # 유저 정보가 있다면 유저 정보 리턴
        user_role_id = int(user_role_id)
        logger.info(f'get user information success\tuser uid: {user_uid}\tuser role: {user_role_id}')
        return user_uid, user_role_id


def get_admin_role_pk() -> Union[rest_framework.response.Response, int]:
    '''
    Config 테이블에서 admin의 role이 몇 이상이지 가져오는 함수

    :return: admin의 최소 role 번호.
        최소 admin role의 정보가 없다면 500 response 리턴.
    '''
    try:
        # 어드민 롤을 정상적으로 가져오면 최소 어드민 롤 리턴
        config_admin_role = Config.objects.get(config_nm='admin_role_pk').config_val
        # logger.debug(f'get admin role success\tmin admin role: {config_admin_role}')
        return int(config_admin_role)
    except:
        # 최소 어드민 롤 정보가 없다면 500 response 리턴
        responses_data = {

            'detail': 'Admin Role not Exist.'

        }
        logger.error('min admin role not found')
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_min_upload_role_pk() -> Union[rest_framework.response.Response, int]:
    '''
    Config 테이블에서 서버에 콘텐츠(사진, 동영상 등)를 업로드 할 수 있는 role이 최소 몇 이상이지 가져오는 함수

    :return: 콘텐츠를 업로드 할 수 있는 최소 role 번호.
        최소 admin role의 정보가 없다면 500 response 리턴.
    '''
    config_admin_role = Config.objects.filter(config_nm='min_upload_role_pk')
    if config_admin_role:
        # 최소 업로드 롤을 정상적으로 가져오면 최소 업로드 롤 리턴
        return int(config_admin_role[0].config_val)
    else:
        # 최소 업로드 롤 정보가 없다면 500 response 리턴
        responses_data = {
            'detail': 'Minimum upload role not exist.'
        }
        logger.error('min upload role not found')
        return Response(responses_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def request_check(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int]]:

    '''
    user header가 정상적으로 리턴됐는지 확인하는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header가 정상적으로 존재한다면 user의 uid, role이 리턴.
        user header가 없다면 500 response 리턴
    '''
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        # get_user_header 에서 response 타입이 리턴됐다면 오류
        return header_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id


def request_check_admin_role(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int, int]]:

    '''
    user header, admin role 모두가 정상적으로 리턴됐는지 확인하는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header, admin role 모두가 정상적으로 존재한다면 user의 uid, role, admin role이 리턴.
        user header, admin role 중 하나라도 없다면 500 response 리턴
    '''
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        # get_user_header 에서 response 타입이 리턴됐다면 오류
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
        # get_admin_role_pk 에서 response 타입이 리턴됐다면 오류
        return admin_role_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id, admin_role_checked


def request_check_admin_upload_role(
        request: rest_framework.request.Request
    ) -> Union[rest_framework.response.Response, Tuple[str, int, int, int]]:


    '''
    user header, admin role, 최소 업로드 가능 role 모두가 정상적으로 리턴됐는지 확인하는 함수

    :param request: 게이트웨이로 부터 전달받은 request
    :return: user header, admin role, 최소 업로드 가능 role 모두가 정상적으로 존재한다면 user의 uid, role, admin role이 리턴.
        user header, admin role, 최소 업로드 가능 role 중 하나라도 없다면 500 response 리턴
    '''
    header_checked = get_user_header(request)
    if isinstance(header_checked, Response):
        # get_user_header 에서 response 타입이 리턴됐다면 오류
        return header_checked
    admin_role_checked = get_admin_role_pk()
    if isinstance(admin_role_checked, Response):
        # get_admin_role_pk 에서 response 타입이 리턴됐다면 오류
        return admin_role_checked
    min_upload_role_checked = get_min_upload_role_pk()
    if isinstance(min_upload_role_checked, Response):
        # get_min_upload_role_pk 에서 response 타입이 리턴됐다면 오류
        return min_upload_role_checked
    user_uid, user_role_id = header_checked
    return user_uid, user_role_id, admin_role_checked, min_upload_role_checked


def get_logger():
    return logger


@api_view(['GET'])
def ping_pong(request):
    # 서버 health check 용도
    return Response({

            'detail': 'pong'
        }, status.HTTP_200_OK)

