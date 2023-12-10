# --------------------------------------------------------------------------
# 자람 허브 model ORM을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


# --------------------------------------------------------------------------
# 추후 Message Queue 로직이 적용되면 사라질 수 있는 기본 모델
# --------------------------------------------------------------------------
class Member(Base):
    __tablename__ = "MEMBER"

    id = Column(String(length=28), primary_key=True, name="MEMBER_PK")
    name = Column(String(length=45), nullable=False, name="MEMBER_NM")
    email = Column(String(length=255), nullable=False, unique=True, name="MEMBER_EMAIL")
    status = Column(SmallInteger, nullable=False, default=1, name="MEMBER_STATUS")
    role_id = Column(
        Integer, ForeignKey("ROLE.ROLE_PK"), nullable=False, name="ROLE_ROLE_PK"
    )

    role = relationship("Role", foreign_keys=[role_id], lazy="selectin")


class Role(Base):
    __tablename__ = "ROLE"

    id = Column(Integer, primary_key=True, autoincrement=True, name="ROLE_PK")
    name = Column(String(length=45), unique=True, nullable=False, name="ROLE_NM")


# --------------------------------------------------------------------------
# 자람 허브 서비스에서 사용하는 모델
# --------------------------------------------------------------------------
class Board(Base):
    __tablename__ = "BOARD"

    id = Column(Integer, primary_key=True, autoincrement=True, name="BOARD_ID_PK")
    name = Column(String(length=45), unique=True, nullable=False, name="BOARD_NAME")
    layout = Column(Integer, nullable=False, name="BOARD_LAYOUT")

    write_level = Column(
        Integer,
        ForeignKey("ROLE.ROLE_PK"),
        nullable=False,
        name="ROLE_ROLE_PK_WRITE_LEVEL",
    )
    read_level = Column(
        Integer,
        ForeignKey("ROLE.ROLE_PK"),
        nullable=False,
        name="ROLE_ROLE_PK_READ_LEVEL",
    )
    comment_write_level = Column(
        Integer,
        ForeignKey("ROLE.ROLE_PK"),
        nullable=False,
        name="ROLE_ROLE_PK_COMMENT_WRITE_LEVEL",
    )

    write_level_role = relationship("Role", foreign_keys=[write_level], lazy="selectin")
    read_level_role = relationship("Role", foreign_keys=[read_level], lazy="selectin")
    comment_write_level_role = relationship(
        "Role", foreign_keys=[comment_write_level], lazy="selectin"
    )


class Post(Base):
    __tablename__ = "POST"

    id = Column(Integer, primary_key=True, autoincrement=True, name="POST_ID_PK")
    title = Column(String(length=100), nullable=False, name="POST_TITLE")
    content = Column(Text, nullable=False, name="POST_CONTENT")
    write_time = Column(DateTime, nullable=False, name="POST_WRITE_TIME")
    update_time = Column(DateTime, nullable=False, name="POST_UPDATE_TIME")

    thumbnail_id = Column(Integer, nullable=True, name="THUMBNAIL_ID_PK")
    board_id = Column(
        Integer,
        ForeignKey("BOARD.BOARD_ID_PK"),
        nullable=False,
        name="BOARD_BOADR_ID_PK",
    )
    member_id = Column(
        String(length=28),
        ForeignKey("MEMBER.MEMBER_PK"),
        nullable=True,
        name="MEMBER_MEMBER_PK",
    )

    thumbnail = relationship("Image", back_populates="post")
    board_relation = relationship("Board", foreign_keys=[board_id], lazy="selectin")
    member_relation = relationship("Member", foreign_keys=[member_id], lazy="selectin")


class Image(Base):
    __tablename__ = "IMAGE"

    id = Column(Integer, primary_key=True, autoincrement=True, name="IMAGE_ID_PK")
    name = Column(String(length=45), nullable=False, name="IMAGE_NAME")
    url = Column(String(length=45), nullable=False, name="IMAGE_URL")

    post_id = Column(
        Integer, ForeignKey("POST.POST_ID_PK"), nullable=False, name="POST_POST_ID_PK"
    )
    member_id = Column(
        String(length=28),
        ForeignKey("MEMBER.MEMBER_PK"),
        nullable=True,
        name="MEMBER_MEMBER_PK",
    )

    post = relationship("Post", back_populates="thumbnail")
    member_relation = relationship("Member", foreign_keys=[member_id], lazy="selectin")


class Comment(Base):
    __tablename__ = "COMMENT"

    id = Column(Integer, primary_key=True, autoincrement=True, name="COMMENT_ID")
    depth = Column(Integer, nullable=False, name="COMMENT_DEPTH")
    content = Column(Text, nullable=False, name="COMMENT_CONTENT")
    write_time = Column(DateTime, nullable=False, name="COMMENT_WRITE_TIME")
    update_time = Column(DateTime, nullable=False, name="COMMENT_UPDATE_TIME")
    delete = Column(SmallInteger, nullable=False, default=0, name="COMMENT_DELETE")

    post_id = Column(
        Integer, ForeignKey("POST.POST_ID_PK"), nullable=False, name="POST_POST_ID_PK"
    )
    member_id = Column(
        String(length=28),
        ForeignKey("MEMBER.MEMBER_PK"),
        nullable=True,
        name="MEMBER_MEMBER_PK",
    )
    comment_id_ref = Column(
        Integer,
        ForeignKey("COMMENT.COMMENT_ID"),
        nullable=True,
        name="COMMENT_COMMENT_ID_REF",
    )

    member_relation = relationship("Member", foreign_keys=[member_id], lazy="selectin")
