# -*- coding: utf-8 -*-
"""Entry removal operations for the trie."""
from typing import Optional

from ..exceptions import ErrorTag, TrieKeyError, TrieTypeError
from ..protocols import GeneralizedKey, TrieKeyToken
from ..types import TrieId
from ..validation import is_generalizedkey

from .trie_mixins import TrieMixinsInterface

# Disabled because pyright does not understand mixins
# use of private attributes from the mixing class as declared
# in the TrieMixinsInterface protocol.
# pyright: reportPrivateUsage=false


class TrieRemovalMixin:
    """Mixin providing entry removal operations.

    Note: This mixin accesses private attributes of the mixing class.
    This is intentional and necessary for the mixin pattern
    """

    def remove(self: TrieMixinsInterface, key: TrieId | GeneralizedKey) -> None:
        """Remove the specified key from the trie.

        Removes the key from the trie. If the key is not found, it raises a KeyError.
        The key can be specified either as a :class:`TrieId` or as a :class:`GeneralizedKey`.

        Args:
            key (TrieId | GeneralizedKey): identifier for key to remove.

        Raises:
            TrieTypeError: if the key arg is not a :class:`TrieId` or a valid :class:`GeneralizedKey`.
            TrieKeyError: if the key arg does not match the id or trie key of any entries in the trie.
        """
        ident: Optional[TrieId] = None
        if isinstance(key, TrieId):
            ident = key
        # If runtime validation is disabled, we just ASSUME the key is a GeneralizedKey
        # if we got to here.
        elif (not self.runtime_validation) or is_generalizedkey(key):
            try:
                ident = self[key].ident
            except KeyError:
                ident = None
            except TypeError as exc:
                raise RuntimeError("[GTR003] failed lookup of key because of unexpected exception") from exc
        else:
            raise TrieTypeError(
                msg="key arg must be of type TrieId or a valid GeneralizedKey",
                tag=ErrorTag.REMOVAL_INVALID_KEY_TYPE
            )

        if ident is None or ident not in self._trie_index:
            raise TrieKeyError(
                msg="key not found",
                tag=ErrorTag.REMOVAL_KEY_NOT_FOUND)

        # Get the node and delete its id from the trie index and entries
        # and remove the node from the trie.
        node = self._trie_index[ident]
        del self._trie_index[ident]
        del self._trie_entries[ident]

        # Remove the id from the node
        node.ident = None

        # If the node still has other trie ids or children, we're done: return
        if node.children:
            return

        # No trie ids or children are left for this node, so prune
        # nodes up the trie tree as needed.
        token: Optional[TrieKeyToken] = node.token
        parent = node.parent
        while parent is not None:
            del parent.children[token]
            # explicitly break possible cyclic references
            node.parent = node.token = None

            # If the parent node has a trie id or children, we're done: return
            if parent.ident or parent.children:
                return
            # Keep purging nodes up the tree
            token = parent.token
            node = parent
            parent = node.parent
        return
