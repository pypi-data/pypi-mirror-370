# python-gen-trie

* 0.1.0 - Initial release to github
* 0.1.1 through 0.1.3 WIP releases
* 0.1.4 - First public release to PyPI
* 0.1.5 - Fix to install instructions
* 0.2.0 - Refactored internal node implementation
* 0.2.1 - Updated examples code
* 0.2.2 - More examples code
* 0.3.0 - Added support for 'key in trie'
* 0.3.1 - Typo correction for example 7
* 0.3.2 - Updated installation instructions
* 0.3.3 - Fix to readthedocs usage page
* 0.4.0 - Deprecated gentrie.Hashable for gentrie.TrieKeyToken and updated documentation. Tuned tests and added more documentation.
* 0.4.1 - Removed use of '@deprecated' decorator as it is only available from Python 3.13 and later. Added example of using dataclass for a class usable as a content-aware trie key token. Added docstrings for test classes. Tweaked clear() method for performance. Simplified prefixes() method slightly. Addressed various minor lint issues.
* 0.4.2 - Performance improvements to \_\_contains\_\_() and suffixes()
* 0.4.3 - Added support for setting values associated with keys in the trie. Added update() method and tests. Made tests less brittle by changing text based state checking with dictionary based state checking. Added warnings about only using immutable objects as trie keys. Added tests for clear() method.
* 0.5.0 - Added support for using GeneralKeys directly in the remove() method; updated the \_\_getitem\_\_() method to support the use of GeneralKeys; added \_\_setitem\_\_() and \_\_delitem\_\_() methods
* 0.5.1 - Updated requirements.txt for Sphinx docs to sphinxawesome-theme==5.3.2
* 0.6.0 - Updated docs, made TrieId a stronger type guarantee and updated tests to match
* 0.7.0 - Changed prefixes() and prefixed_by() methods to return Generators instead of sets
* 0.8.0 - Refactored main code into separate files by functional grouping. Removed Bazel build support.
* 0.8.1 - Added TrieMixinsInterface protocol to cleanup type checking of trie mixins and make the mixin structure better documented
* 0.9.0 - Changed \_\_contains\_\_ and get() to conform to Pythonic conventions. Cleanup of type checking issues subsequent to change to mixin architecture.
* 0.9.1 - Added 'runtime_validation' property and initialization parameter for performance. Tweaked use of pyright directives to reduce visual noise in code. Simplified GeneralizedKey alias declaration by removing explict inclusion of 'str'.
* 0.9.2 - Refactor of exceptions and test code to use tagged exceptions. Seperation of testspecs testing framework into seperate file. First iteration of benchmarking code.
* 0.9.3 - Addition of coverage support. Tests for traversal.py. pytest support. Test orchestration using pytest-order and pytest-dependency. Fixed TrieValueError export.
