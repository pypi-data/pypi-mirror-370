#!/usr/bin/env python3
"""This example demonstrates how to use the GeneralizedTrie
to store and retrieve entries using a dictionary-like syntax.

It includes adding, updating, retrieving, and deleting entries,
as well as checking for existence of keys or identifiers."""

from typing import Optional

from gentrie import GeneralizedTrie, TrieEntry, TrieId

trie = GeneralizedTrie()

# Add entries with different key types to demonstrate flexibility
key1: str = 'key1'  # String key (tokenized as individual characters)
trie[key1] = 'value1'

key2: tuple[int, int, int] = (1, 2, 3)  # Tuple key (tokenized as individual elements)
trie[key2] = 'value2'

key3: tuple[str, str] = ('hello', 'world')  # Tuple of strings (tokenized as individual elements)
trie[key3] = 'value3'

# Retrieve the value for the key 'key1' (the returned value
# from the dictionary is a TrieEntry object - the actual value is in the
# 'value' attribute)
value1 = trie[key1].value
id1: TrieId = trie[key1].ident
print(f'ID for {key1}: {id1}')
print(f'Value for {key1}: {value1}')

# Retrieve the value for key2
value2 = trie[key2].value
print(f'Value for {key2}: {value2}')

# Retrieve the value for key3
value3 = trie[key3].value
print(f'Value for {key3}: {value3}')

# Check if the key key1 exists in the trie
exists_key1 = key1 in trie
print(f'Key {key1} exists: {exists_key1}')

# Check if ident id1 exists in the trie
# This checks if the identifier for key1 exists in the trie.
# This is useful for accessing entries by their identifiers.
#
# The idents and the keys are diffrent things.
# The idents are unique identifiers for the entries, while the keys
# are the actual keys used to access the entries.
# Either can be used to access the entries in the trie,
# and both can be used to check for existence of entries,
# but they are not interchangeable. Ids are faster (*O(1)*) than
# keys (*O(n)* to the length of the keys) for accessing entries.
exists_id1 = id1 in trie
print(f'Ident {id1} exists: {exists_id1}')

# Check if the key2 exists in the trie
exists_key2 = key2 in trie
print(f'Key {key2} exists: {exists_key2}')

# Check if key3 exists in the trie
exists_key3 = key3 in trie
print(f'Key {key3} exists: {exists_key3}')

# Update the value for the key key1
trie[key1] = 'new_value1'
updated_value1 = trie[key1].value
print(f'Updated value for {key1}: {updated_value1}')

# delete the entry for the key2
del trie[key2]
exists_key2_after_delete = key2 in trie
print(f'Key {key2} exists after deletion: {exists_key2_after_delete}')

print("\nDifferent approaches to handle missing keys:")

none_key: str = "none_value_key"
trie[none_key] = None
print(f"Added key '{none_key}' (as characters) with None value for demonstration")

# 1. Exception-based approach (most reliable)
try:
    deleted_entry = trie[key2]
    print(f'1. Exception approach - Value for {key2}: {deleted_entry.value}')
except KeyError as e:
    print(f'1. Exception approach - Key {key2} not found: {e}')

# 2. get() approach - Clear and unambiguous:
# When a key is not found, it returns None.
# When a key exists, it returns the TrieEntry object.
# This makes it easy to distinguish between missing keys and existing None values.
print("\n2. get() approach:")
safe_entry: Optional[TrieEntry] = trie.get(key2)  # Returns None for missing key
none_entry: Optional[TrieEntry] = trie.get(none_key)  # Returns TrieEntry with None value
print(f'Missing key result: {safe_entry}')
print(f'Existing None value result: {none_entry}')

# Demonstrate the clear distinction:
print(f'Missing key is None: {safe_entry is None}')
print(f'Existing entry is TrieEntry: {isinstance(none_entry, TrieEntry)}')

# 3. Membership test first
print("\n3. Membership test approach:")
if key2 in trie:
    print(f'Check first approach - Value: {trie[key2].value}')
else:
    print(f'Check first approach - Key {key2} not found')

if none_key in trie:
    print(f'Check first approach - Value for None key: {trie[none_key].value}')
else:
    print('Check first approach - None key not found')

print("\nWhen to use each approach:")
print("1. Exception approach: When you expect the key to exist")
print("2. get() approach: When key might not exist (recommended)")
print("3. Membership test: When you only need to check existence")

# Clean up the demonstration entry
del trie[none_key]
# Show remaining entries
print("Remaining entries in trie:")
for entry in trie.values():
    print(f"  {entry.key} -> {entry.value}")

# Delete the key1 entry using the ident instead of the key
print(f"\nDeleting entry with ident {id1} (for key '{key1}')")
del trie[id1]

# Show remaining entry values after deletion
print(f"\nRemaining entry values after deleting entry with ident {id1}:")
for entry in trie.values():
    print(f"  {entry.key} -> {entry.value}")

# Demonstrate additional dictionary-like operations
print("\nAdditional dictionary-like operations:")

# Add a new entry
trie['new_key'] = 'new_value'
print("Added new entry: 'new_key' -> 'new_value'")

# Additional dictionary-like operations
print("\nTrie statistics:")
print(f"Number of entries: {len(trie)}")

# Iterate over idents. Keys returns the identifiers of the entries
# which can be used to access the entries directly.
print("All idents for entries in trie:")
for ident in trie.keys():
    print(f"  {ident}")

# Iterate over key-value pairs
print("All ident-value pairs:")
for ident, entry in trie.items():
    print(f"  {ident}: {entry.value}")


# Output:
# ID for key1: 1
# Value for key1: value1
# Value for (1, 2, 3): value2
# Value for ('hello', 'world'): value3
# Key key1 exists: True
# Key (1, 2, 3) exists: True
# Key ('hello', 'world') exists: True
# Updated value for key1: new_value1
# Key (1, 2, 3) exists after deletion: False
#
# Different approaches to handle missing keys:
# Added key 'none_value_key' (as characters) with None value for demonstration
# 1. Exception approach - Key (1, 2, 3) not found: '[GTGI001] key does not match any idents or keys in the trie'
#
# 2. get() approach:
# Missing key result: None
# Existing None value result: TrieEntry(ident=4, key='none_value_key', value=None)
# Missing key is None: True
# Existing entry is TrieEntry: True
#
# 3. Membership test approach:
# Check first approach - Key (1, 2, 3) not found
# Check first approach - Value for None key: None
#
# When to use each approach:
# 1. Exception approach: When you expect the key to exist
# 2. get() approach: When key might not exist (recommended)
# 3. Membership test: When you only need to check existence
# Remaining entries in trie:
#   key1 -> new_value1
#  ('hello', 'world') -> value3
#
# Deleting entry with ident 1 (for key 'key1')
#
# Remaining entry values after deleting entry with ident 1:
#  ('hello', 'world') -> value3
#
# Additional dictionary-like operations:
# Added new entry: 'new_key' -> 'new_value'
#
# Trie statistics:
# Number of entries: 2
# All idents for entries in trie:
#   3
#   5
# All ident-value pairs:
#   3: value3
#   5: new_value
