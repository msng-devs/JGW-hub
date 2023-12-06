# --------------------------------------------------------------------------
# Board 기능의 CRUD 메서드를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ._base import get_object
from app.db.models import Board
from app.schemas import board as schema


async def get_board(db: AsyncSession, board_id: int) -> Optional[schema.BoardSchema]:
    return await get_object(db, Board, board_id, response_model=schema.BoardSchema)
