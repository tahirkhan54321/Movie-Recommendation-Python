# A class for updating the database with CSV data (should the CSV change)
# note that only new CSV ids are added, no need to delete existing data
# management -> commands are for registering actions
# https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/
# update to be run by command line

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

    # extract actors and characters and return a list of them
    def extract_actors_and_characters(self, cast_data, num_to_extract=5):
        try:
            cast_df = pd.DataFrame(json.loads(cast_data))
            filtered_df = cast_df[cast_df['order'] < num_to_extract]
            return filtered_df['name'].tolist(), filtered_df['character'].tolist()
        except (json.JSONDecodeError, KeyError):
            return [], []

    # extract and return credit data
    def extract_crew_member(self, crew_data, job_title):
        try:
            crew_df = pd.DataFrame(json.loads(crew_data))
            member = crew_df[crew_df['job'] == job_title]
            return member['name'].iloc[0] if not member.empty else None
        except(json.JSONDecodeError, KeyError, IndexError):
            return None
        
    # TBC - define composite string using regex
    def create_composite_string(self, title, actors, characters, director, writer, composer):
        cleaned_title = re.sub(r"[^a-zA-Z0-9 ]", "", title)
        cleaned_actors = [re.sub(r"[^a-zA-Z0-9 ]", "", actor) for actor in actors if actor]
        cleaned_characters = [re.sub(r"[^a-zA-Z0-9 ]", "", char) for char in characters if char]
        cleaned_director = re.sub(r"[^a-zA-Z0-9 ]", "", director) if director else ""
        cleaned_writer = re.sub(r"[^a-zA-Z0-9 ]", "", writer) if writer else ""
        cleaned_composer = re.sub(r"[^a-zA-Z0-9 ]", "", composer) if composer else ""

        cleaned_components = [cleaned_title, *cleaned_actors, *cleaned_characters]
        if director:
            cleaned_components.append(cleaned_director)
        if writer:
            cleaned_components.append(cleaned_writer)
        if composer:
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
            if not self.invalid_movie_id(movie_identifier):
                continue

            movie_title = str(row['title'])
            actors, characters = self.extract_actors_and_characters(row['cast'])
            director = self.extract_crew_member(row['crew'], 'Director')
            writer = self.extract_crew_member(row['crew'], 'Writer')
            composer = self.extract_crew_member(row['crew'], 'Composer')
            
            # clean strings using regex 
            string_representation = self.create_composite_string(movie_title, actors, characters, director, writer, composer)

            # Ensure actors and characters have at least 5 elements
            for _ in range(5 - len(actors)):
                actors.append(None)
                characters.append(None)
            
            Movie.objects.get_or_create(
                movie_id = movie_identifier,
                defaults={
                    'title': movie_title,
                    'actor0': actors[0],
                    'actor1': actors[1],
                    'actor2': actors[2],
                    'actor3': actors[3],
                    'actor4': actors[4],
                    'character0': characters[0],
                    'character1': characters[1],
                    'character2': characters[2],
                    'character3': characters[3],
                    'character4': characters[4],
                    'director': director,
                    'writer': writer,
                    'composer': composer,
                    'composite_string': string_representation
                }
            )



