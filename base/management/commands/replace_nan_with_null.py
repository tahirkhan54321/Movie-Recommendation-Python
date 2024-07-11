# management/commands/replace_nan_with_null.py
from django.core.management.base import BaseCommand
from base.models import Movie
import numpy as np

class Command(BaseCommand):
    help = 'Replaces "nan" values with NULL in the Movie model'

    def handle(self, *args, **options):
        fields_to_check = ['budget', 'homepage', 'revenue', 'runtime']  # Add other float/int fields here

        for movie in Movie.objects.all():
            for field in fields_to_check:
                value = getattr(movie, field)
                if isinstance(value, float) and np.isnan(value):  # Check for NaN floats
                    setattr(movie, field, None)
                    movie.save(update_fields=[field])  # Update only this field
                elif isinstance(value, str) and value == 'nan':  # Check for "nan" strings
                    setattr(movie, field, None)
                    movie.save(update_fields=[field])
        
        self.stdout.write(self.style.SUCCESS('Successfully replaced "nan" values with NULL.'))
