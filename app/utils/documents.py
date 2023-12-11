# --------------------------------------------------------------------------
# OpenAPI generator가 읽을 API 문서 내용을 정의하는 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from fastapi import FastAPI

from app.helper.exceptions import ExceptionSchema


def add_description_at_api_tags(app: FastAPI):
    tag_descriptions = {
        # add application's description here
        "board": "게시판 카테고리 API 입니다. \n\n현재 자람 허브에서는 3개의 게시판만 운용하고 있으나, 추후 게시판 확장을 염두하여 API가 설계되었습니다.",
        "post": "게시글 API 입니다.",
        "comment": "댓글 API 입니다.",
    }

    # OpenAPI 태그별 description 생성
    openapi_tags = [
        {"name": tag, "description": desc} for tag, desc in tag_descriptions.items()
    ]

    if app.openapi_tags:
        app.openapi_tags.extend(openapi_tags)
    else:
        app.openapi_tags = openapi_tags


# --------------------------------------------------------------------------
# Descriptions contents for API documentations
# --------------------------------------------------------------------------
general_api_description = """
FastAPI로 재작성된 자람 허브 API v2 문서입니다.

## 개요
자람 허브 API v2는 기존 Django로 작성되었던 자람 허브 API를 FastAPI로 재작성한 API입니다.
기존 자람 허브 API 문서에 있는 기능들을 url을 v1에서 v2로 변경하여 모두 그대로 사용이 가능합니다. 

(예: /hub/api/v1/board/ -> /hub/api/v2/board/)


## V2 변경 사항

1. **Comment API에서 게시물의 모든 댓글을 불러오는 기능의 응답 데이터 변경 -> reply 필드 삭제.**

    변경 내용된 response 예시는 다음과 같습니다.
    
    - 기존 응답 데이터
    ```json
        {
          "count": 123,
          "next": "https://api.jaramgroupware.cloud/hub/api/v1/post/?page=4",
          "previous": "https://api.jaramgroupware.cloud/hub/api/v1/post/?page=2",
          "results": [
            {
              "comment_id": 1,
              "comment_depth": 0,
              "comment_content": "댓글댓글~~~",
              "comment_write_time": "2023-01-04T21:39:20.619843",
              "comment_update_time": "2023-01-04T21:39:20.619843",
              "comment_delete": 0,
              "post_post_id_pk": 1,
              "member_member_pk": {
                "member_pk": "nfkOJDM8492KKMKndods9_@IiNJJjd",
                "member_nm": "이름이름"
              },
              "reply": [
                {
                  "comment_id": 2,
                  "comment_depth": 1,
                  "comment_content": "답변댓글",
                  "comment_write_time": "2023-01-04T21:39:20.619843",
                  "comment_update_time": "2023-01-04T21:39:20.619843",
                  "comment_delete": 0,
                  "post_post_id_pk": 1,
                  "member_member_pk": {
                    "member_pk": "nfkOJDM8492KKMKndods9_@IiNJJjd",
                    "member_nm": "이름이름"
                  },
                  "reply": {}
                }
              ]
            }
          ]
        }
    ```
    - 변경된 응답 데이터
    ```json
        {
          "count": 123,
          "next": "https://api.jaramgroupware.cloud/hub/api/v1/post/?page=4",
          "previous": "https://api.jaramgroupware.cloud/hub/api/v1/post/?page=2",
          "results": [
            {
              "comment_id": 1,
              "comment_depth": 0,
              "comment_content": "댓글댓글~~~",
              "comment_write_time": "2023-10-23T16:08:15",
              "comment_update_time": "2023-10-23T16:08:15",
              "comment_delete": 0,
              "post_post_id_pk": 1,
              "member_member_pk": {
                "member_pk": "nfkOJDM8492KKMKndods9_@IiNJJjd",
                "member_nm": "이름이름"
              },
              "comment_comment_id_ref": 0
            },
            {
              "comment_id": 2,
              "comment_depth": 1,
              "comment_content": "답변댓글",
              "comment_write_time": "2023-10-23T16:08:15",
              "comment_update_time": "2023-10-23T16:08:15",
              "comment_delete": 0,
              "post_post_id_pk": 1,
              "member_member_pk": {
                "member_pk": "nfkOJDM8492KKMKndods9_@IiNJJjd",
                "member_nm": "이름이름"
              },
              "comment_comment_id_ref": 1
            }
          ]
        }
    ```
    
    기존 v1 url : /hub/v1/comment/?page=<page_id>에서는 reply 필드에 특정 댓글의 답글 댓글까지 같이 출력을 하는 형태였으나, \
    이는 답변 댓글이 중복으로 출력되어 같은 댓글이 두번이나 출력될 우려가 있었습니다.
    
    따라서 v2에서는 reply 필드를 삭제하고, comment_comment_id_ref 필드를 추가하여 답변 댓글의 부모 댓글의 id를 출력하도록 변경하였습니다.
    
    변경 사항에 맞춰서 답변 댓글을 출력하는 로직을 수정해주셔야 합니다. (예: 댓글에 답글 부분을 담을 리스트를 선언한 후, \
    comment_comment_id_ref에 값이 있는 경우 해당 댓글을 리스트에 추가 -> 댓글 컨테이너에 render하는 방식으로 구현)
    
2. **url 끝부분에 슬래시 '/'를 붙이는 패턴을 RESTful하게 수정 -> (예: 기존 v1 url : /hub/v1/board/1/ -> v2 url : /hub/v2/board/1)**

    RESTful API에서 '/'는 계층을 구분하기 위해 사용되는 문자입니다.
    
    따라서 후행 슬래시(/)는 의미가 전혀 없고 혼란을 야기할 수 있기 때문에 제거하였습니다.
    
    쿼리 파라미터를 넣을 때에도 기존 v1에서는 /hub/v1/board/?page=1과 같이 ? 앞에 슬래시를 붙여서 쿼리 파라미터를 넣었지만, \
    v2에서는 /hub/v2/board?page=1과 같이 슬래시를 붙이지 않고 쿼리 파라미터를 넣어야 합니다.
    
    클라이언트 개발 시 서버로 url 요청을 보낼 때 슬래시에 유의하여 주시기 바랍니다.


## API 보안 규칙
자람 허브 API를 포함한 Jaram Groupware의 모든 Back-end 서비스는 Gateway를 통해 요청을 보내는 유저의 정보를 검증합니다.

Jaram Groupware의 서비스로 Request를 보낼 때 유저의 정보를 명시하기 위해서는 다음과 같이 Request Header에 유저 token을 명시해야합니다.

```json
{
    "Authorization": "Bearer <유저의 token>"
}
```

**Jaram Groupware에서 사용하는 유저 token에 대한 정보는 자람 그룹웨어 노션 Docs에 기재된 'Jaram Groupware Applications' 중 \
'Token - 자람 허브 토큰 서비스'를 참고해주세요.**

Gateway를 거쳐 유저 검증이 완료된 Request는 모두 다음과 같은 형식의 payload를 Request Header 메타데이터에 포함하게 됩니다.

```json
{
  "user_pk": "유저의 uid",
  "role_pk": "유저의 권한 pk",
}
```

위의 Request Header 메타데이터는 **Request Header에 유저 token이 포함되어 있다면** 자동으로 추가되며, \
자람 허브 API 문서에 HEADER PARAMETETS부분에 명시되어 있는 값들과 일치합니다.

**따라서, API 개발 테스트 상황이 아닌 실제 라이브 서버에서 요청을 보낼 때에는 HEADER PARAMETETS에 명시된 값들을 Request Header에 포함시키는 것이 아니라, \
유저 token만 포함시켜서 Request를 보내면 됩니다.**

Jaram Groupware의 서비스들에는 RBAC(Role Based Access Control)가 적용되어 있습니다.

자람 허브 API는 헤더에 포함된 role_pk 정보를 바탕으로 유저의 권한을 확인하고, 유저가 요청한 API에 대한 권한이 있는지 검증하는 로직이 존재합니다.

유저가 가질 수 있는 Role(권한)은 다음과 같습니다.

| Role name | Role description |
| --- | --- |
| ROLE_GUEST | 게스트 유저 |
| ROLE_USER0 | 자람 수습회원, 준회원 |
| ROLE_USER1 | 자람 정회원 |
| ROLE_ADMIN | 자람 허브 관리자 |
| ROLE_DEV | 자람 허브 개발자 |

Gateway가 프록시하는 모든 Jaram Groupware 서비스는 각 endpoint 별로 유저 인증 필요 여부 및 인증 정보 범위를 조절할 수 있습니다.
배포 후 Gateway-Storm 서비스를 통해 서비스의 endpoint에 대한 유저 인증 여부 및 인증 정보 범위 설정 방법은 노션 문서를 참고해주세요.

만약 자람 허브의 특정 endpoint가 유저의 특정 권한 이상을 요구하는 경우, 설명 상단에 'RBAC - <유저의 권한>'으로 표기되어 있습니다.

그 외 요청에 유저 권한이 없는 경우는 'RBAC - ALL'로 표기되어 있습니다.

특별한 경우(예: 게시글 작성자 본인이거나 관리자만 게시글 수정 가능)에는 'RBAC - AUTH'로 표기되어 있습니다.
"""

# --------------------------------------------------------------------------
# Board API endpoints documentations
# --------------------------------------------------------------------------
read_boards_description = """
RBAC - ALL

모든 게시판 목록을 가져옵니다.
"""

read_board_description = """
RBAC - ALL

지정한 게시판의 데이터를 가져옵니다.
"""

create_board_description = """
RBAC - ROLE_ADMIN

새로운 게시판을 생성합니다.
"""

update_board_description = """
RBAC - ROLE_ADMIN

지정한 게시판의 데이터를 수정합니다. (전체, 부분 업데이트를 지원합니다)
"""

delete_board_description = """
RBAC - ROLE_ADMIN

지정한 게시판을 삭제합니다.
"""

# --------------------------------------------------------------------------
# Post API endpoints documentations
# --------------------------------------------------------------------------
read_posts_description = """
RBAC - ALL

게시글 목록을 가져옵니다.

결과로 가져오는 게시글은 content가 500자로 제한되어 리턴됩니다.

모든 내용을 가져오려면 특정 게시글 가져오기 API를 사용해야합니다.
"""

read_post_description = """
RBAC - AUTH

지정한 게시글의 데이터를 가져옵니다.

요청한 유저의 권한이 가져오려는 게시글이 속한 게시판의 읽기 레벨과 같거나 더 높아야 글 읽기가 가능합니다.

**Admin은 게시판의 읽기 권한과 상관 없이 글 읽기가 가능합니다.**
"""

create_post_description = """
RBAC - AUTH

새로운 게시글을 생성합니다. 

쓰기 요청한 유저의 권한이 작성하려는 게시판의 쓰기 레벨과 같거나 더 높아야 글 작성이 가능합니다.

**Admin은 게시판의 쓰기 권한과 상관 없이 글 작성이 가능합니다.**
"""

update_post_description = """
RBAC - AUTH

지정한 게시글의 데이터를 수정합니다. (전체, 부분 업데이트를 지원합니다) 

요청한 유저가 글을 작성한 본인이면서 요청한 유저의 권한이 수정하려는 게시글이 속한 게시판의 쓰기 레벨과 같거나 더 높아야 글 수정이 가능합니다.

**Admin도 본인이 아니면 글 수정이 불가능합니다.**
"""

delete_post_description = """
RBAC - AUTH

지정한 게시글을 삭제합니다.

**글을 쓴 본인 또는 Admin만 삭제가 가능합니다.**
"""

# --------------------------------------------------------------------------
# Comment API endpoints documentations
# --------------------------------------------------------------------------
read_comments_description = """
RBAC - ALL

특정 게시글의 모든 댓글을 가져옵니다.
"""

create_comment_description = """
RBAC - AUTH

특정 게시글에 댓글을 작성합니다. 

쓰기 요청한 유저의 권한이 작성하려는 게시판의 댓글 쓰기 레벨 (Board.role_role_pk_comment_write_level)과 같거나 더 높아야 글 작성이 가능합니다.

**Admin은 게시판의 쓰기 권한과 상관 없이 댓글 작성이 가능합니다.**
"""

update_comment_description = """
RBAC - AUTH

지정한 댓글의 데이터를 수정합니다 (전체, 부분 업데이트를 지원합니다). 

요청한 유저가 댓글을 작성한 본인이면서 요청한 유저의 권한이 수정하려는 게시글이 속한 게시판의 댓글 쓰기 레벨과 같거나 더 높아야 글 수정이 가능합니다.

**Admin도 본인이 아니면 글 수정이 불가능합니다.**
"""

delete_comment_description = """
RBAC - AUTH

지정한 댓글을 삭제합니다. 

**글을 쓴 본인 또는 Admin만 삭제가 가능합니다.**

데이터를 실제로 삭제하지 않고 comment_delete를 1로 변경합니다.
"""

# --------------------------------------------------------------------------
# Responses Schema documentations
# --------------------------------------------------------------------------
# TODO: 각 endpoint 문서에 렌더링할 400, 403, 404, 500 등의 에러 응답 JSON 스키마 작성
response_403 = {
    403: {
        "model": ExceptionSchema,
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2023-12-11T13:12:47.209076Z",
                    "status": 403,
                    "error": "FORBIDDEN",
                    "message": "해당 유저의 권한으로는 불가능한 작업입니다.",
                    "errorCode": "HB-AUTH-002",
                    "path": "/hub/api/v2/<some/endpoint>",
                }
            }
        },
    },
}
database_err = {
    400: {
        "model": ExceptionSchema,
        "description": "DATABASE ERROR",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2023-12-11T13:12:47.209076Z",
                    "status": "DATABASE_BAD_REQUEST",
                    "error": "DATABASE_BAD_REQUEST",
                    "message": "데이터베이스에 중복된 값이 존재합니다.",
                    "errorCode": "HB-DATA-001",
                    "path": "/hub/api/v2/<some/endpoint>",
                }
            }
        },
    },
}

response_500 = {
    500: {
        "model": ExceptionSchema,
        "description": "UNKNOWN ERROR (서버 내부 로직 에러)",
    },
}

board_response_404 = {
    404: {
        "model": ExceptionSchema,
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2023-12-11T13:12:47.209076Z",
                    "status": 404,
                    "error": "NOT_FOUND",
                    "message": "해당 게시판을 찾을 수 없습니다.",
                    "errorCode": "HB-HTTP-002",
                    "path": "/hub/api/v2/board/<invalid_board_id>",
                }
            }
        },
    },
}

post_response_404 = {
    404: {
        "model": ExceptionSchema,
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2023-12-11T13:12:47.209076Z",
                    "status": 404,
                    "error": "NOT_FOUND",
                    "message": "해당 게시글을 찾을 수 없습니다.",
                    "errorCode": "HB-HTTP-002",
                    "path": "/hub/api/v2/post/<invalid_post_id>",
                }
            }
        },
    },
}

comment_response_404 = {
    404: {
        "model": ExceptionSchema,
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2023-12-11T13:12:47.209076Z",
                    "status": 404,
                    "error": "NOT_FOUND",
                    "message": "해당 댓글을 찾을 수 없습니다.",
                    "errorCode": "HB-HTTP-002",
                    "path": "/hub/api/v2/comment/<invalid_comment_id>",
                }
            }
        },
    },
}
