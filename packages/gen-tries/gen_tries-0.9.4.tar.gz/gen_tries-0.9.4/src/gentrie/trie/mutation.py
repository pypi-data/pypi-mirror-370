# -*- coding: utf-8 -*-
"""Mutation operations for the trie."""

from typing import Any

from ..protocols import GeneralizedKey
from ..types import TrieId

from .trie_mixins import TrieMixinsInterface


class TrieMutationMixin:
    """Mixin providing mutation operations."""

    def __setitem__(self: TrieMixinsInterface, key: GeneralizedKey, value: Any) -> None:
        """Adds or updates an entry in the trie using subscript notation.

        This is a convenience wrapper for the :meth:`update` method.

        Example:
            trie[['ape', 'green', 'apple']] = "A green apple"

        Args:
            key (GeneralizedKey): The key for the entry.
            value (Any): The value to associate with the key.

        Raises:
            InvalidGeneralizedKeyError: If key is not a valid :class:`GeneralizedKey`.
        """
        self.update(key, value)

    def __delitem__(self: TrieMixinsInterface, key: TrieId | GeneralizedKey) -> None:
        """Removes an entry from the trie using subscript notation.

        This is a convenience wrapper for the :meth:`remove` method.

        Example:
            del trie[['ape', 'green', 'apple']]

        Args:
            key (TrieId | GeneralizedKey): The identifier for the entry to remove.

        Raises:
            KeyError: if the key does not exist in the trie.
            TypeError: if the key is not a :class:`TrieId` or a valid :class:`GeneralizedKey`.
        """
        self.remove(key)
