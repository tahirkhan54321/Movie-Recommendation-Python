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

class Command(BaseCommand):
    help = 'Writes movies to the database'

    # boilerplate, defines arguments for command to accept when running from CLI
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV')

    # helper functions
    def import_csv(self, file_path):
        return pd.read_csv(file_path)
    
    # boolean for validation of movie id
    def validate_movie_id(self, movie_id):
        try:
            int(movie_id)
            return not Movie.objects.filter(id=movie_id).exists
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
        
    def write_movies(self, *args, **options):
        file_path = options['csv_file']
        df = self.import_csv(file_path)

        for _, row in df.iterrows():
            movie_id = row['movie_id']
            if not self.validate_movie_id(movie_id):
                continue

            movie_title = str(row['title'])
            actors, characters = self.extract_actors_and_characters(row['cast'])
            director = self.extract_crew_member(row['crew'], 'Director')
            writer = self.extract_crew_member(row['crew'], 'Writer')
            composer = self.extract_crew_member(row['crew'], 'Composer')

            Movie.objects.create(
                movie_id = movie_id,
                title = movie_title,
                actor0 = actors[0] if actors else None,
                actor1 = actors[1] if actors else None,
                actor2 = actors[2] if actors else None,
                actor3 = actors[3] if actors else None,
                actor4 = actors[4] if actors else None,
                character0 = characters[0] if characters else None,
                character1 = characters[1] if characters else None,
                character2 = characters[2] if characters else None,
                character3 = characters[3] if characters else None,
                character4 = characters[4] if characters else None,
                director = director,
                writer = writer,
                composer = composer
            )



