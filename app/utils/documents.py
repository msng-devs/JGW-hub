# --------------------------------------------------------------------------
# OpenAPI generator가 읽을 API 문서 내용을 정의하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from fastapi import FastAPI


def add_description_at_api_tags(app: FastAPI):
    tag_descriptions = {
        # add application's description here
        "board": "게시판 카테고리 API 입니다. \n\n현재 자람 허브에서는 3개의 게시판만 운용하고 있으나, 추후 게시판 확장을 염두하여 API가 설계되었습니다.",
        "post": "게시글 API 입니다.",
    }

    # OpenAPI 태그별 description 생성
    openapi_tags = [
        {"name": tag, "description": desc} for tag, desc in tag_descriptions.items()
    ]

    if app.openapi_tags:
        app.openapi_tags.extend(openapi_tags)
    else:
        app.openapi_tags = openapi_tags
