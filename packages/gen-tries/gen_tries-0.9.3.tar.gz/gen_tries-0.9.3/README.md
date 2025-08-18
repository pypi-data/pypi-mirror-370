# gen-tries

## Name

gen-tries

## Description

A generalized trie implementation for python 3.10 or later that provides classes and
functions to create and manipulate a generalized trie data structure.

Unlike many Trie implementations which only support strings as keys
and token match only at the character level, it is agnostic as to the
types of tokens used to key it and thus far more general purpose.

It requires only that the indexed tokens be hashable (this means that they have
\_\_eq\_\_ and \_\_hash\_\_ methods). This is verified at runtime using the `gentrie.TrieKeyToken` protocol.

Tokens in a key do NOT have to all be the same type as long as they
can be compared for equality.

**Note that objects of user-defined classes meet the `TrieKeyToken` by default, but this
will not work as expected unless they are immutable and have a
content-aware \_\_hash\_\_ method.**

It can handle `Sequence`s of `TrieKeyToken` conforming objects as keys
for the trie out of the box.

As long as the tokens returned by a sequence are hashable, and the hash
is content-aware, it largely 'just works'.

You can 'mix and match' types of objects used as token in a key as
long as they all conform to the `TrieKeyToken` protocol.

## Installation

### Via PyPI

```shell
pip3 install gen-tries
```

### From source

```shell
git clone https://github.com/JerilynFranz/python-gen-tries
cd python-gen-tries
pip3 install .
```

## Usage

### Example 1 - trie of words

```python
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries: list[list[str]] = [
    ['ape', 'green', 'apple'],
    ['ape', 'green'],
    ['ape', 'green', 'pineapple'],
]
for item in entries:
    trie.add(item)
prefixes: set[TrieEntry] = trie.prefixes(['ape', 'green', 'apple'])
print(f'prefixes = {prefixes}')
prefixed_by: set[TrieEntry] = trie.prefixed_by(['ape', 'green'])
print(f'prefixed_by = {prefixed_by}')

# prefixes = {TrieEntry(ident=TrieId(1), key=['ape', 'green', 'apple']),
#             TrieEntry(ident=TrieId(2), key=['ape', 'green'])}
# prefixed_by = {TrieEntry(ident=TrieId(1), key=['ape', 'green', 'apple']),
#             TrieEntry(ident=TrieId(3), key=['ape', 'green', 'pineapple']),
#             TrieEntry(ident=TrieId(2), key=['ape', 'green'])}
```

### Example 2 - trie of tokens from URLs

```python
from gentrie import GeneralizedTrie, TrieEntry

# Create a trie to store website URLs
url_trie = GeneralizedTrie()

# Add some URLs with different components (protocol, domain, path)
url_trie.add(["https", ":", "//", "com", "example", "www", "/", "products", "clothing"],
             "https://www.example.com/products/clothing")
url_trie.add(["http", ":", "//", "org", "/", "example", "blog", "/", "2023", "10", "best-laptops"],
             "http://example.org/blog/2023/10/best-laptops")
url_trie.add(["ftp", ":", "//", "net", "example", "/", "ftp", "/", "data", "images"],
             "ftp://example.net/ftp/data/images")

# Find https URLs with "example.com" domain or sub-domain
print("HTTPS URLs for domains or sub-domains of 'example.com'")
prefixed_by: set[TrieEntry] = url_trie.prefixed_by(["https", ":", "//", "com", "example"])
for entry in prefixed_by:
    print(f"Found URL: {entry.value}")

# Find ftp protocol URLs
print("FTP URLs")
prefixed_by = url_trie.prefixed_by(["ftp"])
for entry in prefixed_by:
    print(f"Found URL: {entry.value}")

# HTTPS URLs for domains or sub-domains of 'example.com'
# Found URL: https://www.example.com/products/clothing
# FTP URLs
# Found URL: ftp://example.net/ftp/data/images
```

### Example 3 - trie of characters from strings

```python
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
keys: list[str] = ['abcdef', 'abc', 'a', 'abcd', 'qrs']
for entry in keys:
    trie.add(entry)
matches: set[TrieEntry] = trie.prefixed_by('abcd')

for trie_entry in sorted(list(matches)):
    print(f'{trie_entry.ident}: {trie_entry.key}')

# 1: abcdef
# 4: abcd
```

### Example 4 - trie of numeric vectors

```python
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries = [
    [128, 256, 512],
    [128, 256],
    [512, 1024],
]
for item in entries:
    trie.add(item)
prefixed_by: set[TrieEntry] = trie.prefixed_by([128])
print(f'prefixed_by = {prefixed_by}')

prefixes: set[TrieEntry] = trie.prefixes([128, 256, 512, 1024])
print(f'prefixes = {prefixes}')

# prefixed_by = {
#   TrieEntry(ident=TrieId(1), key=[128, 256, 512], value=None),
#   TrieEntry(ident=TrieId(2), key=[128, 256], value=None)
# }
# prefixes = {
#   TrieEntry(ident=TrieId(1), key=[128, 256, 512], value=None),
#   TrieEntry(ident=TrieId(2), key=[128, 256], value=None)
# }
```

### Example 5 - trie of tuples

```python
from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
entries = [
    [(1, 2), (3, 4), (5, 6)],
    [(1, 2), (3, 4)],
    [(5, 6), (7, 8)],
]
for item in entries:
    trie.add(item)
prefixed_by: set[TrieEntry] = trie.prefixed_by([(1, 2)])
print(f'prefixed_by = {prefixed_by}')
prefixes: set[TrieEntry] = trie.prefixes([(1, 2), (3, 4), (5, 6), (7, 8)])
print(f'prefixes = {prefixes}')

# prefixed_by = {
#    TrieEntry(ident=TrieId(1), key=[(1, 2), (3, 4), (5, 6)], value=None),
#    TrieEntry(ident=TrieId(2), key=[(1, 2), (3, 4)], value=None)
# }
# prefixes = {
#    TrieEntry(ident=TrieId(1), key=[(1, 2), (3, 4), (5, 6)], value=None),
#    TrieEntry(ident=TrieId(2), key=[(1, 2), (3, 4)], value=None)
# }
```

### Example 6 - Word suggestions

```python
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

suggestions: set[TrieEntry] = trie.prefixed_by('do', depth=2)
print(f'+2 letter suggestions for "do" = {suggestions}')

suggestions = trie.prefixed_by('do', depth=3)
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
```

### Example 7 - checking if key is in the trie

```python
from gentrie import GeneralizedTrie

trie = GeneralizedTrie()
entries: list[str] = [
    'abcdef',
    'abc',
    'abcd',
    'qrf',
]
for item in entries:
    trie.add(item)

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

# abc is in trie
# abcde is not in trie
# qrf is in trie
# abcdef is in trie
```

## Authors and acknowledgment

- Jerilyn Franz

## Copyright

Copyright 2025 by Jerilyn Franz

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
