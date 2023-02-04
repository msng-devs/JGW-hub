from typing import Final

RANDOM_STRING_CHARS: Final = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

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

SURVEY_DB_NAME = 'survey'
SURVEY_POST_DB_NME = 'survey_post'
SURVEY_POST_DB_VALIDATOR = {
    '$jsonSchema': {
        "title": 'schema',
        "description": 'Survey post schema validation',
        "bsonType": 'object',
        "required": [
          'title',
          'description',
          'writer',
          'allow_multiple',
          'role_answer'
        ],
        "properties": {
          "title": {
            "bsonType": 'string',
            "maxLength": 64
          },
          "description": {
            "bsonType": 'string',
            "maxLength": 256
          },
          "writer": {
            "bsonType": 'string'
          },
          "allow_multiple": {
            "bsonType": 'bool'
          },
          "role_answer": {
            "bsonType": 'int'
          },
          "question": {
            "bsonType": 'array',
            "items": {
              "type": 'object'
            }
          },
          "answer": {
            "bsonType": 'array',
            "items": {
              "type": 'object'
            }
          }
        }
      }
}
