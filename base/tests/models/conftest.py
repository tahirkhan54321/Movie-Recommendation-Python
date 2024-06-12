# register your factories and make them available from within our tests

from pytest_factoryboy import register

from .factories import movie_factory

register(movie_factory)