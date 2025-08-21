"""Filesystem-based storage implementation.

This module provides a storage backend that persists entities as files
on the filesystem, with hierarchical directory structure for efficient access.
"""

import os.path
import pickle
from os import PathLike
from pathlib import Path
from typing import Iterable, Optional

from anymodel.storages import Storage
from anymodel.types.mappings import ResultMapping


def _get_relative_path_from_criteria(criteria: dict) -> Path:
    if len(criteria) != 1 or "id" not in criteria:
        raise ValueError(f"Only 'id' criteria is supported for this storage type, got {criteria}.")

    if not criteria["id"]:
        raise ValueError(f"Empty 'id' criteria is not supported for this storage type, got {criteria}.")

    pk = str(criteria["id"])

    if len(pk) <= 4:
        return Path("__") / pk
    if len(pk) <= 6:
        return Path(pk[:2]) / "__" / pk[2:]
    return Path(pk[:2]) / pk[2:4] / pk[4:]


class FileSystemStorage(Storage):
    """Storage backend that persists entities to the filesystem.

    Stores entities as pickled files in a hierarchical directory structure
    based on entity IDs for efficient access to large numbers of entities.
    """

    def __init__(self, path: str | PathLike):
        self.path = Path(path)

    def find_one(self, tablename: str, criteria: dict) -> Optional[ResultMapping]:
        filename = self.path / _get_relative_path_from_criteria(criteria)
        if not os.path.exists(filename):
            return None
        with open(filename, "rb") as f:
            return pickle.load(f)

    def find_all(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                with open(os.path.join(root, file), "rb") as f:
                    yield pickle.load(f)

    def find_many(
        self, tablename: str, criteria: dict, *, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Iterable[ResultMapping]:
        raise NotImplementedError(f'{type(self).__name__} does not implement "find_many" method.')

    def insert(self, tablename: str, values: dict) -> ResultMapping:
        identity = {"id": values["id"]}
        filename = self.path / _get_relative_path_from_criteria(identity)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, "wb+") as f:
            pickle.dump(values, f)
        return identity

    def update(self, tablename: str, criteria: dict, values: dict) -> None:
        pass

    def delete(self, tablename: str, identity: dict) -> None:
        filename = self.path / _get_relative_path_from_criteria(identity)
        if os.path.exists(filename):
            os.remove(filename)
        else:
            raise FileNotFoundError(f"File {filename} not found.")
