from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    RedirectView,
    TagViewSet,
    UserViewSet
)

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path(
        'r/<str:short_string>/',
        RedirectView.as_view(),
        name='recipe-short-link'),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
