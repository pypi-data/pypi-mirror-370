"""Result mapping types for storage operations.

This module provides types for handling results from storage operations,
including metadata about the storage source.
"""

from typing import Any, Iterable, Mapping

ResultMapping = Mapping[str, Any]


class ResultMappingView(ResultMapping):
    """A view over a result mapping with metadata support.

    Wraps a result mapping and adds metadata tracking capabilities
    for storage-specific information.
    """

    def __init__(self, mapping: ResultMapping, **metadata):
        self.mapping = mapping

        if hasattr(self.mapping, "__metadata__"):
            self.__metadata__ = {**self.mapping.__metadata__, **metadata}
        else:
            self.__metadata__ = metadata

    def __getitem__(self, key: str) -> Any:
        return self.mapping[key]

    def __iter__(self) -> Iterable[str]:
        return iter(self.mapping)

    def __len__(self) -> int:
        return len(self.mapping)
