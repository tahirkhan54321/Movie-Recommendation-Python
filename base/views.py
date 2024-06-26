# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from django.http import HttpResponse
from django.contrib import messages # for error messages
from django.shortcuts import render, redirect
from .forms import MovieForm
import re
from .utils import initialize_tfidf, find_similar_movies

# Global variables
vectorizer = None
tfidf = None

# TBC - objective:
# 1 - pull in the form submission
# 2 - validate the form submission
# 3 - find the right movie from the database to match the input (using cleaned_title), confirm this in the form (dropdown?)
# 4 - use TFIDF to find most relevant movies using the movies.composite_string for both the input and the matrix
# 5 - return the 10 most relevant movies
# 6 - render them in a table

def movie_search(request):
    form = MovieForm(request.POST or None)
    similar_movies = None

    if request.method == 'POST':
        if form.is_valid():
            movie_title = form.cleaned_data['title'].lower() # django boilerplate to ensure data consistency
            cleaned_movie_title = clean_title(movie_title)
            # vectorizer not initialised at beginning due to circular import errors
            initialize_tfidf()
            # Find Similar Movies
            similar_movies = find_similar_movies(cleaned_movie_title)
        else:
            messages.error(request, "Invalid movie title, please try another")

    return render(request, 'movie_search.html', {'form': form, 'similar_movies': similar_movies})


# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)