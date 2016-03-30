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
# from django.shortcuts import redirect
# from social.backends.oauth import BaseOAuth1, BaseOAuth2
# from social.backends.google import GooglePlusAuth
# from social.backends.utils import load_backends
# from social.apps.django_app.utils import psa
# from  django.db.models import Q
# import re
# from BeautifulSoup import BeautifulSoup, NavigableString

from datetime import datetime, date
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from parse import *
from recipes.models import Recipe, Note, RecipeUser, Month
from urlparse import urlparse

import math
import operator

PAGE_SIZE = 12

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


def pagination(request, context, page, notes):
    queries_without_page = request.GET.copy()
    if queries_without_page.has_key('page'):
        del queries_without_page['page']
    start = (page - 1) * PAGE_SIZE
    end = min(len(notes), start + PAGE_SIZE)
    pages = range(1, int(math.ceil(len(notes) / (PAGE_SIZE * 1.0))) + 1)
    context['notes'] = notes[start:end]
    context['pages'] = pages
    context['page'] = page
    context['filters'] = {}
    context['queries'] = queries_without_page
    context['previous'] = page - 1 if page - 1 > 0 else 0
    context['next'] = page + 1 if page + 1 <= len(pages) else 0

def home(request):
    context = {}
    if not request.user.is_authenticated():
        return render(request, 'recipeBase.html', context)
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = recipeUser.notes.all().order_by('-recipe__date_added')

    allNotes = recipeUser.notes.all().order_by('-recipe__date_added')

    get = request.GET
    notes_per_field = []

    page = 1
    for field in get:
        note_per_field = Note.objects.none()
        vals = get.getlist(field)
        if field == 'page':
            page = int(get.get(field))
            continue
        for val in vals:
            note_per_field |= recipeUser.notes.filter(**{field + '__icontains': val})
        notes_per_field.append(note_per_field)
    for note_per_field in notes_per_field:
        notes &= note_per_field
    pagination(request, context, page, notes)
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
def shareNote(request, noteId):
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    try:
        note = recipeUser.notes.get(id = noteId)
    except:
        return JsonResponse({'success': False})
    setattr(note, 'shared', True)
    note.save()
    return JsonResponse({'success': True})

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def addSharedRecipe(request, noteId):
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    try:
        note = recipeUser.notes.find(id = noteId)
        return redirect('/recipes/note/' + noteId)
    except:
        try:
            note = get_object_or_404(Note, id = noteId)
            if not note.shared:
                context = {}
                context['errors'] = ['No such recipe']
                return redirect('/recipes/')
        except:
            context = {}
            context['errors'] = ['No such recipe']
            return redirect('/recipes/')
    note.pk = None
    recipe = note.recipe
    recipe.pk = None
    recipe.save()
    note.recipe = recipe
    note.save()
    recipeUser.notes.add(note)
    return redirect('/recipes/note/' + str(note.id))

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
    note = None
    try:
        note = recipeUser.notes.get(id = noteId)
    except:
        note = get_object_or_404(Note, id = noteId)
        context['shared'] = True
        print int(request.GET.get('share', '0'))
        if note.shared == False or not int(request.GET.get('share', '0')):
            raise Http404("No such recipe.")
    context['note'] = note
    context['shareUrl'] = \
        request.build_absolute_uri('/')[:-1] + request.get_full_path() + '?share=1'
    return render(request, 'note.html', context)

@login_required(login_url='/soc/login/google-oauth2/?next=/recipes/')
def tags(request, tags):
    context = {}
    tags = tags.split(',')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.none()
    for tag in tags:
        notes |= recipeUser.notes.filter(tags__icontains = tag)
    pagination(request, context, int(request.GET.get('page', '1')), notes)
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
    page = int(get.get('page', '1'))
    pagination(request, context, page, notes)
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
def getSeasonRecipes(request, month):
    context = {}
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    notes = Note.objects.none()
    if not month:
        month = datetime.now().strftime("%b")
        print month
    month = Month.objects.filter(name__icontains=month)
    if len(month):
        ingredients = month[0].ingredients.split(',')
        for ingredient in ingredients:
            notes |= recipeUser.notes.filter(ingredients__icontains = ingredient)
        context['selected'] = date(1900, month[0].index, 1).strftime('%b')
        context['selectedIndex'] = month[0].index
    months = Month.objects.all()
    ingredientSeasons = {}
    for month in months:
        ingredients = month.ingredients.split(',')
        for ingredient in ingredients:
            seasons = {}
            if ingredient in ingredientSeasons:
                seasons = ingredientSeasons[ingredient]
            seasons[month.index] = True
            ingredientSeasons[ingredient] = seasons
    context['ingredientSeasons'] = {}
    for ingredient in ingredientSeasons:
        months = []
        for i in range(1, 13):
            if i in ingredientSeasons[ingredient]:
                months.append(i)
            else:
                months.append(False)
        context['ingredientSeasons'][ingredient] = months
    context['months'] = ['']
    for i in range(1, 13):
        context['months'].append(date(1900, i, 1).strftime('%b'))

    context['notes'] = notes
    # context['success'] = ingredients
    return render(request, 'seasonal.html', context)


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
    return redirect('/recipes/')

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
        domain = tldextract.extract(recipeUrl).domain
        image = recipeData.get('image', '')
        instructions = '\n'.join(recipeData.get('instructions', []))
        ingredients = '\n'.join(recipeData.get('ingredients', []))
        title = recipeData.get('title')
        servings = post.get('servings', '')
        if 'servings' in recipeData and recipeData['servings']:
            servings = recipeData['servings']
        recipe = Recipe.objects.create(
          url = recipeUrl,
          image = image,
          ingredients = ingredients,
          instructions = instructions,
          title = title,
          date_added = datetime.now()
        )
        note = Note.objects.create(
          recipe = recipe,
          url = recipeUrl,
          image = image,
          ingredients = ingredients,
          instructions = instructions,
          title = title,
          date_added = datetime.now(),
          text = post.get('notes', ''),
          tags = post.get('tags', '') + ','.join(recipeData['tags']),
          rating = post.get('rating', -1),
          site = domain,
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
        soup = BeautifulSoup(bookmarks)
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



def testRecipes(request):
    testUrls = [
        # 'http://cookieandkate.com/2014/feta-fiesta-kale-salad-with-avocado-and-crispy-tortilla-strips/',
        # 'http://cookieandkate.com/2016/lemon-curd-recipe/',
        # 'http://smittenkitchen.com/blog/2016/02/roasted-yams-and-chickpeas-with-yogurt/',
        # 'http://www.epicurious.com/recipes/food/views/chicken-skewers-with-meyer-lemon-salsa-380587',
        # 'http://smittenkitchen.com/blog/2016/03/churros/#more-17497',
        # 'http://www.thekitchn.com/recipe-crispy-garlic-pita-breads-recipes-from-the-kitchn-216127',
        # 'http://www.thekitchn.com/recipe-blistered-tomato-toasts-228917',
        # 'http://www.thekitchn.com/how-to-make-basic-white-sandwich-bread-cooking-lessons-from-the-kitchn-166588',
        # 'http://www.thekitchn.com/how-to-make-brioche-224507',
        # 'http://www.epicurious.com/recipes/food/views/fresh-coconut-layer-cake-241213',
        # 'http://food52.com/recipes/41455-pudding-style-buttercream',
        # 'http://www.bonappetit.com/recipe/colcannon',
        # 'http://www.myrecipes.com/recipe/broccoli-casserole-3',
        # 'http://www.davidlebovitz.com/2016/02/tangerine-sorbet-ice-cream-recipe/',
        # 'http://cooking.nytimes.com/recipes/11631-soft-scrambled-eggs-with-pesto-and-fresh-ricotta?smid=fb-nytdining&smtyp=cur',
        'http://cooking.nytimes.com/recipes/5598-aligot',
        # 'http://www.chowhound.com/recipes/slow-cured-corned-beef-31292'
    ]
    results = []
    for recipeUrl in testUrls:
        results.append(parseRecipe(recipeUrl))
    return JsonResponse({'results': results})
