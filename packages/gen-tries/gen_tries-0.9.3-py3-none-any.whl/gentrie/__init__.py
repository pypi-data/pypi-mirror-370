# -*- coding: utf-8 -*-
"""Package providing a generalized trie implementation.

This package includes classes and functions to create and manipulate a generalized trie
data structure. Unlike common trie implementations that only support strings as keys,
this generalized trie can handle various types of tokens, as long as they are hashable.

.. warning:: **gentrie IS NOT thread-safe**

    It is not designed for concurrent use. If you need a thread-safe trie, you must
    use an external locking mechanism to ensure that either only read-only threads are
    accessing the trie at the same time or that only one write thread and no read threads
    are accessing the trie at the same time.

    One way to do this is to create TWO instances of the trie, one for read-only access and one for write access.

    The read-only instance can be used by multiple threads at the same time, while the write instance can
    be used by only one thread at a time. After a write operation, a new read-only instance can be created
    from the write instance by forking it using :func:`copy.deepcopy()` which can then be used by the
    read-only threads.

Usage
=======

You can create a trie using the `GeneralizedTrie` class:

.. code-block:: python
    :linenos:

    from gentrie import GeneralizedTrie

    # Create a new trie instance
    trie = GeneralizedTrie()

There are three ways to add entries:

1. Using the `trie[key] = value` syntax

This allows you to assign a value directly to a key and will create a
new TrieEntry if the key does not already exist. If the key already exists,
it will update the value associated with that key.

.. code-block:: python
    :linenos:
    :caption: Examples of using the `trie[key] = value` syntax

    # Assigns 'value' to 'key'
    # (tokenized as characters 'k','e','y')
    trie['key'] = 'value'

    # Assigns value 'value2' to key 'another_key' (tokenized as
    # 'a','n','o','t','h','e','r','_','k','e','y','2')
    trie['another_key'] = 'another_value'

    # Changes the value for 'key' (tokenized as 'k', 'e', 'y')
    # to 'new_value'
    trie['key'] = 'new_value'

    # Assigns a tuple of int (tokenized as
    # 128, 96, 160, 0) as a key with the value'value5'
    trie[(128, 96, 160, 0)] = 'value5'

    # Assigns a tuple with mixed value types (tokenized
    # as 128, 'a') as a key with the value 'value5b'
    trie[(128, 'a')] = 'value5b'

    # Assigns a list of words (tokenized as 'hello', 'world')
    # as a key with the value 'value6'
    trie[['hello', 'world']] = 'value6'

2. Using the `trie.add(key, value)` method

    This method adds a new entry to the trie and returns the TrieId
    for the new entry. If the key already exists, it will throw an
    error. The value argument is optional, and if not provided
    the entry will be created with a value of `None`.

3. Using the `trie.update(key, value)` method

    This method adds a new entry or updates an existing entry,
    returning the TrieId for the entry and returns the TrieId of the entry.

    This is the same as using the `trie[key] = value` syntax,
    but it is more explicit about the intention to update or add
    an entry and returns the TrieId of the entry.

    The value argument is optional, and if not provided, the
    entry will be created or updated with a value of `None`.

You can use the `in` operator to check if a key exists in the trie,
e.g., `if key in trie:`. This will return `True` if the key exists,
and `False` otherwise.

There are two ways to directly retrieve entries using their keys:

1. Using the `trie[key | TrieId]` syntax.

    This retrieves the `TrieEntry` associated with the key or TrieId. It
    will raise a `KeyError` if the key/TrieId does not exist. It will raise
    a `TypeError` if the key is not either a valid `TrieId` or `GeneralizedKey`.

    The returned `TrieEntry` contains the key, value, and an identifier
    (ident - of type `TrieId`) that uniquely identifies the entry in the trie.

2. Using the `trie.get(key | TrieId, [default])` method
    This retrieves the `TrieEntry` associated with the key or TrieId,
    returning `None` if the key/TrieId does not exist. This could be
    preferable in cases where you want to avoid exceptions
    for missing keys although it cannot distinguish between a key
    that does not exist and a key that exists with a `None` value
    in the trie by default.

    You *can* provide a different default value to return if the key
    does not exist, which can be useful for handling cases where
    you want to return a specific value instead of `None`.

You can also retrieve all entries that are prefixed by or prefixes for a given key:

- `trie.prefixed_by(key)` returns a Generator of `TrieEntry` objects that
  are prefixed_by of the given key.
- `trie.prefixes(key)` returns a Generator of `TrieEntry` objects that
  are prefixes of the given key.

These methods are useful for searching and retrieving entries
that match a specific pattern or structure in the trie.

Example 1 - Basic Usage
------------------------

.. code-block:: python
    :linenos:

    from gentrie import GeneralizedTrie, TrieEntry

    trie = GeneralizedTrie()
    trie.add(['ape', 'green', 'apple'])
    trie.add(['ape', 'green'])
    matches: set[TrieEntry] = set(trie.prefixes(['ape', 'green']))
    print(matches)

Value of 'matches'::

    {TrieEntry(ident=2, key=['ape', 'green'], value=None)}

Example 2 - Trie of URLs
--------------------------

.. code-block:: python
    :linenos:

    from gentrie import GeneralizedTrie, TrieEntry

    # Create a trie to store website URLs
    url_trie = GeneralizedTrie()

    # Add some URLs with different components (protocol, domain, path)
    url_trie.add(["https", "com", "example", "www", "/", "products", "clothing"], value="Clothing Store")
    url_trie.add(["http", "org", "example", "blog", "/", "2023", "10", "best-laptops"], value="Best Laptops 2023")
    url_trie.add(["ftp", "net", "example", "ftp", "/", "data", "images"], value="FTP Data Images")

    # Find all https URLs with "example.com" domain
    prefixed_by: set[TrieEntry] = set(url_trie.prefixed_by(["https", "com", "example"]))
    print(prefixed_by)

Value of 'prefixed_by'::

    {
        TrieEntry(
            ident=1,
            key=['https', 'com', 'example', 'www', '/', 'products', 'clothing'],
            value='Clothing Store')
    }

Example 3 - Entries prefixed by a key
-------------------------------------

.. code-block:: python
    :linenos:

    from gentrie import GeneralizedTrie, TrieEntry

    trie = GeneralizedTrie()
    trie.add('abcdef')
    trie.add('abc')
    trie.add('qrf')
    matches: set[TrieEntry] = set(trie.prefixed_by('ab'))
    print(matches)

Value of 'matches'::

    {
        TrieEntry(ident=2, key='abc', value=None),
        TrieEntry(ident=1, key='abcdef', value=None)
    }

"""

# Import all public classes and functions
from .exceptions import (
    ErrorTag,
    InvalidTrieKeyTokenError,
    InvalidGeneralizedKeyError,
    DuplicateKeyError,
    TrieKeyError,
    TrieTypeError,
    TrieValueError
)
from .protocols import TrieKeyToken, Hashable, GeneralizedKey
from .types import TrieId, TrieEntry, TRIE_IDENT, TRIE_KEY, TRIE_VALUE
from .validation import is_triekeytoken, is_hashable, is_generalizedkey
from .trie import GeneralizedTrie

__all__ = [
    # Core classes
    'GeneralizedTrie',
    'TrieEntry',
    'TrieId',

    # Protocols and types
    'TrieKeyToken',
    'GeneralizedKey',
    'Hashable',  # deprecated

    # Validation functions
    'is_generalizedkey',
    'is_triekeytoken',
    'is_hashable',  # deprecated

    # Exceptions
    'ErrorTag',
    'InvalidTrieKeyTokenError',
    'InvalidGeneralizedKeyError',
    'DuplicateKeyError',
    'TrieKeyError',
    'TrieTypeError',
    'TrieValueError',

    # Constants
    'TRIE_IDENT',
    'TRIE_KEY',
    'TRIE_VALUE',
]
