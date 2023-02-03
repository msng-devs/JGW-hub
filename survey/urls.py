from django.urls import path, include, re_path
from django.conf import settings
from . import views
from rest_framework import routers, permissions
from rest_framework.urlpatterns import format_suffix_patterns

# app_name = 'jgw_api'
urlpatterns = [
    path('v1/survey/', views.test)
]
