# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

import re
import os
import random
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Max
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import replicate
import markdown2
from .forms import MovieForm, CreateUserForm, ReviewForm, RatingForm, MovieSearchForm
from .utils import initialize_tfidf, find_similar_movies, get_final_recommendations, rerank_recommendations
from .models import Movie, Rating, Review, Watchlist
from dotenv import load_dotenv

# Global variables
vectorizer = None
tfidf = None

# General navbar search
def general_search(request):
    form = MovieSearchForm(request.GET or None)
    search_results = None

    if form.is_valid():
        search_term = form.cleaned_data['title'].lower()
        search_results = Movie.objects.filter(title__icontains=search_term)
    
    context = {'form': form, 'search_results': search_results}

    return render(request, 'search_results.html', context)

# Movie recommendation functions
def movie_search(request):
    form = MovieForm(request.POST or None)
    final_recommendations = None
    similar_movies = None

    if request.method == 'POST':
        if form.is_valid():
            movie_title = form.cleaned_data['title'].lower()
            cleaned_movie_title = clean_title(movie_title)  # Make sure you have this function
            initialize_tfidf()  # Initialize TF-IDF
            similar_movies = find_similar_movies(cleaned_movie_title, top_n=100)
            if similar_movies:
                final_recommendations = get_final_recommendations(
                    list(similar_movies), request.user, top_n=10
                )  # Apply Hybrid Recommender
        else:
            messages.error(request, "Invalid movie title, please try another")

    return render(request, 'movie_search.html', {'form': form, 'final_recommendations': final_recommendations})

# AI chatbot related functions
def chatbot(request):
    if 'conversation_history' not in request.session:
        request.session['conversation_history'] = []

    conversation_history = request.session['conversation_history']

    context = {'conversation_history': conversation_history} 

    if request.method == 'POST':
        if check_rate_limit(request):
            context['error'] = 'You have already made a request today. Please try again tomorrow.'
        else:
            user_input = request.POST.get('user_input')
            bot_response = process_user_input_with_llama(user_input)
            conversation_history.append(('user', user_input))
            conversation_history.append(('bot', bot_response))
            request.session['last_user_input'] = user_input
            request.session['last_request_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    else:
        user_input = request.session.get('last_user_input')
        context['user_input'] = user_input

    return render(request, 'chatbot.html', context)

def process_user_input_with_llama(user_input):
    load_dotenv()
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    model_identifier = replicate.models.get("meta/meta-llama-3-8b-instruct")
    
    input_data = {
        "prompt": user_input,
        "max_new_tokens": 512,
        "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    }

    output_text = ""
    for event in replicate.stream(
        model_identifier,
        input=input_data
    ):
        if event.data:
            output_text += event.data

    html_output = markdown2.markdown(output_text)

    return html_output

# Page details related functions
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

    # Paginate reviews
    reviews_list = Review.objects.filter(movie=movie)
    paginator = Paginator(reviews_list, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "movie": movie,
        "average_rating": average_rating,
        "user_rating": user_rating,
        "reviews": page_obj,
        "rating_form": rating_form,
        "review_form": review_form,
        'page_obj': page_obj,
    }

    return render(request, "movie_details.html", context)

def homepage(request):
    # Top 10 highest rated films
    top_rated_films = Movie.objects.annotate(
        avg_rating=Avg('rating__rating')
    ).order_by('-avg_rating')[:10]

    if len(top_rated_films) < 10:
        remaining_needed = 10 - len(top_rated_films)
        # Exclude movies already in top_rated_films
        random_movies = Movie.objects.exclude(
            pk__in=top_rated_films.values_list('pk', flat=True)
        ).order_by('?')[:remaining_needed] 
        top_rated_films = list(top_rated_films) + list(random_movies)
    
    # Most recently reviewed films
    recently_reviewed_movies = Movie.objects.filter(
        review__isnull=False
    ).annotate(
        avg_rating=Avg('rating__rating'),  # Calculate average rating
        latest_review=Max('review__created_at')  # Get the latest review date
    ).order_by('-latest_review')[:10]

    # If less than 10 movies found, add random movies (excluding those already included)
    if len(recently_reviewed_movies) < 10:
        remaining_needed = 10 - len(recently_reviewed_movies)
        random_movies = Movie.objects.exclude(
            pk__in=recently_reviewed_movies.values_list('pk', flat=True)
        ).order_by('?')[:remaining_needed]
        recently_reviewed_movies = list(recently_reviewed_movies) + list(random_movies)

    # Movie recommendations
    recommended_movies = get_recommendations(request.user) 

    context = {
        'top_rated_films': top_rated_films,
        'recently_reviewed_movies': recently_reviewed_movies,
        'recommended_movies': recommended_movies,
    }

    return render(request, 'homepage.html', context)

    
# Watchlist related functions
@login_required
def add_to_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    _, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
    if created:
        messages.success(request, "Movie added to watchlist.")
    else:
        messages.info(request, "Movie already in watchlist.")
    return redirect('movie_search')

@login_required
def remove_from_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    Watchlist.objects.filter(user=request.user, movie=movie).delete()
    messages.success(request, "Movie removed from watchlist.")
    return redirect('movie_search')

@login_required
def view_watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    return render(request, 'watchlist.html', {'watchlist': watchlist})

# See Ratings and Reviews
@login_required
def user_ratings(request):
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie')
    context = {'user_ratings': user_ratings}
    return render(request, 'user_ratings.html', context)

@login_required
def user_reviews(request):
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    context = {'user_reviews': user_reviews}
    return render(request, 'user_reviews.html', context)

# User related functions
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
            return redirect('movie_search')
        else:
            messages.error(request, "Invalid username or password.")

    context = {}
    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('movie_search')

@login_required
def user_profile(request):
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie')  # Fetch ratings
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')

    context = {
        'user_ratings': user_ratings,
        'user_reviews': user_reviews,
    }
    return render(request, 'user_profile.html', context)

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)

def get_random_movies(count=10, existing_movies=None):
    random_movies = []
    while len(random_movies) < count:
        new_movie = Movie.objects.order_by('?').first()  # Get a single random movie
        if existing_movies is None or new_movie not in existing_movies:
            random_movies.append(new_movie)
    return random_movies

def check_rate_limit(request):
    last_request_time_str = request.session.get('last_request_time')
    if last_request_time_str:
        last_request_time = datetime.datetime.strptime(last_request_time_str, '%Y-%m-%d %H:%M:%S.%f')
        time_difference = datetime.datetime.now() - last_request_time
        if time_difference.days == 0:
            return True  # Rate limit exceeded
    return False  # Rate limit not exceeded

def get_recommendations(user):
    if user.is_authenticated:
        user_ratings = Rating.objects.filter(user=user)
        liked_movie_ids = user_ratings.filter(rating__gte=4).values_list('movie__movie_id', flat=True)

        if liked_movie_ids:
            # Get movies that other users who liked the same movies also liked
            recommended_movie_ids = Rating.objects.filter(
                user__in=Rating.objects.filter(movie__movie_id__in=liked_movie_ids).values('user').distinct(),
                rating__gte=4
            ).exclude(
                movie__movie_id__in=liked_movie_ids 
            ).values('movie__movie_id').distinct()


            recommended_movies = Movie.objects.filter(movie_id__in=recommended_movie_ids).annotate(
                avg_rating=Avg('rating__rating')
            )

            # If not enough recommendations, fill with random movies
            if recommended_movies.count() < 10:
                remaining_needed = 10 - recommended_movies.count()
                random_movies = Movie.objects.exclude(
                    movie_id__in=list(liked_movie_ids) + list(recommended_movies.values_list('movie_id', flat=True))
                ).annotate(
                    avg_rating=Avg('rating__rating')
                ).order_by('?')[:remaining_needed]
                recommended_movies = list(recommended_movies) + list(random_movies)
                
            return recommended_movies[:10]

        else:
            # If no liked movies, return random movies
            recommended_movies = Movie.objects.all().annotate(
                avg_rating=Avg('rating__rating')
            ).order_by('?')[:10]
            return recommended_movies

    else:
        # If not logged in, return random movies
        recommended_movies = Movie.objects.all().annotate(
            avg_rating=Avg('rating__rating')
        ).order_by('?')[:10]
        return recommended_movies