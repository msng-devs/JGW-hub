from django.urls import path
from . import views
from rest_framework import routers

# app_name = 'jgw_api'
#
# router = routers.SimpleRouter()
# router.register(r'testclass/', views.TestHeader, basename='TestClass')

# urlpatterns = router.urls

urlpatterns = [
    path('test/', views.test_header),
    path('testclass/', views.TestHeader.as_view())
]