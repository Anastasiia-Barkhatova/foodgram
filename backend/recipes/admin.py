from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    RecipeIngredient,
    RecipeTag,
    Recipe,
    ShoppingList,
    Tag
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'id',
        'name',
        'slug'
    )
    list_editable = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_editable = (
        'measurement_unit',
    )


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('author', 'name')
    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
        'pub_date',
        'get_is_favorite',
        'get_tags',
        'get_ingredients'
    )
    list_filter = ('tags',)
    filter_horizontal = ('tags', 'ingredients')
    inlines = (RecipeIngredientInline, RecipeTagInline)

    @admin.display(description='В избранном')
    def get_is_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username',)
    list_filter = ('recipe',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username',)
    list_filter = ('recipe',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )
    list_editable = (
        'amount',
    )
    search_fields = ('recipe__name',)


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'tags',
    )
    list_editable = (
        'tags',
    )
    search_fields = ('recipe__name',)
