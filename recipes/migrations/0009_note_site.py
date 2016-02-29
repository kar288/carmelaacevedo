# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20160229_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='site',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
