# -*- coding: utf-8 -*-
"""Core data types for the gentrie package."""

from typing import Any, NamedTuple, Optional

from .protocols import GeneralizedKey


# Constants for TrieEntry fields (performance optimization)
TRIE_IDENT: int = 0
"""Alias for field number 0 (ident) in TrieEntry. It is faster to use this than accessing the field by name."""
TRIE_KEY: int = 1
"""Alias for field number 1 (key) in TrieEntry. It is faster to use this than accessing the field by name."""
TRIE_VALUE: int = 2
"""Alias for field number 2 (value) in TrieEntry. It is faster to use this than accessing the field by name."""


class TrieId(int):
    """Unique identifier for a key in a trie."""
    __slots__ = ()

    def __new__(cls, value: int):
        return int.__new__(cls, value)

    def __str__(self) -> str:
        """Returns a string representation of the TrieId."""
        return f'TrieId({int(self)})'

    def __repr__(self) -> str:
        """Returns a string representation of the TrieId for debugging."""
        return f'TrieId({int(self)})'


class TrieEntry(NamedTuple):
    """A :class:`TrieEntry` is a :class:`NamedTuple` containing the unique identifer and key for an entry in the trie.
    """

    ident: TrieId
    """:class:`TrieId` Unique identifier for a key in the trie. Alias for field number 0."""
    key: GeneralizedKey
    """:class:`GeneralizedKey` Key for an entry in the trie. Alias for field number 1."""
    value: Optional[Any] = None
    """Optional value for the entry in the trie. Alias for field number 2."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrieEntry):
            return False
        return self.ident == other.ident and tuple(self.key) == tuple(
            other.key)

    def __hash__(self) -> int:
        return hash((self.ident, tuple(self.key)))
