# --------------------------------------------------------------------------
# FastAPI application의 custom middleware들을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import json
import logging

from datetime import datetime
from contextvars import ContextVar

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from fastapi import FastAPI

from app.helper.exceptions import InternalException

request_object: ContextVar[Request] = ContextVar("request")


# --------------------------------------------------------------------------
# PaginationMiddleware
# --------------------------------------------------------------------------
class PaginationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_object.set(request)
        response = await call_next(request)
        return response


# --------------------------------------------------------------------------
# ExceptionMiddleware
# --------------------------------------------------------------------------
class ExceptionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, logger: str):
        super().__init__(app)
        self.logger = logging.getLogger(logger)

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except InternalException as e:
            response = {
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "status": e.error_code.value[2],
                "error": e.error_code.value[0],
                "message": e.message,
                "errorCode": e.error_code.value[1],
                "path": request.url.path,
            }
            self.logger.error(json.dumps(response))
            return Response(
                status_code=e.error_code.value[2],
                content=json.dumps(response),
                media_type="application/json",
            )
        except Exception as e:
            print(e)
            response = {
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "status": "INTERNAL_SERVER_ERROR",
                "error": "INTERNAL_SERVER_ERROR",
                "message": "알 수 없는 오류가 발생했습니다.",
                "errorCode": "HB-200",
                "path": request.url.path,
            }
            self.logger.error(json.dumps(response))
            return Response(
                status_code=500,
                content=json.dumps(response),
                media_type="application/json",
            )
