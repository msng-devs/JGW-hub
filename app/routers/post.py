# TODO: Post CRUD endpoint 구현. Post 생성 시 content를 Markdown으로 저장할 수 있도록 구현.
# --------------------------------------------------------------------------
# Post 기능의 API endpoint를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from logging import getLogger

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import database
from app.db.models import Post
from app.helper.pagination import PaginatedResponse, paginate
from app.helper.exceptions import InternalException, ErrorCode
from app.schemas import post as schemas
from app.crud import post as crud
from app.utils import constant


log = getLogger(__name__)
post_router = APIRouter(prefix="/post")


@post_router.get(
    "/",
    response_model=PaginatedResponse[schemas.PostSchema],
    summary="모든 게시글 목록 가져오기",
    description="게시글 목록을 가져옵니다.",
)
async def read_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        default=constant.POST_DEFAULT_PAGE_SIZE,
        ge=constant.POST_MIN_PAGE_SIZE,
        le=constant.POST_MAX_PAGE_SIZE,
    ),
    db: AsyncSession = Depends(database.get_db),
):
    return await paginate(db, select(Post), page, page_size)


@post_router.get(
    "/{post_id}",
    response_model=schemas.PostSchema,
    summary="특정 게시글 가져오기",
    description="지정한 게시글의 데이터를 가져옵니다.",
)
async def read_post(post_id: int, db: AsyncSession = Depends(database.get_db)):
    db_post = await crud.get_post(db, post_id)
    if db_post is None:
        raise InternalException("해당 게시글을 찾을 수 없습니다.", ErrorCode.NOT_FOUND)
    return db_post
