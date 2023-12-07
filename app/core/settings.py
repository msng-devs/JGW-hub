# --------------------------------------------------------------------------
# Backend Application의 설정을 관리하는 파일입니다.
#
# 배포 환경에서는 JGW-Secret 저장소에 있는 값을 바탕으로 설정을 관리하며,
# 테스트 환경에서는 로컬에 있는 .env 파일을 통해 설정을 관리합니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from __future__ import annotations

from typing import Any, Dict

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    SECRET_KEY: str = Field(
        default="example_secret_key_WoW",
        description="Secret key to be used for issuing HMAC tokens.",
    )
    DEBUG_MODE: bool = Field(
        default=True,
        description="If True, run the server in debug mode.",
    )
    LOGGING_DEBUG_LEVEL: bool = Field(
        default=True,
        description="True: DEBUG mode, False:: INFO mode",
    )
    LOG_FILE_PATH: str = Field(
        default="logs/hub.log",
        description="Log file path",
    )
    DATABASE_URI: AnyUrl = Field(
        default="mysql+aiomysql://bnbong:password@localhost:3306/JGW_TEST",
        description="MariaDB connection URI.",
    )
    DATABASE_OPTIONS: Dict[str, Any] = Field(
        default={
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 300,
            "pool_pre_ping": True,
        },
        description="MariaDB option to create a connection.",
    )

    model_config = SettingsConfigDict(env_file=".env")
