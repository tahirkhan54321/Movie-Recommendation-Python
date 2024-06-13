# This file contains the Python functions (views) that handle HTTP requests and return responses, 
# such as rendering templates or returning JSON data.

from .models import Movie
from django.http import HttpResponse
from django.contrib import messages # for error messages
from django.shortcuts import render, redirect
import pandas as pd

def 