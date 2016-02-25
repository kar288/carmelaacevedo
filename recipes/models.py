from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
  url = models.CharField(max_length=200)
  title = models.CharField(max_length=200)
  image = models.CharField(max_length=200)
  ingredients = models.TextField()
  instructions = models.TextField()
  date_added = models.CharField(max_length=200)

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
