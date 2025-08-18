#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script demonstrates how to create a trie, add entries, and check for their existence
using both keys and TrieIds.
"""

from gentrie import GeneralizedTrie, TrieId

trie = GeneralizedTrie()
entries: list[str] = [
    'abcdef',
    'abc',
    'abcd',
    'qrf',
]
# Add entries to the trie and save their TrieIds

entry_ids: list[TrieId] = []
for item in entries:
    ident: TrieId = trie.add(item)
    print(f'Added {item} with {ident}')
    entry_ids.append(ident)

if 'abc' in trie:
    print('abc is in trie')
else:
    print('error: abc is not in trie')

if 'abcde' not in trie:
    print('abcde is not in trie')
else:
    print('error: abcde is in trie')

if 'qrf' not in trie:
    print('error: qrf is not in trie')
else:
    print('qrf is in trie')

if 'abcdef' not in trie:
    print('error: abcdef is not in trie')
else:
    print('abcdef is in trie')

if entry_ids[0] not in trie:
    print(f'error: {entry_ids[0]} is not in trie')
else:
    print(f'{entry_ids[0]} is in trie')

# abc is in trie
# abcde is not in trie
# qrf is in trie
# abcdef is in trie
# TrieId(1) is in trie
