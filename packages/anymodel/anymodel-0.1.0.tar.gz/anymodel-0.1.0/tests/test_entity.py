from unittest.mock import Mock

from anymodel.types.utils import mapper
from ._models import Hero


def test_modified_fields():
    hero = Hero(name="Superman")

    assert hero.__state__.dirty
    assert hero.__pydantic_fields_set__ == {"name"}

    hero.__state__.set_clean()

    assert hero.__state__.clean
    assert hero.__pydantic_fields_set__ == set()

    hero.id = 42
    hero.name = "Batman"

    assert hero.__state__.dirty
    assert hero.__pydantic_fields_set__ == {"id", "name"}


def test_identity():
    # is identity at the right place ? does not make much sense out of a mapping context
    hero = Hero(name="Superman")
    assert hero.__state__.identity is None

    hero.__state__.identity = {"id": 42}
    assert hero.__state__.identity == {"id": 42}
    assert hero.id == 42  # identity setter updates the entity

    hero.__state__.detach()
    assert hero.__state__.identity is None


def test_mapper():
    hero = Hero(name="Superman")
    assert mapper(hero) is None

    mock_mapper = Mock()
    hero.__mapper__ = mock_mapper

    assert mapper(hero) is mock_mapper
