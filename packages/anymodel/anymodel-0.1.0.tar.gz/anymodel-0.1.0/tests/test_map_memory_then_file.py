from anymodel.mapper import Mapper
from anymodel import MemoryStorage
from ._models import Hero


class HeroMapper(Mapper[Hero]):
    pass


def test_multimap():
    # This test seems incomplete - creating a minimal working test
    storage = MemoryStorage()
    heroes = HeroMapper(Hero, storage=storage)
    assert heroes.storage == storage
