"""Storage backends for AnyModel.

This module provides various storage implementations for persisting entities.
Available storage backends include in-memory, filesystem, and SQL database storage.
"""

from anymodel.storages.base import Storage

__all__ = [
    "Storage",
]
