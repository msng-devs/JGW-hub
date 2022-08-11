from django.urls import path, include
from . import views
from rest_framework import routers

# app_name = 'jgw_api'

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='categoty')

urlpatterns = [
    path('', include(router.urls))
]