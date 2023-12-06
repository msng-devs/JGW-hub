# --------------------------------------------------------------------------
# 자람 허브 서비스에 사용되는 상수 모음집입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Final

RANDOM_STRING_CHARS: Final = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)

BOARD_MAX_PAGE_SIZE: Final = 150
BOARD_MIN_PAGE_SIZE: Final = 1
BOARD_DEFAULT_PAGE_SIZE: Final = 10

POST_MAX_PAGE_SIZE: Final = 100
POST_MIN_PAGE_SIZE: Final = 1
POST_DEFAULT_PAGE_SIZE: Final = 10

IMAGE_MAX_PAGE_SIZE: Final = 500
IMAGE_MIN_PAGE_SIZE: Final = 1
IMAGE_DEFAULT_PAGE_SIZE: Final = 50

COMMENT_MAX_PAGE_SIZE: Final = 25
COMMENT_MIN_PAGE_SIZE: Final = 1
COMMENT_DEFAULT_PAGE_SIZE: Final = 10
