#!/usr/bin/env python3

"""Example of using a GeneralizedTrie for word suggestions based on prefixes.
"""
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries: list[str] = [
    'hell',
    'hello',
    'help',
    'dog',
    'doll',
    'dolly',
    'dolphin',
    'do'
]
for item in entries:
    trie.add(item)

suggestions: set[TrieEntry] = set(trie.prefixed_by('do', depth=2))
print(f'+2 letter suggestions for "do" = {suggestions}')

suggestions = set(trie.prefixed_by('do', depth=3))
print(f'+3 letter suggestions for "do" = {suggestions}')

# +2 letter suggestions for "do" = {
#   TrieEntry(ident=TrieId(5), key='doll', value=None),
#   TrieEntry(ident=TrieId(4), key='dog', value=None),
#   TrieEntry(ident=TrieId(8), key='do', value=None)
# }
# +3 letter suggestions for "do" = {
#   TrieEntry(ident=TrieId(5), key='doll', value=None),
#   TrieEntry(ident=TrieId(6), key='dolly', value=None),
#   TrieEntry(ident=TrieId(4), key='dog', value=None),
#   TrieEntry(ident=TrieId(8), key='do', value=None)
# }
