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
        # Config.objects.create(config_nm='admin_role_pk', config_val='500', config_pk=500)

    def __make_header(self):
        header_data = {"HTTP_USER_PK": "pkpkpkpkpkpkpkpkpkpkpk", "HTTP_ROLE_PK": "5"}
        return header_data

    async def test_board_get(self, app_client: AsyncClient):
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
            "role_role_pk_write_level": 1,
            "role_role_pk_read_level": 1,
            "role_role_pk_comment_write_level": 1,
        }

    # def test_board_post(self):
    #     print("Board Api POST Running...")
    #
    #     # given
    #     data = {
    #         "board_name": "test1",
    #         "board_layout": 0,
    #         "role_role_pk_write_level": 100,
    #         "role_role_pk_read_level": 100,
    #         "role_role_pk_comment_write_level": 100,
    #     }
    #
    #     # when
    #     respons: Response = self.client.post(
    #         self.url, data=data, **self.__make_header()
    #     )
    #
    #     # then
    #     i = Board.objects.get(board_name="test1")
    #     responses_data = {
    #         "board_id_pk": i.board_id_pk,
    #         "board_name": i.board_name,
    #         "board_layout": i.board_layout,
    #         "role_role_pk_write_level": i.role_role_pk_write_level.role_pk,
    #         "role_role_pk_read_level": i.role_role_pk_read_level.role_pk,
    #         "role_role_pk_comment_write_level": i.role_role_pk_comment_write_level.role_pk,
    #     }
    #     self.assertEqual(respons.status_code, status.HTTP_201_CREATED)
    #     self.assertJSONEqual(respons.content, responses_data)
    #
    # def test_board_patch_by_id(self):
    #     print("Board Api PATCH BY ID Running...")
    #     # given
    #     Board.objects.create(
    #         board_name="공지사항1",
    #         board_layout=0,
    #         role_role_pk_write_level=Role.objects.get(role_pk=0),
    #         role_role_pk_read_level=Role.objects.get(role_pk=0),
    #         role_role_pk_comment_write_level=Role.objects.get(role_pk=0),
    #     )
    #     Board.objects.create(
    #         board_name="공지사항2",
    #         board_layout=0,
    #         role_role_pk_write_level=Role.objects.get(role_pk=0),
    #         role_role_pk_read_level=Role.objects.get(role_pk=0),
    #         role_role_pk_comment_write_level=Role.objects.get(role_pk=0),
    #     )
    #     patch_data = {"board_name": "자유게시판", "role_role_pk_write_level": 100}
    #
    #     # when
    #     target = "공지사항1"
    #     instance = Board.objects.filter(board_name=target)[0]
    #     key = instance.board_id_pk
    #     respons: Response = self.client.patch(
    #         f"{self.url}{key}/", data=patch_data, **self.__make_header()
    #     )
    #
    #     # then
    #     return_data = {
    #         "board_id_pk": key,
    #         "board_name": "자유게시판",
    #         "board_layout": 0,
    #         "role_role_pk_write_level": 100,
    #         "role_role_pk_read_level": 0,
    #         "role_role_pk_comment_write_level": 0,
    #     }
    #     self.assertEqual(respons.status_code, status.HTTP_200_OK)
    #     self.assertJSONEqual(respons.content, return_data)
    #
    # def test_board_delete_by_id(self):
    #     print("Board Api DELETE BY ID Running...")
    #     # given
    #     Board.objects.create(
    #         board_name="공지사항1",
    #         board_layout=0,
    #         role_role_pk_write_level=Role.objects.get(role_pk=100),
    #         role_role_pk_read_level=Role.objects.get(role_pk=101),
    #         role_role_pk_comment_write_level=Role.objects.get(role_pk=101),
    #     )
    #     Board.objects.create(
    #         board_name="공지사항2",
    #         board_layout=0,
    #         role_role_pk_write_level=Role.objects.get(role_pk=100),
    #         role_role_pk_read_level=Role.objects.get(role_pk=100),
    #         role_role_pk_comment_write_level=Role.objects.get(role_pk=101),
    #     )
    #
    #     # when
    #     target = "공지사항1"
    #     instance = Board.objects.filter(board_name=target)[0]
    #     key = instance.board_id_pk
    #     respons: Response = self.client.delete(
    #         f"{self.url}{key}/", **self.__make_header()
    #     )
    #
    #     # then
    #     self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)


# class BoardApiError(APITestCase):
#     databases = "__all__"
#
#     def setUp(self):
#         self.url = "/hub/api/v1/board/"
#
#     @classmethod
#     def setUpTestData(cls):
#         Role.objects.create(role_pk=0, role_nm="ROLE_GUEST")
#         Role.objects.create(role_pk=1, role_nm="ROLE_USER0")
#         Role.objects.create(role_pk=2, role_nm="ROLE_USER1")
#         Role.objects.create(role_pk=3, role_nm="ROLE_ADMIN")
#         Role.objects.create(role_pk=4, role_nm="ROLE_DEV")
#
#         Config.objects.create(config_nm="admin_role_pk", config_val="4")
#
#     def __make_header(self):
#         header_data = {"HTTP_USER_PK": "pkpkpkpkpkpkpkpkpkpkpk", "HTTP_ROLE_PK": 5}
#         return header_data
#
#     def test_board_get_by_id_not_found(self):
#         print("Board Api GET BY ID not found Running...")
#
#         # given
#         Board.objects.create(
#             board_name="공지사항1",
#             board_layout=0,
#             role_role_pk_write_level=Role.objects.get(role_pk=1),
#             role_role_pk_read_level=Role.objects.get(role_pk=1),
#             role_role_pk_comment_write_level=Role.objects.get(role_pk=1),
#         )
#
#         # when
#         respons: Response = self.client.get(f"{self.url}1000/", **self.__make_header())
#
#         # then
#         return_data = {"detail": "Not found."}
#         self.assertEqual(respons.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertJSONEqual(respons.content, return_data)
#
#     def test_board_post_already_exist(self):
#         print("Board Api POST already exist Running...")
#
#         # given
#         Board.objects.create(
#             board_name="공지사항1",
#             board_layout=0,
#             role_role_pk_write_level=Role.objects.get(role_pk=0),
#             role_role_pk_read_level=Role.objects.get(role_pk=0),
#             role_role_pk_comment_write_level=Role.objects.get(role_pk=0),
#         )
#
#         data = {
#             "board_name": "공지사항1",
#             "board_layout": 0,
#             "role_role_pk_write_level": 0,
#             "role_role_pk_read_level": 20,
#             "role_role_pk_comment_write_level": 0,
#         }
#
#         # when
#         respons: Response = self.client.post(
#             self.url, data=data, **self.__make_header()
#         )
#
#         # then
#         responses_data = {
#             "board_name": ["board with this board name already exists."],
#             "role_role_pk_read_level": ['Invalid pk "20" - object does not exist.'],
#         }
#         self.assertEqual(respons.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertJSONEqual(respons.content, responses_data)
#
#     def test_board_post_required(self):
#         print("Board Api POST already exist not found Running...")
#
#         # given
#
#         data = {
#             "board_name": "공지사항1",
#             "board_layout": 0,
#         }
#
#         # when
#         respons: Response = self.client.post(
#             self.url, data=data, **self.__make_header()
#         )
#
#         # then
#         responses_data = {
#             "role_role_pk_write_level": ["This field is required."],
#             "role_role_pk_read_level": ["This field is required."],
#             "role_role_pk_comment_write_level": ["This field is required."],
#         }
#         self.assertEqual(respons.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertJSONEqual(respons.content, responses_data)
