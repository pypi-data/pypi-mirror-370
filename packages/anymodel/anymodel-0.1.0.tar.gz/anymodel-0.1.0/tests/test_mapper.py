from anymodel import MemoryStorage, Mapper
from ._models import Hero


def test_basics():
    storage = MemoryStorage()
    mapper = Mapper(Hero, storage=storage)
    storage.migrate()  # not necessary for memory storage but we may want to simulate something ?

    assert mapper.primary_key == ("id",)

    hero = Hero(name="Superman")
    assert hero.id is None
    assert hero.__state__ == {"transient", "dirty"}
    assert len(storage) == 0

    mapper.save(hero)
    assert len(storage) == 1
    assert hero.id == 1
    assert hero.__state__ == {"clean"}

    hero.name = "Uberman"
    assert hero.__state__ == {"dirty"}

    mapper.save(hero)
    assert len(storage) == 1
    assert hero.id == 1
    assert hero.__state__ == {"clean"}


def test_relations():
    storage = MemoryStorage()
    mapper = Mapper(Hero, storage=storage)
    storage.migrate()

    assert mapper.primary_key == ("id",)

    hero = Hero(name="Superman")
    assert hero.id is None
    assert hero
