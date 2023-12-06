# --------------------------------------------------------------------------
# pytest의 configuration을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import uvloop
import pytest
import pytest_asyncio

from typing import Iterator, AsyncIterator
from asyncio import AbstractEventLoop

from asgi_lifespan import LifespanManager

from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.db.database import get_db
from app.db.models import Base, Role
from app.core.settings import AppSettings
from app import create_app


app_settings = AppSettings(_env_file=".env")


test_engine = create_async_engine(
    str(app_settings.DATABASE_URI), **app_settings.DATABASE_OPTIONS
)


async def get_test_db():
    test_session_local = AsyncSession(bind=test_engine)  # type: ignore
    try:
        yield test_session_local
    finally:
        await test_session_local.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_db():
    print("initialize test database")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def event_loop() -> Iterator[AbstractEventLoop]:
    loop = uvloop.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def app_client() -> AsyncIterator[AsyncClient]:
    app = create_app(app_settings)
    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(
        app=app, base_url="http://test"
    ) as app_client, LifespanManager(app):
        yield app_client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_data(init_db):
    print("initialize test database")
    async with AsyncSession(bind=test_engine) as session:
        roles = [
            Role(id=1, name="ROLE_GUEST"),
            Role(id=2, name="ROLE_USER0"),
            Role(id=3, name="ROLE_USER1"),
            Role(id=4, name="ROLE_ADMIN"),
            Role(id=5, name="ROLE_DEV"),
        ]
        session.add_all(roles)
        await session.commit()
