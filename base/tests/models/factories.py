import factory
from base.models import Movie

class movie_factory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie
    movie_id = "123"
    title = "Movie0"
    actor0 = "Actor0"
    actor1 = "Actor1"
    actor2 = "Actor2"
    actor3 = "Actor3"
    actor4 = "Actor4"
    character0 = "Character0"
    character1 = "Character1"
    character2 = "Character2"
    character3 = "Character3"
    character4 = "Character4"
    director = "Director0"
    writer = "Writer0"
    composer = "Composer0"