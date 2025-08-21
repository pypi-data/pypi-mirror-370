"""Data mapper implementation for entity persistence.

This module provides the Mapper class which handles the persistence of entities
to various storage backends while maintaining separation between domain logic
and storage concerns.
"""

from functools import cached_property
from typing import TYPE_CHECKING, Iterable, Mapping, Optional, Type

from pyheck import snake

from anymodel.types.collections import Collection
from anymodel.types.entity import Entity
from anymodel.types.utils import getmeta
from anymodel.utilities.identity_map import IdentityMap

if TYPE_CHECKING:
    from anymodel.storages import Storage
    from anymodel.types.relations import Relation


class Mapper[TMappedEntity]:
    """Maps entities to storage backends.

    The Mapper class handles all persistence operations for a specific entity type,
    including CRUD operations, identity mapping, and relation management.
    """

    __type__: Type[TMappedEntity] = None
    __tablename__: str = None

    relations: Mapping[str, "Relation"] = None

    storage: "Storage"

    _cache: Optional[IdentityMap] = None

    def __new__(cls, *args, **kwargs):
        new_object = super().__new__(cls)

        cls._infer_type_if_possible_and_necessary(new_object)

        return new_object

    def __init__(
        self,
        entity_type: Optional[Type[Entity]] = None,
        *,
        relations: Optional[Mapping[str, "Relation"]] = None,
        storage: "Storage",
        cache: Optional[IdentityMap] = None,
    ):
        self.__type__ = self.__type__ or entity_type
        if self.__type__ is None:
            raise ValueError("Entity type not defined at mapper initialization time.")

        if self.__tablename__ is None:
            self.__tablename__ = snake(self.__type__.__name__)

        self.relations = relations or self.relations or {}
        self.storage = storage

        self._cache = cache

        # XXX should the mapper do this ? why this and not migrations ?
        self.storage.add_table(self)

    @cached_property
    def fields(self):
        return self.__type__.model_fields.keys()

    @cached_property
    def primary_key(self):
        def is_primary_key(x):
            return getattr(x, "primary_key", False)

        return tuple((k for k, v in self.__type__.model_fields.items() if is_primary_key(v)))

    def save(self, entity: TMappedEntity) -> TMappedEntity:
        """Saves an entity to the database, either inserting (if not mapped yet) or updating it (if a mapping identity
        is present)."""
        values = self._get_known_modified_values(entity)
        related_values = self._get_known_modified_related_values(entity)

        identity = entity.__state__.identity
        if identity is not None:
            # existing object, update
            self.storage.update(self.__tablename__, identity, values)
            entity.__pydantic_fields_set__ = entity.__pydantic_fields_set__.difference(values.keys())
        else:
            # new object, insert
            new_identity = self.storage.insert(self.__tablename__, values)
            entity.__state__.identity = new_identity
            entity.__state__.set_clean()

        for _field, _related_entities in related_values.items():
            relation = self.relations[_field]
            for _related_entity in _related_entities:
                relation.save(self, entity, _related_entity)

        return self._mapped(entity)

    def find_one_by_pk(self, *pk) -> TMappedEntity:
        """Find an entity by its primary key."""

        if len(pk) != len(self.primary_key):
            raise ValueError(f"Expected {len(self.primary_key)} arguments, got {len(pk)}.")

        # xxx this may be a bit naive, cast all into string will show limits (maybe)
        pk = tuple(map(str, pk))
        if self._cache is not None and (cached := self._cache.get(pk)) is not None:
            return cached
        identity = dict(zip(self.primary_key, pk))

        # find, return None if not found
        if (row := self.storage.find_one(self.__tablename__, identity)) is None:
            return None

        relations = {k: Collection(relation.get_find_callback_for(self, row)) for k, relation in self.relations.items()}

        entity = self.__type__.model_construct(**row, **relations)
        entity.__state__.store = getmeta(row, "store")
        entity.__state__.identity = identity
        entity.__state__.set_clean()

        return self._mapped(entity)

    def find(self, **criteria) -> Iterable[TMappedEntity]:
        for row in self.storage.find_many(self.__tablename__, criteria):
            entity = self.__type__.model_construct(**row)
            entity.__state__.store = getmeta(row, "store")
            entity.__state__.identity = {k: row[k] for k in self.primary_key}
            entity.__state__.set_clean()
            yield self._mapped(entity)

    ### rework needed

    def delete(self, entity: TMappedEntity):
        return self.storage.delete(entity)

    ### (semi) private, don't use out of this class

    def _mapped(self, entity: TMappedEntity) -> TMappedEntity:
        """Make sure an entity is present in the cache."""
        pk = tuple((str(getattr(entity, x)) for x in self.primary_key))
        return self._cache.set(pk, entity) if self._cache is not None else entity

    def _get_known_modified_values(self, entity: TMappedEntity) -> dict:
        """Gets a dict of changed values for the given entity, but limited to the fields we know about."""
        return {k: getattr(entity, k) for k in entity.model_fields_set if k in self.fields}

    def _get_known_modified_related_values(self, entity: TMappedEntity) -> Mapping[str, Entity]:
        """Gets a dict of changed values for the given entity, but limited to the fields we know about."""
        return {k: getattr(entity, k) for k in entity.model_fields_set if k in self.relations}

    @classmethod
    def _infer_type_if_possible_and_necessary(cls, new_object):
        try:
            inferred_type = cls.__orig_bases__[0].__args__[0]
        except (AttributeError, IndexError):
            inferred_type = None
        if (
            new_object.__type__ is None
            and inferred_type
            and (inferred_type is not TMappedEntity)
            and issubclass(inferred_type, Entity)
        ):
            new_object.__type__ = inferred_type
