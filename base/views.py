# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from django.contrib import messages # for error messages
from django.shortcuts import render, redirect
from .forms import MovieForm, CreateUserForm
import re
from .utils import initialize_tfidf, find_similar_movies
from django.contrib.auth.forms import UserCreationForm

# Global variables
vectorizer = None
tfidf = None

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

def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')

    context = {'form':form}
    return render(request, 'register.html', context)
    
def login(request):
    # template_name = 'registration/login.html'
    context = {}
    return render(request, 'login.html', context)

def logout(request):
    # template_name = 'registration/login.html'
    context = {}
    return render(request, 'logout.html', context)

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)