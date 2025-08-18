#!/usr/bin/env python3
"""Example of using a GeneralizedTrie for indexing sequences of tuples"""
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries = [
    [(1, 2), (3, 4), (5, 6)],
    [(1, 2), (3, 4)],
    [(5, 6), (7, 8)],
]
for item in entries:
    trie.add(item)
prefixed_by: set[TrieEntry] = set(trie.prefixed_by([(1, 2)]))
print(f'prefixed_by = {prefixed_by}')
prefixes: set[TrieEntry] = set(trie.prefixes([(1, 2), (3, 4), (5, 6), (7, 8)]))
print(f'prefixes = {prefixes}')

# prefixed_by = {
#    TrieEntry(ident=TrieId(1), key=[(1, 2), (3, 4), (5, 6)], value=None),
#    TrieEntry(ident=TrieId(2), key=[(1, 2), (3, 4)], value=None)
# }
# prefixes = {
#    TrieEntry(ident=TrieId(1), key=[(1, 2), (3, 4), (5, 6)], value=None),
#    TrieEntry(ident=TrieId(2), key=[(1, 2), (3, 4)], value=None)
# }
