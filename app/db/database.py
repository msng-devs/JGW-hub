# --------------------------------------------------------------------------
# Database 연결에 사용되는 로직을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.settings import AppSettings


settings = AppSettings()

SQLALCHEMY_DATABASE_URL: str = str(settings.DATABASE_URI)
engine_options = settings.DATABASE_OPTIONS

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, **engine_options)


# Dependency
async def get_db():
    db = None
    try:
        db = AsyncSession(bind=engine)
        yield db
    finally:
        await db.close()
