"""Type definitions for AnyModel entities and relationships.

This module provides the core types for defining domain models including
entities, collections, and relationships between entities.
"""

from .collections import Collection
from .entity import Entity
from .relations import OneToManyRelation

__all__ = [
    "Collection",
    "Entity",
    "OneToManyRelation",
]
