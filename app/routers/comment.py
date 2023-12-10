# --------------------------------------------------------------------------
# Comment 기능의 API endpoint를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from logging import getLogger
from typing import Tuple
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import database
from app.db.models import Comment
from app.helper.pagination import PaginatedResponse, paginate
from app.helper.exceptions import InternalException, ErrorCode
from app.schemas import comment as schemas
from app.crud import comment as crud
from app.crud import post as post_crud
from app.utils import constant
from ._check import (
    auth,
    check_user,
    check_user_is_admin_or_self,
    check_user_is_admin_or_able_to_comment,
    check_user_is_admin_or_self_or_able_to_comment,
)

log = getLogger(__name__)
comment_router = APIRouter(prefix="/comment")


@comment_router.get(
    "/",
    response_model=PaginatedResponse[schemas.CommentSchema],
    summary="특정 게시글의 모든 댓글 가져오기",
    description="특정 게시글의 모든 댓글을 가져옵니다.",
)
async def read_comments(
    post_id: int = Query(
        ...,
        description="어떤 게시글에 작성된 댓글을 가져올지 지정합니다. \
    \n\n게시글 번호를 지정하지 않으면 422을 응답합니다.",
    ),
    page: int = Query(1, ge=1, description="몇번째 페이지를 가져올지 지정합니다."),
    page_size: int = Query(
        default=constant.COMMENT_DEFAULT_PAGE_SIZE,
        ge=constant.COMMENT_MIN_PAGE_SIZE,
        le=constant.COMMENT_MAX_PAGE_SIZE,
        description="한 페이지에 몇개의 데이터를 가져올지 지정합니다.",
    ),
    db: AsyncSession = Depends(database.get_db),
):
    return await paginate(
        db,
        select(Comment).where(Comment.post_id == post_id),
        page,
        page_size,
    )


@comment_router.post(
    "/",
    response_model=schemas.CommentSchema,
    status_code=201,
    summary="댓글 작성하기",
    description="특정 게시글에 댓글을 작성합니다. 쓰기 요청한 유저의 권한이 작성하려는 게시판의 댓글 쓰기 레벨\
    (Board.role_role_pk_comment_write_level)과 같거나 더 높아야 글 작성이 가능합니다.\
    \n\nadmin은 게시판의 쓰기 권한과 상관 없이 댓글 작성이 가능합니다.",
    dependencies=[Depends(auth)],
)
async def create_comment(
    comment: schemas.CommentCreateBase,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    user_pk, role_pk = request_user
    db_post = await post_crud.get_post(db, comment.post_id)
    if db_post is None:
        raise InternalException("해당 게시글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    await check_user_is_admin_or_able_to_comment(
        db=db, role_pk=role_pk, board_pk=db_post.board_id.comment_write_level.id
    )

    comment_data = comment.model_dump(by_alias=True)
    comment_data["member_member_pk"] = str(user_pk)
    comment_data["comment_write_time"] = datetime.now()
    comment_data["comment_update_time"] = datetime.now()
    comment_schema = schemas.CommentCreateSchema(**comment_data)

    return await crud.create_comment(db, comment_schema)


@comment_router.put(
    "/{comment_id}",
    response_model=schemas.CommentSchema,
    summary="댓글 수정하기 (전체 업데이트)",
    description="지정한 댓글의 데이터를 부분적으로 수정합니다 (전체 업데이트도 지원합니다). 요청한 유저가 댓글을 작성한 본인이면서 \
    요청한 유저의 권한이 수정하려는 게시글이 속한 게시판의 댓글 쓰기 레벨과 같거나 더 높아야 글 수정이 가능합니다.\
    \n\nadmin도 본인이 아니면 글 수정이 불가능합니다.",
    dependencies=[Depends(auth)],
)
@comment_router.patch(
    "/{comment_id}",
    response_model=schemas.CommentSchema,
    summary="댓글 수정하기 (부분 업데이트)",
    description="지정한 댓글의 데이터를 전체적으로 수정합니다 (부분 업데이트도 지원합니다). 요청한 유저가 댓글을 작성한 본인이면서 \
    요청한 유저의 권한이 수정하려는 게시글이 속한 게시판의 댓글 쓰기 레벨과 같거나 더 높아야 글 수정이 가능합니다.\
    \n\nadmin도 본인이 아니면 글 수정이 불가능합니다.",
    dependencies=[Depends(auth)],
)
async def update_comment(
    comment_id: int,
    comment: schemas.CommentUpdateBase,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    await check_user_is_admin_or_self_or_able_to_comment(
        db=db, comment_id=comment_id, user_info=request_user
    )

    comment_data = comment.model_dump(by_alias=True)
    comment_data["comment_update_time"] = datetime.now()
    comment_schema = schemas.CommentUpdateSchema(**comment_data)

    db_comment = await crud.update_comment(db, comment_id, comment_schema)
    if db_comment is None:
        raise InternalException("해당 댓글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_comment


@comment_router.delete(
    "/{comment_id}",
    response_model=schemas.CommentSchema,
    summary="댓글 삭제하기",
    description="지정한 댓글을 삭제합니다. 글을 쓴 본인 또는 관리자만 삭제가 가능합니다.\
                \n\n데이터를 실제로 삭제하지 않고 comment_delete를 1로 변경합니다.",
    dependencies=[Depends(auth)],
)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    await check_user_is_admin_or_self(
        db=db, user_info=request_user, model_id=comment_id, model=Comment
    )

    db_comment = await crud.delete_comment(db, comment_id)
    if db_comment is None:
        raise InternalException("해당 댓글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_comment
