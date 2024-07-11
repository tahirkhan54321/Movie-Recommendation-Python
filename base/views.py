# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from django.contrib import messages # for error messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import MovieForm, CreateUserForm
import re
from .utils import initialize_tfidf, find_similar_movies
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Movie

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

def movie_details(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    context = {"movie": movie}
    return render(request, "movie_details.html", context)

def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('loginPage')

    context = {'form':form}
    return render(request, 'register.html', context)
    
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('movie-search')
        else:
            messages.error(request, "Invalid username or password.")

    context = {}
    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('movie-search')

@login_required
def user_profile(request):
    return render(request, 'user_profile.html')

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)