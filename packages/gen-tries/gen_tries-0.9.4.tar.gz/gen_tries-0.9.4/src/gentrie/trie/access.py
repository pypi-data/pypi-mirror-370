# -*- coding: utf-8 -*-
"""Data access operations for the trie."""

from typing import Any, Optional

from ..exceptions import ErrorTag, InvalidGeneralizedKeyError, TrieKeyError, TrieTypeError
from ..types import TrieEntry, TrieId, GeneralizedKey
from ..validation import is_generalizedkey

from .trie_mixins import TrieMixinsInterface

# Disabled because pyright does not understand mixins
# use of private attributes from the mixing class as declared
# in the TrieMixinsInterface protocol.
# pyright: reportPrivateUsage=false


class TrieAccessMixin:
    """Mixin providing data access operations.

    Note: This mixin accesses private attributes of the mixing class.
    This is intentional and necessary for the mixin pattern.
    """
    def __contains__(self: TrieMixinsInterface, key_or_ident: GeneralizedKey | TrieId) -> bool:
        """Returns True if the trie contains a GeneralizedKey or TrieId matching the passed key.

        This method checks if the trie contains a key that matches the provided key_or_ident.
        The key can be specified either as a :class:`GeneralizedKey` or as a :class:`TrieId`.

        A lookup by :class:`TrieId` is a fast operation (*O(1)* time) while a lookup by :class:`GeneralizedKey`
        involves traversing the trie structure to find a matching key (*O(n)* time in the worst case,
        where n is the key length).

        Args:
            key_or_ident (GeneralizedKey | TrieId): Key or TrieId for matching.

        Returns:
            :class:`bool`: True if there is a matching GeneralizedKey/TrieId in the trie. False otherwise.
        """
        if isinstance(key_or_ident, TrieId):
            # If it's a TrieId, check if it exists in the trie index
            return key_or_ident in self._trie_index

        if self.runtime_validation and not is_generalizedkey(key_or_ident):
            return False

        current_node = self
        for token in key_or_ident:
            if token not in current_node.children:
                return False
            current_node = current_node.children[token]

        return current_node.ident is not None

    def __getitem__(self: TrieMixinsInterface, key: TrieId | GeneralizedKey) -> TrieEntry:
        """Returns the :class:`TrieEntry` for the ident or key with the passed identifier.

        The identifier can be either the :class:`TrieId` (ident) or the :class:`GeneralizedKey` (key)
        for the entry.

        Args:
            key (TrieId | GeneralizedKey): the identifier to retrieve.

        Returns: :class:`TrieEntry`: TrieEntry for the key with the passed identifier.

        Raises:
            TrieKeyError: if the key arg does not match any keys/idents in the trie.
            TrieTypeError: if the key arg is neither a :class:`TrieId` or a valid :class:`GeneralizedKey`.
        """
        if isinstance(key, TrieId):
            if key not in self._trie_index:
                raise TrieKeyError("TrieId not found in trie index", ErrorTag.GETITEM_ID_NOT_FOUND)
            # Return the TrieEntry for the TrieId
            return self._trie_entries[key]

        # If runtime validation is disabled, we just ASSUME the key is a GeneralizedKey if we get here.
        if (not self.runtime_validation) or is_generalizedkey(key):
            # Find the TrieId for the key
            current_node = self
            for token in key:
                if token not in current_node.children:
                    raise TrieKeyError(
                        msg="key does not match any idents or keys in the trie",
                        tag=ErrorTag.GETITEM_KEY_NOT_FOUND,
                    )
                current_node = current_node.children[token]
            if current_node.ident:
                # Return the TrieEntry for the TrieId
                return self._trie_entries[current_node.ident]
            raise TrieKeyError(
                msg="key does not match any idents or keys in the trie",
                tag=ErrorTag.GETITEM_NOT_TERMINAL,
            )

        # If we reach here, the passed key was neither a TrieId nor a GeneralizedKey
        raise TrieTypeError(
            msg="key must be either a :class:TrieId or a :class:`GeneralizedKey`",
            tag=ErrorTag.GETITEM_INVALID_KEY_TYPE
        )

    def get(self: TrieMixinsInterface,
            key: TrieId | GeneralizedKey,
            default: Optional[Any] = None) -> Optional[TrieEntry | Any]:
        """Returns the :class:`TrieEntry` for the ident or key with the passed identifier.

        The identifier can be either the :class:`TrieId` (ident) or the :class:`GeneralizedKey` (key)
        for the entry.

        If the key is not found, it returns the default value if provided or None if not provided.

        Args:
            key (TrieId | GeneralizedKey): the identifier to retrieve.
            default (Optional[TrieEntry | Any], default=None): The default value to return if the key is not found.

        Returns: :class:`TrieEntry`: TrieEntry for the key with the passed identifier or the default value if not found.
        """
        try:
            return self[key]
        except (TrieKeyError, TrieTypeError, InvalidGeneralizedKeyError):
            return default
