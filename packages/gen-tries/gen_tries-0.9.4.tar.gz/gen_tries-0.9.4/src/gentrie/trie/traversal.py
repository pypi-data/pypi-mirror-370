# -*- coding: utf-8 -*-
"""Traversal operations for GeneralizedTrie."""

from collections import deque
from typing import Generator

from ..exceptions import InvalidGeneralizedKeyError, ErrorTag, TrieTypeError, TrieValueError
from ..protocols import GeneralizedKey
from ..types import TrieEntry
from ..validation import is_generalizedkey

from .trie_mixins import TrieMixinsInterface

# Disabled because pyright does not understand mixins
# use of private attributes from the mixing class as declared
# in the TrieMixinsInterface protocol.
# pyright: reportPrivateUsage=false


class TrieTraversalMixin:
    """Mixin providing traversal operations (prefixes, prefixed_by)."""

    def prefixes(self: TrieMixinsInterface, key: GeneralizedKey) -> Generator[TrieEntry, None, None]:
        """Yields TrieEntry instances for all keys in the trie that are a prefix of the passed key.

        Searches the trie for all keys that are prefix matches
        for the key and yields their TrieEntry instances.

        .. note::

            The `prefixes` method finds all keys that are prefixes of the passed
            key.  For example, `trie.prefixes('apple')` will find entries for
            keys like 'a', 'apple' and 'app'.

        .. warning:: **GOTCHA: Generators**

            Because generators are not executed until the first iteration,
            they may not behave as expected if not consumed properly. For example,
            exceptions will not be raised until the generator is iterated over.

        Args:
            key (GeneralizedKey): Key for matching.

        Yields:
            :class:`TrieEntry`: The next matching :class:`TrieEntry` instance.

        Raises:
            InvalidGeneralizedKeyError:
                If key is not a valid :class:`GeneralizedKey`
                (is not a :class:`Sequence` of :class:`TrieKeyToken` objects).

        Usage::

            from gentrie import GeneralizedTrie, TrieEntry

            trie: GeneralizedTrie = GeneralizedTrie()
            keys: list[str] = ['abcdef', 'abc', 'a', 'abcd', 'qrs']
            for entry in keys:
                trie.add(entry)
            matches_generator: Generator[TrieEntry, None, None] = trie.prefixes('abcd')
            for trie_entry in sorted(list(matches_generator)):
                print(f'{trie_entry.ident}: {trie_entry.key}')

            # 2: abc
            # 3: a
            # 4: abcd
        """
        if self.runtime_validation and not is_generalizedkey(key):
            raise InvalidGeneralizedKeyError(
                msg="key is not a valid `GeneralizedKey`",
                tag=ErrorTag.TRIE_PREFIXES_INVALID_GENERALIZED_KEY
            )

        current_node = self

        for token in key:
            if current_node.ident:
                yield self._trie_entries[current_node.ident]
            if token not in current_node.children:
                return  # no match in children, so the generator is done
            current_node = current_node.children[token]

        # If we reached here, we have a match for the full key
        if current_node.ident:
            yield self._trie_entries[current_node.ident]

    def prefixed_by(self: TrieMixinsInterface, key: GeneralizedKey, depth: int = -1
                    ) -> Generator[TrieEntry, None, None]:
        """Yields all entries in the trie that are prefixed by the given key, up to a specified depth.

        Searches the trie for all keys that start with the provided key and yields their
        :class:`TrieEntry` instances.

        .. note::
            The `prefixed_by` method finds all keys that start with the given
            prefix. For example, `trie.prefixed_by('app')` will find entries for
            keys like 'apple' and 'application'.

        .. warning:: **GOTCHA: Generators**

            Because generators are not executed until the first iteration,
            they may not behave as expected if not consumed properly. For example,
            exceptions will not be raised until the generator is iterated over.

        Args:
            key (GeneralizedKey): Key for matching.
            depth (`int`, default=-1): Depth starting from the matched key to include.
                The depth determines how many 'layers' deeper into the trie to look for prefixed_by.:
                * A depth of -1 (the default) includes ALL entries for the exact match and all children nodes.
                * A depth of 0 only includes the entries for the *exact* match for the key.
                * A depth of 1 includes entries for the exact match and the next layer down.
                * A depth of 2 includes entries for the exact match and the next two layers down.

        Yields:
            :class:`TrieEntry`: The next matching :class:`TrieEntry` instance.

        Raises:
            InvalidGeneralizedKeyError:
                If key arg is not a valid GeneralizedKey.
            TrieTypeError:
                If depth arg is not an int.
            TrieValueError:
                If depth arg is less than -1.


        Usage::

            from gentrie import GeneralizedTrie, TrieEntry

            trie = GeneralizedTrie()
            keys: list[str] = ['abcdef', 'abc', 'a', 'abcd', 'qrs']
            for entry in keys:
                trie.add(entry)
            matches_generator = trie.prefixed_by('abcd')

            for trie_entry in sorted(list(matches_generator)):
                print(f'{trie_entry.ident}: {trie_entry.key}')

            # 1: abcdef
            # 4: abcd
        """
        if self.runtime_validation and not is_generalizedkey(key):
            raise InvalidGeneralizedKeyError(
                msg="key arg is not a valid GeneralizedKey",
                tag=ErrorTag.TRIE_PREFIXED_BY_INVALID_GENERALIZED_KEY
            )

        if not isinstance(depth, int):  # type: ignore[reportUnnecessaryIsInstance]
            raise TrieTypeError(
                msg="depth must be an int",
                tag=ErrorTag.TRIE_PREFIXED_BY_BAD_DEPTH_TYPE
            )
        if depth < -1:
            raise TrieValueError(
                msg="depth cannot be less than -1",
                tag=ErrorTag.TRIE_PREFIXED_BY_BAD_DEPTH_VALUE
            )

        current_node = self
        try:
            for token in key:
                current_node = current_node.children[token]
        except KeyError:
            return  # No match, so the generator is empty

        # Perform a breadth-first search to collect prefixed keys up to the specified depth
        queue = deque([(current_node, depth)])

        while queue:
            node, current_depth = queue.popleft()
            if node.ident:
                yield self._trie_entries[node.ident]
            if current_depth != 0:
                for child in node.children.values():
                    queue.append((child, current_depth - 1))
