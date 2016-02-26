# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_note_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='difficulty',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='rating',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='servings',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
