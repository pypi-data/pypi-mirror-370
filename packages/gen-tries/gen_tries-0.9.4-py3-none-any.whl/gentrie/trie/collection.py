# -*- coding: utf-8 -*-
"""Collection operations for GeneralizedTrie."""

from typing import Generator

from ..types import TrieEntry, TrieId

from .trie_mixins import TrieMixinsInterface


class TrieCollectionMixin:
    """Mixin providing collection operations (__len__, __iter__, keys, values, items)."""

    def __len__(self: TrieMixinsInterface) -> int:
        """Returns the number of keys in the trie.

        Returns:
            :class:`int`: Number of keys in the trie.

        Usage::

            n_keys: int = len(trie)

        """
        return len(self._trie_index)  # pyright: ignore[reportPrivateUsage]

    def __iter__(self: TrieMixinsInterface) -> Generator[TrieId, None, None]:
        """Returns an iterator for the trie.

        The generator yields the :class:`TrieId`for each key in the trie.

        Returns:
            :class:`Generator[TrieId, None, None]`: Generator for the trie.
        """
        # pylint: disable=consider-iterating-dictionary
        return (
            entry for entry in self._trie_entries.keys()  # pyright: ignore[reportPrivateUsage]
            )

    def keys(self: TrieMixinsInterface) -> Generator[TrieId, None, None]:
        """Returns an iterator for all the TrieIds in the trie.

        The generator yields the :class:`TrieId` for each key in the trie.

        It returns TrieIds instead of GeneralizedKeys because TrieIds are

        1. Faster: Lookups using TrieIds are *O(1)* for time regardless
           of the length of the GeneralizedKey they are associated with vs *O(n)*
           to the length of keys for operations using GeneralizedKeys to look
           up entries.

        2. More efficient memory usage: TrieIds are typically smaller in size
           compared to GeneralizedKeys, leading to reduced memory overhead
           when storing and processing keys in the trie.

        3. Guaranteed stable even with key modifications: TrieIds remain
           consistent even if the underlying GeneralizedKey changes, making
           them more reliable for long-term storage and retrieval.

        Returns:
            :class:`Generator[TrieId, None, None]`: Generator for the trie.
        """
        # pylint: disable=consider-iterating-dictionary
        return (entry for entry in self._trie_entries.keys())  # pyright: ignore[reportPrivateUsage]

    def values(self: TrieMixinsInterface) -> Generator[TrieEntry, None, None]:
        """Returns an iterator for all the TrieEntry entries in the trie.

        The generator yields the :class:`TrieEntry` for each key in the trie.

        Returns:
            :class:`Generator[TrieEntry, None, None]`: Generator for the trie.
        """
        return (entry for entry in self._trie_entries.values())  # pyright: ignore[reportPrivateUsage]

    def items(self: TrieMixinsInterface) -> Generator[tuple[TrieId, TrieEntry], None, None]:
        """Returns an iterator for the trie.

        The keys are the TrieIds and the values are the TrieEntry instances.

        The generator yields the :class:`TrieId` and :class:`TrieEntry` for each key in the trie.

        Returns:
            :class:`Generator[tuple[TrieId, TrieEntry], None, None]`: Generator for the trie.
        """
        return ((key, value) for key, value in self._trie_entries.items())   # pyright: ignore[reportPrivateUsage]
