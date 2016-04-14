# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0022_auto_20160414_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='site',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
