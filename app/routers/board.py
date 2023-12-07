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
    summary="모든 게시판 목록 가져오기",
    description="게시판 목록을 가져옵니다.",
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
    summary="특정 게시판 가져오기",
    description="지정한 게시판의 데이터를 가져옵니다.",
)
async def read_board(board_id: int, db: AsyncSession = Depends(database.get_db)):
    db_board = await crud.get_board(db, board_id)
    if db_board is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_board


@board_router.post(
    "/",
    response_model=schemas.BoardSchema,
    status_code=201,
    summary="게시판 생성",
    description="새로운 게시판을 생성합니다.",
)
async def create_board(
    board: schemas.BoardCreateSchema, db: AsyncSession = Depends(database.get_db)
):
    db_board = await crud.create_board(db, board)
    return db_board


@board_router.put(
    "/{board_id}",
    response_model=schemas.BoardSchema,
    summary="게시판 수정 (전체 업데이트)",
    description="지정한 게시판의 데이터를 전체적으로 수정합니다. (부분 업데이트도 지원합니다)",
)
@board_router.patch(
    "/{board_id}",
    response_model=schemas.BoardSchema,
    summary="게시판 수정 (부분 업데이트)",
    description="지정한 게시판의 데이터를 부분적으로 수정합니다.",
)
async def update_board(
    board_id: int,
    board: schemas.BoardUpdateSchema,
    db: AsyncSession = Depends(database.get_db),
):
    db_board = await crud.update_board(db, board_id, board)
    if db_board is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_board


@board_router.delete(
    "/{board_id}",
    status_code=204,
    summary="게시판 삭제",
    description="지정한 게시판을 삭제합니다.",
)
async def delete_board(board_id: int, db: AsyncSession = Depends(database.get_db)):
    deleted_id = await crud.delete_board(db, board_id)
    if deleted_id is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
