from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.urls import reverse

from recipes.constants import (
    INGREDIENT_NAME_LENGHT,
    MIN_COOKING_TIME,
    NAME_LENGHT,
    MEASUREMENT_UNIT_LENGHT,
    MIN_INGREDIENTS_AMOUNT,
    TAG_NAME_LENGHT
)
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Тег',
        max_length=TAG_NAME_LENGHT,
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=TAG_NAME_LENGHT,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=('Slug может содержать только буквы, '
                         'цифры, дефисы и подчеркивания.')
            )
        ]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=INGREDIENT_NAME_LENGHT,
        db_index=True,
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MEASUREMENT_UNIT_LENGHT,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        help_text='Автор рецепта',
        related_name='recipes'
    )
    name = models.CharField(
        'Название блюда',
        max_length=NAME_LENGHT
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipes_images/',
    )
    text = models.TextField(
        'Описание блюда',
        help_text='Опишите этапы приготовления блюда')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Название тега',
        help_text='Выберите теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления блюда',
        validators=[MinValueValidator(
            MIN_COOKING_TIME,
            'Минимальное время приготовления блюда должно быть не меньше 1 мин'
        )
        ],
        help_text='Укажите время приготовления блюда в минутах')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            MIN_INGREDIENTS_AMOUNT,
            'Минимальное количество должно быть не меньше 1')
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class RecipeTag(models.Model):
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_tag'
    )

    class Meta:
        verbose_name = 'Тег для рецепта'
        verbose_name_plural = 'Теги для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tags'),
                name='unique_recipe_tags')
        ]

    def __str__(self):
        return f'{self.recipe} - {self.tags}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранные рецепты'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_user_favorite')
        ]
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'

    def __str__(self):
        return f'{self.user} добавил в "Избранное" рецепт "{self.recipe}"'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепты в списке покупок',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_user_shopping_list')
        ]
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
