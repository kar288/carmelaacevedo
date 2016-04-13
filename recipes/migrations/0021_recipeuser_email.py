# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_recipeuser_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeuser',
            name='email',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
