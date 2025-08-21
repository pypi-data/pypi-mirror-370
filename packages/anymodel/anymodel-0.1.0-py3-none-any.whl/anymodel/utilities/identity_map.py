"""Identity map implementation for preventing duplicate entity instances.

This module provides the IdentityMap class which ensures that only one
instance of an entity with a given identity exists in memory at a time.
"""

from typing import Any, MutableMapping
from weakref import WeakValueDictionary

from anymodel.types.entity import Entity

Identity = tuple[str, ...]


class IdentityMap:
    """Maintains a single instance per entity identity.

    Uses weak references to allow garbage collection of entities
    that are no longer referenced elsewhere in the application.
    """

    _map: MutableMapping[Identity, Any]

    def __init__(self):
        self._map = WeakValueDictionary()

    def set(self, key: Identity, entity: Entity | None):
        if entity is None:
            return None
        self._map[key] = entity
        return entity

    def get(self, key: Identity) -> Entity | None:
        return self._map.get(tuple(key))
