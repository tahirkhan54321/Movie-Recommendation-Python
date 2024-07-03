# Model based forms for creating forms

from django.forms import ModelForm
from .models import Movie
from django import forms
from django.contrib.auth.models import User

class MovieForm(ModelForm):
    class Meta:
        model = Movie
        fields = ('title',)

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')  # Adjust fields as needed