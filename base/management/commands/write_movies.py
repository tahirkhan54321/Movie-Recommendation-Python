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
from datetime import datetime


class Command(BaseCommand):
    help = 'Writes movies to the database'

    # boilerplate, defines arguments for command to accept when running from CLI
    def add_arguments(self, parser):
        parser.add_argument('--credits_csv', type=str, help='Path to credits file')
        parser.add_argument('--movies_csv', type=str, help='Path to movie file')

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

    # Get genres
    def extract_genres(self, genre_data):
        try:
            genre_df = pd.DataFrame(json.loads(genre_data))
            return "|".join(genre_df['name'].tolist())
        except (json.JSONDecodeError, KeyError):
            return ""

    # Get keywords
    def extract_keyword(self, keyword_data):
        try:
            keyword_df = pd.DataFrame(json.loads(keyword_data))
            return "|".join(keyword_df['name'].tolist())
        except (json.JSONDecodeError, KeyError):
            return ""

    # Get production companies
    def extract_production_companies(self, production_companies_data):
        try:
            production_companies_df = pd.DataFrame(json.loads(production_companies_data))
            return "|".join(production_companies_df['name'].tolist())
        except (json.JSONDecodeError, KeyError):
            return ""
    
    # Get production countries
    def extract_production_countries(self, production_countries_data):
        try:
            production_countries_df = pd.DataFrame(json.loads(production_countries_data))
            return "|".join(production_countries_df['name'].tolist())
        except (json.JSONDecodeError, KeyError):
            return ""

    # Get release date in appropriate format for data model
    def extract_release_date(self, date_string):
        try:
            if isinstance(date_string, str):
                # First try parsing with the YYYY-MM-DD format
                try:
                    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
                    return date_obj
                except ValueError:  # If it fails, try dd/mm/yyyy
                    date_obj = datetime.strptime(date_string, '%d/%m/%Y')
                    return date_obj
            else:
                raise ValueError(f"Expected string format, got: {date_string}")

        except ValueError:  # Catch invalid date format
            print(f"Invalid date format: {date_string}")
            return None  # Or a default date if needed
    
    # Get the spoken languages
    def extract_spoken_languages(self, spoken_language_data):
        try:
            spoken_language_df = pd.DataFrame(json.loads(spoken_language_data))
            return "|".join(spoken_language_df['name'].tolist())
        except (json.JSONDecodeError, KeyError):
            return ""
        
    # write movies to the database assuming the movie id provided is unique
    # handle naming is a requirement for BaseCommand
    def handle(self, *args, **options):
        credits_file_path = options['credits_csv']
        movies_file_path = options['movies_csv']
        credits_df = self.import_csv(credits_file_path)
        movies_df = self.import_csv(movies_file_path)

        for _, row in credits_df.iterrows():
            
            movie_identifier = row['movie_id']
            additional_row = movies_df[movies_df['id'] == movie_identifier].iloc[0]

            movie_title = str(row['title'])
            cleaned_movie_title = self.clean_title(movie_title) 

            # Extract all actors and characters
            actor_string = self.extract_actors(row['cast'])
            character_string = self.extract_characters(row['cast'])

            # Construct the composite string (pass crew data directly)
            string_representation = self.create_composite_string(
                movie_title, row['cast'], row['crew'] 
            )

            # Gather the additional data from the movies.csv
            additional_data = {
                'budget': additional_row.get('budget', None),
                'homepage': additional_row.get('homepage', None),
                'language': additional_row.get('original_language', None),
                'overview': additional_row.get('overview', None), 
                'genres': self.extract_genres(additional_row['genres']),
                'keywords': self.extract_keyword(additional_row['keywords']),
                'production_companies': self.extract_production_companies(additional_row['production_companies']),
                'production_countries': self.extract_production_countries(additional_row['production_countries']),
                'release_date': self.extract_release_date(additional_row['release_date']),
                'revenue': additional_row.get('revenue', None), 
                'runtime': additional_row.get('runtime', None),
                'spoken_languages': self.extract_spoken_languages(additional_row['spoken_languages']),
                'status': additional_row.get('status', None),
                'tagline': additional_row.get('tagline', None)
            }


            # Validate integer fields
            try:
                additional_data['revenue'] = int(additional_data['revenue'])
            except (ValueError, TypeError):
                additional_data['revenue'] = None

            try:
                additional_data['runtime'] = int(additional_data['runtime'])
            except (ValueError, TypeError):
                additional_data['runtime'] = None


            # Populate the Movie objects
            Movie.objects.update_or_create(
                movie_id=movie_identifier,
                defaults={
                    'title': movie_title,
                    'cleaned_title': cleaned_movie_title,
                    'actors': actor_string,
                    'characters': character_string,
                    'director': self.extract_crew_member(row['crew'], 'Director'),  
                    'writer': self.extract_crew_member(row['crew'], 'Writer'),
                    'composer': self.extract_crew_member(row['crew'], 'Composer'),
                    'composite_string': string_representation,
                    **additional_data
                }
            )




