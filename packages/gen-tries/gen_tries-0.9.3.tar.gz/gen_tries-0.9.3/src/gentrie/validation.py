# -*- coding: utf-8 -*-

"""Validation functions for the gentrie package."""

from collections.abc import Sequence
from typing import Any
from warnings import warn

from .protocols import TrieKeyToken


def is_triekeytoken(token: Any) -> bool:
    """Tests token for whether it is a valid :class:`TrieKeyToken`.

    A valid :class:`TrieKeyToken` is a hashable object (implements both ``__eq__()`` and ``__hash__()`` methods).

    Examples:
    :class:`bool`, :class:`bytes`, :class:`float`, :class:`frozenset`,
    :class:`int`, :class:`str`, :class:`None`, :class:`tuple`.

    Args:
        token (Any): Object for testing.

    Returns:
        :class:`bool`: ``True`` if a valid :class:`TrieKeyToken`, ``False`` otherwise.
    """
    return isinstance(token, TrieKeyToken)


def is_hashable(token: Any) -> bool:
    """is_hashable is deprecated and will be removed in a future version.

    This function is a wrapper for :func:`is_triekeytoken` and is only provided for backward compatibility.

    Use :func:`is_triekeytoken` instead.
    """
    warn(
        "is_hashable is deprecated and will be removed in a future version. Use is_triekeytoken instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return is_triekeytoken(token)


def is_generalizedkey(key: Any) -> bool:
    """Tests key for whether it is a valid `GeneralizedKey`.

    A valid :class:`GeneralizedKey` is a :class:`Sequence` that returns
    :class:`TrieKeyToken` protocol conformant objects when
    iterated. It must have at least one token.

    Parameters:
        key (Any): Key for testing.

    Returns:
        :class:`bool`: ``True`` if a valid :class:`GeneralizedKey`, ``False`` otherwise.
    """
    # This complex logic makes this hotpath code MUCH faster (as much as 50 or 60 times) by performing
    # very fast dedicated checks for common types before performing much slower per-token generalized
    # protocol based checks.

    # Fast path 1: A non-empty string or bytes is a valid key.
    if isinstance(key, (str, bytes)) and key:
        return True

    # General check: Must be a sequence.
    if not isinstance(key, Sequence):
        return False

    # Now that we know it's a sequence, we can safely check its length.
    # An empty sequence is not a valid key.
    if not key:
        return False

    # Fast path 2: Check for sequences of common, simple built-in types.
    # This is much faster than the general protocol check.
    if all(isinstance(t, (int, float, complex, frozenset, tuple, bool, str, bytes)
                      ) for t in key):  # pyright: ignore[reportUnknownVariableType]
        return True

    # Fallback/Cold path: Perform the slower, general protocol check.
    # This only runs if the fast path fails.
    return all(isinstance(t, TrieKeyToken) for t in key)  # pyright: ignore[reportUnknownVariableType]
