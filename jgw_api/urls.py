from django.urls import path, include, re_path
from django.conf import settings
from . import views
from rest_framework import routers, permissions
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView, SpectacularJSONAPIView

# app_name = 'jgw_api'

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls))
]

if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]