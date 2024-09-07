from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djoser.serializers import SetPasswordSerializer

from api.pagination import LimitedPagination
from users.models import Subscription, User
from users.permissions import IsSelfOrAdminOrReadOnly, IsAdminOrAuthor
from users.serializers import (
    SubscribeSerializer,
    SubscriptionSerializer,
    UserAvatarSerializer,
    UserReadSerializer,
    UserWriteSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (IsSelfOrAdminOrReadOnly, )
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
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user)
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
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(
                'Пароль изменен',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()

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
        if request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            request.user.save()
            return Response(
                'Аватар успешно удален',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            if Subscription.objects.filter(user=user, author=author).exists():
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
                author, data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.filter(user=user, author=author).delete()
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
