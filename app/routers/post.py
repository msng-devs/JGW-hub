# --------------------------------------------------------------------------
# Post 기능의 API endpoint를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from logging import getLogger
from typing import Optional, Tuple
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import database
from app.db.models import Post, Member
from app.helper.pagination import PaginatedResponse, paginate
from app.helper.exceptions import InternalException, ErrorCode
from app.schemas import post as schemas
from app.crud import post as crud
from app.utils import constant
from ._check import (
    auth,
    check_user,
    check_user_is_admin_or_self,
    check_user_is_admin_or_able_to_post,
    check_user_is_admin_or_able_to_read,
    check_user_is_admin_or_self_or_able_to_post,
)

log = getLogger(__name__)
post_router = APIRouter(prefix="/post")


@post_router.get(
    "/list",
    response_model=PaginatedResponse[schemas.PostPreviewSchema],
    summary="모든 게시글 목록 가져오기",
    description="게시글 목록을 가져옵니다.\n\n결과로 가져오는 게시글은 content가 500자로 제한되어 리턴됩니다. \
    \n\n모든 내용을 가져오려면 특정 게시글 가져오기 API를 사용해야합니다.",
)
async def read_posts(
    page: int = Query(1, ge=1, description="몇번째 페이지를 가져올지 지정합니다."),
    page_size: int = Query(
        default=constant.POST_DEFAULT_PAGE_SIZE,
        ge=constant.POST_MIN_PAGE_SIZE,
        le=constant.POST_MAX_PAGE_SIZE,
        description="한 페이지에 몇개의 데이터를 가져올지 지정합니다.",
    ),
    start_date: Optional[datetime] = Query(
        None, description="게시글을 지정한 날짜부터 작성된 글을 가져옵니다.", example="2023-02-10T01:00:00"
    ),
    end_date: Optional[datetime] = Query(
        None, description="게시글을 지정한 날짜까지 작성된 글을 가져옵니다.", example="2023-02-10T01:00:00"
    ),
    writer_uid: Optional[str] = Query(
        None,
        description="uid의 사용자가 작성한 글을 가져옵니다.",
        example="SLDOqpd04867JDKVUqprod-203JI",
    ),
    writer_name: Optional[str] = Query(
        None, description="지정한 이름을 가진 사용자가 작성한 글을 가져옵니다.", example="이준혁"
    ),
    board: Optional[int] = Query(None, description="지정한 게시판에 작성된 글을 가져옵니다.", example=1),
    title: Optional[str] = Query(
        None, description="지정한 단어가 제목에 포함된 글을 가져옵니다.", example="테스트"
    ),
    order: Optional[str] = Query(
        None, description="지정한 필드를 기준으로 정렬하여 게시글을 가져옵니다.", example="id"
    ),
    desc: Optional[int] = Query(
        None, description="order가 존재할 때, desc을 1로 지정하면 역순으로 정렬하여 게시글을 가져옵니다.", example=1
    ),
    db: AsyncSession = Depends(database.get_db),
):
    conditions = []
    query = select(Post)

    if start_date:
        conditions.append(Post.write_date >= start_date)
    if end_date:
        conditions.append(Post.write_date <= end_date)
    if writer_uid:
        conditions.append(Post.member_id == writer_uid)
    if writer_name:
        query = query.join(Post.member_relation).filter(Member.name == writer_name)
    if board:
        conditions.append(Post.board_id == board)
    if title:
        conditions.append(Post.title.contains(title))

    query = query.where(and_(*conditions))

    if order:
        order_clause = getattr(Post, order)
        if desc:
            order_clause = order_clause.desc()
        query = query.order_by(order_clause)

    return await paginate(db, query, page, page_size)


@post_router.get(
    "/{post_id}",
    response_model=schemas.PostSchema,
    summary="특정 게시글 가져오기",
    description="지정한 게시글의 데이터를 가져옵니다. 요청한 유저의 권한이 가져오려는 게시글이 속한 게시판의 읽기 레벨과 같거나 \
    더 높아야 글 읽기가 가능합니다.\n\n관리자는 게시판의 읽기 권한과 상관 없이 글 읽기가 가능합니다.",
    dependencies=[Depends(auth)],
)
async def read_post(
    post_id: int,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    user_pk, role_pk = request_user

    db_post = await crud.get_post(db, post_id)
    if db_post is None:
        raise InternalException("해당 게시글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)

    await check_user_is_admin_or_able_to_read(
        db=db, role_pk=role_pk, board_pk=db_post.board_id.read_level.id
    )
    return db_post


@post_router.post(
    "/",
    response_model=schemas.PostSchema,
    status_code=201,
    summary="게시글 생성",
    description="새로운 게시글을 생성합니다. 쓰기 요청한 유저의 권한이 작성하려는 게시판의 쓰기 레벨과 같거나 더 높아야 글 작성이 가능합니다.\
                \n\n관리자는 게시판의 쓰기 권한과 상관 없이 글 작성이 가능합니다.",
    dependencies=[Depends(auth)],
)
async def create_post(
    post: schemas.PostCreateBase,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    user_pk, role_pk = request_user
    await check_user_is_admin_or_able_to_post(
        db=db, role_pk=role_pk, board_pk=post.board_id
    )

    post_data = post.model_dump(by_alias=True)
    post_data["member_member_pk"] = str(user_pk)
    post_schema = schemas.PostCreateSchema(**post_data)

    return await crud.create_post(db, post_schema)


@post_router.put(
    "/{post_id}",
    response_model=schemas.PostSchema,
    summary="게시글 수정 (전체 업데이트)",
    description="지정한 게시글의 데이터를 전체적으로 수정합니다. (부분 업데이트도 지원합니다) 요청한 유저가 글을 작성한 본인이면서 \
    요청한 유저의 권한이 수정하려는 게시글이 속한 게시판의 쓰기 레벨과 같거나 더 높아야 글 수정이 가능합니다.\
    \n\n관리자도 본인이 아니면 글 수정이 불가능합니다.",
    dependencies=[Depends(auth)],
)
@post_router.patch(
    "/{post_id}",
    response_model=schemas.PostSchema,
    summary="게시글 수정 (부분 업데이트)",
    description="지정한 게시글의 데이터를 부분적으로 수정합니다. 요청한 유저가 글을 작성한 본인이면서 \
    요청한 유저의 권한이 수정하려는 게시글이 속한 게시판의 쓰기 레벨과 같거나 더 높아야 글 수정이 가능합니다.\
    \n\n관리자도 본인이 아니면 글 수정이 불가능합니다.",
    dependencies=[Depends(auth)],
)
async def update_post(
    post_id: int,
    post: schemas.PostUpdateSchema,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    await check_user_is_admin_or_self_or_able_to_post(
        db=db,
        post_id=post_id,
        user_info=request_user,
    )

    db_post = await crud.update_post(db, post_id, post)
    if db_post is None:
        raise InternalException("해당 게시글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_post


@post_router.delete(
    "/{post_id}",
    status_code=204,
    summary="게시글 삭제",
    description="지정한 게시글을 삭제합니다.\n\n글을 쓴 본인 또는 관리자만 삭제가 가능합니다.",
    dependencies=[Depends(auth)],
)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(database.get_db),
    request_user: Tuple[str, int] = Depends(check_user),
):
    await check_user_is_admin_or_self(db=db, user_info=request_user, post_id=post_id)
    deleted_id = await crud.delete_post(db, post_id)
    if deleted_id is None:
        raise InternalException("해당 게시글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
