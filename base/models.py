# This file is where you define your data models, 
# which are Python classes that represent database tables.

from django.db import models
from django.contrib.auth.models import User

#users
#ratings
#movies

class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    actor0 = models.CharField(max_length=200, null=True)
    actor1 = models.CharField(max_length=200, null=True)
    actor2 = models.CharField(max_length=200, null=True)
    actor3 = models.CharField(max_length=200, null=True)
    actor4 = models.CharField(max_length=200, null=True)
    character0 = models.CharField(max_length=200, null=True)
    character1 = models.CharField(max_length=200, null=True)
    character2 = models.CharField(max_length=200, null=True)
    character3 = models.CharField(max_length=200, null=True)
    character4 = models.CharField(max_length=200, null=True)
    # gender = models.IntegerField()
    director = models.CharField(max_length=200, null=True)
    writer = models.CharField(max_length=200, null=True)
    composer = models.CharField(max_length=200, null=True)