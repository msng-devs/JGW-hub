from django.urls import path, include, re_path
from django.conf import settings
from . import views
from rest_framework import routers, permissions
from rest_framework.urlpatterns import format_suffix_patterns
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView, SpectacularJSONAPIView

# app_name = 'jgw_api'

router = routers.DefaultRouter()
router.register(r'v1/board', views.BoardViewSet, basename='board')
# router.register(r'post', views.PostViewSet, basename='post')
router.register(r'v1/image', views.ImageViewSet, basename='image')
router.register(r'v1/comment', views.CommentViewSet, basename='comment')
# router.register(r'v1/survey', views.SurveyViewSet, basename='survey')

urlpatterns = [
    path('', include(router.urls)),
    path('ping/', views.ping_pong)
]




post_get_list = views.PostViewSet.as_view({
    'get': 'list'
})

post_post_list = views.PostViewSet.as_view({
    'post': 'create'
})

post_detail = views.PostViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns += format_suffix_patterns([
    path('v1/post/list/', post_get_list, name='post-get-list'),
    path('v1/post/', post_post_list, name='post-post-list'),
    path('v1/post/<int:pk>/', post_detail, name='post-detail'),
])




survey_post_post = views.SurveyViewSet.as_view({
    'post': 'create_post',
    'get': 'list_post'
})

survey_post_answer = views.SurveyViewSet.as_view({
    'post': 'create_answer'
})

urlpatterns += format_suffix_patterns([
    path('v1/survey/', survey_post_post, name='survey-post-post'),
    path('v1/survey/<str:pk>/answer/', survey_post_answer, name='survey-answer-post'),
])

if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]