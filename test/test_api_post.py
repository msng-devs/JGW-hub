# --------------------------------------------------------------------------
# Post의 API router을 테스트하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import random
import string
import markdown
import pytest_asyncio

from httpx import AsyncClient
from datetime import datetime, timedelta

from app.db.models import Post
from test.conftest import test_engine, AsyncSession

from .test_api_board import _create_test_board_at_db


async def _create_test_post_at_db(
    post_title: str,
    post_content: str,
    post_write_date: datetime,
    post_update_date: datetime,
    board_board_id_pk: int,
    member_member_pk: str,
    thumbnail_id_pk: int = None,
):
    async with AsyncSession(bind=test_engine) as session:
        test_post = Post(
            title=post_title,
            content=post_content,
            write_date=post_write_date,
            update_date=post_update_date,
            board_id=board_board_id_pk,
            member_id=member_member_pk,
            thumbnail_id=thumbnail_id_pk,
        )
        session.add(test_post)
        await session.commit()
        await session.refresh(test_post)


class TestPostApi:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.url = "/hub/api/v2/post/"
        self.member_id = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
        for i in range(5):
            await _create_test_board_at_db(
                board_name=f"공지사항{i}",
                board_layout=0,
                role_role_pk_write_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_read_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_comment_write_level=random.choice([1, 2, 3, 4, 5]),
            )

    def __make_header(self):
        header_data = {
            "HTTP_USER_PK": "pkpkpkpkpkpkpkpkpkpkpkpkpkpk",
            "HTTP_ROLE_PK": "5",
        }
        return header_data

    async def _create_random_posts(
        self,
        iter_num: int,
        member_member_pk: str = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk",
        board_board_id_pk: int = 1,
        content: str = "".join(
            random.choices(string.ascii_letters + string.digits, k=501)
        ),
    ):
        for i in range(iter_num):
            days_ago = random.randint(1, 30)
            write_date = datetime.now() - timedelta(days=days_ago)
            update_date = write_date + timedelta(days=random.randint(0, 5))
            content = markdown.markdown(content)

            await _create_test_post_at_db(
                post_title="test_title" + str(i),
                post_content=content,
                post_write_date=write_date,
                post_update_date=update_date,
                board_board_id_pk=board_board_id_pk,
                member_member_pk=member_member_pk,
                thumbnail_id_pk=None,
            )

    async def test_get_posts(self, app_client: AsyncClient):
        print("Post Api GET all Running...")

        # given
        await self._create_random_posts(20)

        # when
        response = await app_client.get(self.url, headers=self.__make_header())

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 20
        assert response_data.get("next") == "http://test/hub/api/v2/post/?page=2"
        assert response_data.get("previous") is None
        assert len(response_data.get("results")) == 10
        assert response_data.get("results")[0].get("post_id_pk") == 1
        assert len(response_data.get("results")[0].get("post_content")) == 500

    async def test_get_posts_by_desc(self, app_client: AsyncClient):
        print("Post Api GET desc Running...")

        # given
        await self._create_random_posts(20)

        # when
        query_params = {
            "page": 1,
            "page_size": 10,
            "order": "id",
            "desc": 1,
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("results")[0].get("post_id_pk") == 20

    async def test_get_posts_by_date(self, app_client: AsyncClient):
        print("Post Api GET date Running...")

        # given
        await self._create_random_posts(20)

        # when (start_date)
        formatted_date = (datetime.now() - timedelta(days=5)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        query_params = {
            "page": 1,
            "page_size": 10,
            "start_date": formatted_date,
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then (start_date)
        response_data = response.json()
        if response_data.get("results"):
            response_datetime = datetime.strptime(
                response_data.get("results")[0].get("post_write_date"),
                "%Y-%m-%dT%H:%M:%S",
            )
            assert response.status_code == 200
            assert response_datetime >= datetime.strptime(
                formatted_date, "%Y-%m-%dT%H:%M:%S"
            )

        else:
            print("요청은 정상적으로 수행 되었으나, 조건에 맞는 post가 없습니다.")
            assert response.status_code == 200

        # when (end_date)
        formatted_date = (datetime.now() - timedelta(days=5)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        query_params = {
            "page": 1,
            "page_size": 10,
            "end_date": formatted_date,
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then (end_date)
        response_data = response.json()
        if response_data.get("results"):
            response_datetime = datetime.strptime(
                response_data.get("results")[0].get("post_write_date"),
                "%Y-%m-%dT%H:%M:%S",
            )
            assert response.status_code == 200
            assert response_datetime <= datetime.strptime(
                formatted_date, "%Y-%m-%dT%H:%M:%S"
            )

        else:
            print("요청은 정상적으로 수행 되었으나, 조건에 맞는 post가 없습니다.")
            assert response.status_code == 200

    async def test_get_posts_by_writer_uid(self, app_client: AsyncClient):
        print("Post Api GET writer uid Running...")

        # given
        await self._create_random_posts(3)
        await self._create_random_posts(
            3, member_member_pk="idididididididididididididid"
        )

        # when
        query_params = {
            "page": 1,
            "page_size": 10,
            "writer_uid": self.member_id,
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 3
        assert (
            response_data.get("results")[0].get("member_member_pk").get("member_pk")
            == self.member_id
        )

    async def test_get_posts_by_writer_name(self, app_client: AsyncClient):
        print("Post Api GET writer name Running...")

        # given
        await self._create_random_posts(3)
        await self._create_random_posts(
            3, member_member_pk="idididididididididididididid"
        )

        # when
        query_params = {
            "page": 1,
            "page_size": 10,
            "writer_name": "Test Member",
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 3
        assert (
            response_data.get("results")[0].get("member_member_pk").get("member_nm")
            == "Test Member"
        )

    async def test_get_posts_by_board(self, app_client: AsyncClient):
        print("Post Api GET board Running...")

        # given
        await self._create_random_posts(5)
        await self._create_random_posts(5, board_board_id_pk=2)

        # when
        query_params = {
            "page": 1,
            "page_size": 10,
            "board": 2,
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 5
        assert (
            response_data.get("results")[0].get("board_board_id_pk").get("board_id_pk")
            == 2
        )
        assert (
            response_data.get("results")[0].get("board_board_id_pk").get("board_name")
            == "공지사항1"
        )

    async def test_get_posts_by_title(self, app_client: AsyncClient):
        print("Post Api GET title Running...")

        # given
        await self._create_random_posts(20)

        # when
        query_params = {
            "page": 1,
            "page_size": 10,
            "title": "test_title1",
        }
        response = await app_client.get(
            self.url, params=query_params, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 11
        assert response_data.get("results")[0].get("post_title") == "test_title1"
        assert response_data.get("results")[1].get("post_title") == "test_title10"

    async def test_get_post_by_id(self, app_client: AsyncClient):
        print("Post Api GET BY ID Running...")

        # given
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=datetime.now(),
            post_update_date=datetime.now(),
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )

        # when
        response = await app_client.get(f"{self.url}1", headers=self.__make_header())

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("post_title") == "test_title"
        assert response_data.get("post_content") == "<p>test_content</p>"
        assert response_data.get("board_board_id_pk").get("board_id_pk") == 1
        assert response_data.get("board_board_id_pk").get("board_name") == "공지사항0"
        assert response_data.get("thumbnail_id_pk") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("member_member_pk").get("member_nm") == "Test Member"

    async def test_create_post(self, app_client: AsyncClient):
        print("Post Api CREATE Running...")

        # given
        data = {
            "post_title": "test_title",
            "post_content": "test_content",
            "post_write_time": str(datetime.now()),
            "post_update_time": str(datetime.now()),
            "thumbnail_id_pk": None,
            "board_board_id_pk": 1,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 201
        assert response_data.get("post_title") == "test_title"
        assert response_data.get("post_content") == "<p>test_content</p>"
        assert response_data.get("board_board_id_pk").get("board_id_pk") == 1
        assert response_data.get("board_board_id_pk").get("board_name") == "공지사항0"
        assert response_data.get("thumbnail_id_pk") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("member_member_pk").get("member_nm") == "Test Member"

    async def test_patch_post_by_id(self, app_client: AsyncClient):
        print("Post Api PATCH BY ID Running...")

        # given
        previous_date = datetime(2021, 1, 1, 1, 1, 1)
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=previous_date,
            post_update_date=previous_date,
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )

        data = {
            "post_title": "test_title2",
            "post_update_time": str(datetime.now()),
        }

        # when
        response = await app_client.patch(
            f"{self.url}1", json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("post_title") == "test_title2"
        assert response_data.get("post_update_date") != response_data.get(
            "post_write_date"
        )

        assert response_data.get("post_content") == "<p>test_content</p>"
        assert response_data.get("board_board_id_pk").get("board_id_pk") == 1
        assert response_data.get("board_board_id_pk").get("board_name") == "공지사항0"
        assert response_data.get("thumbnail_id_pk") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("member_member_pk").get("member_nm") == "Test Member"

    async def test_put_post_by_id(self, app_client: AsyncClient):
        print("Post Api PUT BY ID Running...")

        # given
        previous_date = datetime(2021, 1, 1, 1, 1, 1)
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=previous_date,
            post_update_date=previous_date,
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )

        data = {
            "post_title": "test_title2",
            "post_content": "test_content2",
            "post_update_time": str(datetime.now()),
            "thumbnail_id_pk": None,
            "board_board_id_pk": 2,
        }

        # when
        response = await app_client.put(
            f"{self.url}1", json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("post_title") == "test_title2"
        assert response_data.get("post_content") == "<p>test_content2</p>"
        assert response_data.get("post_update_date") != response_data.get(
            "post_write_date"
        )

        assert response_data.get("board_board_id_pk").get("board_id_pk") == 2
        assert response_data.get("board_board_id_pk").get("board_name") == "공지사항1"
        assert response_data.get("thumbnail_id_pk") is None
        assert response_data.get("member_member_pk").get("member_pk") == self.member_id
        assert response_data.get("member_member_pk").get("member_nm") == "Test Member"

    async def test_delete_post_by_id(self, app_client: AsyncClient):
        print("Post Api DELETE BY ID Running...")

        # given
        previous_date = datetime(2021, 1, 1, 1, 1, 1)
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=previous_date,
            post_update_date=previous_date,
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )

        # when
        response = await app_client.delete(f"{self.url}1", headers=self.__make_header())

        # then
        assert response.status_code == 204


class TestPostApiError:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.url = "/hub/api/v2/post/"
        self.member_id = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
        for i in range(5):
            await _create_test_board_at_db(
                board_name=f"공지사항{i}",
                board_layout=0,
                role_role_pk_write_level=4,
                role_role_pk_read_level=2,
                role_role_pk_comment_write_level=random.choice([1, 2, 3, 4, 5]),
            )

    def __make_header(
        self, role_pk: int = 5, user_pk: str = "pkpkpkpkpkpkpkpkpkpkpkpkpkpk"
    ):
        header_data = {
            "HTTP_USER_PK": user_pk,
            "HTTP_ROLE_PK": str(role_pk),
        }
        return header_data

    async def test_create_post_forbidden_role_read(self, app_client: AsyncClient):
        print("Post Api read Forbidden Role Running...")

        # given
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=datetime.now(),
            post_update_date=datetime.now(),
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )

        # when
        response = await app_client.get(
            f"{self.url}1", headers=self.__make_header(role_pk=1)
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("error") == "FORBIDDEN"
        assert response_data.get("errorCode") == "HB-AUTH-002"
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."

    async def test_create_post_forbidden_role_post(self, app_client: AsyncClient):
        print("Post Api create Forbidden Role Running...")

        # given
        data = {
            "post_title": "test_title",
            "post_content": "test_content",
            "post_write_time": str(datetime.now()),
            "post_update_time": str(datetime.now()),
            "thumbnail_id_pk": None,
            "board_board_id_pk": 1,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header(role_pk=3)
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("error") == "FORBIDDEN"
        assert response_data.get("errorCode") == "HB-AUTH-002"
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."

    async def test_create_post_forbidden_role_put(self, app_client: AsyncClient):
        print("Post Api edit Forbidden Role Running...")

        # given
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=datetime.now(),
            post_update_date=datetime.now(),
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )
        data = {
            "post_title": "test_title2",
            "post_update_time": str(datetime.now()),
        }

        # when
        response = await app_client.put(
            f"{self.url}1", json=data, headers=self.__make_header(role_pk=1)
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("error") == "FORBIDDEN"
        assert response_data.get("errorCode") == "HB-AUTH-002"
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."

        data_check_1 = (
            await app_client.get(f"{self.url}1", headers=self.__make_header())
        ).json()

        # when
        response = await app_client.put(
            f"{self.url}1",
            json=data,
            headers=self.__make_header(
                role_pk=3, user_pk="idididididididididididididid"
            ),
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("error") == "FORBIDDEN"
        assert response_data.get("errorCode") == "HB-AUTH-002"
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."

        data_check_2 = (
            await app_client.get(f"{self.url}1", headers=self.__make_header())
        ).json()

        assert data_check_1 == data_check_2

    async def test_create_post_forbidden_role_delete(self, app_client: AsyncClient):
        print("Post Api delete Forbidden Role Running...")

        # given
        content_str = "test_content"
        content = markdown.markdown(content_str)
        await _create_test_post_at_db(
            post_title="test_title",
            post_content=content,
            post_write_date=datetime.now(),
            post_update_date=datetime.now(),
            board_board_id_pk=1,
            member_member_pk=self.member_id,
            thumbnail_id_pk=None,
        )

        # when
        response = await app_client.delete(
            f"{self.url}1",
            headers=self.__make_header(
                role_pk=3, user_pk="idididididididididididididid"
            ),
        )

        # then
        response_data = response.json()
        assert response.status_code == 403
        assert response_data.get("status") == 403
        assert response_data.get("error") == "FORBIDDEN"
        assert response_data.get("errorCode") == "HB-AUTH-002"
        assert response_data.get("message") == "해당 유저의 권한으로는 불가능한 작업입니다."

        data_check = (
            await app_client.get(f"{self.url}1", headers=self.__make_header())
        ).json()

        assert data_check is not None
