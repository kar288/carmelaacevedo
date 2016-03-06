from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from mimetypes import guess_type
from django.conf import settings
import csv
import re
from random import randint
# import datetime
from datetime import datetime
from topia.termextract import tag
from topia.termextract import extract

import urllib2

from urlparse import urlparse
import tldextract
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

import operator

import re

from BeautifulSoup import BeautifulSoup, NavigableString


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
        #     'field': 'created_at',
        #     'display': 'Date added',
        #     'selected': 'date_added_formatted' == field
        # }, {
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
        context['filters'][field] = getTopValues(allNotes, field, get.getlist(field))
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
    elements = {}
    for el in sorted_vals_els:
        elements[el] = el in selected
    return elements

def recrawlImages(request):
    context = {}
    recipes = Note.objects.all()
    for recipe in recipes:
        if not recipe.image:
            req = urllib2.Request(recipe.url, headers={'User-Agent' : "Magic Browser"})
            html = urllib2.urlopen(req)
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            imageUrl = getImage(soup)
            setattr(recipe, 'image', imageUrl)
            recipe.save()
    return render(request, 'index.html', context)

def convertNotes(request):
    context = {'notes': []}
    notes = Note.objects.all()
    for note in notes:
        recipe = note.recipe
        # setattr(note, 'url', recipe.url)
        # setattr(note, 'title', recipe.title)
        # setattr(note, 'image', recipe.image)
        # setattr(note, 'ingredients', recipe.ingredients)
        # setattr(note, 'instructions', recipe.instructions)
        # setattr(note, 'date_added', recipe.date_added)
        # parsed_uri = urlparse(recipe.url)
        # domain = '{uri.netloc}'.format(uri = parsed_uri)
        # setattr(note, 'site', domain)

        # extracted = tldextract.extract(note.url)
        # setattr(note, 'site', extracted.domain)

        # setattr(note, 'difficulty', Note.NONE)

        # setattr(note, 'tags', note.tags.replace('\n', ','))

        recipeData = parseRecipe(note.url)

        if len(recipeData['ingredients']) and note.ingredients == '':
            setattr(note, 'ingredients', '\n'.join(recipeData['ingredients']))

        if len(recipeData['instructions']) and note.instructions == '':
            setattr(note, 'instructions', '\n'.join(recipeData['instructions']))

        if 'servings' in recipeData and len(recipeData['servings']) and note.servings == '':
            setattr(note, 'servings', recipeData['servings'])
        # date = datetime.strptime(recipe.date_added, "%Y-%m-%d %H:%M:%S.%f")
        # # print date
        # setattr(note, 'created_at', date)
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
    if not post:
        return redirect('/recipes/addRecipe/')
    recipeUser = get_object_or_404(RecipeUser, googleUser = request.user)
    if 'recipeUrl' in post:
        recipeUrl = post['recipeUrl']
        addRecipeByUrl(recipeUser, recipeUrl, post)
    return redirect('/recipes/')

def getImage(soup, attr=None, key=None):
    imageUrl = ''
    attrs = [attr] if attr is not None else [
        {"property": "og:image"},
        {"name": "twitter:image:src"},
        {"itemprop": "image"},
        {"rel": "image_src"}
    ]
    keys = [key] if key is not None else [
        'content',
        'src',
        'href'
    ]
    for attr in attrs:
        image = soup.find(attrs={"property": "og:image"})
        if image:
            for key in keys:
                if image.has_key(key):
                    imageUrl = image[key]
                    break
        if imageUrl:
            break
    if not imageUrl:
        images = soup.findAll('img')
        imageUrl = images[0]['src']

    return imageUrl

def getTags(soup, attr=None, link=None):
    tagsResult = []
    tagAttrs = [attr] if attr is not None else [
        {'itemprop': 'keywords'},
        {'name': 'keywords'},
        {'property': 'article:tag'},
        {'name': 'sailthru.tags'},
        {'name': 'parsely-tags'}
    ]
    tagLinks = []
    if link is None:
        tagLinks = [
            'tags-nutrition-container',
            re.compile(r'.*post-categories.*'),
            re.compile(r'.*postmetadata.*')
        ]
    elif link:
        tagLinks = [link]
    tagContainer = None
    for tagLink in tagLinks:
        tagContainer = soup.findAll(attrs={'class': tagLink})
        if tagContainer:
            break
    if tagContainer and len(tagContainer):
        tags = tagContainer[0].findAll('a')
        tagVals = [tag.text.lower() for tag in tags]
        tagsResult = tagVals
    else:
        print tagAttrs
        for tagAttr in tagAttrs:
            print tagAttr
            tags = soup.findAll(attrs=tagAttr)
            tagsArray = [tag['content'].lower() for tag in tags if 'content' in tag]
            if len(tagsArray) == 1 and ',' in tagsArray[0]:
                tagsArray = tagsArray[0].split(',')
            tagsArray = [tag.strip() for tag in tagsArray]
            tagsResult = tagsArray
            if len(tagsArray):
                break
    return tagsResult

def getTagsForNote(note):
    tags = ['breakfast', 'lunch', 'dinner', 'snack', 'vegetarian', 'vegan']
    text = note.title
    words = text.split(' ')
    longerWords = [word.lower() for word in words if len(word) > 2 and word[-3:] != 'ing']
    return longerWords + tags

def traverse(nodes, separator):
    texts = []
    for node in nodes:
        parts = []
        for part in node.findAll(text=True):
            stripped = part.strip()
            if len(stripped):
                parts.append(stripped)
        texts.append(separator.join(parts))
    return texts
    # return '\n'.join(texts)

def testRecipes(request):
    testUrls = [
        'http://smittenkitchen.com/blog/2016/02/roasted-yams-and-chickpeas-with-yogurt/',
        # 'http://smittenkitchen.com/blog/2016/03/churros/#more-17497',
        # 'http://www.thekitchn.com/recipe-crispy-garlic-pita-breads-recipes-from-the-kitchn-216127',
        # # 'http://www.thekitchn.com/recipe-blistered-tomato-toasts-228917',
        # 'http://www.epicurious.com/recipes/food/views/fresh-coconut-layer-cake-241213',
        # 'http://food52.com/recipes/41455-pudding-style-buttercream',
        # 'http://www.bonappetit.com/recipe/colcannon',
        # 'http://www.myrecipes.com/recipe/broccoli-casserole-3',
        # 'http://www.davidlebovitz.com/2016/02/tangerine-sorbet-ice-cream-recipe/',
        # 'http://cooking.nytimes.com/recipes/11631-soft-scrambled-eggs-with-pesto-and-fresh-ricotta?smid=fb-nytdining&smtyp=cur',
        # 'http://www.chowhound.com/recipes/slow-cured-corned-beef-31292'
    ]
    results = []
    for recipeUrl in testUrls:
        results.append(parseRecipe(recipeUrl))
    return JsonResponse({'results': results})

def parseRecipe(url):
    #TEST
    # get = request.GET
    # recipeUrl = get['url']
    recipe = {'url': url}
    try:
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        html = urllib2.urlopen(req)
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        print url
        if 'nyt' in url:
            parseNYT(soup, recipe)
        elif 'food52' in url:
            parseFood52(soup, recipe)
        elif 'epicurious' in url:
            parseEpicurious(soup, recipe)
        elif 'davidlebovitz' in url:
            parseDavidLebovitz(soup, recipe)
        elif 'myrecipes' in url:
            parseMyRecipes(soup, recipe)
        elif 'bonappetit' in url:
            parseBonAppetit(soup, recipe)
        elif 'chowhound' in url:
            parseChowhound(soup, recipe)
        elif 'smittenkitchen' in url:
            parseSmittenKitchen(soup, recipe)
        else:
            parseGeneral(url, soup, recipe)
    except urllib2.HTTPError, err:
        print 'Could not get recipe: ' + recipeUrl
    return recipe

def parserTemplate(soup, recipe, tagAttr, tagLink, ingredientAttr):
    recipe['title'] = soup.find(attrs={'property': 'og:title'})['content']
    recipe['tags'] = getTags(soup, tagAttr, tagLink)
    instructionElements = soup.findAll(attrs={'itemprop': 'recipeInstructions'})
    recipe['instructions'] = traverse(instructionElements, '\n')
    ingredientElements = soup.findAll(attrs={'itemprop': ingredientAttr})
    recipe['ingredients'] = traverse(ingredientElements, ' ')
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    return recipe


def parseNYT(soup, recipe):
    return parserTemplate(soup, recipe,
        {},
        'tags-nutrition-container',
        'recipeIngredient'
    )

def parseBonAppetit(soup, recipe):
    return parserTemplate(soup, recipe,
        {'property': 'article:tag'},
        '',
        'ingredients'
    )

def parseChowhound(soup, recipe):
    return parserTemplate(soup, recipe,
        {},
        re.compile(r'.*freyja_tagslist.*'),
        'ingredients'
    )

def parseEpicurious(soup, recipe):
    return parserTemplate(soup, recipe,
        {'itemprop': 'keywords'},
        '',
        'ingredients'
    )

def parseFood52(soup, recipe):
    return parserTemplate(soup, recipe,
        {'name': 'sailthru.tags'},
        '',
        'ingredients'
    )

def parseMyRecipes(soup, recipe):
    return parserTemplate(soup, recipe,
        {'name': 'keywords'},
        '',
        'recipeIngredient'
    )

def parseDavidLebovitz(soup, recipe):
    return parserTemplate(soup, recipe,
        {'property': 'article:tag'},
        '',
        'recipeIngredient'
    )

def parseSmittenKitchen(soup, recipe):
    recipe['title'] = soup.find('a', attrs={'rel': 'bookmark'}).text
    recipe['tags'] = getTags(soup, {}, re.compile(r'.*postmetadata.*'))
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    instructions = []
    ingredients = []
    recipe['ingredients'] = ingredients
    recipe['instructions'] = instructions

    servings = soup.body.find(text=re.compile('^(Serve|Yield)[s]*.*'))
    if not servings:
        return recipe
    node = servings.parent
    recipe['servings'] = ' '.join(node.findAll(text=True)).strip()
    while True:
        node = node.nextSibling
        if isinstance(node, NavigableString):
            continue
        if node.name == 'script':
            break

        texts = node.findAll(text=True)
        texts = [i.strip() for i in texts]
        if node.find('br'):
            ingredients += texts
        else:
            instructions += texts
    recipe['ingredients'] = ingredients
    recipe['instructions'] = instructions
    return recipe

def parseGeneral(url, soup, recipe):
    recipe['image'] = getImage(soup)
    ogTitle = soup.find(attrs={'property': 'og:title'})
    if ogTitle:
        recipe['title'] = ogTitle['content']
    else:
        recipe['title'] = soup.title.string

    instructionElements = soup.findAll(attrs={'itemprop': 'recipeInstructions'})
    recipe['instructions'] = traverse(instructionElements, '\n')
    recipe['tags'] = getTags(soup)
    ingredientElements = soup.findAll(attrs={'itemprop': 'recipeIngredient'})
    if not len(ingredientElements):
        ingredientElements = soup.findAll(attrs={'itemprop': 'ingredients'})
    recipe['ingredients'] = traverse(ingredientElements, ' ')

    return recipe

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
        if recipeData['servings']:
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
    return render(request, 'addRecipes.html', context)


def save_profile_picture(strategy, user, response, details,
                         is_new=False,*args,**kwargs):

  # if strategy.backend.name == "google-oauth2":
    profile = user.userprofile
    profile.profile_photo.save('{0}_social.jpg'.format(user.username),
                           ContentFile(response.content))
    profile.save()

def save_profile(backend, user, response, *args, **kwargs):
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
