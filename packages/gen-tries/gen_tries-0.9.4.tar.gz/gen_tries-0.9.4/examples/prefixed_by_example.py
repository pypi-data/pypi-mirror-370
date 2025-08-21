#!/usr/bin/env python3
"""Example of using a GeneralizedTrie for indexing sequences of strings."""
from typing import Generator
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
keys: list[str] = ['abcdef', 'abc', 'a', 'abcd', 'qrs']
for entry in keys:
    trie.add(entry)
matches: Generator[TrieEntry, None, None] = trie.prefixed_by('abcd')

for trie_entry in sorted(list(matches)):
    print(f'{trie_entry.ident}: {trie_entry.key}')

# 1: abcdef
# 4: abcd
