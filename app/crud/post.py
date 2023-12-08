# --------------------------------------------------------------------------
# Post 기능의 CRUD 메서드를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ._base import create_object, update_object, delete_object
from app.db.models import Post
from app.schemas import post as schema


async def get_post(db: AsyncSession, post_id: int) -> Optional[schema.PostSchema]:
    post = await db.get(Post, post_id)
    if post:
        return schema.PostSchema.model_validate(post.__dict__)
    else:
        return None
