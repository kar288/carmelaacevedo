# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0021_recipeuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='recipe',
            field=models.OneToOneField(null=True, verbose_name='recipe', to='recipes.Recipe'),
        ),
    ]
