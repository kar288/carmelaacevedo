# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_auto_20160413_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeuser',
            name='profilePic',
            field=models.CharField(max_length=400, null=True),
        ),
    ]
