#!/usr/bin/env python3
"""Assigning Values to Entries in a Generalized Trie.

This script demonstrates how to create a Generalized Trie, add
or update entries with values, and retrieve entries, suffixes,
and prefixes with their associated values.

There are three ways to add entries:

1. Using the `trie[key] = value` syntax

    This allows you to assign a value directly to a key and
    will create a new entry if the key does not already exist.
    If the key already exists, it will update the value
    associated with that key.

2. Using the `trie.add(key, value)` method

    This method adds a new entry to the trie. If the key
    already exists, it will throw an error. The value argument
    is optional, and if not provided the entry will be created
    with a `None` value.

3. Using the `trie.update(key, value)` method

    This method adds a new entry or updates an existing entry.
    This is the same as using the `trie[key] = value` syntax,
    but it is more explicit about the intention to update or
    add an entry.

    The value argument is optional, and if not provided, the
    entry will be created or updated with a `None` value.


You can use the `in` operator to check if a key exists in the
trie, e.g., `if key in trie:`. This will return `True` if the
key exists, and `False` otherwise.

There are two ways to directly retrieve entries using their keys:

1. Using the `trie[key | TrieId]` syntax.

    This retrieves the `TrieEntry` associated with the key or
    TrieId. It will raise a `KeyError` if the key/TrieId does
    not exist. It will raise a `TypeError` if the key is not a
    valid `TrieId` or `GeneralizedKey`.

    The `TrieEntry` contains the key, value, and an identifier
    (ident - of type `TrieId`) that uniquely identifies the
    entry in the trie.

    You can also use the `trie.get(key | TrieId)` method to
    retrieve the `TrieEntry` associated with the key or TrieId,
    which is similar to the `trie[key]` syntax but allows for a
    default value to be specified if the key/TrieId does not exist
    rather than raising an exception.

2. Using the `trie.get(key | TrieId, [default])` method
    This retrieves the `TrieEntry` associated with the key or
    TrieId, returning `None` if the key/TrieId does not exist.
    This could be preferable in cases where you want to avoid
    exceptions.

    You *can* provide a default value to return if the key
    does not exist, which can be useful for handling cases where
    you want to return a specific value instead of `None`.

You can also retrieve all entries that are prefixes for or prefixed by
a given key:

- `trie.prefixed_by(key)` returns a set of `TrieEntry` objects that
  are prefixed_by of the given key.
- `trie.prefixes(key)` returns a set of `TrieEntry` objects that
  are prefixes of the given key.

These methods are useful for searching and retrieving entries
that match a specific pattern or structure in the trie.
"""
from gentrie import DuplicateKeyError, GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()

# Adding entries using the trie[key] = value syntax
entries: list[tuple[str, str | list[str]]] = [
    ('abcdef', 'value1'),
    ('abc', 'value2'),
    ('abcd', 'value3'),
    ('qrf', 'value4'),
    ('xyz', ['lists', 'are', 'also', 'supported']),
    ('xy', 'value6'),
]
for key, value in entries:
    trie[key] = value

prefixed_by: set[TrieEntry] = set(trie.prefixed_by('xy'))
print(f'prefixed_by = {prefixed_by}')

prefixes: set[TrieEntry] = set(trie.prefixes('abcdefg'))
print(f'prefixes = {prefixes}')

# prefixed_by = {
#     TrieEntry(ident=6, key='xy', value='value6'),
#     TrieEntry(ident=5, key='xyz', value=['lists','are', 'also', 'supported'])
# }
#
# prefixes = {
#     TrieEntry(ident=3, key='abcd', value='value3'),
#     TrieEntry(ident=2, key='abc', value='value2'),
#     TrieEntry(ident=1, key='abcdef', value='value1')
# }

# Adding using the add method
# This will throw an error if the key already exists.
more_entries: list[tuple[str | tuple[int, ...], str]] = [
    ((128, 96, 160, 0), 'value5'),
    ((128, 90), 'value5b'),
    ('xy', 'value6'),
]
for key, value in more_entries:
    try:
        trie.add(key, value)
        print(f'Added entry: {key} -> {value}')
    except DuplicateKeyError:
        print(f'DuplicateKeyError - entry already exists: {key}')

prefixed_by: set[TrieEntry] = set(trie.prefixed_by([128]))
print(f'prefixed_by = {prefixed_by}')

prefixes: set[TrieEntry] = set(trie.prefixes([128, 90]))
print(f'prefixes = {prefixes}')

# prefixed_by = {
#     TrieEntry(ident=8, key=(128, 90), value='value5b'),
#     TrieEntry(ident=7, key=(128, 96, 160, 0), value='value5')
# }
#
# prefixes = {
#     TrieEntry(ident=8, key=(128, 90), value='value5b')
# }

# Updating or adding entries using the update method
# This will update the value if the key already exists,
# or create a new entry if it does not.
# This is the same as using the trie[key] = value syntax.
even_more_entries: list[tuple[str, str]] = [
    ('abcdefghi', 'value7'),
    ('abcd', 'value8'),
]
for key, value in even_more_entries:
    trie.update(key, value)

prefixed_by = set(trie.prefixed_by('abcd'))
print(f'prefixed_by = {prefixed_by}')

prefixes = set(trie.prefixes('abcdefg'))
print(f'prefixes = {prefixes}')

# prefixed_by = {
#     TrieEntry(ident=3, key='abcd', value='value8'),
#     TrieEntry(ident=9, key='abcdefghi', value='value7'),
#     TrieEntry(ident=1, key='abcdef', value='value1')
# }
#
# prefixes = {
#     TrieEntry(ident=2, key='abc', value='value2'),
#     TrieEntry(ident=3, key='abcd', value='value8'),
#     TrieEntry(ident=1, key='abcdef', value='value1')
# }
