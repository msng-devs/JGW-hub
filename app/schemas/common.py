# --------------------------------------------------------------------------
# API에 사용되는 기본 스키마를 정의한 모듈입니다.
#
# serialization_alias : JSON으로 직렬화할 때 사용할 이름을 지정합니다.
# validation_alias : validation을 할 때 사용할 이름을 지정합니다.
#
# from_attributes : ORM 모델을 스키마로 변환할 때 사용합니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
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

    class Config:
        orm_mode = True
        from_attributes = True


class MemberSchema(BaseModel):
    id: str = Field(
        ...,
        title="Member's ID (pk)",
        description="회원의 고유 식별자입니다.",
        serialization_alias="member_pk",
    )
    name: str = Field(
        ...,
        title="Member's Name",
        description="회원의 이름입니다.",
        serialization_alias="member_nm",
    )

    class Config:
        orm_mode = True
        from_attributes = True
