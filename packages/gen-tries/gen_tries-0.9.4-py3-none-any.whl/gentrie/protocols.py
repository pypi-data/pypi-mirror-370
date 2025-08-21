# -*- coding: utf-8 -*-
"""Protocols and type definitions for the gentrie package."""

from collections.abc import Sequence
from typing import Protocol, TypeAlias, runtime_checkable


@runtime_checkable
class TrieKeyToken(Protocol):
    """:class:`TrieKeyToken` is a protocol that defines key tokens that are usable with a :class:`GeneralizedTrie`.

    The protocol requires that a token object be *hashable*. This means that it
    implements both an ``__eq__()`` method and a ``__hash__()`` method.

    Some examples of built-in types that are suitable for use as tokens in a key:

    * :class:`str`
    * :class:`bytes`
    * :class:`int`
    * :class:`float`
    * :class:`complex`
    * :class:`frozenset`
    * :class:`tuple`
    * :class:`None`

    Note: frozensets and tuples are only hashable *if their contents are hashable*.

    Usage:

    .. code-block:: python
        :linenos:

        from gentrie import TrieKeyToken

        token = SomeTokenClass()
        if isinstance(token, TrieKeyToken):
            print("supports the TrieKeyToken protocol")
        else:
            print("does not support the TrieKeyToken protocol")

    .. warning:: **Using User Defined Classes As Tokens In Keys**

        User-defined classes are hashable by default, but you should implement the
        ``__eq__()`` and ``__hash__()`` dunder methods in a content-aware way (the hash and eq values
        must depend on the content of the object) if you want to use them as tokens in a key. The default
        implementation of ``__eq__()`` and ``__hash__()`` uses the memory address of the object, which
        means that two different instances of the same class will not be considered equal.

    """
    def __eq__(self, value: object, /) -> bool: ...

    def __hash__(self) -> int: ...


@runtime_checkable
class Hashable(TrieKeyToken, Protocol):
    """The Hashable protocol is deprecated and will be removed in a future version.

    This protocol is a sub-class of :class:`TrieKeyToken` and is only provided for backward compatibility.

    Use :class:`TrieKeyToken` instead.
    """
    def __eq__(self, value: object, /) -> bool: ...

    def __hash__(self) -> int: ...


GeneralizedKey: TypeAlias = Sequence[TrieKeyToken]
"""A :class:`GeneralizedKey` is an object of any class that is a :class:`Sequence` and
that when iterated returns tokens conforming to the :class:`TrieKeyToken` protocol.


.. warning:: **Keys Must Be Immutable**

    Once a key is added to the trie, neither the key sequence itself nor any of its
    constituent tokens should be mutated. Modifying a key after it has been added
    can corrupt the internal state of the trie, leading to unpredictable behavior
    and making entries unreachable. The trie does not create a deep copy of keys
    for performance reasons.

    If you need to modify a key, you should remove the old key and add a new one
    with the modified value.

**Examples of valid :class:`GeneralizedKey` types**

* :class:`str`
* :class:`bytes`
* :class:`list[bool]`
* :class:`list[int]`
* :class:`list[bytes]`
* :class:`list[str]`
* :class:`list[Optional[str]]`
* :class:`tuple[int, int, str]`

"""
