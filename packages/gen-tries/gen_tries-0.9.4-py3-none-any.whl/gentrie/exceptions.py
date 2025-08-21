#  -*- coding: utf-8 -*-
"""Custom exceptions for the gentrie package."""
from enum import Enum


class ErrorTag(str, Enum):
    """Tags for error path identification for tests for the gentrie packages.

    ErrorTags' are used to identify specific error conditions in the gentrie package.
    Tests use these tags to assert specific error condition paths.
    """
    # __getitem__() tags
    GETITEM_ID_NOT_FOUND = "GETITEM_ID_NOT_FOUND"
    GETITEM_KEY_NOT_FOUND = "GETITEM_KEY_NOT_FOUND"
    GETITEM_INVALID_KEY_TYPE = "GETITEM_INVALID_KEY_TYPE"
    GETITEM_NOT_TERMINAL = "GETITEM_NOT_TERMINAL"

    # removal() tags
    REMOVAL_INVALID_KEY_TYPE = "REMOVAL_INVALID_KEY_TYPE"
    REMOVAL_KEY_NOT_FOUND = "REMOVAL_KEY_NOT_FOUND"

    # prefixes() tags
    TRIE_PREFIXES_INVALID_GENERALIZED_KEY = "TRIE_PREFIXES_INVALID_GENERALIZED_KEY"

    # prefixed_by() tags
    TRIE_PREFIXED_BY_INVALID_GENERALIZED_KEY = "TRIE_PREFIXED_BY_INVALID_GENERALIZED_KEY"
    TRIE_PREFIXED_BY_BAD_DEPTH_TYPE = "TRIE_PREFIXED_BY_BAD_DEPTH_TYPE"
    TRIE_PREFIXED_BY_BAD_DEPTH_VALUE = "TRIE_PREFIXED_BY_BAD_DEPTH_VALUE"

    # _store_entry() tags
    STORE_ENTRY_INVALID_GENERALIZED_KEY = "STORE_ENTRY_INVALID_GENERALIZED_KEY"
    STORE_ENTRY_DUPLICATE_KEY = "STORE_ENTRY_DUPLICATE_KEY"


class TrieTypeError(TypeError):
    """Base class for all trie-related type errors.

    It differs from a standard TypeError by the addition of a
    tag code used to very specifically identify where the error
    was thrown in the code for testing and development support.

    This tag code does not have a direct semantic meaning except to identify
    the specific code throwing the exception for tests.

    Args:
        msg (str): The error message.
        tag (ErrorTag): The tag code.
    """
    def __init__(self, msg: str, tag: ErrorTag) -> None:
        """Create a new TrieTypeError.

        Args:
            msg (str): The error message.
            tag (str): The tag code.
        """
        self.tag_code: ErrorTag = tag
        super().__init__(msg)


class TrieKeyError(KeyError):
    """Base class for all trie-related key errors.

    It differs from a standard KeyError by the addition of a
    tag code used to very specifically identify where the error
    was thrown in the code for testing and development support.

    This tag code does not have a direct semantic meaning except to identify
    the specific code throwing the exception for tests.

    Args:
        msg (str): The error message.
        tag (ErrorTag): The tag code.
    """
    def __init__(self, msg: str, tag: ErrorTag) -> None:
        self.tag_code: ErrorTag = tag
        super().__init__(msg)


class TrieValueError(ValueError):
    """Base class for all trie-related value errors.

    It differs from a standard ValueError by the addition of a
    tag code used to very specifically identify where the error
    was thrown in the code for testing and development support.

    This tag code does not have a direct semantic meaning except to identify
    the specific code throwing the exception for tests.

    Args:
        msg (str): The error message.
        tag (ErrorTag): The tag code.
    """
    def __init__(self, msg: str, tag: ErrorTag) -> None:
        self.tag_code: ErrorTag = tag
        super().__init__(msg)


class InvalidTrieKeyTokenError(TrieTypeError):
    """Raised when a token in a key is not a valid :class:`TrieKeyToken` object.

    This is a sub-class of :class:`TrieTypeError`."""


class InvalidGeneralizedKeyError(TrieTypeError):
    """Raised when a key is not a valid :class:`GeneralizedKey` object.

    This is a sub-class of :class:`TrieTypeError`."""


class DuplicateKeyError(TrieKeyError):
    """Raised when an attempt is made to add a key that is already in the trie
    with a different associated value.

    This is a sub-class of :class:`TrieKeyError`."""
