"""Utility functions for type operations.

This module provides utility functions for working with entities
and their metadata.
"""


def mapper(mixed):
    """Get the mapper associated with an object."""
    return getattr(mixed, "__mapper__", None)


def getmeta(mixed, key, default=None):
    """Get metadata value from an object.

    Args:
        mixed: Object to get metadata from
        key: Metadata key to retrieve
        default: Default value if key not found

    Returns:
        The metadata value or default
    """
    metadata = getattr(mixed, "__metadata__", None)
    if metadata:
        return metadata.get(key, default)
    return default
