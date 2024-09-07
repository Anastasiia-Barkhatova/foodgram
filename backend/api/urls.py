from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    RedirectView,
    TagViewSet
)


router = DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path(
        'r/<str:short_string>/',
        RedirectView.as_view(),
        name='recipe-short-link'),
]
