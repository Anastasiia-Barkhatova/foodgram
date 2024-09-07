# Generated by Django 3.2.16 on 2024-08-30 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20240830_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=32, verbose_name='Тег'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=32, unique=True, verbose_name='Слаг'),
        ),
    ]