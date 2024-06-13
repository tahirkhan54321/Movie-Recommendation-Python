from django.test import TestCase
from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command
from unittest.mock import patch
from base.models import Movie
import pandas as pd
from base.management.commands.write_movies import Command

class CommandTestCase(TestCase):

    def setUp(self):
        # Create test data in a DataFrame (mimicking CSV)
        self.test_data = pd.DataFrame({
            'movie_id': [100, 101, 102],
            'title': ['Test Movie 1', 'Test Movie 2', 'Invalid Movie'],
            'cast': ['[{"order": 0, "name": "Actor A", "character": "Char A"}, {"order": 1, "name": "Actor B", "character": "Char B"}]',
                     '[{"order": 0, "name": "Actor C", "character": "Char C"}]',
                     '[{"order": 0, "name": "Actor D", "character": "Char D"}, {"order": 1, "name": "Actor E", "character": "Char E"}]'],
            'crew': ['[{"job": "Director", "name": "Director X"}, {"job": "Writer", "name": "Writer Y"}]',
                     '[{"job": "Director", "name": "Director Z"}]',
                     'invalid_json'] 
        })

        # Create an existing movie in the database
        Movie.objects.create(movie_id=101, title='Existing Movie') 

    # --- Test Cases ---

    # @patch('pandas.read_csv')  # Mock CSV reading
    def test_write_movies_success(self):
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.return_value = self.test_data
            call_command('write_movies', csv_file='test.csv')  # Simulate command execution

        # Assert that movies were created correctly
        self.assertEqual(Movie.objects.count(), 3) 
        new_movie = Movie.objects.get(movie_id=100)
        self.assertEqual(new_movie.title, 'Test Movie 1')
        self.assertEqual(new_movie.actor0, 'Actor A')

    @patch('pandas.read_csv')
    def test_validate_movie_id(self, mock_read_csv):
        mock_read_csv.return_value = self.test_data  

        command = Command()
        self.assertTrue(command.validate_movie_id(100)) # New ID
        self.assertFalse(command.validate_movie_id(101)) # Existing ID
        self.assertFalse(command.validate_movie_id('invalid')) # Non-integer ID

    def test_extract_actors_and_characters(self):
        command = Command()
        actors, characters = command.extract_actors_and_characters(self.test_data['cast'][0])
        self.assertEqual(actors, ['Actor A', 'Actor B'])
        self.assertEqual(characters, ['Char A', 'Char B'])

        # Test empty or invalid JSON
        actors, characters = command.extract_actors_and_characters('invalid_json')
        self.assertEqual(actors, [])
        self.assertEqual(characters, [])

    def test_extract_crew_member(self):
        command = Command()
        director = command.extract_crew_member(self.test_data['crew'][0], 'Director')
        self.assertEqual(director, 'Director X')

        # Test invalid JSON
        director = command.extract_crew_member('invalid_json', 'Director')
        self.assertIsNone(director)
