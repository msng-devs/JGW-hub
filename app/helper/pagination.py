# --------------------------------------------------------------------------
# 자람 허브의 페이징 처리를 위한 헬퍼 함수 및 스키마들을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import List, Generic, TypeVar, Optional

from pydantic import Field, AnyHttpUrl
from pydantic.generics import GenericModel
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middlewares import request_object


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    count: int = Field(..., title="Count", description="불러온 아이템 전체 개수를 나타냅니다.")
    next: Optional[AnyHttpUrl] = Field(
        None,
        title="Next",
        description="데이터를 불러올 다음 페이지의 URL을 나타냅니다.",
    )
    previous: Optional[AnyHttpUrl] = Field(
        None,
        title="Previous",
        description="데이터를 불러왔던 이전 페이지의 URL을 나타냅니다.",
    )
    results: List[T] = Field(
        ...,
        title="Results",
        description="불러온 아이템들의 정보들을 리스트로 나타냅니다.",
    )


class Paginator:
    def __init__(self, session: AsyncSession, query: Select, page: int, per_page: int):
        self.session = session
        self.query = query
        self.page = page
        self.page_size = per_page
        self.limit = per_page * page
        self.offset = (page - 1) * per_page
        self.request = request_object.get()
        # computed later
        self.number_of_pages = 0
        self.next = ""
        self.previous = ""

    def _get_next_page(self) -> Optional[str]:
        if self.page >= self.number_of_pages:
            return
        url = self.request.url.include_query_params(page=self.page + 1)
        return str(url)

    def _get_previous_page(self) -> Optional[str]:
        if self.page == 1 or self.page > self.number_of_pages + 1:
            return
        url = self.request.url.include_query_params(page=self.page - 1)
        return str(url)

    async def get_response(self) -> dict:
        return {
            "count": await self._get_total_count(),
            "next": self._get_next_page(),
            "previous": self._get_previous_page(),
            "results": [
                todo
                for todo in await self.session.scalars(
                    self.query.limit(self.limit).offset(self.offset)
                )
            ],
        }

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.page_size
        quotient = count // self.page_size
        return quotient if not rest else quotient + 1

    async def _get_total_count(self) -> int:
        from sqlalchemy import select

        count = await self.session.scalar(
            select(func.count()).select_from(self.query.subquery())
        )
        self.number_of_pages = self._get_number_of_pages(count)
        return count


async def paginate(db: AsyncSession, query: Select, page: int, page_size: int) -> dict:
    paginator = Paginator(db, query, page, page_size)
    return await paginator.get_response()
