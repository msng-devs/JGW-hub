# --------------------------------------------------------------------------
# Backend Application과 router을 연결하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from fastapi import APIRouter

from .board import board_router

router = APIRouter(prefix="/hub/api/v2")


@router.get(
    "/ping",
    summary="Server health check",
    description="FastAPI 서버가 정상적으로 동작하는지 확인합니다.",
)
async def ping():
    return {"ping": "pong"}


router.include_router(board_router, tags=["board"])
