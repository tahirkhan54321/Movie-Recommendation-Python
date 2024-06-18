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

    # extract and return credit data
    def extract_crew_member(self, crew_data, job_title):
        try:
            crew_df = pd.DataFrame(json.loads(crew_data))
            member = crew_df[crew_df['job'] == job_title]
            return member['name'].iloc[0] if not member.empty else None
        except(json.JSONDecodeError, KeyError, IndexError):
            return None
        
    # define composite string using regex
    def create_composite_string(self, title, cast_data, director, writer, composer):
        cleaned_title = self.clean_title(title)

        # Extract actors and characters
        actor_string = self.extract_actors(cast_data)
        character_string = self.extract_characters(cast_data)
        
        # Split strings into lists and clean individual names/characters
        # note that re.sub will remove leading and trailing spaces
        cleaned_actors = [re.sub(r"[^a-zA-Z0-9 ]", "", actor) for actor in actor_string.split("|") if actor]
        cleaned_characters = [re.sub(r"[^a-zA-Z0-9 ]", "", char) for char in character_string.split("|") if char]

        cleaned_director = re.sub(r"[^a-zA-Z0-9 ]", "", director) if director else ""
        cleaned_writer = re.sub(r"[^a-zA-Z0-9 ]", "", writer) if writer else ""
        cleaned_composer = re.sub(r"[^a-zA-Z0-9 ]", "", composer) if composer else ""

        cleaned_components = [cleaned_title, *cleaned_actors, *cleaned_characters]
        if cleaned_director:
            cleaned_components.append(cleaned_director)
        if cleaned_writer:
            cleaned_components.append(cleaned_writer)
        if cleaned_composer:
            cleaned_components.append(cleaned_composer)
        
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
            cleaned_movie_title = self.clean_title(movie_title)  # Pass movie_title directly

            # Extract all actors and characters
            actor_string = self.extract_actors(row['cast'])
            character_string = self.extract_characters(row['cast'])

            director = self.extract_crew_member(row['crew'], 'Director')
            writer = self.extract_crew_member(row['crew'], 'Writer')
            composer = self.extract_crew_member(row['crew'], 'Composer')

            string_representation = self.create_composite_string(
                movie_title, row['cast'], director, writer, composer
            )  # Pass cast data directly

            Movie.objects.get_or_create(
                movie_id=movie_identifier,
                defaults={
                    'title': movie_title,
                    'cleaned_title': cleaned_movie_title,
                    'actors': actor_string,
                    'characters': character_string,
                    'director': director,
                    'writer': writer,
                    'composer': composer,
                    'composite_string': string_representation
                }
        )




