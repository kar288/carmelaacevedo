# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20160225_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='tags',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
