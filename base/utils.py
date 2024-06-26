# helper methods for views.py
# circumvents issues around dependency injection, circular imports, encapsulation, and order of operations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Movie
import numpy as np


# Global variable to store the vectorizer and TF-IDF matrix
vectorizer = None
tfidf = None

def initialize_tfidf():
    """Initializes the TF-IDF vectorizer and matrix."""
    global vectorizer, tfidf
    vectorizer = TfidfVectorizer(ngram_range=(1, 2)) # finds similarities for one and two word groups
    tfidf = vectorizer.fit_transform(Movie.objects.values_list('composite_string', flat=True))


def find_similar_movies(cleaned_title):
    """Finds similar movies based on the cleaned title's composite string."""
    cleaned_title = cleaned_title.lower()
    query_movie = Movie.objects.filter(title__iexact=cleaned_title).first()
    if query_movie: # Check if the movie exists
        query_vec = vectorizer.transform([query_movie.composite_string]) # Now use composite_string
        similarity = cosine_similarity(query_vec, tfidf).flatten()

        # Get top 10 similar movie IDs
        top_indices = np.argsort(similarity)[-10:][::-1]  # Reverse for descending order
        movie_ids = list(Movie.objects.values_list('movie_id', flat=True))
        similar_movies = [movie_ids[i] for i in top_indices]  
        return Movie.objects.filter(movie_id__in=similar_movies)

    return Movie.objects.none() 
