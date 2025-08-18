#!/usr/bin/env python3
"""Example of using prefixes() method"""
from typing import Generator

from gentrie import GeneralizedTrie, TrieEntry

trie: GeneralizedTrie = GeneralizedTrie()
keys: list[str] = ['abcdef', 'abc', 'a', 'abcd', 'qrs']
for entry in keys:
    trie.add(entry)
matches: Generator[TrieEntry, None, None] = trie.prefixes('abcd')
for trie_entry in sorted(list(matches)):
    print(f'{trie_entry.ident}: {trie_entry.key}')

# 2: abc
# 3: a
# 4: abcd
