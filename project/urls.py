from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import app.views
import recipes.views

# Examples:
# url(r'^$', 'project.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^db', app.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', app.views.home, name='home'),
    url(r'^resume$', app.views.resume, name='resume'),
    url(r'^pictures$', app.views.pictures, name='pictures'),
    url(r'^resumeHtml$', app.views.resumeHtml, name='resumeHtml'),
    url(r'^netflix', app.views.netflix, name='netflix'),
    url(r'^getMovies/(?P<lid>ls[0-9]+)', app.views.getMovies, name='getMovies'),
    url(r'^getMovie/(?P<year>[0-9]+)/(?P<titleName>.+)', app.views.getMovie, name='getMovie'),
    url(r'^googled336ac59e4c9735b.html$', app.views.googleSearch, name='googleSearch'),
    url(r'^recipes/$', recipes.views.home, name='recipesHome'),
    url("^soc/", include("social.apps.django_app.urls", namespace="social")),
    url(r'^login/$', recipes.views.home),
    url(r'^logout/$', recipes.views.logout, name='logout'),
    url(r'^done/$', recipes.views.home, name='done'),
    url(r'^recipes/recrawlImages$', recipes.views.recrawlImages, name='recrawlImages'),
    url(r'^recipes/addNote/$', recipes.views.addNote, name='addNote'),
    url(r'^recipes/addBulk/$', recipes.views.addBulk, name='addBulk'),
    url(r'^recipes/processBulk/$', recipes.views.processBulk, name='processBulk'),
    url(r'^recipes/addRecipe/$', recipes.views.addRecipeHtml, name='addRecipe'),
    url(r'^recipes/addRecipes/$', recipes.views.addRecipesHtml, name='addRecipes'),
    url(r'^recipes/note/(?P<noteId>[0-9]+)/$', recipes.views.note, name='note'),
    url(r'^recipes/editNote/(?P<noteId>[0-9]+)/$', recipes.views.editNote, name='editNote'),
    url(r'^recipes/editNoteHtml/(?P<noteId>[0-9]+)/$', recipes.views.editNoteHtml, name='editNoteHtml'),
    url(r'^recipes/deleteNote/(?P<noteId>[0-9]+)/$', recipes.views.deleteNote, name='deleteNote'),
    url(r'^recipes/deleteNoteHtml/(?P<noteId>[0-9]+)/$', recipes.views.deleteNoteHtml, name='deleteNoteHtml'),
]
