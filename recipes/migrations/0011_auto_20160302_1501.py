# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20160229_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='difficulty',
            field=models.CharField(default='-', max_length=1, choices=[('H', 'Hard'), ('M', 'Medium'), ('-', '-')]),
        ),
    ]
