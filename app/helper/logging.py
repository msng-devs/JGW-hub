# --------------------------------------------------------------------------
# Backend Application의 logger을 정의하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging
import logging.handlers

from app.core.settings import AppSettings


LOGGING_FORMAT = (
    "[%(levelname)1.1s "
    "%(asctime)s "
    "P%(process)d "
    "%(threadName)s "
    "%(module)s:%(lineno)d] "
    "%(message)s"
)


def init_logger(root_logger_name: str, app_settings: AppSettings) -> logging.Logger:
    app_logger_level = (
        logging.DEBUG if app_settings.LOGGING_DEBUG_LEVEL else logging.INFO
    )

    logging_file = app_settings.LOG_FILE_PATH
    error_logging_file = logging_file.replace(".log", "_errors.log")

    logging.basicConfig(
        level=app_logger_level, format=LOGGING_FORMAT, filename=logging_file
    )

    # Access log - HTTP status, 로직 Exception 등이 포함됩니다.
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.setLevel(app_logger_level)
    file_handler = logging.FileHandler(logging_file)
    file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    uvicorn_logger.addHandler(file_handler)

    # Error log - Jaram Groupware 에러 로그 규격에 맞는 에러 로그가 포함됩니다.
    uvicorn_error_logger = logging.getLogger("hub_error_logger")
    error_file_handler = logging.FileHandler(error_logging_file)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    uvicorn_error_logger.addHandler(error_file_handler)

    return logging.getLogger(root_logger_name)
