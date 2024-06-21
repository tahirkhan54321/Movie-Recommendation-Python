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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Global variables
# vectorizer = TfidfVectorizer(ngram_range=(1,2))
# tfidf = vectorizer.fit_transform(Movie.objects.values_list('cleaned_title', flat=True))

# TBC - objective:
# 1 - pull in the form submission
# 2 - validate the form submission
# 3 - find the right movie to and assign to value
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
            # Find Similar Movies
            similar_movies = find_similar_movies(cleaned_movie_title)
            return render(request, 'movie_search.html', {'similar_movies': similar_movies})
        else:
            messages.error(request, "Invalid movie title")

    return render(request, 'movie_search.html')
    
def find_similar_movies(title):
    query_vec = vectorizer.transform([title])
    similarity = cosine_similarity(query_vec, tfidf).flatten()

    # Get top 10 similar movie IDs
    top_indices = np.argsort(similarity)[-10:][::-1]  # Reverse for descending order
    movie_ids = [Movie.objects.values_list('id', flat=True)[i] for i in top_indices]
    
    # Fetch Movie Objects
    similar_movies = Movie.objects.filter(id__in=movie_ids) 

    return similar_movies

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)