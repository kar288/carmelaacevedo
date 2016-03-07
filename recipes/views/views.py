# from django.http import HttpResponse
# from mimetypes import guess_type
# from django.conf import settings
# import csv
# import re
# from random import randint
# from topia.termextract import tag
# from topia.termextract import extract
# import urllib2
# import tldextract
# import xml.etree.ElementTree as ET
# from django.template import loader
# from django.http import JsonResponse
# from django.shortcuts import redirect
# from social.backends.oauth import BaseOAuth1, BaseOAuth2
# from social.backends.google import GooglePlusAuth
# from social.backends.utils import load_backends
# from social.apps.django_app.utils import psa
# from  django.db.models import Q
# import re
# from BeautifulSoup import BeautifulSoup, NavigableString

from datetime import datetime
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from parse import *
from recipes.models import Recipe, Note, RecipeUser
from urlparse import urlparse

import operator

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
    notes = recipeUser.notes.all().order_by('-recipe__date_added')

    allNotes = recipeUser.notes.all().order_by('-recipe__date_added')

    get = request.GET
    notes_per_field = []
    if get:
        for field in get:
            note_per_field = Note.objects.none()
            vals = get.getlist(field)
            for val in vals:
                note_per_field |= recipeUser.notes.filter(**{field + '__icontains': val})
            notes_per_field.append(note_per_field)
    for note_per_field in notes_per_field:
        notes &= note_per_field

    context['notes'] = notes
    context['filters'] = {}
    fields = ['tags', 'site']
    # fields = ['tags', 'site', 'rating']
    for field in fields:
        values = getTopValues(allNotes, field, get.getlist(field))
        if values:
            context['filters'][field] = values
    return render(request, 'index.html', context)

def getTopValues(notes, field, selected):
    vals = {}
    for note in notes:
        noteVals = getattr(note, field, '')
        if field == 'tags':
            noteVals = noteVals.split(',')
        else:
            noteVals = [noteVals]
        for noteVal in noteVals:
            if not noteVal:
                continue
            if not noteVal in vals:
                vals[noteVal] = 0
            vals[noteVal] += 1
    sorted_vals = sorted(vals.items(), key=operator.itemgetter(1))
    sorted_vals_els = []
    for val in sorted_vals:
        sorted_vals_els.append(val[0])
    sorted_vals_els.reverse()
    sorted_vals_els = sorted_vals_els[:10]

    elements = []
    for el in sorted_vals_els:
        elements.append({'name': el, 'selected': el in selected})
    return elements

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
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.none()
    for term in terms:
        notes |= recipeUser.notes.filter(tags__icontains = term)
        notes |= recipeUser.notes.filter(ingredients__icontains = term)
        notes |= recipeUser.notes.filter(title__icontains = term)
        notes |= recipeUser.notes.filter(difficulty__icontains = term)
        notes |= recipeUser.notes.filter(servings__icontains = term)
        notes |= recipeUser.notes.filter(site__icontains = term)
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
    context['tags'] = getTagsForNote(note)
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
    return render(request, 'addRecipe.html', {
        'rates': [5, 4, 3, 2, 1],
        'note': {'rating': -1}
    })

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
            elif field == 'difficulty':
                setattr(note, 'difficulty', post.get('difficulty', '-'))
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
    if not post or not 'recipeUrl' in post or not len(post['recipeUrl']):
        return redirect('/recipes/addRecipe/')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    recipeUrl = post['recipeUrl']
    error = addRecipeByUrl(recipeUser, recipeUrl, post)
    if error:
        return render(request, 'addRecipe.html', {'errors': [error]})
    return redirect('/recipes/')

def getTagsForNote(note):
    tags = ['breakfast', 'lunch', 'dinner', 'snack', 'vegetarian', 'vegan']
    text = note.title
    words = text.split(' ')
    longerWords = [word.lower() for word in words if len(word) > 2 and word[-3:] != 'ing']
    return longerWords + tags

def addRecipeByUrl(recipeUser, recipeUrl, post):
    try:
        recipeData = parseRecipe(recipeUrl)
        extracted = tldextract.extract(recipeUrl)
        recipe = Recipe.objects.create(
          url = recipeUrl,
          image = recipeData['image'],
          ingredients = '\n'.join(recipeData['ingredients']),
          instructions = '\n'.join(recipeData['instructions']),
          title = recipeData['title'],
          date_added = datetime.now()
        )
        servings = post.get('servings', '')
        if 'servings' in recipeData and recipeData['servings']:
            servings = recipeData['servings']
        note = Note.objects.create(
          recipe = recipe,
          url = recipeUrl,
          image = recipeData['image'],
          ingredients = '\n'.join(recipeData['ingredients']),
          instructions = '\n'.join(recipeData['instructions']),
          title = recipeData['title'],
          date_added = datetime.now(),
          text = post.get('notes', ''),
          tags = post.get('tags', '') + ','.join(recipeData['tags']),
          rating = post.get('rating', -1),
          site = extracted.domain,
          difficulty = post.get('difficulty', ''),
          servings = servings
        )
        recipeUser.notes.add(note)
    except urllib2.URLError, err:
        return 'Could not get recipe: ' + recipeUrl
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
    if not post or not 'bookmarks' in request.FILES:
        return render(request, 'addRecipes.html', context)
    if not request.FILES['bookmarks'].name.endswith('.html'):
        return render(request, 'addRecipes.html', {'errors': ['Please upload an html file']})

    try:
        bookmarks = request.FILES['bookmarks'].read()
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
    except Exception as e:
        print e
        return render(request, 'addRecipes.html', {'errors': ['Invalid bookmark file']})
    return render(request, 'addRecipes.html', context)


def save_profile_picture(strategy, user, response, details,
                         is_new=False,*args,**kwargs):
    profile = user.userprofile
    profile.profile_photo.save('{0}_social.jpg'.format(user.username),
                           ContentFile(response.content))
    profile.save()

def save_profile(backend, user, response, *args, **kwargs):
  if backend.name == "google-oauth2":
    try:
      recipeUser = RecipeUser.objects.get(googleUser = user)
    except RecipeUser.DoesNotExist:
      recipeUser = RecipeUser.objects.create(googleUser = user)

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/recipes/')
