# -*- coding: utf-8 -*-
"""Entry storage operations for the trie."""

# pylint does not understand the Protocol declaration of the mixing class
# pylint: disable=no-member

from typing import Any, cast, Optional

from ..exceptions import DuplicateKeyError, InvalidGeneralizedKeyError, ErrorTag
from ..nodes import Node
from ..protocols import GeneralizedKey
from ..types import TrieEntry, TrieId
from ..validation import is_generalizedkey

from .trie_mixins import TrieMixinsInterface

# Disabled because pyright does not understand mixins
# use of private attributes from the mixing class as declared
# in the TrieMixinsInterface protocol.
# pyright: reportPrivateUsage=false


class TrieStorageMixin:
    """Mixin providing entry storage operations."""

    def add(self: TrieMixinsInterface, key: GeneralizedKey, value: Optional[Any] = None) -> TrieId:
        """Adds the key to the trie.

        .. warning:: **Keys Must Be Immutable**

            Once a key is added to the trie, neither the key sequence itself nor any of its
            constituent tokens should be mutated. Modifying a key after it has been added
            can corrupt the internal state of the trie, leading to unpredictable behavior
            and making entries unreachable. The trie does not create a deep copy of keys
            for performance reasons.

            If you need to modify a key, you should remove the old key and add a new one
            with the modified value.

        Args:
            key (GeneralizedKey): Must be an object that can be iterated and that when iterated
                returns elements conforming to the :class:`TrieKeyToken` protocol.
            value (Optional[Any], default=None): Optional value to associate with the key.

        Raises:
            InvalidGeneralizedKeyError:
                If key is not a valid :class:`GeneralizedKey`.
            DuplicateKeyError:
                If the key is already in the trie.

        Returns:
            :class:`TrieId`: Id of the inserted key. If the key was not in the trie,
            it returns the id of the new entry. If the key was already in the trie,
            it raises a :class:`DuplicateKeyError`.
        """
        return self._store_entry(key=key, value=value, allow_value_update=False)

    def update(self: TrieMixinsInterface, key: GeneralizedKey, value: Optional[Any] = None) -> TrieId:
        """Updates the key/value pair in the trie.

        .. warning:: **Keys Must Be Immutable**

            Once a key is added to the trie, neither the key sequence itself nor any of its
            constituent tokens should be mutated. Modifying a key after it has been added
            can corrupt the internal state of the trie, leading to unpredictable behavior
            and making entries unreachable. The trie does not create a deep copy of keys
            for performance reasons.

            If you need to modify a key, you should remove the old key and add a new one
            with the modified value.

        Args:
            key (GeneralizedKey): Must be an object that can be iterated and that when iterated
                returns elements conforming to the :class:`TrieKeyToken` protocol.
            value (Optional[Any], default=None): Optional value to associate with the key.

        Raises:
            InvalidGeneralizedKeyError:
                If key is not a valid :class:`GeneralizedKey`.

        Returns:
            :class:`TrieId`: Id of the inserted key. If the key was already in the trie with the same value
            it returns the id for the already existing entry. If the key was not already in the trie,
            it returns the id for a new entry.
        """
        return self._store_entry(key=key, value=value, allow_value_update=True)

    def _store_entry(self: TrieMixinsInterface,
                     key: GeneralizedKey,
                     value: Any,
                     allow_value_update: bool) -> TrieId:
        """Stores a key/value pair entry in the trie.

        Args:
            key (GeneralizedKey): Must be an object that can be iterated and that when iterated
            returns elements conforming to the :class:`TrieKeyToken` protocol.
            value (Optional[Any], default=None): Optional value to associate with the key.
            allow_value_update (bool):
            Whether to allow overwriting the value if the key already exists.
        Raises:
            InvalidGeneralizedKeyError: If key is not a valid :class:`GeneralizedKey`.
            DuplicateKeyError: If the key is already in the trie and `allow_value_update` is False.

        Returns:
            :class:`TrieId`: Id of the key's entry. If the key was not in the trie,
            it returns the id of the new entry. If the key was already in the trie and
            `allow_value_update` is True, it updates the value and returns the existing id.
            If the key was already in the trie and `allow_value_update` is False,
            it raises a :class:`DuplicateKeyError`.
        """
        if self.runtime_validation and not is_generalizedkey(key):
            raise InvalidGeneralizedKeyError(
                msg="key is not a valid `GeneralizedKey`",
                tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY)

        # Traverse the trie to find the insertion point for the key,
        # creating nodes as necessary.
        current_node = self
        for token in key:
            if token not in current_node.children:
                child_node = Node(token=token, parent=current_node)  # type: ignore[reportArgumentType]
                current_node.children[token] = child_node
            current_node = current_node.children[token]

        # This key is already in the trie (it has a trie id)
        if current_node.ident:
            # If we allow updating, update the value and return the existing id
            if allow_value_update:
                current_node.value = value
                self._trie_entries[current_node.ident] = TrieEntry(
                    current_node.ident, key, value)
                return current_node.ident

            # The key is already in the trie but we are not allowing updating values - so raise an error
            raise DuplicateKeyError(
                msg=("Attempted to store a key with a value that is already in the trie "
                     " - use `update()` to change the value of an existing key."),
                tag=ErrorTag.STORE_ENTRY_DUPLICATE_KEY)

        # Assign a new trie id for the node and set the value
        self._ident_counter += 1
        new_ident = TrieId(self._ident_counter)
        current_node.ident = new_ident
        current_node.value = value
        self._trie_index[new_ident] = cast(Node, current_node)
        self._trie_entries[new_ident] = TrieEntry(new_ident, key, value)

        return new_ident
