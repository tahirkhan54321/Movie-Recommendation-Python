# This file is where you define your data models, 
# which are Python classes that represent database tables.

from django.db import models
from django.contrib.auth.models import User

#users
#ratings
#movies

class Movies(models.Model):
    id = models.IntegerField()
    title = models.CharField(max_length=200)
    actor0 = models.CharField(max_length=200)
    actor1 = models.CharField(max_length=200)
    actor2 = models.CharField(max_length=200)
    actor3 = models.CharField(max_length=200)
    actor4 = models.CharField(max_length=200)
    character0 = models.CharField(max_length=200)
    character2 = models.CharField(max_length=200)
    character3 = models.CharField(max_length=200)
    character4 = models.CharField(max_length=200)
    character5 = models.CharField(max_length=200)
    gender = models.IntegerField()
    director = models.CharField(max_length=200)
    writer = models.CharField(max_length=200)
    composer = models.CharField(max_length=200)