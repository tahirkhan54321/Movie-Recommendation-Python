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
from .forms import MovieForm, CreateUserForm, ReviewForm, RatingForm
from .utils import initialize_tfidf, find_similar_movies
from .models import Movie, Rating, Review

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

    # Initialize forms (outside POST handling)
    reviews = Review.objects.filter(movie=movie)
    review_form = ReviewForm(request.POST or None)
    rating_form = RatingForm(request.POST or None)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to submit a review or rating.")
        else:
            # Check which form was submitted
            if 'rating' in request.POST and rating_form.is_valid():
                rating_value = rating_form.cleaned_data['rating']
                Rating.objects.update_or_create(
                    user=request.user,
                    movie=movie,
                    defaults={'rating': rating_value}
                )
                messages.success(request, "Your rating has been updated.")
                average_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
                user_rating = rating_value
                return HttpResponseRedirect(request.path_info)

            elif 'review' in request.POST and review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()
                messages.success(request, "Your review has been submitted!")
                return HttpResponseRedirect(request.path_info)

    context = {
        "movie": movie,
        "average_rating": average_rating,
        "user_rating": user_rating,
        "reviews": reviews,
        "rating_form": rating_form,
        "review_form": review_form,
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