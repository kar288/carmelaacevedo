# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_auto_20160411_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='url',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='url',
            field=models.CharField(max_length=200),
        ),
    ]
