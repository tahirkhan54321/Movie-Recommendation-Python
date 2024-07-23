# helper methods for views.py
# circumvents issues around dependency injection, circular imports, encapsulation, and order of operations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from .models import Movie, Rating, Review
import numpy as np


# Global variable to store the vectorizer and TF-IDF matrix
vectorizer = None
tfidf = None

def initialize_tfidf():
    """Initializes the TF-IDF vectorizer and matrix."""
    global vectorizer, tfidf
    vectorizer = TfidfVectorizer(ngram_range=(1, 2)) # finds similarities for one and two word groups
    tfidf = vectorizer.fit_transform(Movie.objects.values_list('composite_string', flat=True))

def analyze_sentiment(review_text):
    """Analyses review sentiment based on a review's content."""
    analysis = TextBlob(review_text)
    return analysis.sentiment.polarity

def find_similar_movies(cleaned_title, top_n=100):
    """Finds similar movies based on the cleaned title's composite string."""
    cleaned_title = cleaned_title.lower()
    query_movie = Movie.objects.filter(title__iexact=cleaned_title).first()
    if query_movie: # Check if the movie exists
        query_vec = vectorizer.transform([query_movie.composite_string]) # Now use composite_string
        similarity = cosine_similarity(query_vec, tfidf).flatten()

        # Get top n similar movie IDs
        top_indices = np.argsort(similarity)[-top_n:][::-1]  # Reverse for descending order
        movie_ids = list(Movie.objects.values_list('movie_id', flat=True))

        similar_movies = []
        for i in top_indices:
            movie_id = movie_ids[int(i)]
            if movie_id != query_movie.pk:  # Exclude the query movie
                similar_movies.append(movie_id)
            if len(similar_movies) >= top_n:  # Stop after getting 10
                break
            
        return Movie.objects.filter(movie_id__in=similar_movies)

    return Movie.objects.none() 


def rerank_recommendations(movies, user):
    """Alters the recommendations taking user ratings into account."""
    if not user.is_authenticated:
        return movies

    user_ratings = Rating.objects.filter(user=user).values_list('movie__movie_id', 'rating')
    user_movie_ids, user_ratings_list = zip(*user_ratings)  

    # Calculating similarity scores using cosine_similarity and add to the similarity_scores dictionary
    similarity_scores = {}
    for other_user_id, movie_id, rating in Rating.objects.values_list('user__id', 'movie__movie_id', 'rating'):
        if other_user_id != user.id and movie_id in [movie.movie_id for movie in movies]:
            other_user_ratings = Rating.objects.filter(user__id=other_user_id).values_list('rating', flat=True)
            similarity = cosine_similarity([user_ratings_list], [list(other_user_ratings)])[0][0]
            similarity_scores.setdefault(movie_id, []).append((other_user_id, similarity, rating))
    
    predicted_ratings = {}
    for movie in movies:
        similar_users = similarity_scores.get(movie.movie_id, [])
        weighted_sum = 0
        similarity_sum = 0

        # Ratings taken into account
        for other_user_id, similarity, rating in similar_users:
            weighted_sum += similarity * rating
            similarity_sum += similarity

        # Reviews taken into account
        for other_user_id, similarity, rating in similar_users:
            review = Review.objects.filter(user__id=other_user_id, movie=movie).first()
            sentiment_weight = 1.0  # Neutral weight
            if review:
                sentiment = analyze_sentiment(review.review)
                sentiment_weight = 1.0 + sentiment  # Increase weight for positive reviews, decrease for negative
            weighted_sum += similarity * rating * sentiment_weight
            similarity_sum += similarity

        # Similarity score taken into account
        if similarity_sum > 0: 
            predicted_ratings[movie.movie_id] = weighted_sum / similarity_sum
        else:
            predicted_ratings[movie.movie_id] = 0 

    reranked_movies = sorted(movies, key=lambda movie: predicted_ratings.get(movie.movie_id, 0), reverse=True)
    return reranked_movies

def get_final_recommendations(movies, user, top_n=10):
    """Use rerank only if the conditions are met - this is the function called in views.py"""
    if not user.is_authenticated:
        return movies[:top_n]

    min_user_ratings_threshold = 5
    min_global_ratings_threshold = 1000
    total_ratings_count = Rating.objects.count()

    if Rating.objects.filter(user=user).count() >= min_user_ratings_threshold and total_ratings_count >= min_global_ratings_threshold:
        movies = rerank_recommendations(movies, user)

    return movies[:top_n]