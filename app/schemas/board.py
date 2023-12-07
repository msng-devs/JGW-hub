# --------------------------------------------------------------------------
# Board 기능의 스키마를 정의한 모듈입니다.
#
# serialization_alias : JSON으로 직렬화할 때 사용할 이름을 지정합니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from __future__ import annotations

from pydantic import BaseModel, Field


class RoleSchema(BaseModel):
    id: int = Field(
        ...,
        title="Role's ID (pk)",
        description="권한의 고유 식별자입니다.",
        serialization_alias="role_id_pk",
    )
    name: str = Field(
        ...,
        title="Role's Name",
        description="권한의 이름입니다.",
        serialization_alias="role_name",
    )

    class ConfigDict:
        orm_mode = True


class BoardCreateSchema(BaseModel):
    name: str = Field(
        ...,
        title="Board's Name",
        description="게시판의 이름입니다.",
        alias="board_name",
    )
    layout: int = Field(
        ...,
        title="Board's Layout",
        description="게시판의 레이아웃입니다.",
        alias="board_layout",
    )
    write_level: int = Field(
        ...,
        title="Board's Write Level",
        description="게시판의 글 작성 권한입니다. (Role pk)",
        alias="role_role_pk_write_level",
    )
    read_level: int = Field(
        ...,
        title="Board's Read Level",
        description="게시판의 글 읽기 권한입니다. (Role pk)",
        alias="role_role_pk_read_level",
    )
    comment_write_level: int = Field(
        ...,
        title="Board's Comment Write Level",
        description="게시판의 댓글 작성 권한입니다. (Role pk)",
        alias="role_role_pk_comment_write_level",
    )


class BoardUpdateSchema(BaseModel):
    name: str = Field(
        None,
        title="Board's Name",
        description="게시판의 이름입니다.",
        alias="board_name",
    )
    layout: int = Field(
        None,
        title="Board's Layout",
        description="게시판의 레이아웃입니다.",
        alias="board_layout",
    )
    write_level: int = Field(
        None,
        title="Board's Write Level",
        description="게시판의 글 작성 권한입니다. (Role pk)",
        alias="role_role_pk_write_level",
    )
    read_level: int = Field(
        None,
        title="Board's Read Level",
        description="게시판의 글 읽기 권한입니다. (Role pk)",
        alias="role_role_pk_read_level",
    )
    comment_write_level: int = Field(
        None,
        title="Board's Comment Write Level",
        description="게시판의 댓글 작성 권한입니다. (Role pk)",
        alias="role_role_pk_comment_write_level",
    )


class BoardSchema(BaseModel):
    id: int = Field(
        ...,
        title="Board's ID (pk)",
        description="게시판의 고유 식별자입니다.",
        serialization_alias="board_id_pk",
    )
    name: str = Field(
        ...,
        title="Board's Name",
        description="게시판의 이름입니다.",
        serialization_alias="board_name",
    )
    layout: int = Field(
        ...,
        title="Board's Layout",
        description="게시판의 레이아웃입니다.",
        serialization_alias="board_layout",
    )
    write_level: RoleSchema | int = Field(
        ...,
        title="Board's Write Level",
        description="게시판의 글 작성 권한입니다. (Role pk)",
        serialization_alias="role_role_pk_write_level",
    )
    read_level: RoleSchema | int = Field(
        ...,
        title="Board's Read Level",
        description="게시판의 글 읽기 권한입니다. (Role pk)",
        serialization_alias="role_role_pk_read_level",
    )
    comment_write_level: RoleSchema | int = Field(
        ...,
        title="Board's Comment Write Level",
        description="게시판의 댓글 작성 권한입니다. (Role pk)",
        serialization_alias="role_role_pk_comment_write_level",
    )

    class ConfigDict:
        orm_mode = True
