# This file is used to customize the built-in Django admin interface, 
# where you can register your models 
# and configure how they should be displayed and edited.

from django.contrib import admin
from .models import Movie

admin.site.register(Movie)