# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_note_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 29, 14, 0, 56, 488562), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 29, 14, 1, 4, 887879), auto_now_add=True),
            preserve_default=False,
        ),
    ]
