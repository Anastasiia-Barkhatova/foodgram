from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import baseconv
from django.views import View
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from api.constants import (
    PDFFONTIZE,
    PDFTEXTBEGINX,
    PDFTEXTBEGINY,
    PDFHEADBEGINY
)
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitedPagination
from api.permissions import (
    AdminOrReadOnly,
    IsAdminOrAuthor,
    IsAuthorOrAdminOrReadOnly
)
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingListSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserAvatarSerializer,
    UserReadSerializer,
    UserWriteSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)

from users.models import Subscription, User


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

    def handle_favorite_shopping_cart(
            self, request, pk, model_class, serializer_class
    ):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        object_data = model_class.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if object_data.exists():
                return Response(
                    'Вы уже добавили этот рецепт',
                    status=status.HTTP_400_BAD_REQUEST
                )
            obj = model_class.objects.create(user=user, recipe=recipe)
            serializer = serializer_class(
                obj, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not object_data.exists():
            return Response(
                {'errors': 'Вы не добавляли этот рецепт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        object_data.delete()
        return Response(
            f'Рецепт "{recipe.name}" успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
    )
    def get_delete_favorite(self, request, pk=None):
        return self.handle_favorite_shopping_cart(
            request, pk, Favorite, FavoriteSerializer
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
        ).annotate(total_amount=Sum('amount'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Список.pdf"'
        p = canvas.Canvas(response)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(
            TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf')
        )
        text_object = p.beginText(PDFTEXTBEGINX, PDFTEXTBEGINY)
        text_object.setFont('DejaVuSans', PDFFONTIZE)
        p.setFont('DejaVuSans-Bold', PDFFONTIZE)
        for item in ingredients:
            text_object.textLine(
                f'{item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) - '
                f'{item["total_amount"]}'
            )
        p.drawString(
            PDFTEXTBEGINX,
            PDFHEADBEGINY,
            'Список ингредиентов для сохраненных рецептов'
        )
        p.drawText(text_object)
        p.showPage()
        p.save()
        return response

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
    )
    def shopping_list(self, request, pk=None):
        return self.handle_favorite_shopping_cart(
            request, pk, ShoppingList, ShoppingListSerializer
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    pagination_class = LimitedPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] or self.action == 'get_me':
            return UserReadSerializer
        return UserWriteSerializer

    @action(
        detail=False,
        methods=('get',),
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        methods=('post',),
        detail=False,
        url_path='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(
            'Пароль изменен',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=('put', 'patch', 'delete'),
        url_path='me/avatar',
        url_name='me-avatar',
        permission_classes=(IsAuthenticated,)
    )
    def update_delete_avatar(self, request):
        if request.method == 'PATCH' or request.method == 'PUT':
            serializer = UserAvatarSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        request.user.avatar.delete(save=True)
        request.user.save()
        return Response(
            'Аватар успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        subscriptions = Subscription.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if subscriptions.exists():
                return Response(
                    'Вы уже подписаны на этого автора.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    'Вы не можете подписаться на самого себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                data={},
                context={'request': request, 'author': author, 'user': user}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not subscriptions.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscriptions.delete()
        return Response(
            f'Вы отписались от пользователя {author.username}',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions',
        permission_classes=(IsAuthenticated, IsAdminOrAuthor)

    )
    def subscriptions(self, request):
        authors = User.objects.filter(subscribers__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(authors),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
