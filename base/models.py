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