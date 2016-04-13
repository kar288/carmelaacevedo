# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0017_auto_20160411_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeuser',
            name='facebookUser',
            field=models.OneToOneField(related_name='facebookUser', null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipeuser',
            name='googleUser',
            field=models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
