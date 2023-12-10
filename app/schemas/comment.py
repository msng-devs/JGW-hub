# --------------------------------------------------------------------------
# Comment 기능의 스키마를 정의한 모듈입니다.
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


class CommentCreateBase(BaseModel):
    depth: int = Field(
        ...,
        title="Comment's Depth",
        description="댓글의 깊이입니다. 생성할 데이터가 몇번째 깊이의 대댓글인지 표현합니다. 최상위 댓글은 0입니다.",
        alias="comment_depth",
    )
    content: str = Field(
        ...,
        title="Comment's Content",
        description="댓글의 내용입니다. (plainText)",
        alias="comment_content",
    )
    delete: int = Field(
        ...,
        title="Comment's Delete",
        description="댓글의 삭제 여부입니다. 초기에는 0으로 설정.",
        alias="comment_delete",
    )
    post_id: int = Field(
        ...,
        title="Comment's Post ID",
        description="댓글의 게시글 ID입니다.",
        alias="post_post_id_pk",
    )
    comment_id_ref: Optional[int] = Field(
        None,
        title="Comment's Comment ID",
        description="작성하려는 댓글의 부모 댓글 pk입니다. 최상위 댓글이라면 null.",
        alias="comment_comment_id_ref",
    )


class CommentCreateSchema(CommentCreateBase):
    member_id: str = Field(
        ...,
        title="Comment's Member ID",
        description="댓글의 회원 ID입니다.",
        alias="member_member_pk",
    )
    write_time: datetime = Field(
        ...,
        title="Comment's Write Date",
        description="댓글의 작성일입니다.",
        alias="comment_write_time",
    )
    update_time: datetime = Field(
        ...,
        title="Comment's Update Date",
        description="댓글의 수정일입니다.",
        alias="comment_update_time",
    )


class CommentUpdateBase(BaseModel):
    depth: Optional[int] = Field(
        None,
        title="Comment's Depth",
        description="댓글의 깊이입니다. 생성할 데이터가 몇번째 깊이의 대댓글인지 표현합니다. 최상위 댓글은 0입니다.",
        alias="comment_depth",
    )
    content: Optional[str] = Field(
        None,
        title="Comment's Content",
        description="댓글의 내용입니다. (plainText)",
        alias="comment_content",
    )
    delete: Optional[int] = Field(
        None,
        title="Comment's Delete",
        description="댓글의 삭제 여부입니다. 초기에는 0으로 설정.",
        alias="comment_delete",
    )
    post_id: Optional[int] = Field(
        None,
        title="Comment's Post ID",
        description="댓글의 게시글 ID입니다.",
        alias="post_post_id_pk",
    )
    comment_id_ref: Optional[int] = Field(
        None,
        title="Comment's Comment ID",
        description="작성하려는 댓글의 부모 댓글 pk입니다. 최상위 댓글이라면 null.",
        alias="comment_comment_id_ref",
    )


class CommentUpdateSchema(CommentUpdateBase):
    update_time: datetime = Field(
        ...,
        title="Comment's Update Date",
        description="댓글의 수정일입니다.",
        alias="comment_update_time",
    )


class CommentSchema(BaseModel):
    id: int = Field(
        ...,
        title="Comment's ID (pk)",
        description="댓글의 고유 식별자입니다.",
        serialization_alias="comment_id",
    )
    depth: int = Field(
        ...,
        title="Comment's Depth",
        description="댓글의 깊이입니다.",
        serialization_alias="comment_depth",
    )
    content: str = Field(
        ...,
        title="Comment's Content",
        description="댓글의 내용입니다.",
        serialization_alias="comment_content",
    )
    write_time: datetime = Field(
        ...,
        title="Comment's Write Date",
        description="댓글의 작성일입니다.",
        serialization_alias="comment_write_time",
    )
    update_time: datetime = Field(
        ...,
        title="Comment's Update Date",
        description="댓글의 수정일입니다.",
        serialization_alias="comment_update_time",
    )
    delete: int = Field(
        ...,
        title="Comment's Delete",
        description="댓글의 삭제 여부입니다.",
        serialization_alias="comment_delete",
    )
    post_id: int = Field(
        ...,
        title="Comment's Post ID",
        description="댓글의 게시글 ID입니다.",
        serialization_alias="post_post_id_pk",
    )
    member_id: MemberSchema = Field(
        ...,
        title="Comment's Member ID",
        description="댓글의 작성자 ID입니다.",
        validation_alias="member_relation",
        serialization_alias="member_member_pk",
    )
    comment_id_ref: Optional[int] = Field(
        None,
        title="Comment's Comment ID",
        description="댓글의 댓글 ID입니다.",
        serialization_alias="comment_comment_id_ref",
    )

    class Config:
        from_attributes = True
