# from django.core.management import call_command
# from django.test import TestCase
# from io import StringIO
# from base.models import Movie
# import pandas as pd

# class ImportMoviesTestCase(TestCase):

#     def setUp(self):
#         # Create a temporary CSV file with test data
#         self.data = {
#             'movie_id': [123, 456, 789, 1011],  # Valid and invalid IDs
#             'title': ['Test Movie 1', 'Test Movie 2', 'Existing Movie', ''],  # Valid, existing, and empty title
#             'cast': [
#                 '[{"name": "Actor A", "character": "Character A"}]', 
#                 '[{"name": "Actor B", "character": "Character B"}, {"name": "Actor C", "character": "Character C"}]',
#                 '[{"name": "Actor D", "character": "Character D"}, {"name": "Actor E", "character": "Character E"}]',
#                 '[]'  # Empty cast
#             ],
#             'crew': [
#                 '[{"job": "Director", "name": "Director A"}]',
#                 '[{"job": "Writer", "name": "Writer B"}, {"job": "Composer", "name": "Composer C"}]',
#                 '[{"job": "Director", "name": "Director D"}, {"job": "Writer", "name": "Writer E"}, {"job": "Composer", "name": "Composer F"}]',
#                 '[]'  # Empty crew
#             ]
#         }
#         self.df = pd.DataFrame(self.data)

#     def test_import_valid_data(self):
#         self.df.to_csv('test_movies.csv', index=False)

#         out = StringIO()
#         call_command('write_movies', 'test_movies.csv', stdout=out)

#         self.assertEqual(Movie.objects.count(), 2)  # Only 2 valid entries should be added

#         movie1 = Movie.objects.get(id=123)
#         self.assertEqual(movie1.title, 'Test Movie 1')
#         # ... (Verify cast, crew, etc.)

#         movie2 = Movie.objects.get(id=456)
#         self.assertEqual(movie2.title, 'Test Movie 2')
#         # ... (Verify cast, crew, etc.)

#     def test_skip_existing_movies(self):
#         Movie.objects.create(id=789, title='Existing Movie')  # Pre-existing movie
#         self.df.to_csv('test_movies.csv', index=False)

#         out = StringIO()
#         call_command('write_movies', 'test_movies.csv', stdout=out)
#         self.assertIn('Duplicate movie_id or other integrity error for 789', out.getvalue())

#         self.assertEqual(Movie.objects.count(), 3)  # 2 new + 1 existing
        
#     def test_invalid_movie_id(self):
#         self.df.to_csv('test_movies.csv', index=False)

#         out = StringIO()
#         call_command('write_movies', 'test_movies.csv', stdout=out)
#         self.assertIn('Invalid movie_id: 1011', out.getvalue())

#         self.assertEqual(Movie.objects.count(), 2)
    
#     def test_empty_title(self):
#         self.df.to_csv('test_movies.csv', index=False)

#         out = StringIO()
#         call_command('write_movies', 'test_movies.csv', stdout=out)

#         self.assertEqual(Movie.objects.count(), 2)

#     def test_empty_cast_and_crew(self):
#         self.df.to_csv('test_movies.csv', index=False)

#         out = StringIO()
#         call_command('write_movies', 'test_movies.csv', stdout=out)

#         movie = Movie.objects.get(id=123) 
#         self.assertEqual(movie.actor0, 'Actor A')
#         self.assertEqual(movie.character0, 'Character A')
#         self.assertIsNone(movie.actor1)
#         self.assertIsNone(movie.character1)
#         #...similarly for other actors/characters
#         self.assertEqual(movie.director, 'Director A')
#         self.assertIsNone(movie.writer)
#         self.assertIsNone(movie.composer)

#         # ... (Similar checks for the movie with id=456 to make sure 
#         #      that it has multiple actors and crew members)


#     def tearDown(self):
#         # Clean up the temporary CSV file
#         import os
#         os.remove('test_movies.csv') 
