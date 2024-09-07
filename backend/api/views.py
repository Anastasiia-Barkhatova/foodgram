from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import baseconv
from django.views import View
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from api.constnts import (
    PDFFONTIZE,
    PDFTEXTBEGINX,
    PDFTEXTBEGINY,
    PDFHEADBEGINY
)
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitedPagination
from api.permissions import AdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingListSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    http_method_names = ('get',)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitedPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        if self.action == 'shopping_list':
            return ShoppingListSerializer
        if self.action == 'get_favorite':
            return FavoriteSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def get_favotite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Вы уже добавили этот рецепт в избранное.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(
                favorite, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Вы не добавляли этот рецепт в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            f'Рецепт "{recipe.name}" успешно удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Список.pdf"'
        p = canvas.Canvas(response)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(
            TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf')
        )
        textobject = p.beginText(PDFTEXTBEGINX, PDFTEXTBEGINY)
        textobject.setFont('DejaVuSans', PDFFONTIZE)
        p.setFont('DejaVuSans-Bold', PDFFONTIZE)
        for item in ingredients:
            textobject.textLine(
                f'{item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) - {item["amount"]}'
            )
        p.drawString(
            PDFTEXTBEGINX,
            PDFHEADBEGINY,
            'Список ингредиентов для сохраненных рецептов'
        )
        p.drawText(textobject)
        p.showPage()
        p.save()
        return response

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_list(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Вы уже добавили этот рецепт в список покупок.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ShoppingListSerializer(
                favorite, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Вы не добавляли этот рецепт в список покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingList.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            f'Рецепт "{recipe.name}" удален из списка покупок',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        short_string = baseconv.base62.encode(pk)
        short_link = request.build_absolute_uri(
            reverse('recipe-short-link', kwargs={
                'short_string': short_string
            })
        )
        return Response({'short-link': short_link})


class RedirectView(View):
    def get(self, request, short_string):
        recipe_id = baseconv.base62.decode(short_string)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f'/recipes/{recipe.pk}/')
