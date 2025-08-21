from sqlalchemy.exc import OperationalError
from typing import Optional

from anymodel.types.entity import Entity
from anymodel.mapper import Mapper
from anymodel.storages.sqlalchemy import SqlAlchemyStorage
import pytest


class Hero(Entity):
    id: Optional[int] = None
    name: str


class HeroMapper(Mapper[Hero]):
    pass


def test_basics():
    storage = SqlAlchemyStorage("sqlite:///:memory:")
    mapper = HeroMapper(storage=storage)

    hero = Hero(name="Superman")

    with pytest.raises(OperationalError):
        mapper.save(hero)

    storage.migrate()

    # Test is incomplete - storage doesn't have a save method
    # hero = Hero(id=1, name="Superman")
    # hero = storage.save(hero)
