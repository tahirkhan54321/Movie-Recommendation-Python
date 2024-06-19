# This file is where you define your data models, 
# which are Python classes that represent database tables.

from django.db import models
from django.contrib.auth.models import User

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