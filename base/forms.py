# Model based forms for creating forms

from django.forms import ModelForm
from .models import Movie, Review, Rating
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class MovieForm(ModelForm):
    class Meta:
        model = Movie
        fields = ('title',)

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'review']

class MovieSearchForm(forms.Form):
    title = forms.CharField(max_length=255, label='Search Movie: ')