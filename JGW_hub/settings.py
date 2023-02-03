"""
Django settings for JGW_hub project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import sys

import JGW_hub.db_router
from JGW_hub import debug

from secrets_content.files.secret_key import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = MY_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(debug.is_debug))
# DEBUG = False
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
ALLOWED_HOSTS = []
ALLOWED_HOSTS = [] if DEBUG else MY_ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'jgw_api',
    'survey'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'JGW_hub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'JGW_hub.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = MY_DATABASES

# DATABASE_ROUTERS = [
#     'JGW_hub.db_router.DatabaseRouter'
# ]

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SPECTACULAR_SETTINGS = {
    'TITLE': 'Jaram Hub Api 문서',
    'VERSION': '1.0.0',
    'SWAGGER_UI_SETTINGS': {

    },
    'SERVE_AUTHENTICATION': None,
    'SERVE_INCLUDE_SCHEMA': False,
}

DEFAULT_RENDERER_CLASSES = ['rest_framework.renderers.JSONRenderer']

if DEBUG:
    DEFAULT_RENDERER_CLASSES += [
        'rest_framework.renderers.BrowsableAPIRenderer'
    ]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES
    # 'DEFAULT_AUTHENTICATION_CLASSES': [],
    # 'DEFAULT_PERMISSION_CLASSES': [],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'format1': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'format2': {
            'format': '[%(asctime)s] %(levelname)s [%(pathname)s-%(name)s:%(lineno)s] %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'format1',
            'filters': ['require_debug_false']
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'format2',
            'filters': ['require_debug_false'],
            'filename': BASE_DIR / 'logs/hub_errors.log',
            'maxBytes': 1024 * 1024 * 200,
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'format2',
            'filters': ['require_debug_false'],
            'filename': BASE_DIR / 'logs/hub.log',
            'maxBytes': 1024 * 1024 * 200,
            'backupCount': 10,
            'encoding': 'utf-8',
        },
    },
    # 로거
    'loggers': {
        'hub': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'hub_error': {
            'handlers': ['console', 'file_error', 'file'],
            'level': 'DEBUG'
        }
    }
}

CORS_ORIGIN_ALLOW_ALL = MY_CORS_ORIGIN_ALLOW_ALL
CORS_ALLOW_CREDENTIALS = MY_CORS_ALLOW_CREDENTIALS
CORS_ALLOW_METHODS = MY_CORS_ALLOW_METHODS
CORS_ALLOW_HEADERS = MY_CORS_ALLOW_HEADERS
APPEND_SLASH = MY_APPEND_SLASH
