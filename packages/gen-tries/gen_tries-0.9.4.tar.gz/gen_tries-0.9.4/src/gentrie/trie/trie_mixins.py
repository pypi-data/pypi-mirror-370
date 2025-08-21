"""Protocol for all GeneralizedTrie trie mixins."""

from typing import Any, Iterator, Optional, Protocol

from ..nodes import Node
from ..protocols import GeneralizedKey, TrieKeyToken
from ..types import TrieId, TrieEntry


class TrieMixinsInterface(Protocol):
    """
    Protocol defining the complete public API and shared private state
    for all mixins used within the GeneralizedTrie implementation.
    """
    # --- Shared Private State ---
    # These attributes are the "contract" for the shared data model.
    runtime_validation: bool
    _ident_counter: int
    _trie_index: dict[TrieId, Node]
    _trie_entries: dict[TrieId, TrieEntry]
    children: dict[TrieKeyToken, Node]
    ident: Optional[TrieId]
    parent: Optional["TrieMixinsInterface"]
    token: Optional[TrieKeyToken]
    value: Any

    # --- Shared Public API ---
    # These methods form the "contract" for the shared behavior.
    # Any method that one mixin needs to call from another must be here.

    # pylint: disable=missing-function-docstring

    # From storage.py
    def add(self, key: GeneralizedKey, value: Optional[Any] = None) -> TrieId: ...
    def update(self, key: GeneralizedKey, value: Optional[Any] = None) -> TrieId: ...

    # From access.py
    def __getitem__(self, key: TrieId | GeneralizedKey) -> TrieEntry: ...
    def __contains__(self, key_or_ident: TrieId | GeneralizedKey) -> bool: ...
    def get(self, key: TrieId | GeneralizedKey, default: Any = None) -> TrieEntry | Any: ...

    # From removal.py
    def remove(self, key: TrieId | GeneralizedKey) -> None: ...
    def __delitem__(self, key: TrieId | GeneralizedKey) -> None: ...

    # From traversal.py
    def prefixes(self, key: GeneralizedKey) -> Iterator[TrieEntry]: ...
    def prefixed_by(self, key: GeneralizedKey, depth: int = -1) -> Iterator[TrieEntry]: ...

    # From collection.py
    def __iter__(self) -> Iterator[TrieId]: ...
    def __len__(self) -> int: ...

    # --- Private Implementation Details ---
    # These are included for type-checking purposes for methods that are
    # defined and called within the same mixin, but where the public-facing
    # methods use the protocol for `self`. They are not considered part of
    # the public API of the final class.
    def _store_entry(self, key: GeneralizedKey, value: Any, allow_value_update: bool) -> TrieId: ...
