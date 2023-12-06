# --------------------------------------------------------------------------
# Backend Application과 router을 연결하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from fastapi import APIRouter

router = APIRouter(prefix="/hub/api/v2")


@router.get("/ping")
async def ping():
    return {"ping": "pong"}
