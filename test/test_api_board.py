# --------------------------------------------------------------------------
# Board의 API router을 테스트하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import random
import pytest_asyncio

from httpx import AsyncClient

from test.conftest import test_engine, AsyncSession

from app.db.models import Board


async def _create_test_board_at_db(
    board_name: str,
    board_layout: int,
    role_role_pk_write_level: int,
    role_role_pk_read_level: int,
    role_role_pk_comment_write_level: int,
):
    async with AsyncSession(bind=test_engine) as session:
        test_board = Board(
            name=board_name,
            layout=board_layout,
            write_level=role_role_pk_write_level,
            read_level=role_role_pk_read_level,
            comment_write_level=role_role_pk_comment_write_level,
        )
        session.add(test_board)
        await session.commit()
        await session.refresh(test_board)


class TestBoardApi:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, app_client: AsyncClient):
        self.url = "/hub/api/v2/board/"

    def __make_header(self):
        header_data = {
            "HTTP_USER_PK": "pkpkpkpkpkpkpkpkpkpkpkpkpkpk",
            "HTTP_ROLE_PK": "5",
        }
        return header_data

    async def test_get_boards(self, app_client: AsyncClient):
        print("Board Api GET ALL Pagination Running...")

        # given
        for i in range(20):
            await _create_test_board_at_db(
                board_name=f"공지사항{i}",
                board_layout=0,
                role_role_pk_write_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_read_level=random.choice([1, 2, 3, 4, 5]),
                role_role_pk_comment_write_level=random.choice([1, 2, 3, 4, 5]),
            )

        # when
        headers = self.__make_header()
        response = await app_client.get(self.url, params={"page": 1}, headers=headers)

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("count") == 20
        assert response_data.get("next") == "http://test/hub/api/v2/board/?page=2"
        assert response_data.get("previous") is None
        assert len(response_data.get("results")) == 10
        assert response_data.get("results")[0].get("board_name") == "공지사항0"

    async def test_get_board_by_id(self, app_client: AsyncClient):
        print("Board Api GET BY ID Running...")

        # given
        await _create_test_board_at_db(
            board_name="공지사항1",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )
        await _create_test_board_at_db(
            board_name="공지사항2",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )

        # when
        response = await app_client.get(f"{self.url}1", headers=self.__make_header())

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data == {
            "board_id_pk": 1,
            "board_name": "공지사항1",
            "board_layout": 0,
            "role_role_pk_write_level": {"role_id_pk": 1, "role_name": "ROLE_GUEST"},
            "role_role_pk_read_level": {"role_id_pk": 1, "role_name": "ROLE_GUEST"},
            "role_role_pk_comment_write_level": {
                "role_id_pk": 1,
                "role_name": "ROLE_GUEST",
            },
        }

    async def test_create_board(self, app_client: AsyncClient):
        print("Board Api POST Running...")

        # given
        data = {
            "board_name": "test1",
            "board_layout": 0,
            "role_role_pk_write_level": 1,
            "role_role_pk_read_level": 1,
            "role_role_pk_comment_write_level": 1,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 201
        assert response_data == {
            "board_id_pk": 1,
            "board_name": "test1",
            "board_layout": 0,
            "role_role_pk_write_level": {"role_id_pk": 1, "role_name": "ROLE_GUEST"},
            "role_role_pk_read_level": {"role_id_pk": 1, "role_name": "ROLE_GUEST"},
            "role_role_pk_comment_write_level": {
                "role_id_pk": 1,
                "role_name": "ROLE_GUEST",
            },
        }

    async def test_patch_board_by_id(self, app_client: AsyncClient):
        print("Board Api PATCH BY ID Running...")

        # given
        await _create_test_board_at_db(
            board_name="공지사항1",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )
        await _create_test_board_at_db(
            board_name="공지사항2",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )
        patch_data = {"board_name": "자유게시판", "role_role_pk_write_level": 3}

        # when
        response = await app_client.patch(
            f"{self.url}1", json=patch_data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data == {
            "board_id_pk": 1,
            "board_name": "자유게시판",
            "board_layout": 0,
            "role_role_pk_write_level": {"role_id_pk": 3, "role_name": "ROLE_USER1"},
            "role_role_pk_read_level": {"role_id_pk": 1, "role_name": "ROLE_GUEST"},
            "role_role_pk_comment_write_level": {
                "role_id_pk": 1,
                "role_name": "ROLE_GUEST",
            },
        }

    async def test_put_board_by_id(self, app_client: AsyncClient):
        print("Board Api PUT BY ID Running...")

        # given
        await _create_test_board_at_db(
            board_name="공지사항1",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )
        await _create_test_board_at_db(
            board_name="공지사항2",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )
        put_data = {
            "board_name": "자유게시판",
            "board_layout": 0,
            "role_role_pk_write_level": 3,
            "role_role_pk_read_level": 4,
            "role_role_pk_comment_write_level": 5,
        }

        # when
        response = await app_client.put(
            f"{self.url}1", json=put_data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 200
        assert response_data == {
            "board_id_pk": 1,
            "board_name": "자유게시판",
            "board_layout": 0,
            "role_role_pk_write_level": {"role_id_pk": 3, "role_name": "ROLE_USER1"},
            "role_role_pk_read_level": {"role_id_pk": 4, "role_name": "ROLE_ADMIN"},
            "role_role_pk_comment_write_level": {
                "role_id_pk": 5,
                "role_name": "ROLE_DEV",
            },
        }

    async def test_delete_board_by_id(self, app_client: AsyncClient):
        print("Board Api DELETE BY ID Running...")

        # given
        await _create_test_board_at_db(
            board_name="공지사항1",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )
        await _create_test_board_at_db(
            board_name="공지사항2",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )

        # when
        response = await app_client.delete(f"{self.url}1", headers=self.__make_header())

        # then
        assert response.status_code == 204

        # deletion check
        response_check = await app_client.get(
            f"{self.url}1", headers=self.__make_header()
        )
        response_data = response_check.json()
        assert response_check.status_code == 404
        assert response_data.get("status") == 404
        assert response_data.get("error") == "NOT_FOUND"
        assert response_data.get("errorCode") == "HB-001"


class TestBoardApiError:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, app_client: AsyncClient):
        self.url = "/hub/api/v2/board/"
        # Config.objects.create(config_nm='admin_role_pk', config_val='500', config_pk=500)

    def __make_header(self):
        header_data = {"HTTP_USER_PK": "pkpkpkpkpkpkpkpkpkpkpk", "HTTP_ROLE_PK": "5"}
        return header_data

    async def _create_test_board_api(
        self,
        app_client: AsyncClient,
        board_name: str,
        board_layout: int,
        role_role_pk_write_level: int,
        role_role_pk_read_level: int,
        role_role_pk_comment_write_level: int,
    ):
        data = {
            "board_name": board_name,
            "board_layout": board_layout,
            "role_role_pk_write_level": role_role_pk_write_level,
            "role_role_pk_read_level": role_role_pk_read_level,
            "role_role_pk_comment_write_level": role_role_pk_comment_write_level,
        }
        response = await app_client.post(
            "/hub/api/v2/board/", json=data, headers=self.__make_header()
        )
        return response

    async def test_board_get_by_id_not_found(self, app_client: AsyncClient):
        print("Board Api GET BY ID not found Running...")

        # given
        await _create_test_board_at_db(
            board_name="공지사항1",
            board_layout=0,
            role_role_pk_write_level=1,
            role_role_pk_read_level=1,
            role_role_pk_comment_write_level=1,
        )

        # when
        response = await app_client.get(f"{self.url}1000", headers=self.__make_header())

        # then
        response_data = response.json()
        assert response.status_code == 404
        assert response_data.get("status") == 404
        assert response_data.get("error") == "NOT_FOUND"
        assert response_data.get("errorCode") == "HB-001"

    async def test_board_post_already_exist(self, app_client: AsyncClient):
        print("Board Api POST already exist Running...")

        # given
        await self._create_test_board_api(
            app_client=app_client,
            board_name="공지사항1",
            board_layout=0,
            role_role_pk_write_level=0,
            role_role_pk_read_level=0,
            role_role_pk_comment_write_level=0,
        )

        data = {
            "board_name": "공지사항1",
            "board_layout": 0,
            "role_role_pk_write_level": 0,
            "role_role_pk_read_level": 2,
            "role_role_pk_comment_write_level": 0,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        assert response.status_code == 400
        assert response_data.get("status") == "BAD_REQUEST"
        assert response_data.get("message") == "데이터베이스에 중복된 값이 존재합니다."
        assert response_data.get("errorCode") == "HB-004"

    async def test_board_post_required(self, app_client: AsyncClient):
        print("Board Api POST already exist not found Running...")

        # given
        data = {
            "board_name": "공지사항1",
            "board_layout": 0,
        }

        # when
        response = await app_client.post(
            self.url, json=data, headers=self.__make_header()
        )

        # then
        response_data = response.json()
        err_detail = response_data.get("detail")
        assert response.status_code == 422
        assert err_detail[0].get("type") == "missing"
        assert err_detail[0].get("msg") == "Field required"
        assert err_detail[0].get("loc") == ["body", "role_role_pk_write_level"]

        assert err_detail[1].get("type") == "missing"
        assert err_detail[1].get("msg") == "Field required"
        assert err_detail[1].get("loc") == ["body", "role_role_pk_read_level"]

        assert err_detail[2].get("type") == "missing"
        assert err_detail[2].get("msg") == "Field required"
        assert err_detail[2].get("loc") == ["body", "role_role_pk_comment_write_level"]
