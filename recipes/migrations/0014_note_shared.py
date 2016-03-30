# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='shared',
            field=models.BooleanField(default=False),
        ),
    ]
