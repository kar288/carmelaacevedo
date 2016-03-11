import tldextract
import urllib2
import os
import codecs
import sys
import urllib2
from BeautifulSoup import BeautifulSoup, NavigableString
# from django.shortcuts import render, redirect, get_object_or_404
from parse import *
# from recipes.models import Recipe, Note, RecipeUser

def getRecipes(index):
    urlsFile = open('./media/urls.txt', 'r')
    recipesFile = codecs.open('./media/recipes.csv','a','utf-8')

    for i, line in enumerate(urlsFile):
        if i < index:
            continue
        else:
            recipe = parseRecipe(line.strip())
            print i, recipe['url']
            if len(recipe['tags']):
                recipeStr = '"' + recipe['title'] + '",' \
                + '"' + recipe['url'] + '",' \
                + '"' + ' '.join(recipe['tags']) + '",' \
                + '"' + ' '.join(recipe['ingredients']).replace('\n', '') + '",' \
                + '"' + ' '.join(recipe['instructions']).replace('\n', '') + '"\n'
                recipesFile.write(recipeStr)
    urlsFile.close()
    recipesFile.close()

def getRecipesNYT(index, fileName):
    urlsFile = open(fileName, 'r')
    recipesFile = codecs.open('./media/recipesNYT.csv','a','utf-8')

    for i, line in enumerate(urlsFile):
        if i < index:
            continue
        else:
            recipe = parseRecipe(line.strip())
            print i, recipe['url']
            if len(recipe['tags']):
                recipeStr = '"' + recipe['title'] + '",' \
                + '"' + recipe['url'] + '",' \
                + '"' + ' '.join(recipe['tags']) + '",' \
                + '"' + ' '.join(recipe['ingredients']).replace('\n', '') + '",' \
                + '"' + ' '.join(recipe['instructions']).replace('\n', '') + '"\n'
                recipesFile.write(recipeStr)
    urlsFile.close()
    recipesFile.close()

def getRecipesFood52(index, fileName):
    # urlsFile = open(fileName, 'r')
    recipesFile = codecs.open('./media/recipesFood52.csv','a','utf-8')

    for i in range(index, 40800):
        if i < index:
            continue
        else:
            try:
                recipe = parseRecipe('http://food52.com/recipes/' + str(i))
                print i, recipe['url']
                if len(recipe['tags']):
                    recipeStr = '"' + recipe['title'] + '",' \
                    + '"' + recipe['url'] + '",' \
                    + '"' + ' '.join(recipe['tags']) + '",' \
                    + '"' + ' '.join(recipe['ingredients']).replace('\n', '') + '",' \
                    + '"' + ' '.join(recipe['instructions']).replace('\n', '') + '"\n'
                    recipesFile.write(recipeStr)
            except urllib2.HTTPError, e:
                print e
    # urlsFile.close()
    recipesFile.close()

def getUrls():
    recipesFile = codecs.open('./media/urlsNYT.txt','a','utf-8')
    for i in range(368):
        print 'page ' + str(i)
        url = 'http://cooking.nytimes.com/search?q=&page=' + str(i)
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        html = urllib2.urlopen(req)
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        articles = soup.findAll(attrs={'data-type': "recipe"})
        urls = [article.get('data-url') for article in articles if article.get('data-url')]
        for url in urls:
            recipesFile.write('http://cooking.nytimes.com' + url + '\n')
    recipesFile.close()

# def getUrlsFood52():
#     recipesFile = codecs.open('./media/urlsFood52.txt','a','utf-8')
#     seasons = ['summer', 'winter']
#     sizes = [482, 507]
#     start = [0, 0]
#     for j in range(4):
#         for i in range(start[j], sizes[j]):
#             print 'page ' + str(i) + ' ' + seasons[j]
#             url = 'http://food52.com/recipes/' + seasons[j] + '?page=' + str(i)
#             req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
#             html = urllib2.urlopen(req)
#             soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
#             articles = soup.findAll(attrs={'data-type': "recipe"})
#             urls = [article.find('a').get('href') for article in articles]
#             for url in urls:
#                 recipesFile.write('http://food52.com' + url + '\n')
#     recipesFile.close()
#
# smittenkitchen
# http://smittenkitchen.com/recipes/
# lists = document.getElementsByClassName('entry')[0].getElementsByClassName('lcp_catlist')
# for (var i = 0; i < lists.length; i++) {
#   links = lists[i].getElementsByTagName('a');
#   for (var j = 0; j < links.length; j++) {
#     a.push(links[j])
#   }
# }
# ~4000

if __name__ == "__main__":
    # if len(sys.argv):
    #     print 'not enough arguments'
    # else:
    if sys.argv[1] == 'getRecipes':
        getRecipes(4231)
    elif sys.argv[1] == 'getRecipesNYT':
        getRecipesNYT(17158, './media/urlsNYT.txt')
    elif sys.argv[1] == 'getRecipesFood52':
        getRecipesFood52(37856, './media/recipesFood52.txt')
    elif sys.argv[1] == 'getUrls':
        getUrls()
    elif sys.argv[1] == 'getUrlsFood52':
        getUrlsFood52()
