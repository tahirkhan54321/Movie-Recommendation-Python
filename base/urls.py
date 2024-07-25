"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('movie_search', views.movie_search, name='movie_search'),
    path('search/', views.general_search, name='general_search'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='loginPage'),
    path('logout/', views.logoutUser, name='logout'), 
    path('profile/', views.user_profile, name='user_profile'),
    path('movie/<int:pk>', views.movie_details, name='movie_details'),
    path('profile/watchlist/', views.view_watchlist, name='watchlist'),
    path('add_to_watchlist/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('profile/ratings/', views.user_ratings, name='user_ratings'),
    path('profile/reviews/', views.user_reviews, name='user_reviews'),
    
]
