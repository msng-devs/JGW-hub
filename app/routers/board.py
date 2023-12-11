# --------------------------------------------------------------------------
# Board 기능의 API endpoint를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from logging import getLogger
from typing import Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import database
from app.db.models import Board
from app.helper.pagination import PaginatedResponse, paginate
from app.helper.exceptions import InternalException, ErrorCode
from app.schemas import board as schemas
from app.crud import board as crud
from app.utils import constant, documents
from app.utils.documents import response_403, response_500, board_response_404
from ._check import check_user, check_user_is_admin, auth

log = getLogger(__name__)
board_router = APIRouter(prefix="/board")


@board_router.get(
    "",
    responses={**response_500},
    response_model=PaginatedResponse[schemas.BoardSchema],
    summary="모든 게시판 목록 가져오기",
    description=documents.read_boards_description,
)
async def read_boards(
    page: int = Query(1, ge=1, description="몇번째 페이지를 가져올지 지정합니다."),
    page_size: int = Query(
        default=constant.BOARD_DEFAULT_PAGE_SIZE,
        ge=constant.BOARD_MIN_PAGE_SIZE,
        le=constant.BOARD_MAX_PAGE_SIZE,
        description="한 페이지에 몇개의 데이터를 가져올지 지정합니다.",
    ),
    db: AsyncSession = Depends(database.get_db),
):
    return await paginate(db, select(Board), page, page_size)


@board_router.get(
    "/{board_id}",
    responses={**board_response_404, **response_500},
    response_model=schemas.BoardSchema,
    summary="특정 게시판 가져오기",
    description=documents.read_board_description,
)
async def read_board(board_id: int, db: AsyncSession = Depends(database.get_db)):
    db_board = await crud.get_board(db, board_id)
    if db_board is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_board


@board_router.post(
    "",
    responses={**response_403, **response_500},
    response_model=schemas.BoardSchema,
    status_code=201,
    summary="게시판 생성",
    description=documents.create_board_description,
    dependencies=[Depends(auth)],
)
async def create_board(
    board: schemas.BoardCreateSchema,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    user_pk, role_pk = request_user
    await check_user_is_admin(db=db, role_pk=role_pk)

    db_board = await crud.create_board(db, board)
    return db_board


@board_router.put(
    "/{board_id}",
    responses={**response_403, **board_response_404, **response_500},
    response_model=schemas.BoardSchema,
    summary="게시판 수정 (전체 업데이트)",
    description=documents.update_board_description,
    dependencies=[Depends(auth)],
)
@board_router.patch(
    "/{board_id}",
    responses={**response_403, **board_response_404, **response_500},
    response_model=schemas.BoardSchema,
    summary="게시판 수정 (부분 업데이트)",
    description=documents.update_board_description,
    dependencies=[Depends(auth)],
)
async def update_board(
    board_id: int,
    board: schemas.BoardUpdateSchema,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    user_pk, role_pk = request_user
    await check_user_is_admin(db=db, role_pk=role_pk)

    db_board = await crud.update_board(db, board_id, board)
    if db_board is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_board


@board_router.delete(
    "/{board_id}",
    responses={**response_403, **board_response_404, **response_500},
    status_code=204,
    summary="게시판 삭제",
    description=documents.delete_board_description,
    dependencies=[Depends(auth)],
)
async def delete_board(
    board_id: int,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    user_pk, role_pk = request_user
    await check_user_is_admin(db=db, role_pk=role_pk)

    deleted_id = await crud.delete_board(db, board_id)
    if deleted_id is None:
        raise InternalException("해당 게시판을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
