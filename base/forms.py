# Model based forms for creating forms

from django.forms import ModelForm
from .models import Movie
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
        fields = ['username', 'email', 'password1', 'password2']  # TBC Adjust fields as needed