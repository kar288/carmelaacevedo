from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from mimetypes import guess_type
from django.conf import settings
import csv
import re
from random import randint
import datetime

import urllib2
import xml.etree.ElementTree as ET
from NetflixRoulette import *
from django.template import loader
from django.http import JsonResponse


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login

from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa
from recipes.models import Recipe, Note, RecipeUser

import urllib2
from BeautifulSoup import BeautifulSoup


# from .models import Greeting


# Create your views here.
def home(request):
    context = {}
    print request.user
    print request.user.is_authenticated()
    if not request.user.is_authenticated():
        return render(request, 'index.html', context)
    try:
      recipeUser = RecipeUser.objects.get(googleUser = request.user)
      print(recipeUser.notes.all())
      context['notes'] = recipeUser.notes.all()
    except RecipeUser.DoesNotExist:
      print('USER NOT FOUND')
    return render(request, 'index.html', context)

# Create your views here.
def addNote(request):
    print request.user
    print request.POST
    post = request.POST
    if not post:
        return redirect('/recipes/')
    try:
      recipeUser = RecipeUser.objects.get(googleUser = request.user)
      print(recipeUser.notes.all())
    #   notes = recipeUser.notes.all()
    #   recipeUser.notes.
      if 'recipeUrl' in post:
          recipeUrl = post['recipeUrl']
          html = urllib2.urlopen(recipeUrl);
        #   print(html.read().decode('utf-8'))
          soup = BeautifulSoup(html)
        #   print soup.title.string
          imageUrl = ''
          image = soup.findAll(attrs={"itemprop": "image"})
        #   print image
          if len(image) :
            if image[0].has_key('content'):
              imageUrl = image[0]['content']
            elif image[0].has_key('src'):
              imageUrl = image[0]['src']
        #   print imageUrl
          ingredients = []
          ingredientElements = soup.findAll(attrs={"itemprop": "ingredients"})
          traverse(ingredientElements, ingredients)
          instructions = []
          instructionElements = \
            soup.findAll(attrs={"itemprop": "recipeInstructions"})
          traverse(instructionElements, instructions)
        #   $('[itemprop="recipeInstructions"]')
        #   $('[itemprop="ingredients"]')
        #   $('[itemprop="image"]') $('figure')
          recipe = Recipe.objects.create(
            url = recipeUrl,
            image = imageUrl,
            ingredients = '*'.join(ingredients),
            instructions = '*'.join(instructions),
            title = soup.title.string,
            date_added = datetime.datetime.now()
          )
          print(recipe)
          if 'notes' in post:
              note = Note.objects.create(
                recipe = recipe,
                text = post['notes']
              )
              recipeUser.notes.add(note)
    except RecipeUser.DoesNotExist:
      print('USER NOT FOUND')
    return redirect('/recipes/')

def traverse(nodes, s):
  for node in nodes:
    if node.children:
      traverse(node.children, s);
    else:
      s.append(node.text);


def save_profile_picture(strategy, user, response, details,
                         is_new=False,*args,**kwargs):

  # if strategy.backend.name == "google-oauth2":
    profile = user.userprofile
    profile.profile_photo.save('{0}_social.jpg'.format(user.username),
                           ContentFile(response.content))
    profile.save()

def save_profile(backend, user, response, *args, **kwargs):
  # print(response)
  if backend.name == "google-oauth2":
    print('------------------------------------------')
    print type(user)
    print('------------------------------------------')
    recipeUser = None
    try:
      recipeUser = RecipeUser.objects.get(googleUser = user)
      print(recipeUser.googleUser)
    except RecipeUser.DoesNotExist:
      print('USER NOT FOUND')
      recipeUser = RecipeUser.objects.create(googleUser = user)

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/recipes/')
