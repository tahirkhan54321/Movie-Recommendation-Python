from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import BaseCommand
from unittest.mock import patch
from base.models import Movie
import pandas as pd
from base.management.commands.write_movies import Command

class TestWriteMovies(TestCase):
    def setUp(self):
        # Create test data in a DataFrame (mimicking CSV)
        self.test_data = pd.DataFrame({
            'movie_id': [100, 101, 102],
            'title': ['Test Movie 1', 'Test Movie 2', 'Invalid Movie'],
            'cast': [
                '[{"name": "Actor A", "character": "Char A"}, {"name": "Actor B", "character": "Char B"}]',
                '[{"name": "Actor C", "character": "Char C"}]',
                '[{"name": "Actor D", "character": "Char D"}, {"name": "Actor E", "character": "Char E"}]'
            ],
            'crew': [
                '[{"job": "Director", "name": "Director X"}, {"job": "Writer", "name": "Writer Y"}, {"job": "Director", "name": "Director Z"}]',  # Multiple Directors
                '[{"job": "Writer", "name": "Writer A"}, {"job": "Writer", "name": "Writer B"}]',  # Multiple Writers
                'invalid_json'
            ]
        })

        # Create an existing movie in the database
        Movie.objects.create(movie_id=101, title='Existing Movie')

    @patch('pandas.read_csv')
    def test_write_movies_success(self, mock_read_csv):
        mock_read_csv.return_value = self.test_data
        call_command('write_movies', csv_file='test.csv')

        self.assertEqual(Movie.objects.count(), 3)

        # Test Movie 1 (new movie)
        new_movie = Movie.objects.get(movie_id=100)
        self.assertEqual(new_movie.title, 'Test Movie 1')
        self.assertEqual(new_movie.actors, 'Actor A|Actor B')
        self.assertEqual(new_movie.characters, 'Char A|Char B')
        self.assertEqual(new_movie.director, 'Director X|Director Z')
        self.assertEqual(new_movie.writer, 'Writer Y')

        # Test Movie 2 (existing movie, should not be updated)
        existing_movie = Movie.objects.get(movie_id=101)
        self.assertEqual(existing_movie.title, 'Existing Movie')

        # Test composite string generation
        composite_string = Movie.objects.get(movie_id=100).composite_string
        expected_components = ['test movie 1', 'actor a', 'actor b', 'char a', 'char b', 'director x', 'director z', 'writer y']
        for component in expected_components:
            self.assertIn(component, composite_string)
        

    @patch('pandas.read_csv')
    def test_invalid_movie_id(self, mock_read_csv):
        mock_read_csv.return_value = self.test_data

        command = Command() 
        self.assertTrue(command.invalid_movie_id(100))  # New ID
        self.assertTrue(command.invalid_movie_id(101))  # Existing ID
        self.assertFalse(command.invalid_movie_id('invalid'))  # Non-integer ID


    def test_extract_actors(self):  # Test the extract_actors method
        command = Command()
        actors = command.extract_actors(self.test_data['cast'][0])
        self.assertEqual(actors, 'Actor A|Actor B')

        # Test empty JSON
        actors = command.extract_actors("[]") 
        self.assertEqual(actors, "")

        # Test invalid JSON
        actors = command.extract_actors("invalid_json")
        self.assertEqual(actors, "")

    def test_extract_characters(self):  # Test the extract_characters method
        command = Command()
        characters = command.extract_characters(self.test_data['cast'][0])
        self.assertEqual(characters, 'Char A|Char B')
        
        # Test empty or invalid JSON
        characters = command.extract_characters("[]")
        self.assertEqual(characters, "")

        # Test invalid JSON
        characters = command.extract_characters("invalid_json")
        self.assertEqual(characters, "")

    def test_extract_crew_member(self):
        command = Command()
        director = command.extract_crew_member(self.test_data['crew'][0], 'Director')
        self.assertEqual(director, 'Director X|Director Z')

        # Test invalid JSON
        director = command.extract_crew_member('invalid_json', 'Director')
        self.assertIsNone(director)
    
    def test_create_composite_string(self):
        command = Command()
        composite_string = command.create_composite_string(
            self.test_data['title'][0], 
            self.test_data['cast'][0], 
            self.test_data['crew'][0]
        )
        expected_components = ['test movie 1', 'actor a', 'actor b', 'char a', 'char b', 'director x', 'director z', 'writer y']
        for component in expected_components:
            self.assertIn(component, composite_string)
