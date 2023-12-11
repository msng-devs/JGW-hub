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

from pydantic import BaseModel, Field


class ErrorCode(Enum):
    BAD_REQUEST = ("BAD_REQUEST", "HB-HTTP-001", 400)
    NOT_FOUND = ("NOT_FOUND", "HB-HTTP-002", 404)
    UNKNOWN_ERROR = ("UNKNOWN_ERROR", "HB-GENL-001", 500)
    UNAUTHORIZED = ("UNAUTHORIZED", "HB-AUTH-001", 401)
    FORBIDDEN = ("FORBIDDEN", "HB-AUTH-002", 403)


class ExceptionSchema(BaseModel):
    timestamp: str = Field(
        ...,
        description="에러가 발생한 시간입니다.",
    )
    status: int = Field(..., description="에러의 HTTP status code 입니다.")
    error: str = Field(
        ...,
        description="에러의 이름입니다.",
    )
    message: str = Field(
        ...,
        description="에러의 메시지 내용입니다.",
    )
    errorCode: str = Field(
        ...,
        description="에러의 코드입니다.",
    )
    path: str = Field(
        ...,
        description="에러가 발생한 경로입니다.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "default": {
                    "timestamp": "2021-10-17T16:55:00.000000Z",
                    "status": 500,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "서버 로직에 알 수 없는 오류가 발생했습니다.",
                    "errorCode": "HB-GENL-000",
                    "path": "/hub/api/v2/<some/endpoint>",
                }
            }
        }


class InternalException(Exception):
    def __init__(self, message: str, error_code: ErrorCode):
        self.message = message
        self.error_code = error_code
