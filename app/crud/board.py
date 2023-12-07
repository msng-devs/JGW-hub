# --------------------------------------------------------------------------
# Board 기능의 CRUD 메서드를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ._base import create_object, update_object, delete_object
from app.db.models import Board
from app.schemas import board as schema


async def get_board(db: AsyncSession, board_id: int) -> Optional[schema.BoardSchema]:
    board = await db.get(Board, board_id)
    if board:
        return schema.BoardSchema.model_validate(board.__dict__)
    else:
        return None


async def create_board(
    db: AsyncSession, board: schema.BoardCreateSchema
) -> schema.BoardSchema:
    return await create_object(db, Board, board, response_model=schema.BoardSchema)


async def update_board(
    db: AsyncSession, board_id: int, board: schema.BoardUpdateSchema
) -> Optional[schema.BoardSchema]:
    return await update_object(db, Board, board_id, board, response_model=schema.BoardSchema)


async def delete_board(db: AsyncSession, board_id: int) -> Optional[int]:
    return await delete_object(db, Board, board_id)
