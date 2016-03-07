import tldextract
import re
import urllib2

from BeautifulSoup import BeautifulSoup, NavigableString

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
        for tagAttr in tagAttrs:
            tags = soup.findAll(attrs=tagAttr)
            tagsArray = [tag['content'].lower() for tag in tags if tag and tag.has_key('content')]
            if len(tagsArray) == 1 and ',' in tagsArray[0]:
                tagsArray = tagsArray[0].split(',')
            tagsArray = [tag.strip() for tag in tagsArray]
            tagsResult = tagsArray
            if len(tagsArray):
                break
    return tagsResult

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
        # 'http://smittenkitchen.com/blog/2016/02/roasted-yams-and-chickpeas-with-yogurt/',
        # 'http://www.epicurious.com/recipes/food/views/chicken-skewers-with-meyer-lemon-salsa-380587',
        # 'http://smittenkitchen.com/blog/2016/03/churros/#more-17497',
        'http://www.thekitchn.com/recipe-crispy-garlic-pita-breads-recipes-from-the-kitchn-216127',
        'http://www.thekitchn.com/recipe-blistered-tomato-toasts-228917',
        'http://www.thekitchn.com/how-to-make-basic-white-sandwich-bread-cooking-lessons-from-the-kitchn-166588',
        'http://www.thekitchn.com/how-to-make-brioche-224507',
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
    if not url.startswith('http'):
        url = 'http://' + url
    recipe = {'url': url}
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
    elif 'thekitchn' in url:
        parseTheKitchn(soup, recipe)
    else:
        parseGeneral(url, soup, recipe)
    return recipe

def parserTemplate(soup, recipe, tagAttr, tagLink, ingredientAttr):
    recipe['title'] = soup.find(attrs={'property': 'og:title'})['content']
    recipe['tags'] = getTags(soup, tagAttr, tagLink)
    instructionElements = soup.findAll(attrs={'itemprop': 'recipeInstructions'})
    recipe['instructions'] = traverse(instructionElements, '\n')
    ingredientElements = soup.findAll(attrs={'itemprop': ingredientAttr})
    recipe['ingredients'] = traverse(ingredientElements, ' ')
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    servings = soup.findAll(attrs={'itemprop': 'recipeYield'})
    recipe['servings'] = ' '.join(traverse(servings, ' '))
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

    servings = soup.body.find(text=re.compile('^(Serve|Yield|Make)[s]*.*'))
    if not servings:
        return recipe
    node = servings.parent
    recipe['servings'] = ' '.join(node.findAll(text=True)).strip()
    while True:
        node = node.nextSibling
        if isinstance(node, NavigableString):
            continue
        if not node or node.name == 'script':
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

def parseTheKitchn(soup, recipe):
    recipe['title'] = soup.find(attrs={'property': 'og:title'})['content']
    recipe['tags'] = getTags(soup, {}, re.compile(r'.*post-categories.*'))
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    servings = soup.findAll(attrs={'itemprop': 'recipeYield'})
    recipe['servings'] = ' '.join(traverse(servings, ' '))

    ingredientElements = soup.findAll(attrs={'itemprop': 'ingredients'})
    recipe['ingredients'] = traverse(ingredientElements, ' ')

    instructions = []
    ingredients = []

    node = soup.body.find(text=re.compile('^(Serves|Yield|Makes)[s]*[: ].*'))
    recipe['servings'] = node
    if not node or node == None:
        return recipe
    while isinstance(node, NavigableString) or not node.name == 'p':
        if node.parent:
            node = node.parent
        else:
            break
    while True:
        node = node.nextSibling
        if isinstance(node, NavigableString):
            continue
        if not node or node.name == 'script':
            break

        texts = node.findAll(text=True)
        texts = [i.strip() for i in texts if len(i.strip())]
        if node.find('br') and not node.find('li'):
            ingredients += texts
        else:
            instructions += texts
    if not len(recipe['ingredients']):
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

    servings = soup.findAll(attrs={'itemprop': 'recipeYield'})
    recipe['servings'] = ' '.join(traverse(servings, ' '))

    return recipe
