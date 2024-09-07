from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet


router = DefaultRouter()

router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
