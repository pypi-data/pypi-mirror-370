#!/usr/bin/env python3
"""Example of using a GeneralizedTrie for indexing sequences of words
"""
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries: list[list[str]] = [
    ['ape', 'green', 'apple'],
    ['ape', 'green'],
    ['ape', 'green', 'pineapple'],
]
for item in entries:
    trie.add(item)
prefixes: set[TrieEntry] = set(trie.prefixes(['ape', 'green', 'apple']))
print(f'prefixes = {prefixes}')
prefixed_by: set[TrieEntry] = set(trie.prefixed_by(['ape', 'green']))
print(f'prefixed_by = {prefixed_by}')

# prefixes = {
#   TrieEntry(ident=TrieId(1), key=['ape', 'green', 'apple'], value=None),
#   TrieEntry(ident=TrieId(2), key=['ape', 'green'], value=None)
# }
# prefixed_by = {
#   TrieEntry(ident=TrieId(1), key=['ape', 'green', 'apple'], value=None),
#   TrieEntry(ident=TrieId(2), key=['ape', 'green'], value=None),
#   TrieEntry(ident=TrieId(3), key=['ape', 'green', 'pineapple'], value=None)
# }
