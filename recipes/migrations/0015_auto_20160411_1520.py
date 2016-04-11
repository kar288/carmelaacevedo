# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_note_shared'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='image',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='note',
            name='servings',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='note',
            name='url',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='title',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='url',
            field=models.CharField(max_length=400),
        ),
    ]
