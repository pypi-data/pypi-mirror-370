==============
Using gen-trie
==============

.. _gentrie-installation:


.. index::

------------
Installation
------------

**Via PyPI**::

    pip3 install gen-tries
    
**From source**::

    git clone https://github.com/JerilynFranz/python-gen-tries
    cd python-gen-tries
    pip3 install .

-----
Usage
-----
The `gentrie` module provides a `GeneralizedTrie` class that allows you to create a trie structure for
storing and searching sequences of items, such as strings, lists, or tuples.

Below are some examples of how to use the `GeneralizedTrie` class.

Examples
========

Assigning Values to Entries
---------------------------
.. include:: ../../examples/assigning_values_to_entries.py
   :code: python

Dictionary Syntax Examples
---------------------------
.. include:: ../../examples/dictionary_syntax_examples.py
   :code: python

By Letter
----------------

.. include:: ../../examples/by_letter.py
   :code: python

By Tuple
----------------

.. include:: ../../examples/by_tuple.py
   :code: python

By Word
----------------

.. include:: ../../examples/by_word.py
   :code: python


Key In Trie
----------------

.. include:: ../../examples/key_in_trie.py
   :code: python


Prefixes
----------------

.. include:: ../../examples/prefixes_example.py
   :code: python

Prefixed By
----------------

.. include:: ../../examples/prefixed_by_example.py
   :code: python

URL Suffixes
----------------

.. include:: ../../examples/url_suffixes.py
   :code: python

Word Suggestions
----------------

.. include:: ../../examples/word_suggestion.py
   :code: python


Trie of numeric vectors
------------------------

.. include:: ../../examples/by_numeric_vector.py
   :code: python
   
