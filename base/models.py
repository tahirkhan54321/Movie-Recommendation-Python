# This file is where you define your data models, 
# which are Python classes that represent database tables.

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

#users
#ratings
#movies

class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    cleaned_title = models.CharField(max_length=255)
    actors = models.TextField(null=True)
    characters = models.TextField(null=True)
    director = models.TextField(null=True)
    writer = models.TextField(null=True)
    composer = models.TextField(null=True)
    composite_string = models.TextField(null=True)
    budget = models.IntegerField(null=True)
    genres = models.TextField(null=True)
    homepage = models.URLField(null=True)
    keywords = models.TextField(null=True)
    language = models.CharField(max_length=255, null=True)
    overview = models.TextField(null=True)
    production_companies = models.TextField(null=True)
    production_countries = models.TextField(null=True)
    release_date = models.DateField(null=True)
    revenue	= models.IntegerField(null=True)
    runtime	= models.IntegerField(null=True)
    spoken_languages = models.TextField(null=True)
    status = models.CharField(max_length=255, null=True)
    tagline	= models.TextField(null=True)

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    #tbc - add review