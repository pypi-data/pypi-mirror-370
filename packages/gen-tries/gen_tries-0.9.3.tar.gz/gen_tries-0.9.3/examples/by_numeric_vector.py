#!/usr/bin/env python3
"""Example of using a GeneralizedTrie for 'by number' indexing
of numeric sequences/vectors.
"""
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries = [
    [128, 256, 512],
    [128, 256],
    [512, 1024],
]
for item in entries:
    trie.add(item)
prefixed_by: set[TrieEntry] = set(trie.prefixed_by([128]))
print(f'prefixed_by = {prefixed_by}')

prefixes: set[TrieEntry] = set(trie.prefixes([128, 256, 512, 1024]))
print(f'prefixes = {prefixes}')

# prefixed_by = {
#   TrieEntry(ident=TrieId(1), key=[128, 256, 512], value=None),
#   TrieEntry(ident=TrieId(2), key=[128, 256], value=None)
# }
# prefixes = {
#   TrieEntry(ident=TrieId(1), key=[128, 256, 512], value=None),
#   TrieEntry(ident=TrieId(2), key=[128, 256], value=None)
# }
