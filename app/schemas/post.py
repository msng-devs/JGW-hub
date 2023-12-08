# --------------------------------------------------------------------------
# Post 기능의 스키마를 정의한 모듈입니다.
#
# serialization_alias : JSON으로 직렬화할 때 사용할 이름을 지정합니다.
# validation_alias : validation을 할 때 사용할 이름을 지정합니다.
#
# from_attributes : ORM 모델을 스키마로 변환할 때 사용합니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import MemberSchema
from .board import BoardSchema


class PostCreateSchema(BaseModel):
    title: str = Field(
        ...,
        title="Post's Title",
        description="게시글의 제목입니다.",
        alias="post_title",
    )
    content: str = Field(
        ...,
        title="Post's Content",
        description="게시글의 내용입니다.",
        alias="post_content",
    )
    write_date: datetime = Field(
        ...,
        title="Post's Write Date",
        description="게시글의 작성일입니다.",
        alias="post_write_time",
    )
    update_date: datetime = Field(
        ...,
        title="Post's Update Date",
        description="게시글의 수정일입니다.",
        alias="post_update_time",
    )
    thumbnail_id: int = Field(
        None,
        title="Post's Thumbnail ID",
        description="게시글의 썸네일 ID입니다.",
        alias="thumbnail_id_pk",
    )
    board_id: int = Field(
        ...,
        title="Post's Board ID",
        description="게시글의 게시판 ID입니다.",
        alias="board_board_id_pk",
    )


class PostUpdateSchema(BaseModel):
    title: str = Field(
        None,
        title="Post's Title",
        description="게시글의 제목입니다.",
        alias="post_title",
    )
    content: str = Field(
        None,
        title="Post's Content",
        description="게시글의 내용입니다.",
        alias="post_content",
    )
    update_date: datetime = Field(
        None,
        title="Post's Update Date",
        description="게시글의 수정일입니다.",
        alias="post_update_time",
    )
    thumbnail_id: int = Field(
        None,
        title="Post's Thumbnail ID",
        description="게시글의 썸네일 ID입니다.",
        alias="thumbnail_id_pk",
    )
    board_id: int = Field(
        None,
        title="Post's Board ID",
        description="게시글의 게시판 ID입니다.",
        alias="board_board_id_pk",
    )


class PostSchema(BaseModel):
    id: int = Field(
        ...,
        title="Post's ID (pk)",
        description="게시글의 고유 식별자입니다.",
        serialization_alias="post_id_pk",
    )
    title: str = Field(
        ...,
        title="Post's Title",
        description="게시글의 제목입니다.",
        serialization_alias="post_title",
    )
    content: str = Field(
        ...,
        title="Post's Content",
        description="게시글의 내용입니다.",
        serialization_alias="post_content",
    )
    write_date: datetime = Field(
        ...,
        title="Post's Write Date",
        description="게시글의 작성일입니다.",
        serialization_alias="post_write_date",
    )
    update_date: datetime = Field(
        ...,
        title="Post's Update Date",
        description="게시글의 수정일입니다.",
        serialization_alias="post_update_date",
    )
    thumbnail_id: Optional[int] = Field(
        None,
        title="Post's Thumbnail ID",
        description="게시글의 썸네일 ID입니다.",
        serialization_alias="thumbnail_id_pk",
    )
    board_id: BoardSchema = Field(
        ...,
        title="Post's Board ID",
        description="게시글의 게시판 ID입니다.",
        validation_alias="board_relation",
        serialization_alias="board_board_id_pk",
    )
    member_id: MemberSchema = Field(
        None,
        title="Post's Member ID",
        description="게시글의 작성자 ID입니다.",
        validation_alias="member_relation",
        serialization_alias="member_member_pk",
    )

    class Config:
        orm_mode = True
        from_attributes = True
