# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from django.http import HttpResponseRedirect
from django.contrib import messages # for error messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import MovieForm, CreateUserForm
from .utils import initialize_tfidf, find_similar_movies
from .models import Movie, Rating

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

    average_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, movie=movie).rating
        except Rating.DoesNotExist:
            pass

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to rate movies.")
        else:
            rating_value = int(request.POST.get('rating'))
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating_value}
            )
            if created:
                messages.success(request, "Your rating has been submitted.")
            else:
                messages.success(request, "Your rating has been updated.")
            average_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']

            # Update user_rating after submission
            user_rating = rating_value

        # Redirect to the same page to refresh the template
        return HttpResponseRedirect(request.path_info)

    context = {
        "movie": movie,
        "average_rating": average_rating,
        "user_rating": user_rating,
    }
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
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie')  # Fetch ratings

    context = {
        'user_ratings': user_ratings
    }
    return render(request, 'user_profile.html', context)

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)