# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from .models import Movie
import sklearn
from django.http import HttpResponse
from django.contrib import messages # for error messages
from django.shortcuts import render, redirect
import pandas as pd
from .forms import MovieForm
import re
from sklean.feature_extraction.text import Tf

# objective:
# 1 - pull in the form submission
# 2 - validate the form submission
# 3 - find the right movie to and assign to value (icontains)
# 4 - use TFIDF to find most relevant movies
# 5 - return only 10 of the relevant movies
# 6 - render them in a table
def movie_search(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            movie_title = form.cleaned_data['title']
            cleaned_movie_title = clean_title(movie_title)
        else:
            messages.error(request, "Could not find movie")
        

    return render(request, 'movie_search.html')

# helper function
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)