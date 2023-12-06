from django.urls import path, include

from django.conf import settings

from backups.views import *
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularRedocView,
    SpectacularAPIView,
)

# app_name = 'jgw_api'

router = routers.DefaultRouter()
router.register(r"v1/board", BoardViewSet, basename="board")
# router.register(r'v1/post', views.PostViewSet, basename='post')
# router.register(r'v1/image', views.ImageViewSet, basename='image')
router.register(r"v1/comment", CommentViewSet, basename="comment")
# router.register(r'v1/survey', views.SurveyViewSet, basename='survey')

urlpatterns = [path("", include(router.urls)), path("ping/", ping_pong)]

post_get_list = PostViewSet.as_view({"get": "list"})

post_post_list = PostViewSet.as_view({"post": "create"})

post_detail = PostViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns += format_suffix_patterns(
    [
        path("v1/post/list/", post_get_list, name="post-get-list"),
        path("v1/post/", post_post_list, name="post-post-list"),
        path("v1/post/<int:pk>/", post_detail, name="post-detail"),
    ]
)

survey_post_post = SurveyViewSet.as_view({"post": "create_post", "get": "list_post"})

survey_post_get = SurveyViewSet.as_view(
    {"get": "retrieve_post", "delete": "delete_post", "patch": "patch_post"}
)

survey_post_answer = SurveyViewSet.as_view(
    {
        "post": "create_answer",
        "get": "list_answers",
    }
)

urlpatterns += format_suffix_patterns(
    [
        path("v1/survey/", survey_post_post, name="survey-post-post"),
        path("v1/survey/<str:pk>/", survey_post_get, name="survey-post-get"),
        path(
            "v1/survey/<str:pk>/answer/", survey_post_answer, name="survey-answer-post"
        ),
    ]
)

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
