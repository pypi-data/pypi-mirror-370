#!/usr/bin/env python3
"""Example of using a GeneralizedTrie for 'by letter' string indexing.
"""

from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries: list[str] = [
    'abcdef',
    'abc',
    'abcd',
    'qrf',
]
for item in entries:
    trie.add(item)

prefixed_by: set[TrieEntry] = set(trie.prefixed_by('abcd'))
print(f'prefixed_by = {prefixed_by}')

prefixes: set[TrieEntry] = set(trie.prefixes('abcdefg'))
print(f'prefixes = {prefixes}')

# prefixed_by = {
#   TrieEntry(ident=TrieId(1), key='abcdef', value=None),
#   TrieEntry(ident=TrieId(3), key='abcd', value=None)}
# prefixes = {
#   TrieEntry(ident=TrieId(2), key='abc', value=None),
#   TrieEntry(ident=TrieId(3), key='abcd', value=None),
#   TrieEntry(ident=TrieId(1), key='abcdef', value=None)}
