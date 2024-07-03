# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from django.http import HttpResponse
from django.contrib import messages # for error messages
from django.shortcuts import render, redirect
from .forms import MovieForm
import re
from .utils import initialize_tfidf, find_similar_movies
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import UserCreationForm

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

class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Log in the user immediately after registration
        return response
    
class UserLoginView(LoginView):
    template_name = 'registration/login.html'

# helper functions
def clean_title(movie_title):
    return re.sub("[^a-zA-Z0-9 ]", "", movie_title)