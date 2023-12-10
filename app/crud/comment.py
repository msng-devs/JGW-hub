# --------------------------------------------------------------------------
# Comment 기능의 CRUD 메서드를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ._base import create_object, update_object
from app.db.models import Comment
from app.schemas import comment as schema


async def create_comment(
    db: AsyncSession, comment: schema.CommentCreateSchema
) -> schema.CommentSchema:
    return await create_object(
        db=db, model=Comment, obj=comment, response_model=schema.CommentSchema
    )


async def update_comment(
    db: AsyncSession, comment_id: int, comment: schema.CommentUpdateSchema
) -> Optional[schema.CommentSchema]:
    return await update_object(
        db=db,
        model=Comment,
        model_id=comment_id,
        obj=comment,
        response_model=schema.CommentSchema,
    )


async def delete_comment(
    db: AsyncSession, comment_id: int
) -> Optional[schema.CommentSchema]:
    return await update_object(
        db,
        Comment,
        comment_id,
        schema.CommentUpdateSchema(
            comment_delete=1, comment_update_time=datetime.now()
        ),
        response_model=schema.CommentSchema,
    )
