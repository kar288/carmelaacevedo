from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from mimetypes import guess_type
from django.conf import settings
import csv
import re
from random import randint

import urllib2
import xml.etree.ElementTree as ET
from NetflixRoulette import *
from django.template import loader, Context
from django.http import JsonResponse

from .models import Greeting


# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


def index(request):
  return HttpResponse('Hello from Python!')

def home(request):
  els = [{
    'title': 'OpenMathMap',
    'url': 'http://map.mathweb.org',
    'image': 'images/openmathmap-thumbnail-bw.png',
    'text': ['Bachelor Thesis Project:',
      'An interactive map interface that helps user navigate through the world of math.',
      'Conducted user studies to evaluate the system.'
    ]
  }, {
    'title': 'Pricer',
    'url': 'http://pricer.herokuapp.com',
    'image': 'images/pricer-thumbnail.png',
    'text': ['Class project',
      'Guess prices of amazon items in a fun game inspired from the Price is Rigtht.',
      'Using Django, jQuery and the Amazon API to create a web application'
    ]
  }, {
    'title': 'Movie finder',
    'url': '/netflix/ls000426137',
    'image': 'images/netflix-imdb.png',
    'text': ['Weekend project:',
      'Find out which movies or series of an IMDB list are in Netflix.'
    ]
  }, {
    'title': 'Photography',
    'url': '/pictures',
    'image': 'images/photography-thumbnail.png',
    'text': ['Showcase of personal photography projects.',
      'It includes a project studying linear photography inspired by Gego.'
    ]
  }];
  print(els)
  return render(request, 'homePortfolio.html', {'homeCards': els});

def resume(request):
  with open(settings.MEDIA_ROOT + 'Resume.pdf', 'r') as pdf:
    response = HttpResponse(pdf.read(), content_type='application/pdf')
  response['Content-Disposition'] = 'inline;filename=CarmelaAcevedo.pdf'
  response['title'] = 'Carmela Acevedo - Resume'
  return response
  pdf.closed

def resumeHtml(request):
  return render(request, 'resume.html', {})

def pictures(request):
  pics = [];
  for i in range(14):
    pics.append('images/mutableLandscapes' + str(i + 2) + '.png');
  return render(request, 'pictures.html', {'pics': pics});

def getMovie(request, year, titleName):
  try:
    netflixData = get_all_data(titleName, int(year))
    if netflixData:
      print netflixData
      data = {
        'show_id': netflixData['show_id'],
        'poster': netflixData['poster'],
        'show_title': netflixData['show_title'],
        'release_year': netflixData['release_year'],
        'summary': netflixData['summary'],
        'director': netflixData['director'],
        'runtime': netflixData['runtime'],
        'category': netflixData['category'],
        'color': ['#F7F9FE', '#ECF1F2', '#DCE8EB', '#CBDBE0', '#BED2D9'][randint(0, 5)],
      }
      return render(request, 'movie.html', data)
    else:
      return JsonResponse({})
  except:
    return JsonResponse({})

def getMovies(request, lid):
  num = re.compile('(.*) \(([0-9]+)')
  # listID = 'ls072734994';
  # listID = 'ls000426137';

  url = 'http://rss.imdb.com/list/' + lid + '/'
  response = urllib2.urlopen(url).read();
  print response;
  root = ET.fromstring(response).find('channel');
  listTitle = root.find('title').text
  listDescription = root.find('description').text
  items = root.findall('item');
  movies = [];
  for node in items:
    title = node.find('title');
    titleName, year = num.findall(title.text)[0];
    movies.append({'title': titleName, 'year': year});
  return JsonResponse({
    'movies': movies,
    'title': listTitle,
    'description': listDescription,
  })

def netflix(request):
  return render(request, 'netflix.html');

def googleSearch(request):
  return render(request, 'googled336ac59e4c9735b.html');
