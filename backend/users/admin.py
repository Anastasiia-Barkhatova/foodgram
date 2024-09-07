from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ('email', 'username')
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_blocked',
    )
    list_editable = (
        'is_blocked',
    )
    fieldsets = (
        ('Регистрационные данные', {
            'fields': ('username', 'email', 'password', 'date_joined'),
        }),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'avatar'),
        })
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('author',)
    search_fields = ('user__username',)
