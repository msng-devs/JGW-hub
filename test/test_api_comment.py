# --------------------------------------------------------------------------
# Comment의 API router을 테스트하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import random
import markdown
import pytest_asyncio

from httpx import AsyncClient
from datetime import datetime, timedelta

from app.db.models import Comment
from test.conftest import test_engine, AsyncSession

from .test_api_board import _create_test_board_at_db
from .test_api_post import _create_test_post_at_db


async def _create_test_comment_at_db(
    post_id: int,
    member_pk: str,
    comment_write_time: datetime = datetime.now(),
    comment_update_time: datetime = datetime.now(),
    comment_delete: int = 0,
    comment_depth: int = 0,
    comment_content: str = "test",
    comment_comment_id_ref: int = None,
):
    async with AsyncSession(bind=test_engine) as session:
        comment = Comment(
            depth=comment_depth,
            content=comment_content,
            write_time=comment_write_time,
            update_time=comment_update_time,
            delete=comment_delete,
            post_id=post_id,
            member_id=member_pk,
            comment_id_ref=comment_comment_id_ref,
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment


class TestCommentApi:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.url = "/hub/api/v2/comment/"
        self.member_id = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
        for i in range(5):
            await _create_test_board_at_db(
                board_name=f"공지사항{i}",
                board_layout=0,
                role_role_pk_write_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_read_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_comment_write_level=random.choice([1, 2, 3, 4, 5]),
            )

        for i in range(5):
            days_ago = random.randint(1, 30)
            write_date = datetime.now() - timedelta(days=days_ago)
            update_date = write_date + timedelta(days=random.randint(0, 5))
            content = f"test_post_content_{i}"
            content = markdown.markdown(content)
            await _create_test_post_at_db(
                post_title="test_title" + str(i),
                post_content=content,
                post_write_time=write_date,
                post_update_time=update_date,
                board_board_id_pk=random.choice([1, 2, 3, 4, 5]),
                member_member_pk=self.member_id,
                thumbnail_id_pk=None,
            )

    def __make_header(
        self, role_pk: int = 5, user_pk: str = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
    ):
        header_data = {
            "user_pk": user_pk,
            "role_pk": str(role_pk),
        }
        return header_data

    async def test_get_comments(self, app_client: AsyncClient):
        print("Comment Api GET ALL Running...")

        # given
        for i in range(3):
            await _create_test_comment_at_db(
                post_id=1,
                member_pk=self.member_id,
                comment_content=f"test_content_{i}",
                comment_depth=0,
            )

        for i in range(2):
            await _create_test_comment_at_db(
                post_id=1,
                member_pk=self.member_id,
                comment_content=f"test_reply_content_{i}",
                comment_depth=1,
                comment_comment_id_ref=1,
            )

        # when
        query_params = {"post_id": 1}

        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 5
        assert response_data.get("next") is None
        assert response_data.get("previous") is None
        assert len(response_data.get("results")) == 5
        assert response_data.get("results")[0].get("comment_id") == 1
        assert response_data.get("results")[0].get("comment_depth") == 0
        assert response_data.get("results")[0].get("comment_delete") == 0

        # when
        query_params = {"post_id": 1, "page": 1, "page_size": 3}

        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 5
        assert (
            response_data.get("next")
            == "http://test/hub/api/v2/comment/?post_id=1&page_size=3&page=2"
        )
        assert len(response_data.get("results")) == 3
        assert response_data.get("results")[0].get("comment_id") == 1
        assert response_data.get("results")[0].get("comment_depth") == 0
        assert response_data.get("results")[0].get("comment_delete") == 0

    async def test_create_comment(self, app_client: AsyncClient):
        print("Comment Api POST Running...")

        # given
        data = {
            "comment_depth": 0,
            "post_post_id_pk": 1,
            "comment_content": "test_content",
            "comment_delete": 0,
            "comment_comment_id_ref": None,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 201
        assert response_data.get("comment_id") == 1
        assert response_data.get("comment_depth") == 0
        assert response_data.get("comment_delete") == 0
        assert response_data.get("post_post_id_pk") == 1
        assert response_data.get("comment_comment_id_ref") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("comment_write_time") is not None
        assert response_data.get("comment_update_time") is not None

    async def test_create_child_comment(self, app_client: AsyncClient):
        print("Comment Api child comment POST Running...")

        # given
        await _create_test_comment_at_db(
            post_id=1,
            member_pk=self.member_id,
            comment_content="test_comment",
            comment_depth=0,
        )

        data = {
            "comment_depth": 1,
            "post_post_id_pk": 1,
            "comment_content": "test_content",
            "comment_delete": 0,
            "comment_comment_id_ref": 1,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 201
        assert response_data.get("comment_id") == 2
        assert response_data.get("comment_depth") == 1
        assert response_data.get("comment_delete") == 0
        assert response_data.get("post_post_id_pk") == 1
        assert response_data.get("comment_comment_id_ref") == 1
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("comment_write_time") is not None
        assert response_data.get("comment_update_time") is not None

    async def test_patch_comment_by_id(self, app_client: AsyncClient):
        print("Comment Api PATCH BY ID Running...")

        # given
        days_ago = random.randint(1, 30)
        previous_date = datetime.now() - timedelta(days=days_ago)

        await _create_test_comment_at_db(
            post_id=1,
            member_pk=self.member_id,
            comment_content="test_comment",
            comment_depth=0,
            comment_write_time=previous_date,
            comment_update_time=previous_date,
        )

        data = {
            "comment_content": "test_content",
        }

        # when
        response = await app_client.patch(
            f"{self.url}1", json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("comment_id") == 1
        assert response_data.get("comment_depth") == 0
        assert response_data.get("comment_delete") == 0
        assert response_data.get("comment_content") == "test_content"
        assert response_data.get("post_post_id_pk") == 1
        assert response_data.get("comment_comment_id_ref") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("comment_write_time") == previous_date.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        assert response_data.get("comment_update_time") != response_data.get(
            "comment_write_time"
        )

    async def test_put_comment_by_id(self, app_client: AsyncClient):
        print("Comment Api PUT BY ID Running...")

        # given
        days_ago = random.randint(1, 30)
        previous_date = datetime.now() - timedelta(days=days_ago)

        await _create_test_comment_at_db(
            post_id=1,
            member_pk=self.member_id,
            comment_content="test_comment",
            comment_depth=0,
            comment_write_time=previous_date,
            comment_update_time=previous_date,
        )

        data = {
            "comment_depth": 1,
            "post_post_id_pk": 2,
            "comment_content": "edited_content",
            "comment_delete": 1,
            "comment_comment_id_ref": 1,
        }

        # when
        response = await app_client.put(
            f"{self.url}1", json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("comment_id") == 1
        assert response_data.get("comment_depth") == 1
        assert response_data.get("comment_content") == "edited_content"
        assert response_data.get("comment_delete") == 1
        assert response_data.get("post_post_id_pk") == 2
        assert response_data.get("comment_comment_id_ref") == 1
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("comment_write_time") == previous_date.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        assert response_data.get("comment_update_time") != response_data.get(
            "comment_write_time"
        )

    async def test_delete_comment_by_id(self, app_client: AsyncClient):
        print("Comment Api DELETE BY ID Running...")

        # given
        days_ago = random.randint(1, 30)
        previous_date = datetime.now() - timedelta(days=days_ago)

        await _create_test_comment_at_db(
            post_id=1,
            member_pk=self.member_id,
            comment_content="test_comment",
            comment_depth=0,
            comment_write_time=previous_date,
            comment_update_time=previous_date,
        )

        # when
        response = await app_client.delete(f"{self.url}1", headers=self.__make_header())

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("comment_id") == 1
        assert response_data.get("comment_content") == "test_comment"
        assert response_data.get("comment_delete") == 1
        assert response_data.get("post_post_id_pk") == 1
        assert response_data.get("comment_comment_id_ref") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("comment_write_time") == previous_date.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        assert response_data.get("comment_update_time") != response_data.get(
            "comment_write_time"
        )


class TestCommentApiError:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.url = "/hub/api/v2/comment/"
        self.member_id = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
        for i in range(5):
            await _create_test_board_at_db(
                board_name=f"공지사항{i}",
                board_layout=0,
                role_role_pk_write_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_read_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_comment_write_level=random.choice([2, 3, 4, 5]),
            )

        for i in range(5):
            days_ago = random.randint(1, 30)
            write_date = datetime.now() - timedelta(days=days_ago)
            update_date = write_date + timedelta(days=random.randint(0, 5))
            content = f"test_post_content_{i}"
            content = markdown.markdown(content)
            await _create_test_post_at_db(
                post_title="test_title" + str(i),
                post_content=content,
                post_write_time=write_date,
                post_update_time=update_date,
                board_board_id_pk=random.choice([1, 2, 3, 4, 5]),
                member_member_pk=self.member_id,
                thumbnail_id_pk=None,
            )

    def __make_header(
        self, role_pk: int = 5, user_pk: str = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
    ):
        header_data = {
            "user_pk": user_pk,
            "role_pk": str(role_pk),
        }
        return header_data

    async def test_get_comments_post_id_error(self, app_client: AsyncClient):
        print("Comment Api GET id Error Running...")

        # given
        for i in range(3):
            await _create_test_comment_at_db(
                post_id=1,
                member_pk=self.member_id,
                comment_content=f"test_content_{i}",
                comment_depth=0,
            )

        for i in range(2):
            await _create_test_comment_at_db(
                post_id=1,
                member_pk=self.member_id,
                comment_content=f"test_reply_content_{i}",
                comment_depth=1,
                comment_comment_id_ref=1,
            )

        # when
        query_params = {"page": 1, "page_size": 3}

        response = await app_client.get(self.url, params=query_params)

        # then
        assert response.status_code == 422

        # when
        query_params = {"post_id": 100, "page": 1, "page_size": 3}

        response = await app_client.get(self.url, params=query_params)

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 0
        assert response_data.get("next") is None
        assert response_data.get("previous") is None
        assert len(response_data.get("results")) == 0

    async def test_create_comment_forbidden_role(self, app_client: AsyncClient):
        print("Comment Api POST Forbidden Role Running...")

        # given
        data = {
            "comment_depth": 0,
            "post_post_id_pk": 1,
            "comment_content": "test_content",
            "comment_delete": 0,
            "comment_comment_id_ref": None,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header(role_pk=1)
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."
        assert response_data.get("errorCode") == "HB-AUTH-002"

    async def test_edit_comment_forbidden_role(self, app_client: AsyncClient):
        print("Comment Api PUT Forbidden Role Running...")

        # given
        await _create_test_comment_at_db(
            post_id=1,
            member_pk=self.member_id,
            comment_content="test_comment",
            comment_depth=0,
        )

        data = {
            "comment_depth": 1,
            "post_post_id_pk": 2,
            "comment_content": "edited_content",
            "comment_delete": 1,
            "comment_comment_id_ref": 1,
        }

        # when
        response = await app_client.put(
            f"{self.url}1", json=data, headers=self.__make_header(role_pk=1)
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."
        assert response_data.get("errorCode") == "HB-AUTH-002"

        # when
        response = await app_client.put(
            f"{self.url}1",
            json=data,
            headers=self.__make_header(
                role_pk=5, user_pk="idididididididididididididid"
            ),
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."
        assert response_data.get("errorCode") == "HB-AUTH-002"
