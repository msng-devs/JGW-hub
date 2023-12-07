# --------------------------------------------------------------------------
# Board 기능의 API endpoint를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import database
from app.db.models import Board
from app.helper.pagination import PaginatedResponse, paginate
from app.helper.exceptions import InternalException, ErrorCode
from app.schemas import board as schemas
from app.crud import board as crud
from app.utils import constant

log = getLogger(__name__)
board_router = APIRouter(prefix="/board")


@board_router.get(
    "/",
    response_model=PaginatedResponse[schemas.BoardSchema],
    summary="Read items",
    description="Read items",
)
async def read_boards(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        default=constant.BOARD_DEFAULT_PAGE_SIZE,
        ge=constant.BOARD_MIN_PAGE_SIZE,
        le=constant.BOARD_MAX_PAGE_SIZE,
    ),
    db: AsyncSession = Depends(database.get_db),
):
    return await paginate(db, select(Board), page, page_size)


@board_router.get(
    "/{board_id}",
    response_model=schemas.BoardSchema,
    summary="Read item",
    description="Read item",
)
async def read_board(board_id: int, db: AsyncSession = Depends(database.get_db)):
    db_board = await crud.get_board(db, board_id)
    if db_board is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_board
