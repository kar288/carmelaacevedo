from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from mimetypes import guess_type
from django.conf import settings
import csv
import re
from random import randint
# import datetime
from datetime import datetime

import urllib2

from urlparse import urlparse
import xml.etree.ElementTree as ET
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
from  django.db.models import Q
from  django.db.models.functions import Lower

from BeautifulSoup import BeautifulSoup

def getTableFields(field):
    return [{
            'field': 'image',
            'display': '',
            'selected': 'image' == field
        }, {
            'field': 'title',
            'display': 'Title',
            'selected': 'title' == field
        }, {
            'field': 'site',
            'display': 'Site',
            'selected': 'site' == field
        }, {
            'field': 'difficulty',
            'display': 'Difficulty',
            'selected': 'difficulty' == field
        }, {
            'field': 'servings',
            'display': 'Servings',
            'selected': 'servings' == field
        }, {
            'field': 'created_at',
            'display': 'Date added',
            'selected': 'date_added_formatted' == field
        }, {
            'field': 'rating',
            'display': 'Rating',
            'selected': 'rating' == field
        }]

# Create your views here.
def home(request):
    context = {}
    if not request.user.is_authenticated():
        return render(request, 'recipeBase.html', context)
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    context['notes'] = recipeUser.notes.all().order_by('-recipe__date_added')
    return render(request, 'index.html', context)

def recrawlImages(request):
    context = {}
    recipes = Recipe.objects.all()
    for recipe in recipes:
        print recipe.image, recipe.url
        if not recipe.image:
            req = urllib2.Request(recipe.url, headers={'User-Agent' : "Magic Browser"})
            html = urllib2.urlopen(req)
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            imageUrl = getImage(soup)
            print 'changing image to :' + imageUrl
            setattr(recipe, 'image', imageUrl)
            recipe.save()
    return render(request, 'index.html', context)

def convertNotes(request):
    context = {'notes': []}
    notes = Note.objects.all()
    for note in notes:
        recipe = note.recipe
        setattr(note, 'url', recipe.url)
        setattr(note, 'title', recipe.title)
        setattr(note, 'image', recipe.image)
        setattr(note, 'ingredients', recipe.ingredients)
        setattr(note, 'instructions', recipe.instructions)
        setattr(note, 'date_added', recipe.date_added)
        parsed_uri = urlparse(recipe.url)
        domain = '{uri.netloc}'.format(uri = parsed_uri)
        setattr(note, 'site', domain)
        date = datetime.strptime(recipe.date_added, "%Y-%m-%d %H:%M:%S.%f")
        # print date
        setattr(note, 'created_at', date)
        note.save()
        context['notes'].append(note)
    return render(request, 'index.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def table(request, field):
    context = {}
    field = field if field else 'title'
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    context['notes'] = recipeUser.notes.all().order_by(Lower(field))
    context['fields'] = getTableFields(field)
    return render(request, 'table.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def tableAll(request, field):
    context = {}
    field = field if field else 'title'
    context['notes'] = Note.objects.all().order_by(Lower(field))
    context['fields'] = getTableFields(field)
    return render(request, 'table.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def note(request, noteId):
    context = {}
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        context['note'] = note
    return render(request, 'note.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def tags(request, tags):
    context = {}
    tags = tags.split(',')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.none()
    for tag in tags:
        notes |= recipeUser.notes.filter(tags__icontains = tag)
    context['notes'] = notes
    return render(request, 'index.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def search(request):
    context = {}
    get = request.GET
    if not get:
        return redirect('/recipes/')
    query = get.get('query', '')
    context['query'] = query
    terms = query.split(' ')
    print terms
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.none()
    for term in terms:
        notes |= recipeUser.notes.filter(tags__icontains = term)
        notes |= recipeUser.notes.filter(recipe__ingredients__icontains = term)
        notes |= recipeUser.notes.filter(recipe__title__icontains = term)
        notes |= recipeUser.notes.filter(difficulty__icontains = term)
        notes |= recipeUser.notes.filter(servings__icontains = term)
    context['notes'] = notes
    return render(request, 'index.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def advancedSearch(request):
    context = {}
    get = request.GET
    if not get:
        return redirect('/recipes/')
    query = get
    context['advancedQuery'] = get
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.all()
    for field in query:
        q = query.get(field, '').strip().split(' ')
        if not len(q):
            continue
        print field, q
        for term in q:
            if field == 'tags':
                notes &= recipeUser.notes.filter(tags__icontains = term)
            if field == 'title':
                notes &= recipeUser.notes.filter(recipe__title__icontains = term)
            if field == 'ingredients':
                notes &= recipeUser.notes.filter(recipe__ingredients__icontains = term)
            if field == 'instructions':
                notes &= recipeUser.notes.filter(recipe__instructions__icontains = term)
            if field == 'notes':
                notes &= recipeUser.notes.filter(text__icontains = term)
            if field == 'difficulty':
                notes &= recipeUser.notes.filter(difficulty__icontains = term)
            if field == 'servings':
                notes &= recipeUser.notes.filter(servings__icontains = term)
    context['notes'] = notes
    return render(request, 'advancedSearch.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def ingredients(request, ingredients):
    context = {}
    ingredients = ingredients.split(',')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.none()
    for ingredient in ingredients:
        notes |= recipeUser.notes.filter(recipe__ingredients__icontains = ingredient)
    context['notes'] = notes
    return render(request, 'index.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def editNoteHtml(request, noteId):
    context = {'edit': True, 'rates': [5, 4, 3, 2, 1]}
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        context['note'] = note
    return render(request, 'note.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def deleteNoteHtml(request, noteId):
    context = {}
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        context['note'] = note
    return render(request, 'deleteNote.html', context)

def deleteNote(request, noteId):
    context = {}
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        recipe = note.recipe
        context['success'] = ['Recipe was deleted: ' + note.title]
        recipe.delete()
        note.delete()
        context['notes'] = recipeUser.notes.all()
    return render(request, 'index.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def advancedSearchHtml(request, field):
    return render(request, 'advancedSearch.html')

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def addRecipeHtml(request):
    return render(request, 'addRecipe.html')

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def addRecipesHtml(request):
    return render(request, 'addRecipes.html')

def editNote(request, noteId):
    context = {}
    post = request.POST
    if not post:
        return redirect('/recipes/note/' + noteId)
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        for field in post:
            if field == 'rating':
                setattr(note, 'rating', post.get('rating', -1))
            else:
                setattr(note, field, clean(post.get(field, '')))
        note.save()
        context['note'] = note
    return redirect('/recipes/note/' + noteId)

def clean(str):
    return str.replace('\r', '').strip()

# Create your views here.
def addNote(request):
    post = request.POST
    if not post:
        return redirect('/recipes/addRecipe/')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    if 'recipeUrl' in post:
        recipeUrl = post['recipeUrl']
        addRecipeByUrl(recipeUser, recipeUrl, post)
    return redirect('/recipes/')

def getImage(soup):
    imageUrl = ''
    image = soup.find('meta', attrs={"property": "og:image"})
    image2 = soup.find('meta', attrs={"name": "twitter:image:src"})
    if image:
      print ('op:image')
      if image.has_key('content'):
        imageUrl = image['content']
    elif image2:
        print ('twitter image src')
        print image2
        if image2:
          if image2.has_key('content'):
            imageUrl = image2['content']
    else:
        image = soup.findAll(attrs={"itemprop": "image"})
        if len(image) :
          if image[0].has_key('content'):
            imageUrl = image[0]['content']
          elif image[0].has_key('src'):
            imageUrl = image[0]['src']
    print imageUrl
    return imageUrl

def addRecipeByUrl(recipeUser, recipeUrl, post):
    try:
        req = urllib2.Request(recipeUrl, headers={'User-Agent' : "Magic Browser"})
        html = urllib2.urlopen(req)
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        imageUrl = getImage(soup)
        ingredients = []
        ingredientElements = soup.findAll(attrs={"itemprop": "ingredients"})
        traverse(ingredientElements, ingredients)
        instructions = []
        instructionElements = \
          soup.findAll(attrs={"itemprop": "recipeInstructions"})
        traverse(instructionElements, instructions)
        recipe = Recipe.objects.create(
          url = recipeUrl,
          image = imageUrl,
          ingredients = '\n'.join(ingredients),
          instructions = '\n'.join(instructions),
          title = soup.title.string,
          date_added = datetime.now()
        )
        note = Note.objects.create(
          recipe = recipe,
          url = recipeUrl,
          image = imageUrl,
          ingredients = '\n'.join(ingredients),
          instructions = '\n'.join(instructions),
          title = soup.title.string,
          date_added = datetime.now(),
          text = post.get('notes', ''),
          tags = post.get('tags', ''),
          rating = post.get('rating', -1),
          difficulty = post.get('difficulty', ''),
          servings = post.get('servings', '')
        )
        recipeUser.notes.add(note)
    except urllib2.HTTPError, err:
        return 'Could not get recipe: ' + recipeUrl

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def addBulk(request):
    context = {'errors': []}
    post = request.POST
    if not post:
        return redirect('/recipes/addRecipes/')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    bookmarks = post.getlist('bookmark')
    for recipeUrl in bookmarks:
        error = addRecipeByUrl(recipeUser, recipeUrl, post)
        context['errors'].append(error)
    return redirect('/recipes/')

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def processBulk(request):
    context = {}
    post = request.POST
    cookingDomains = {
        'food52.com': True,
        'smittenkitchen.com': True,
        'www.thekitchn.com': True,
        'www.epicurious.com': True,
        'allrecipes.com': True,
        'cooking.nytimes.com': True,
        'www.food.com': True,
        'www.101cookbooks.com': True,
        'www.marthastewart.com': True,
        'www.jamieoliver.com': True,
        'allrecipes.com': True,
    }
    if not post:
        return render(request, 'addRecipes.html', context)
    if 'bookmarks' in post:
        bookmarks = post['bookmarks']
        soup = BeautifulSoup(bookmarks, convertEntities=BeautifulSoup.HTML_ENTITIES)
        urls = []
        tags = soup.findAll('a')
        for tag in tags:
            href = tag.get('href')
            text = tag.text if tag.text else href
            parsed_uri = urlparse(href)
            domain = '{uri.netloc}'.format(uri=parsed_uri)
            color = 'white'
            if domain in cookingDomains or 'recipe' in text.lower():
                color = 'rgba(38, 166, 154, 0.3)'
            urls.append({
                'url': href,
                'name': text,
                'color': color
            })
        context['urls'] = urls
    return render(request, 'addRecipes.html', context)

def traverse(nodes, s):
    for node in nodes:
        for child in node.recursiveChildGenerator():
            name = getattr(child, "name", None)
            if name is None and not child.isspace(): # leaf node, don't print spaces
                s.append(child.strip())


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
