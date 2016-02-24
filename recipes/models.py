from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
  url = models.CharField(max_length=30)
  title = models.CharField(max_length=30)
  date_added = models.CharField(max_length=30)

class Note(models.Model):
  recipe = models.OneToOneField(
    Recipe,
    on_delete=models.CASCADE,
    verbose_name="recipe",
  )
  text = models.TextField()
  # date_added = models.CharField(max_length=30)

class RecipeUser(models.Model):
  googleUser = models.OneToOneField(User, on_delete=models.CASCADE)
  notes = models.ManyToManyField(
    Note
  )
