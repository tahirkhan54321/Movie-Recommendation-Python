# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from .models import Movie
from django.http import HttpResponse
from django.contrib import messages # for error messages
from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from .forms import MovieForm
import re
from sklean.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# TBC - objective:
# 1 - pull in the form submission
# 2 - validate the form submission
# 3 - find the right movie to and assign to value (icontains)
# 4 - use TFIDF to find most relevant movies
# 5 - return only 10 of the relevant movies
# 6 - render them in a table
def movie_search(request):
    # 1, 2 - pull in and validate
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            movie_title = form.cleaned_data['title']
            cleaned_movie_title = clean_title(movie_title)
        else:
            messages.error(request, "Invalid movie title")
    
    # 3 - find the right movie and assign its value
    # TBC - what if we find more than one movie?


    # 3.5 - extract the searched movie composite string

    # 4 - TBC - use TFIDF to find relevant composite strings
        vectorizer = TfidfVectorizer(ngram_range=(1,2))
        tfidf = vectorizer.fit_transform(Movie["cleaned_movie_title"]) # TBC

    # 5 - get the movie ids and return only 10 relevant movies

    # 6 - render them in a table
        

    return render(request, 'movie_search.html')

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)

# TBC - example code to be refactored into a true search
def search(title):
    title = clean_title(title)
    query_vec = vectorizer.transform([title])
    similarity = cosine_similarity(query_vec, tfidf).flatten()