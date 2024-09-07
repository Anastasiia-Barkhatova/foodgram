from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    USERNAME_MAX_LENGTH
)


class User(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=USERNAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=USERNAME_MAX_LENGTH,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        error_messages={'unique': "Это имя пользователя уже занято."},
    )
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': "Пользователь с таким email уже зарегистрирован."
        },
        max_length=EMAIL_MAX_LENGTH,
    )
    password = models.CharField(
        'Пароль',
        max_length=PASSWORD_MAX_LENGTH,
    )
    is_blocked = models.BooleanField('Заблокирован', default=False)
    avatar = models.ImageField(
        'Фото профиля',
        upload_to='avatars/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_user_author')
        ]
        verbose_name = 'подписчики'
        verbose_name_plural = 'подписчики'

    def __str__(self):
        return f'{self.user} подписан на пользователя {self.author}'
