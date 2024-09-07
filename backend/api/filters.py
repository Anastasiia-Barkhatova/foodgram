from django_filters import rest_framework as filters

from recipes.models import Ingredient, Tag
from users.models import User


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.CharFilter(method='get_favorited',)
    is_in_shopping_cart = filters.CharFilter(method='get_shopping_cart',)

    def get_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name', )

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            name__istartswith=value
        )
