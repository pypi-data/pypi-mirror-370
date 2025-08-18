#!/usr/bin/env python3
"""Example of using a GeneralizedTrie for indexing website URLs by path"""
from typing import Generator

from gentrie import GeneralizedTrie, TrieEntry

# Create a trie to store website URLs
url_trie = GeneralizedTrie()

# Add some URLs with different components (protocol, domain, path)
url_trie.add(["https", ":", "//", "com", "example", "www", "/", "products", "clothing"],
             "https://www.example.com/products/clothing")
url_trie.add(["http", ":", "//", "org", "/", "example", "blog", "/", "2023", "10", "best-laptops"],
             "http://example.org/blog/2023/10/best-laptops")  # DevSkim: ignore DS137138
url_trie.add(["ftp", ":", "//", "net", "example", "/", "ftp", "/", "data", "images"],
             "ftp://example.net/ftp/data/images")

# Find https URLs with "example.com" domain or sub-domain
print("HTTPS URLs for domains or sub-domains of 'example.com'")
prefixed_by: Generator[TrieEntry, None, None] = url_trie.prefixed_by(["https", ":", "//", "com", "example"])
for entry in prefixed_by:
    print(f"Found URL: {entry.value}")

# Find ftp protocol URLs
print("FTP URLs")
prefixed_by: Generator[TrieEntry, None, None] = url_trie.prefixed_by(["ftp"])
for entry in prefixed_by:
    print(f"Found URL: {entry.value}")

# HTTPS URLs for domains or sub-domains of 'example.com'
# Found URL: https://www.example.com/products/clothing
# FTP URLs
# Found URL: ftp://example.net/ftp/data/images
