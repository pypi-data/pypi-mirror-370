"""Entity base class and state management.

This module provides the Entity base class for domain objects and
the MappingState class for tracking entity persistence state.
"""

from functools import cached_property
from typing import Optional

from pydantic import BaseModel

_IDENTITY_ATTRIBUTE = "__identity__"


class MappingState:
    """Tracks the persistence state of an entity.

    Manages whether an entity is transient, dirty, or clean,
    and maintains the entity's identity in the storage system.
    """

    def __init__(self, entity):
        self._entity = entity
        self._identity = None
        self._store = None

    @property
    def transient(self):
        """is the related entity transiant, aka not mapped to anything (yet)?"""
        return self.identity is None

    @property
    def dirty(self):
        """is the entity modified since the last clean state (from storage or defaults)?"""
        return bool(len(self._entity.__pydantic_fields_set__))

    @property
    def clean(self):
        """is the entity clean? (aka not modified since last save)"""
        return not self.dirty

    @property
    def identity(self):
        return self._identity

    @identity.setter
    def identity(self, value: dict):
        self._identity = value

        # XXX maybe not the right place, should the state really update the entity ???? And if so, should it mark it
        # as clean ?
        self._entity.__dict__.update(value)

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, value: Optional[str]):
        self._store = value

    def detach(self):
        self._identity = None

    def set_clean(self):
        self._entity.__pydantic_fields_set__ = set()

    def __eq__(self, other):
        return set(other) == set(
            k
            for k, v in {
                "clean": self.clean,
                "dirty": self.dirty,
                "transient": self.transient,
            }.items()
            if v
        )


class Entity(BaseModel):
    """Base class for domain entities.

    Extends Pydantic's BaseModel with state tracking capabilities
    for use with the data mapper pattern. Entities track their
    modification state and storage identity.
    """

    @cached_property
    def __state__(self):
        """lazy initialized object to store the mapping state of the entity."""
        return MappingState(self)

    def __repr__(self):
        transient = "~" if self.__state__.transient else ""
        dirty = "*" if self.__state__.dirty else ""
        store = f" (&{self.__state__.store})" if self.__state__.store else ""
        return f"<{transient}{type(self).__name__}{dirty} {hex(id(self))}> {super().__str__()}{store}>"
