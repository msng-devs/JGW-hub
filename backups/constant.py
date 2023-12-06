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

SURVEY_MAX_PAGE_SIZE: Final = 50
SURVEY_MIN_PAGE_SIZE: Final = 1
SURVEY_DEFAULT_PAGE_SIZE: Final = 10

ANSWER_MAX_PAGE_SIZE: Final = 100
ANSWER_MIN_PAGE_SIZE: Final = 25
ANSWER_DEFAULT_PAGE_SIZE: Final = 50

SURVEY_DB_NAME = 'survey'
SURVEY_POST_DB_NME = 'survey_post'
SURVEY_POST_DB_VALIDATOR = {
    '$jsonSchema': {
        "title": 'survey post schema',
        "description": 'survey post schema validation',
        "bsonType": 'object',
        "required": [
          'title',
          'description',
          'writer',
          'role',
          "quizzes",
          "answers"
        ],
        "properties": {
          "title": {
            "bsonType": 'string',
            "maxLength": 32
          },
          "description": {
            "bsonType": 'string',
            "maxLength": 256
          },
          "writer": {
            "bsonType": 'string',
          },
          "role": {
            "bsonType": 'int'
          },
          "quizzes": {
            "bsonType": 'array',
            "items": {
              "bsonType": 'object'
            }
          },
          "answers": {
            "bsonType": 'array',
            "items": {
              "bsonType": 'object'
            }
          }
        }
      }
}

SURVEY_TEXT = 'text'
SURVEY_SELECT_ONE = 'select_one'

SURVEY_TEXT_QUIZ = 'quiz_' + SURVEY_TEXT
SURVEY_TEXT_QUIZ_VALIDATOR = {
    '$jsonSchema': {
        "title": 'text question schema',
        "description": 'text question schema validation',
        "bsonType": 'object',
        "required": [
          "title",
          "description",
          "require",
          "answers"
        ],
        "properties": {
          "title": {
            "bsonType": 'string',
            "maxLength": 32
          },
          "description": {
            "bsonType": 'string',
            "maxLength": 256
          },
          "require": {
            "bsonType": 'bool',
          },
          "answers": {
            "bsonType": 'array',
            "items": {
              "bsonType": 'object'
            }
          }
        }
      }
}
SURVEY_TEXT_ANSWER = 'answer_' + SURVEY_TEXT
SURVEY_TEXT_ANSWER_VALIDATOR = {
    '$jsonSchema': {
        "title": 'text answer schema',
        "description": 'text answer schema validation',
        "bsonType": 'object',
        "required": [
          "user",
          "text",
        ],
        "properties": {
          "user": {
            "bsonType": 'string',
            "maxLength": 32
          },
          "text": {
            "bsonType": 'string',
            "maxLength": 256
          },
        }
      }
}

SURVEY_SELECT_ONE_QUIZ = 'quiz_' + SURVEY_SELECT_ONE
SURVEY_SELECT_ONE_QUIZ_VALIDATOR = {
    '$jsonSchema': {
        "title": 'text question schema',
        "description": 'text question schema validation',
        "bsonType": 'object',
        "required": [
          "title",
          "description",
          "require",
          "answers"
        ],
        "properties": {
          "title": {
            "bsonType": 'string',
            "maxLength": 32
          },
          "description": {
            "bsonType": 'string',
            "maxLength": 256
          },
          "require": {
            "bsonType": 'bool',
          },
          "options": {
            "bsonType": 'array',
            "minItems": 1,
            "items": {
              "bsonType": 'object',
              "required": [
                  "text"
              ],
              "properties": {
                "text": {
                    "bsonType": 'string',
                    "maxLength": 16
                }
              },
            }
          },
          "answers": {
            "bsonType": 'array',
            "items": {
              "bsonType": 'object'
            }
          }
        }
      }
}
SURVEY_SELECT_ONE_ANSWER = 'answer_' + SURVEY_SELECT_ONE
SURVEY_SELECT_ONE_ANSWER_VALIDATOR = {
    '$jsonSchema': {
        "title": 'text answer schema',
        "description": 'text answer schema validation',
        "bsonType": 'object',
        "required": [
          "user",
          "selection",
        ],
        "properties": {
          "user": {
            "bsonType": 'string',
            "maxLength": 32
          },
          "selection": {
            "bsonType": 'int',
          },
        }
      }
}

SURVEY_TEXT_CODE = 0
SURVEY_SELECT_ONE_CODE = 1
SURVEY_SELECT_MULTIPLE_CODE = 2

QUIZ_TYPE_I2S = {
  0: SURVEY_TEXT,
  1: SURVEY_SELECT_ONE,
}
QUIZ_TYPE_S2I = {
  SURVEY_TEXT: 0,
  SURVEY_SELECT_ONE: 1,
}

SURVEY_QUIZ = 'survey_quiz'
SURVEY_ANSWER = 'survey_answer'

TIME_QUERY = '%Y-%m-%dT%H-%M-%S'
