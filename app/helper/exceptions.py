# --------------------------------------------------------------------------
# Backned Application의 Exception class를 정의한 모듈입니다.
#
# InternalException을 raise하여 원하는 에러 코드를 로그에 남길 수 있습니다.
#
# 현재 로직에 구현된 ErrorCodes:
#    BAD_REQUEST: HB-HTTP-000, HTTP 400 에러입니다.
#    NOT_FOUND: HB-HTTP-001, HTTP 404 에러입니다.
#    UNKNOWN_ERROR: HB-GENL-000, 서버 로직 상에 문제가 발생할 때 미들웨어가 raise하는
#                                에러코드입니다.
#    UNKNOWN_ERROR: HB-GENL-001, 서버 로직 상에 문제가 발생할 때 유저레벨에서 raise할 수
#                                있는 에러코드입니다.
#    UNAUTHORIZED: HB-AUTH-001, HTTP 401 에러입니다.
#    FORBIDDEN: HB-AUTH-002, HTTP 403 에러입니다.
#    DATABASE_BAD_REQUEST: HB-DATA-001, 데이터베이스에 중복된 값이 존재할 때 발생하는
#                                       에러코드입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from enum import Enum


class ErrorCode(Enum):
    BAD_REQUEST = ("BAD_REQUEST", "HB-HTTP-001", 400)
    NOT_FOUND = ("NOT_FOUND", "HB-HTTP-002", 404)
    UNKNOWN_ERROR = ("UNKNOWN_ERROR", "HB-GENL-001", 500)
    UNAUTHORIZED = ("UNAUTHORIZED", "HB-AUTH-001", 401)
    FORBIDDEN = ("FORBIDDEN", "HB-AUTH-002", 403)


class InternalException(Exception):
    def __init__(self, message: str, error_code: ErrorCode):
        self.message = message
        self.error_code = error_code
