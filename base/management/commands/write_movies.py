# A class for updating the database with CSV data (should the CSV change)
# note that only new CSV ids are added, no need to delete existing data
# management -> commands are for registering actions
# https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/
# update to be run by command line
# Note that when running the command, you need to specify the path to the CSV file

import csv
import json
from django.core.management.base import BaseCommand, CommandParser
from base.models import Movie
import pandas as pd
import re

class Command(BaseCommand):
    help = 'Writes movies to the database'

    # boilerplate, defines arguments for command to accept when running from CLI
    def add_arguments(self, parser):
        parser.add_argument('--csv_file', type=str, help='Path to CSV')

    # helper functions
    def import_csv(self, file_path):
        return pd.read_csv(file_path)
    
    # boolean for validation of movie id
    def invalid_movie_id(self, movie_identifier):
        try:
            int(movie_identifier)
            return Movie.objects.filter(movie_id=movie_identifier).exists
        except ValueError:
            return False
    
    # removes unwanted characters from the movie title
    def clean_title(self, movie_title):
        return re.sub("[^a-zA-Z0-9 ]", "", movie_title)

    # extract actors and return pipe delimited string
    def extract_actors(self, cast_data):
        try:
            cast_df = pd.DataFrame(json.loads(cast_data))
            return "|".join(cast_df['name'].tolist()) 
        except (json.JSONDecodeError, KeyError):
            return ""

    # extract characters and return pipe delimited string
    def extract_characters(self, cast_data):
        try:
            cast_df = pd.DataFrame(json.loads(cast_data))
            return "|".join(cast_df['character'].tolist())
        except (json.JSONDecodeError, KeyError):
            return ""

    # extract and return credit data for director, etc as a pipe delimited string
    def extract_crew_member(self, crew_data, job_title):
        try:
            crew_df = pd.DataFrame(json.loads(crew_data))
            members = crew_df[crew_df['job'] == job_title]  # Get all matching rows

            if not members.empty:
                names = members['name'].tolist()  # Extract all names as a list
                return "|".join(names)          # Join names with pipe separator
            else:
                return None

        except (json.JSONDecodeError, KeyError, IndexError):
            return None

        
    # define composite string using regex
    def create_composite_string(self, title, cast_data, crew_data):
        cleaned_title = self.clean_title(title)

        # Extract actors and characters
        actor_string = self.extract_actors(cast_data)
        character_string = self.extract_characters(cast_data)
        
        # Split strings into lists and clean individual names/characters
        cleaned_actors = [re.sub(r"[^a-zA-Z0-9 ]", "", actor) for actor in actor_string.split("|") if actor]
        cleaned_characters = [re.sub(r"[^a-zA-Z0-9 ]", "", char) for char in character_string.split("|") if char]

        # Extract and clean crew members (director, writer, composer)
        cleaned_director = self.extract_crew_member(crew_data, 'Director')
        cleaned_writer = self.extract_crew_member(crew_data, 'Writer')
        cleaned_composer = self.extract_crew_member(crew_data, 'Composer')

        # Assuming cleaned_director, cleaned_writer, cleaned_composer are already strings,
        # split them into lists (if not None) and clean individual names
        cleaned_directors = [re.sub(r"[^a-zA-Z0-9 ]", "", director) for director in cleaned_director.split("|") if director] if cleaned_director else []
        cleaned_writers = [re.sub(r"[^a-zA-Z0-9 ]", "", writer) for writer in cleaned_writer.split("|") if writer] if cleaned_writer else []
        cleaned_composers = [re.sub(r"[^a-zA-Z0-9 ]", "", composer) for composer in cleaned_composer.split("|") if composer] if cleaned_composer else []

        cleaned_components = [cleaned_title, *cleaned_actors, *cleaned_characters, *cleaned_directors, *cleaned_writers, *cleaned_composers]
        composite_string = " ".join(cleaned_components).lower()

        return composite_string


        
    # write movies to the database assuming the movie id provided is unique
    # handle naming is a requirement for BaseCommand
    def handle(self, *args, **options):
        file_path = options['csv_file']
        df = self.import_csv(file_path)

        for _, row in df.iterrows():
            movie_identifier = row['movie_id']
            if not self.invalid_movie_id(movie_identifier):  # Assuming this method checks for valid movie IDs
                continue

            movie_title = str(row['title'])
            cleaned_movie_title = self.clean_title(movie_title) 

            # Extract all actors and characters
            actor_string = self.extract_actors(row['cast'])
            character_string = self.extract_characters(row['cast'])

            # Construct the composite string (pass crew data directly)
            string_representation = self.create_composite_string(
                movie_title, row['cast'], row['crew'] 
            )

            Movie.objects.get_or_create(
                movie_id=movie_identifier,
                defaults={
                    'title': movie_title,
                    'cleaned_title': cleaned_movie_title,
                    'actors': actor_string,
                    'characters': character_string,
                    'director': self.extract_crew_member(row['crew'], 'Director'),  
                    'writer': self.extract_crew_member(row['crew'], 'Writer'),
                    'composer': self.extract_crew_member(row['crew'], 'Composer'),
                    'composite_string': string_representation
                }
            )




