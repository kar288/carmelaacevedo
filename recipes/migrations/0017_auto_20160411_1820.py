# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20160411_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='url',
            field=models.CharField(max_length=200, db_index=True),
        ),
    ]
