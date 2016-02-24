# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 19:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='notes',
        ),
        migrations.AlterField(
            model_name='note',
            name='recipe',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='recipe'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='googleUser',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='notes',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='recipes.Note', verbose_name='recipe note'),
        ),
    ]