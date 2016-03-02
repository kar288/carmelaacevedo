from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
  url = models.CharField(max_length=200)
  title = models.CharField(max_length=200)
  image = models.CharField(max_length=200)
  ingredients = models.TextField()
  instructions = models.TextField()
  date_added = models.CharField(max_length=200)
  def ingredients_as_list(self):
    return self.ingredients.split('\n')
  def instructions_as_list(self):
    return self.instructions.split('\n')

class Note(models.Model):
    HARD = 'H'
    MEDIUM = 'M'
    EASY = 'E'
    NONE = '-'
    RECIPE_DIFFICULTY = (
        (HARD, 'Hard'),
        (MEDIUM, 'Medium'),
        (EASY, 'Easy'),
        (NONE, '-'),
    )
    difficulty = models.CharField(max_length=1,
        choices=RECIPE_DIFFICULTY,
        default=NONE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    ingredients = models.TextField()
    instructions = models.TextField()
    date_added = models.CharField(max_length=200)
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="recipe",
    )
    text = models.TextField()
    tags = models.TextField()
    rating = models.IntegerField()
    servings = models.CharField(max_length=200)
    site = models.CharField(max_length=200)

    def tags_as_list(self):
        tags = self.tags.split('\n')
        newTags = []
        for tag in tags:
            newTags.append(tag.replace('\r', '').strip())
        print newTags
        return newTags
    def rating_as_list(self):
        return range(self.rating)
    def ingredients_as_list(self):
        return self.ingredients.split('\n')
    def instructions_as_list(self):
        return self.instructions.split('\n')
    def title_short(self):
        return self.title[:30]
    def date_added_formatted(self):
        # return self.date_added
        return self.created_at.strftime("%d/%b/%y")

class RecipeUser(models.Model):
  googleUser = models.OneToOneField(User, on_delete=models.CASCADE)
  notes = models.ManyToManyField(
    Note
  )
