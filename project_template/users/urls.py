from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views.read_views import *
from .views.write_views import *

router = DefaultRouter()
router.register('user', UserViewset, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
