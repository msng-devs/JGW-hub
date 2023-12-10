# --------------------------------------------------------------------------
# 헤더 관련 로직을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from logging import getLogger
from typing import Tuple, Any

from fastapi import Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Role, Board, Post, Comment
from app.helper.exceptions import InternalException, ErrorCode

log = getLogger(__name__)


def auth(request: Request):
    header = request.headers
    uid = header.get("user_pk") if header.get("user_pk") else None
    role = header.get("role_pk") if header.get("role_pk") else None

    if uid is None or role is None:
        raise InternalException("인증 정보가 없습니다.", ErrorCode.BAD_REQUEST)
    if len(uid) != 28:
        raise InternalException("잘못된 인증 정보입니다.", ErrorCode.BAD_REQUEST)


async def check_user(
    user_pk: str = Header(
        None, description="사용자의 고유 식별자입니다.", convert_underscores=False
    ),
    role_pk: int = Header(None, description="사용자의 이름입니다.", convert_underscores=False),
) -> Tuple[str, int]:
    if not user_pk or not role_pk:
        raise InternalException("사용자 정보가 없습니다.", ErrorCode.BAD_REQUEST)

    return user_pk, role_pk


async def get_admin_role(
    db: AsyncSession,
) -> Role:
    query = select(Role).filter(Role.name == "ROLE_ADMIN")
    result = await db.execute(query)
    admin_role = result.scalar_one()

    return admin_role


async def check_user_is_admin(db: AsyncSession, role_pk: int):
    admin_role = await get_admin_role(db)

    if role_pk < admin_role.id:
        raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)


async def check_user_is_admin_or_self(
    db: AsyncSession,
    user_info: Tuple[str, int],
    model_id: int,
    model: Any,
):
    user_pk, role_pk = user_info
    admin_role = await get_admin_role(db)

    if role_pk < admin_role.id:
        post_owner = await db.get(model, model_id)
        if user_pk != post_owner.member_id:
            raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)


async def check_user_is_admin_or_able_to_post(
    db: AsyncSession, role_pk: int, board_pk: int
):
    admin_role = await get_admin_role(db)

    if role_pk < admin_role.id:
        board_post_role = await db.get(Board, board_pk)
        if role_pk < board_post_role.write_level:
            raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)


async def check_user_is_admin_or_self_or_able_to_post(
    db: AsyncSession, post_id: int, user_info: Tuple[str, int]
):
    user_pk, role_pk = user_info
    admin_role = await get_admin_role(db)
    post = await db.get(Post, post_id)

    if role_pk < admin_role.id:
        board = await db.get(Board, post.board_id)
        if role_pk < board.write_level or user_pk != post.member_id:
            raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)

    elif user_pk != post.member_id:
        raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)


async def check_user_is_admin_or_able_to_read(
    db: AsyncSession, role_pk: int, board_pk: int
):
    admin_role = await get_admin_role(db)

    if role_pk < admin_role.id:
        board_post_role = await db.get(Board, board_pk)
        if role_pk < board_post_role.read_level:
            raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)


async def check_user_is_admin_or_able_to_comment(
    db: AsyncSession, role_pk: int, board_pk: int
):
    admin_role = await get_admin_role(db)

    if role_pk < admin_role.id:
        board_post_role = await db.get(Board, board_pk)
        if role_pk < board_post_role.comment_write_level:
            raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)


async def check_user_is_admin_or_self_or_able_to_comment(
    db: AsyncSession, comment_id: int, user_info: Tuple[str, int]
):
    user_pk, role_pk = user_info
    admin_role = await get_admin_role(db)
    comment = await db.get(Comment, comment_id)
    post = await db.get(Post, comment.post_id)

    if role_pk < admin_role.id:
        board = await db.get(Board, post.board_id)
        if role_pk < board.comment_write_level or user_pk != comment.member_id:
            raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)

    elif user_pk != comment.member_id:
        raise InternalException("해당 유저의 권한으로는 불가능한 작업입니다.", ErrorCode.FORBIDDEN)
