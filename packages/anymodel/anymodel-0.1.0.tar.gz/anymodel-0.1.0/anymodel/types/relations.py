"""Entity relationship definitions.

This module provides classes for defining relationships between entities,
supporting lazy loading and automatic persistence of related entities.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from anymodel.mapper import Mapper  # noqa: F401


class Relation(ABC):
    """Abstract base class for entity relationships."""

    @abstractmethod
    def get_find_callback_for(self, mapper, entity):
        raise NotImplementedError

    @abstractmethod
    def save(self, mapper, entity, related_entity):
        raise NotImplementedError


class OneToManyRelation(Relation):
    """Represents a one-to-many relationship between entities.

    Manages the loading and persistence of related entities in
    a one-to-many relationship.
    """

    def __init__(self, mapper: "Mapper"):
        self.mapper = mapper

    def get_find_callback_for(self, mapper, row):
        def load():
            return self.mapper.find(**{f"{mapper.__tablename__}_id": str(row["id"])})

        return load

    def save(self, mapper, entity, related_entity):
        setattr(related_entity, f"{mapper.__tablename__}_id", entity.id)
        return self.mapper.save(related_entity)
