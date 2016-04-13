# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_recipeuser_profilepic'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeuser',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
