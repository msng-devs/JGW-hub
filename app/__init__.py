# --------------------------------------------------------------------------
# FastAPI Application을 생성하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging

from setuptools_scm import get_version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import engine
from app.db.models import Base
from app.routers import router
from app.core.settings import AppSettings
from app.core.middlewares import PaginationMiddleware, RouterLoggingMiddleware
from app.utils.documents import add_description_at_api_tags
from app.helper.logging import init_logger as _init_logger


try:
    __version__ = get_version(
        root="../", relative_to=__file__
    )  # git version (dev version)
except LookupError:
    __version__ = "2.0.0"  # production version


logger = logging.getLogger(__name__)


def init_logger(app_settings: AppSettings) -> None:
    _init_logger(f"fastapi-backend@{__version__}", app_settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Application startup")
        logger.info("Create connection and setting up database")
        async with engine.begin() as conn:
            logger.info("DB connected with url %s", engine.url)
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        logger.info("Application shutdown")


def create_app(app_settings: AppSettings) -> FastAPI:
    """FastAPI Application을 생성하는 핵심 메서드입니다.

    Jaram Groupware의 모든 서비스는 Gateway를 통해 프록시로 접근을 하기 때문에 FastAPI application을 선언할 때
    root_path를 설정하여 /hub/api/v2/ 경로를 root_path로 설정하여 OpenAPI 문서를 랜더링하게 해야하지만,
    배포 환경에서 API 문서 노출을 최소화 하기 위해 In-Application에서 문서를 랜더링하지 못하도록 설정하였습니다.

    **미들웨어**
     - CORSMiddleware : CORS 설정을 위한 미들웨어입니다. CORS 관련 설정은 모두 Gateway에서 담당하기 때문에 Allow-Origin을 모두 허용합니다.
     - PaginationMiddleware : Pagination을 위한 미들웨어입니다.
     - RouterLoggingMiddleware : 각 API 요청에 대한 로깅을 위한 미들웨어입니다. 현재 자람 허브 v2 앱의 로그를 기록하는 서비스는
                                 Uvicorn, RouterLoggingMiddleware 두가지 입니다.
                                 Uvicorn은 각 HTTP 요청에 대한 요약 정보 및 내부 로직 에러 로깅을 담당하고,
                                 RouterLoggingMiddleware는 각 HTTP 요청에 대한 상세 정보 로깅을 담당합니다.
    """
    logger.info(
        "FastAPI application running in DEBUG mode: %s", app_settings.DEBUG_MODE
    )
    app = FastAPI(
        title="자람 허브 API v2",
        description="FastAPI로 재작성된 자람 허브 API 입니다.",
        version=__version__,
        lifespan=lifespan,
        docs_url="/hub/api/v2/docs",
        redoc_url="/hub/api/v2/redoc",
    )

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PaginationMiddleware)
    app.add_middleware(RouterLoggingMiddleware, logger=logger)

    app.include_router(router)

    add_description_at_api_tags(app)

    return app