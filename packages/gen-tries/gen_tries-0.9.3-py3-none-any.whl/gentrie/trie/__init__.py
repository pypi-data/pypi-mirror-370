# -*- coding: utf-8 -*-
"""Main GeneralizedTrie implementation."""

from .access import TrieAccessMixin
from .base import TrieBase
from .collection import TrieCollectionMixin
from .mutation import TrieMutationMixin
from .removal import TrieRemovalMixin
from .storage import TrieStorageMixin
from .traversal import TrieTraversalMixin


class GeneralizedTrie(
    TrieBase,
    TrieStorageMixin,
    TrieAccessMixin,
    TrieRemovalMixin,
    TrieTraversalMixin,
    TrieMutationMixin,
    TrieCollectionMixin
):
    """A general purpose trie.

    Unlike many trie implementations which only support strings as keys
    and token match only at the character level, it is agnostic as to the
    types of tokens used to key it and thus far more general purpose.

    It requires only that the indexed tokens be hashable. This is verified
    at runtime using the :class:`gentrie.TrieKeyToken` protocol.

    Tokens in a key do NOT have to all be the same type as long as they
    can be compared for equality.

    It can handle a :class:`Sequence` of :class:`TrieKeyToken` conforming objects as keys
    for the trie out of the box.

    You can 'mix and match' types of objects used as token in a key as
    long as they all conform to the :class:`TrieKeyToken` protocol.

    The code emphasizes robustness and correctness.

    .. warning:: **GOTCHA: Using User Defined Classes As Tokens In Keys**

        Objects of user-defined classes are conformant with the :class:`TrieKeyToken` protocol
        by default, but **this will not work as naively expected.** The hash value of an object
        is based on its memory address by default. This results in the hash value of an object changing
        every time the object is created and means that the object will not be found in
        the trie unless you have a reference to the original object.

        If you want to use a user-defined class as a token in a key to look up by value
        instead of the instance, you must implement the ``__eq__()`` and ``__hash__()``
        dunder methods in a content aware way (the hash and eq values must depend on the
        content of the object).

        .. tip:: **Using `dataclasses.dataclass` For Content-Aware User Defined Classes**

            A simple way to implement a user-defined class that is content aware hashable
            is to use the :class:`dataclasses.dataclass` decorator using the ``frozen=True`` and
            ``eq=True`` options . This will automatically implement appropriate ``__eq__()``
            and ``__hash__()`` methods for you.

            .. code-block:: python
                :linenos:
                :caption: Example of a content-aware user-defined class

                from dataclasses import dataclass

                from gentrie import TrieKeyToken

                @dataclass(frozen=True, eq=True)
                class MyTokenClass:
                    name: str
                    value: int

                # Create an instance of the token class
                token = MyTokenClass(name="example", value=42)

                # Check if the token is hashable
                if isinstance(token, TrieKeyToken):
                    print("token is usable as a TrieKeyToken")
                else:
                    print("token is not usable as a TrieKeyToken")

    """

    # All functionality is provided by the mixins
