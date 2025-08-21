"""In-memory storage implementation for testing and temporary data."""

from collections import defaultdict
from functools import reduce
from typing import Iterable, Optional

from anymodel.storages import Storage
from anymodel.types.entity import Entity
from anymodel.types.mappings import ResultMapping


class MemoryStorage(Storage):
    """In-memory storage backend.

    Stores entities in dictionaries without persistence. Useful for testing
    and temporary data that doesn't need to survive application restarts.
    """

    def __init__(self):
        self._tables = defaultdict(dict)
        self._autoincrements = defaultdict(int)

    def __len__(self):
        return reduce(lambda x, y: x + len(y), self._tables.values(), 0)

    def migrate(self, **kwargs):
        pass

    def delete(self, entity: Entity) -> Entity:
        pass

    def find_one(self, tablename: str, criteria: dict) -> Optional[ResultMapping]:
        for row in self.find_many(tablename, criteria, limit=1):
            return row

    def find_many(
        self, tablename: str, criteria: dict, *, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Iterable[ResultMapping]:
        limit, offset = max(limit, 0) if limit is not None else None, max(offset or 0, 0)
        current = 0

        for row in self._tables[tablename].values():
            # Stop if limit is reached, implemented here to support limit=0
            if limit is not None and current >= limit:
                break

            # Check if row matches criteria
            for k, v in criteria.items():
                if row.get(k) != v:
                    break

            # Yield row if all criteria are met
            else:
                # ... but not until offset is reached
                if offset > 0:
                    offset -= 1
                    continue

                yield row
                current += 1

    def insert(self, tablename: str, values: dict) -> ResultMapping:
        if "id" not in values:
            self._autoincrements[tablename] += 1
            identity = {"id": self._autoincrements[tablename]}
        else:
            identity = {"id": values["id"]}

        # XXX we cast as string here for performances reasons (dicts with string keyx are way faster than anything else)
        # This may not be the best idea.
        _key = str(identity["id"])
        self._tables[tablename][_key] = {**values, **identity}

        return identity

    def update(self, tablename: str, criteria: dict, values: dict) -> None:
        if (row := self.find_one(tablename, criteria)) is not None:
            _key = str(row["id"])
            self._tables[tablename][_key] = {**row, **values}
            return self._tables[tablename][_key]
        raise ValueError("Row not found, cannot update.")
