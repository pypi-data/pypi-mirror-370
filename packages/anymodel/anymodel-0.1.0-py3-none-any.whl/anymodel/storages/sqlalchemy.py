"""SQLAlchemy-based storage implementation.

This module provides a storage backend that persists entities to
SQL databases using SQLAlchemy, with support for automatic migrations.
"""

from typing import Any, Iterable, Optional, Union, override

from sqlalchemy import URL, Column, MetaData, Table, create_engine
from sqlmodel.main import get_sqlalchemy_type

from anymodel import Mapper
from anymodel.storages import Storage
from anymodel.types.entity import Entity
from anymodel.types.mappings import ResultMapping
from anymodel.utilities.migrations import automigrate


class SqlAlchemyStorage(Storage):
    """Storage backend for SQL databases via SQLAlchemy.

    Provides persistence to any SQLAlchemy-supported database with
    automatic schema migration capabilities.
    """

    def __init__(self, url: Union[str, URL], **kwargs: Any):
        self.engine = create_engine(url, **kwargs)
        self.metadata = MetaData()
        self.tables = {}

    def insert(self, tablename: str, values: dict) -> ResultMapping:
        """Insert a new row into the table, returns the newly generated primary key."""
        table = self.tables[tablename]

        with self.engine.connect() as conn:
            result = conn.execute(table.insert().values(values))
            conn.commit()

        return result.inserted_primary_key._mapping

    def update(self, tablename: str, identity: dict, values: dict) -> None:
        """Updates an existing row in the table."""
        table = self.tables[tablename]
        criteria = _as_criteria(table, identity)

        with self.engine.connect() as conn:
            conn.execute(table.update().where(*criteria).values(values))
            conn.commit()

    @override
    def find_one(self, tablename: str, criteria: dict) -> Optional[ResultMapping]:
        table = self.tables[tablename]
        criteria = _as_criteria(table, criteria)

        query = table.select().where(*criteria)
        with self.engine.connect() as conn:
            result = conn.execute(query)
            row = result.fetchone()
            if row is None:
                return None
            return row._mapping

    @override
    def find_many(self, tablename: str, criteria: dict, *, limit=None, offset=None) -> Iterable[ResultMapping]:
        table = self.tables[tablename]
        criteria = _as_criteria(table, criteria)

        query = table.select().where(*criteria)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        with self.engine.connect() as conn:
            result = conn.execute(query)
            for row in result:
                yield row._mapping

    ### rework (or work) needed

    @override
    def delete(self, entity: Entity) -> Entity:
        ...
        return entity

    @override
    def add_table(self, mapper: Mapper):
        if mapper.__tablename__ in self.tables:
            raise ValueError(f'Table for "{mapper.__tablename__}" already registered.')

        columns = []

        for field in mapper.primary_key:
            field_info = mapper.__type__.model_fields[field]
            columns.append(Column(field, get_sqlalchemy_type(field_info), primary_key=True))

        for field in mapper.fields:
            if field in mapper.primary_key:
                continue
            field_info = mapper.__type__.model_fields[field]
            columns.append(Column(field, get_sqlalchemy_type(field_info)))

        self.tables[mapper.__tablename__] = Table(mapper.__tablename__, self.metadata, *columns)

    @override
    def migrate(self, **kwargs):
        old_echo = self.engine.echo
        self.engine.echo = kwargs.get("echo", old_echo)
        try:
            automigrate(self.engine, self.metadata)
        finally:
            self.engine.echo = old_echo


def _as_criteria(table: Table, criteria: dict[str, Any]) -> list:
    return [getattr(table.c, col) == val for col, val in criteria.items()]
