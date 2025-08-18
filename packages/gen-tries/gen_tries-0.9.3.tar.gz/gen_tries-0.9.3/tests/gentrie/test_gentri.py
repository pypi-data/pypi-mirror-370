"""Tests for the gentrie module."""
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

import unittest
from collections.abc import Iterable
from textwrap import dedent
from typing import Any

import pytest


from src.gentrie import (DuplicateKeyError, ErrorTag, GeneralizedTrie,
                         InvalidGeneralizedKeyError, TrieEntry, TrieId,
                         TrieKeyError, TrieKeyToken, TrieTypeError,
                         TrieValueError, is_generalizedkey)

from ..testspec import TestSpec, run_tests_list


class MockDefaultTrieKeyToken:
    """A mock class that implements the TrieKeyToken interface.

    This class is used to test the behavior of the GeneralizedTrie with user-defined classes
    and ensures that it can handle instances of classes that do not implement content-aware
    equality.
    """
    def __init__(self, a: tuple[int, int, int], b: str) -> None:
        self.a = a
        self.b = b


class MockContentAwareTrieKeyToken:
    """A mock class that implements the TrieKeyToken interface and uses content for equality."""
    def __init__(self, a: tuple[int, int, int], b: str) -> None:
        self.a = a
        self.b = b

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash((self.a, self.b))


class TestGeneralizedTrie(unittest.TestCase):
    """Test the GeneralizedTrie class and its methods."""

    @pytest.mark.order(1)
    @pytest.mark.dependency(name='test_trieid_class')
    def test_trieid_class(self) -> None:
        """Test the creation of TrieId instances."""
        tests: list[TestSpec] = [
            TestSpec(
                name="[TTI001] Creating TrieId(1) results in a TrieId instance",
                action=lambda: isinstance(TrieId(1), TrieId),  # type: ignore[reportUnknownMemberType]
                expected=True,
            ),
            TestSpec(
                name="[TTI002] int(1) is not a TrieId",
                action=lambda: isinstance(int(1), TrieId),
                expected=False,
            ),
            TestSpec(
                name="[TTI003] TrieId(2) is not equal to TrieId(1)",
                action=lambda: TrieId(2) == TrieId(1),
                expected=False,
            ),
            TestSpec(
                name="[TTI004] TrieId(1) is equal to itself",
                action=lambda: TrieId(1) == TrieId(1),
                expected=True,
            ),
        ]

        run_tests_list(self, tests)

    @pytest.mark.order(after='test_trieid_class')
    @pytest.mark.dependency(
        name='test_triekeytoken_supported_and_unsupported_builtin_types')
    def test_triekeytoken_supported_and_unsupported_builtin_types(self) -> None:
        """Tests that built in types are correctly classified as supported or unsupported."""
        TEST_ID: int = 0
        TEST_VALUE: int = 1
        good_types: list[tuple[str, Any]] = [
            ('TTKT_TSBT001', 'a'),
            ('TTKT_TSBT002', str('ab')),
            ('TTKT_TSBT003', frozenset('abc')),
            ('TTKT_TSBT004', tuple(['a', 'b', 'c', 'd'])),
            ('TTKT_TSBT005', int(1)),
            ('TTKT_TSBT006', float(2.0)),
            ('TTKT_TSBT007', complex(3.0, 4.0)),
            ('TTKT_TSBT008', bytes(456)),
        ]

        tests: list[TestSpec] = [
            TestSpec(
                name=f"[{testcase[TEST_ID]}] isinstance({repr(testcase[TEST_VALUE])}, TrieKeyToken) (True)",
                action=isinstance,
                args=[testcase[TEST_VALUE], TrieKeyToken],
                expected=True,
            )
            for testcase in good_types
        ]
        run_tests_list(self, tests)

        bad_types: list[tuple[str, Any]] = [
            ('TTKT_TUBT001', set('a')),
            ('TTKT_TUBT002', list(['a', 'b'])),
            ('TTKT_TUBT003', dict({'a': 1, 'b': 2, 'c': 3})),
            ('TTKT_TUBT004', set('abc')),
        ]

        tests = [
            TestSpec(
                name=f"[{testcase[TEST_ID]}] isinstance({repr(testcase[TEST_VALUE])}, TrieKeyToken) (False)",
                action=isinstance,
                args=[testcase[TEST_VALUE], TrieKeyToken],
                expected=False,
            )
            for testcase in bad_types
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_triekeytoken_supported_and_unsupported_builtin_types'])
    @pytest.mark.dependency(
        name='test_generalizedkey_supported_and_unsupported_builtin_types',
        depends=['test_triekeytoken_supported_and_unsupported_builtin_types'])
    def test_generalizedkey_supported_and_unsupported_builtin_types(self) -> None:
        """Tests supported and unsupported types for generalized keys.

        This test checks that types like strings, lists, and tuples
        of immutable types are recognized as valid generalized keys
        while non-sequence or mutable types like dict, set, and complex
        numbers are not considered valid generalized keys."""
        TEST_ID: int = 0
        TEST_VALUE: int = 1
        good_keys: list[tuple[str, Any]] = [
            ('TGK_SBT001', 'a'),
            ('TGK_SBT002', str('ab')),
            ('TGK_SBT003', ['a', 'b']),
            ('TGK_SBT004', tuple(['a', 'b', 'c', 'd'])),
            ('TGK_SBT005', [int(1)]),
            ('TGK_SBT006', [float(2.0)]),
            ('TGK_SBT007', [complex(3.0, 4.0)]),
            ('TGK_SBT007', [b'abc']),
            ('TGK_SBT008', b'abc')
        ]
        tests: list[TestSpec] = [
            TestSpec(
                name=f"[{testcase[TEST_ID]}] is_generalizedkey({repr(testcase[TEST_VALUE])}) (True)",
                action=is_generalizedkey,
                args=[testcase[TEST_VALUE]],
                expected=True,
            )
            for testcase in good_keys
        ]
        run_tests_list(self, tests)

        # Test cases for unsupported types
        bad_keys: list[tuple[str, Any]] = [
            ('TGK_TUBT001', ''),  # empty string is invalid as a GeneralizedKey
            ('TGK_TUBT002', dict({'a': 1, 'b': 2, 'c': 3})),
            ('TGK_TUBT003', set('abc')),
            ('TGK_TUBT004', frozenset('abc')),
            ('TGK_TUBT005', complex(3.0, 4.0)),
        ]

        tests = [
            TestSpec(
                name=f"[{testcase[TEST_ID]}] is_generalizedkey({repr(testcase[TEST_VALUE])}) (False)",
                action=is_generalizedkey,
                args=[testcase[TEST_VALUE]],
                expected=False,
            )
            for testcase in bad_keys
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_generalizedkey_supported_and_unsupported_builtin_types'])
    @pytest.mark.dependency(
        name='test_is_generalizedkey',
        depends=['test_generalizedkey_supported_and_unsupported_builtin_types'])
    def test_is_generalizedkey(self) -> None:
        """Test the is_generalizedkey function with various inputs.

        This test checks that the is_generalizedkey function correctly identifies
        valid and invalid generalized keys."""
        tests: list[TestSpec] = [
            TestSpec(
                name="[TIGK001] is_generalizedkey('a') (True)",
                action=is_generalizedkey,
                args=['a'],
                expected=True
            ),
            TestSpec(
                name="[TIGK002] is_generalizedkey(['a', 'b']) (True)",
                action=is_generalizedkey,
                args=[['a', 'b']],
                expected=True
            ),
            TestSpec(
                name="[TIGK003] is_generalizedkey(b'abc') (True)",
                action=is_generalizedkey,
                args=[b'abc'],
                expected=True
            ),
            TestSpec(
                name="[TIGK004] is_generalizedkey('') (False)",
                action=is_generalizedkey,
                args=[''],
                expected=False
            ),
            TestSpec(
                name="[TIGK005] is_generalizedkey([]) (False)",
                action=is_generalizedkey,
                args=[[]],
                expected=False
            ),
            TestSpec(
                name="[TIGK006] is_generalizedkey(123) (False)",
                action=is_generalizedkey,
                args=[123],
                expected=False
            ),
            TestSpec(
                name="[TIGK007] is_generalizedkey(None) (False)",
                action=is_generalizedkey,
                args=[None],
                expected=False
            ),
            TestSpec(
                name="[TIGK008] is_generalizedkey({'a': 1}) (False)",
                action=is_generalizedkey,
                args=[{'a': 1}],
                expected=False
            ),
            TestSpec(
                name="[TIGK009] is_generalizedkey(['a', {'b': 1}]) (False)",
                action=is_generalizedkey,
                args=[['a', {'b': 1}]],
                expected=False
            ),
            TestSpec(
                name="[TIGK010] is_generalizedkey(['a', ['b', ['c']]]) (False)",
                action=is_generalizedkey,
                args=[['a', ['b', ['c']]]],
                expected=False
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(order=6)
    @pytest.mark.dependency(name='test_create_trie')
    def test_create_trie(self) -> None:
        """Test the creation of a GeneralizedTrie instance.

        This test checks that the GeneralizedTrie can be instantiated without any arguments
        and that it raises a TypeError when an invalid filter_id is provided."""
        tests: list[TestSpec] = [
            TestSpec(
                name="[TCT001] create GeneralizedTrie()",
                action=GeneralizedTrie,
                validate_result=lambda found: isinstance(found,  # type: ignore[reportUnknownMemberType]
                                                         GeneralizedTrie),
            ),
            TestSpec(
                name="[TCT002] create GeneralizedTrie(filter_id=1)",
                action=GeneralizedTrie,
                kwargs={"filter_id": 1},
                exception=TypeError,
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_contains', 'test_bool'])
    @pytest.mark.dependency(
        name='test_clear',
        depends=['test_create_trie', 'test_add', 'test_contains', 'test_bool', 'test_keys'])
    def test_clear(self) -> None:
        """Test the clear method of GeneralizedTrie."""
        trie = GeneralizedTrie()
        trie.add("a")
        trie.add("b")
        self.assertEqual(len(trie), 2, "[TCL001] Trie should have 2 entries after adding 'a' and 'b'")
        self.assertTrue("a" in trie, "[TCL002] Trie should contain 'a' after addition")

        trie.clear()

        self.assertEqual(len(trie), 0, "[TCL003] Trie should be empty after clear()")
        self.assertFalse(bool(trie), "[TCL004] Trie should evaluate to False after clear()")
        self.assertFalse("a" in trie, "[TCL005] Trie should not contain 'a' after clear()")
        # pylint: disable=protected-access
        self.assertEqual(trie._ident_counter, 0,  # type: ignore[reportUnknownMemberType]
                         "[TCL006] Trie ident counter should be reset after clear()")
        self.assertEqual(list(trie.keys()), [], "[TCL007] Trie keys should be empty after clear()]")

    @pytest.mark.order(after="test_create_trie")
    @pytest.mark.dependency(
        name='test_add',
        depends=['test_create_trie', 'test_trieid_class'])
    def test_add(self) -> None:
        """Test the add method of GeneralizedTrie.

        This test covers adding various types of keys to the trie using the add() method, including strings,
        lists, and frozensets, and checks the expected behavior of the trie after each addition.
        It also includes tests for error handling when invalid keys are added."""
        # pylint: disable=protected-access, no-member
        trie = GeneralizedTrie()
        tests: list[TestSpec] = [
            # Initialize from a list of strings and validate we get the expected id
            TestSpec(
                name="[TA001] trie.add(['tree', 'value', 'ape'])",
                action=trie.add,
                args=[["tree", "value", "ape"]],
                kwargs={},
                expected=TrieId(1),
            ),
            # Validate the dictionary representation of the trie is correct after initialization
            TestSpec(
                name="[TA002] _as_dict()",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'ape': {
                                            'ident': TrieId(1),
                                            'token': 'ape',
                                            'value': None,
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'ape'], value=None)"}
                }
            ),

            # Add another entry ['tree', 'value'] and validate we get the expected id for it
            TestSpec(
                name="[TA003] trie.add(['tree', 'value']",
                action=trie.add,
                args=[["tree", "value"]],
                expected=TrieId(2),
            ),
            # Validate the _as_dict representation of the trie is correct
            TestSpec(
                name="[TA004] _as_dict()",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': TrieId(2),
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'ape': {
                                            'ident': TrieId(1),
                                            'token': 'ape',
                                            'value': None,
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1), TrieId(2)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'ape'], value=None)",
                        TrieId(2): "TrieEntry(ident=TrieId(2), key=['tree', 'value'], value=None)"
                    }
                }
            ),
            # Add a string entry 'abcdef' and validate we get the expected id for it
            TestSpec(
                name="[TA005] trie.add('abcdef')",
                action=trie.add,
                args=["abcdef"],
                expected=TrieId(3),
            ),
            # Add another entry [1, 3, 4, 5] and validate we get the expected id for it
            TestSpec(
                name="[TA006] trie.add([1, 3, 4, 5])",
                action=trie.add,
                args=[[1, 3, 4, 5]],
                kwargs={},
                expected=TrieId(4),
            ),
            # Add a frozenset entry and validate we get the expected id for it
            TestSpec(
                name="[TA007] trie.add(frozenset([1]), 3, 4, 5])",
                action=trie.add,
                args=[[frozenset([1]), 3, 4, 5]],
                kwargs={},
                expected=TrieId(5),
            ),
            # Add another frozenset entry and validate we get a different id for it
            # than for the previously added frozenset
            TestSpec(
                name="[TA008] trie.add(frozenset([1]), 3, 4, 5])",
                action=trie.add,
                args=[[frozenset([1]), 3, 4, 6]],
                expected=TrieId(6),
            ),
            # Attempt to add an integer as a key and validate we get the expected exception
            TestSpec(
                name="[TA009] trie.add(1)",
                action=trie.add,
                args=[1],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY,
            ),
            # Attempt to add an empty list as a key and validate we get the expected exception
            TestSpec(
                name="[TA010] trie.add([])",
                action=trie.add,
                args=[[]],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY,
            ),
            # Attempt to add a set as a key element and validate we get the expected exception
            TestSpec(
                name="[TA011] trie.add([set([1]), 3, 4, 5])",
                action=trie.add,
                args=[[set([1]), 3, 4, 5]],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY,
            ),
            # Add a key that is a list of integers and validate we get the expected id for it
            TestSpec(
                name="[TA012] trie.add(key=[1, 3, 4, 7])",
                action=trie.add,
                kwargs={"key": [1, 3, 4, 7]},
                expected=TrieId(7),
            ),
            # Attempt to pass add the wrong number of arguments and validate we get the expected exception
            TestSpec(name="[TA013] trie.add()",
                     action=trie.add,
                     exception=TypeError),
            TestSpec(
                name="[TA014] trie.add(['a'], ['b'], ['c'])",
                action=trie.add,
                args=[["a"], ["b"], ["c"]],
                exception=TypeError,
            ),
            # Validate the length of the trie after all additions
            TestSpec(name="[TA015] len(trie)", action=len, args=[trie], expected=7),
            # Add duplicate entry ['tree', 'value', 'ape'] and validate we get a DuplicateKeyError
            TestSpec(
                name="[TA016] trie.add(['tree', 'value', 'ape'])",
                action=trie.add,
                args=[["tree", "value", "ape"]],
                kwargs={},
                exception=DuplicateKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_DUPLICATE_KEY,
            ),
            # Validate the length of the trie trying to add duplicate ['tree', 'value', 'ape'] is unchanged
            TestSpec(name="[TA017] len(trie)", action=len, args=[trie], expected=7),
            # Add a trie entry with a value and validate we get the expected id for it
            TestSpec(
                name="[TA018] trie.add(['tree', 'value', 'cheetah'], 'feline')",
                action=trie.add,
                args=[["tree", "value", "cheetah"], "feline"],
                expected=TrieId(8),
            ),

        ]
        run_tests_list(self, tests)

        # New untouched trie for the next sequence of tests
        # Not using clear() here to keep the clear() tests cleanly separated
        # from the add() tests.
        trie = GeneralizedTrie()

        # Test cases for setting values on trie entries
        tests = [
            # Initialize the trie with a key with a value and validate we get the expected id
            TestSpec(
                name="[TA019] trie.add(['tree', 'value', 'cheetah'], 'feline')",
                action=trie.add,
                args=[["tree", "value", "cheetah"], "feline"],
                expected=TrieId(1),
            ),
            # validate that entry 1 (with the key ['tree', 'value', 'cheetah']) has the value of 'feline'
            TestSpec(
                name="[TA020] trie[1].value == 'feline' (_as_dict() check)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': 'feline',
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value='feline')"
                    }
                },
            ),
            # Add the same key with the same value and validate we get the same id as before
            # (this is to test that the trie does not create a new entry for the same key with the same value
            # and that it does not throw an error)
            TestSpec(
                name="[TA021] trie.add(['tree', 'value', 'cheetah'], 'feline')",
                action=trie.add,
                args=[["tree", "value", "cheetah"], "feline"],
                exception=DuplicateKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_DUPLICATE_KEY,
                # This is expected to raise a DuplicateKeyError, but we are testing that the trie
                # does not change its state after adding the same key with the same value.
                # So we do not expect the trie to change, and we will validate that in the
                # next test case.
            ),
            # validate that the trie is unchanged after exception for trying to add the same key with the same value
            TestSpec(
                name="[TA022] trie[1].value == 'feline' (_as_dict() check)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': 'feline',
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value='feline')"
                    }
                },
            ),
            # Add the same key with a DIFFERENT value (default of None) and validate we get a DuplicateKeyError
            TestSpec(
                name="[TA022] trie.add(['tree', 'value', 'cheetah'])",
                action=trie.add,
                args=[["tree", "value", "cheetah"]],
                exception=DuplicateKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_DUPLICATE_KEY,
            ),
            # Validate that the trie is unchanged after attempting to add the same key with a different value of None
            # (this is to test that the trie has not changed the trie despite throwing an error)
            # Validate that the trie is unchanged after attempting to add the same key with a different value of None
            # (this is to test that the trie has not changed the trie despite throwing an error)
            TestSpec(
                name="[TA023] trie[1].value == 'feline' (_as_dict() check, no change after DuplicateKeyError)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': 'feline',
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value='feline')"
                    }
                },
            ),
            # Add the same key with a DIFFERENT value (explictly specified) and validate we get a DuplicateKeyError
            TestSpec(
                name="[TA024] trie.add(['tree', 'value', 'cheetah'], 'canide)",
                action=trie.add,
                args=[["tree", "value", "cheetah"], "canide"],
                exception=DuplicateKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_DUPLICATE_KEY,
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_create_trie', 'test_trieid_class'])
    @pytest.mark.dependency(
        name='test_update',
        depends=['test_create_trie', 'test_trieid_class'])
    def test_update(self) -> None:
        """Test the update method of GeneralizedTrie.

        This test covers adding various types of keys to the trie via the update() method, including strings,
        lists, and frozensets, and checks the expected behavior of the trie after each addition.
        It also includes tests for error handling when invalid keys are added."""
        # pylint: disable=protected-access, no-member
        trie = GeneralizedTrie()
        tests: list[TestSpec] = [
            # Initialize from a list of strings and validate we get the expected id
            TestSpec(
                name="[TU001] trie.update(['tree', 'value', 'ape'])",
                action=trie.update,
                args=[["tree", "value", "ape"]],
                kwargs={},
                expected=TrieId(1),
            ),
            # Validate the dictionary representation of the trie is correct after initialization
            TestSpec(
                name="[TU002] _as_dict()",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'ape': {
                                            'ident': TrieId(1),
                                            'token': 'ape',
                                            'value': None,
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'ape'], value=None)"}
                }
            ),

            # Add another entry ['tree', 'value'] and validate we get the expected id for it
            TestSpec(
                name="[TU003] trie.update(['tree', 'value']",
                action=trie.update,
                args=[["tree", "value"]],
                expected=TrieId(2),
            ),
            # Validate the _as_dict representation of the trie is correct
            TestSpec(
                name="[TU004] _as_dict()",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': TrieId(2),
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'ape': {
                                            'ident': TrieId(1),
                                            'token': 'ape',
                                            'value': None,
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1), TrieId(2)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'ape'], value=None)",
                        TrieId(2): "TrieEntry(ident=TrieId(2), key=['tree', 'value'], value=None)"
                    }
                }
            ),
            # Add a string entry 'abcdef' and validate we get the expected id for it
            TestSpec(
                name="[TU005] trie.update('abcdef')",
                action=trie.update,
                args=["abcdef"],
                expected=TrieId(3),
            ),
            # Add another entry [1, 3, 4, 5] and validate we get the expected id for it
            TestSpec(
                name="[TU006] trie.update([1, 3, 4, 5])",
                action=trie.update,
                args=[[1, 3, 4, 5]],
                kwargs={},
                expected=TrieId(4),
            ),
            # Add a frozenset entry and validate we get the expected id for it
            TestSpec(
                name="[TU007] trie.update(frozenset([1]), 3, 4, 5])",
                action=trie.update,
                args=[[frozenset([1]), 3, 4, 5]],
                kwargs={},
                expected=TrieId(5),
            ),
            # Add another frozenset entry and validate we get a different id for it
            # than for the previously added frozenset
            TestSpec(
                name="[TU008] trie.update(frozenset([1]), 3, 4, 5])",
                action=trie.update,
                args=[[frozenset([1]), 3, 4, 6]],
                expected=TrieId(6),
            ),
            # Attempt to add an integer as a key and validate we get the expected exception
            TestSpec(
                name="[TU009] trie.update(1)",
                action=trie.update,
                args=[1],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY,
            ),
            # Attempt to add an empty list as a key and validate we get the expected exception
            TestSpec(
                name="[TU010] trie.update([])",
                action=trie.update,
                args=[[]],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY,
            ),
            # Attempt to add a set as a key element and validate we get the expected exception
            TestSpec(
                name="[TU011] trie.update([set([1]), 3, 4, 5])",
                action=trie.update,
                args=[[set([1]), 3, 4, 5]],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_INVALID_GENERALIZED_KEY,
            ),
            # Add a key that is a list of integers and validate we get the expected id for it
            TestSpec(
                name="[TU012] trie.update(key=[1, 3, 4, 7])",
                action=trie.update,
                kwargs={"key": [1, 3, 4, 7]},
                expected=TrieId(7),
            ),
            # Attempt to pass add the wrong number of arguments and validate we get the expected exception
            TestSpec(name="[TU013] trie.update()", action=trie.update, exception=TypeError),
            TestSpec(
                name="[TU014] trie.update(['a'], ['b'], ['c'])",
                action=trie.update,
                args=[["a"], ["b"], ["c"]],
                exception=TypeError,
            ),
            # Validate the length of the trie after all additions
            TestSpec(name="[TU015] len(trie)", action=len, args=[trie], expected=7),
            # Add duplicate entry ['tree', 'value', 'ape'] and validate we get the original id for it
            TestSpec(
                name="[TU016] trie.update(['tree', 'value', 'ape'])",
                action=trie.update,
                args=[["tree", "value", "ape"]],
                kwargs={},
                expected=TrieId(1),
            ),
            # Validate the length of the trie after adding duplicate ['tree', 'value', 'ape'] is unchanged
            TestSpec(name="[TU017] len(trie)", action=len, args=[trie], expected=7),
            # Add a trie entry with a value and validate we get the expected id for it
            TestSpec(
                name="[TU018] trie.update(['tree', 'value', 'cheetah'], 'feline')",
                action=trie.update,
                args=[["tree", "value", "cheetah"], "feline"],
                expected=TrieId(8),
            ),

        ]
        run_tests_list(self, tests)

        # New untouched trie for the next sequence of tests
        # Not using clear() here to keep the clear() tests cleanly separated
        # from the update() tests.
        trie = GeneralizedTrie()

        # Test cases for setting values on trie entries
        tests = [
            # Initialize the trie with a key with a value and validate we get the expected id
            TestSpec(
                name="[TU019] trie.update(['tree', 'value', 'cheetah'], 'feline')",
                action=trie.update,
                args=[["tree", "value", "cheetah"], "feline"],
                expected=TrieId(1),
            ),
            # validate that entry 1 (with the key ['tree', 'value', 'cheetah']) has the value of 'feline'
            TestSpec(
                name="[TU020] trie[1].value == 'feline' (_as_dict() check)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': 'feline',
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value='feline')"
                    }
                },
            ),
            # Add the same key with the same value and validate we get the same id as before
            # (this is to test that the trie does not create a new entry for the same key with the same value
            # and that it does not throw an error)
            TestSpec(
                name="[TU021] trie.update(['tree', 'value', 'cheetah'], 'feline')",
                action=trie.update,
                args=[["tree", "value", "cheetah"], "feline"],
                expected=TrieId(1),
            ),
            # validate that the trie is unchanged after adding the same key with the same value
            TestSpec(
                name="[TU022] trie[1].value == 'feline' (_as_dict() check)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': 'feline',
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value='feline')"
                    }
                },
            ),
            # Add the same key with a DIFFERENT value (default of None) and validate we get the expected id
            # (this is to test that the trie updates the value of the existing entry)
            TestSpec(
                name="[TU023] trie.update(['tree', 'value', 'cheetah'])",
                action=trie.update,
                args=[["tree", "value", "cheetah"]],
                expected=TrieId(1),
            ),
            # Validate that the trie was correctly updated after adding the same key with a different value of None
            TestSpec(
                name="[TU024] trie[1].value == None (_as_dict() check)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': None,
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value=None)"
                    }
                },
            ),
            # Add the same key with a DIFFERENT value (explictly specified) and validate we get the same id as before
            TestSpec(
                name="[TU025] trie.update(['tree', 'value', 'cheetah'], 'canide)",
                action=trie.update,
                args=[["tree", "value", "cheetah"], "canide"],
                expected=TrieId(1),
            ),
            # Validate that the trie was correctly updated after adding the same key with a different value of 'canide'
            TestSpec(
                name="[TU026] trie[1].value == 'canide' (_as_dict() check)",
                action=trie._as_dict,  # type: ignore[reportUnknownMemberType]
                expected={
                    'ident': None,
                    'children': {
                        'tree': {
                            'ident': None,
                            'token': 'tree',
                            'value': None,
                            'parent': None,
                            'children': {
                                'value': {
                                    'ident': None,
                                    'token': 'value',
                                    'value': None,
                                    'parent': 'tree',
                                    'children': {
                                        'cheetah': {
                                            'ident': TrieId(1),
                                            'token': 'cheetah',
                                            'value': 'canide',
                                            'parent': 'value',
                                            'children': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'trie_index': [TrieId(1)],
                    'trie_entries': {
                        TrieId(1): "TrieEntry(ident=TrieId(1), key=['tree', 'value', 'cheetah'], value='canide')"
                    }
                },
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_create_trie', 'test_add'])
    @pytest.mark.dependency(
        name='test_add_user_defined_classes',
        depends=['test_create_trie', 'test_add'])
    def test_add_user_defined_classes(self) -> None:
        """Test adding user-defined classes to GeneralizedTrie.

        This test checks that the trie can handle user-defined classes that implement
        the TrieKeyToken interface and that it can distinguish between different instances
        of these classes based on their content."""
        trie = GeneralizedTrie()
        a: list[str | MockDefaultTrieKeyToken] = ['red', MockDefaultTrieKeyToken(a=(1, 2, 3), b='hello')]
        b: list[str | MockDefaultTrieKeyToken] = ['red', MockDefaultTrieKeyToken(a=(1, 2, 3), b='hello')]
        c: list[str | MockContentAwareTrieKeyToken] = ['red', MockContentAwareTrieKeyToken(a=(1, 2, 3), b='hello')]
        d: list[str | MockContentAwareTrieKeyToken] = ['red', MockContentAwareTrieKeyToken(a=(1, 2, 3), b='hello')]

        with self.subTest(msg='[TAUDC001] a <=> b'):
            self.assertNotEqual(a, b)
        with self.subTest(msg='[TAUDC002] a <=> a'):
            self.assertEqual(a, a)
        with self.subTest(msg='[TAUDC003] c <=> d'):
            self.assertEqual(c, d)
        with self.subTest(msg='[TAUDC004] c <=> c'):
            self.assertEqual(c, c, msg='c <=> c')

        tests: list[TestSpec] = [
            TestSpec(
                name="[TAUDC005] trie.add(['red', MockDefaultTrieKeyToken(a=(1, 2, 3), b='hello')])",
                action=trie.add,
                args=[a],
                expected=TrieId(1),
            ),
            TestSpec(
                name="[TAUDC006] trie.add(['red', MockDefaultTrieKeyToken(a=[1, 2, 3], b='hello')])",
                action=trie.add,
                args=[b],
                expected=TrieId(2),
            ),
            TestSpec(
                name="[TAUDC007] trie.add(['red', MockContentAwareTrieKeyToken(a=(1, 2, 3), b='hello')])",
                action=trie.add,
                args=[c],
                expected=TrieId(3),
            ),
            TestSpec(
                name="[TAUDC008] trie.add(['red', MockContentAwareTrieKeyToken(a=(1, 2, 3), b='hello')])",
                action=trie.add,
                args=[d],
                exception=DuplicateKeyError,
                exception_tag=ErrorTag.STORE_ENTRY_DUPLICATE_KEY,
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_create_trie', 'test_add', 'test_trieid_class'])
    @pytest.mark.dependency(
        name='test_prefixes',
        depends=['test_create_trie', 'test_add', 'test_trieid_class'])
    def test_prefixes(self) -> None:
        """Test the prefixes method of GeneralizedTrie.

        This test checks that the prefixes method correctly identifies all prefixes
        of a given key in the trie, including those that are not complete entries."""
        trie: GeneralizedTrie = GeneralizedTrie()
        tests: list[TestSpec] = [
            TestSpec(
                name="[TGT_TP001] trie.prefixes(['tree', 'value', 'ape']) (empty trie)",
                action=lambda key: list(trie.prefixes(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree', 'value', 'ape']],
                expected=[]
            ),
            TestSpec(
                name="[TGT_TP002] trie.add(['tree', 'value', 'ape'])",
                action=trie.add,
                args=[["tree", "value", "ape"]],
                expected=TrieId(1)
            ),
            TestSpec(
                name="[TGT_TP003] trie.prefixes(['tree', 'value', 'ape']) (exact key in trie)",
                action=lambda key: list(trie.prefixes(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree', 'value', 'ape']],
                expected=[TrieEntry(TrieId(1), ['tree', 'value', 'ape'])]
            ),
            TestSpec(
                name=("[TGT_TP004] trie.prefixes(['tree', 'value', 'ape', 'grape']) "
                      "(NOT exact key in trie, but has other keys that are prefix)"),
                action=lambda key: list(trie.prefixes(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree', 'value', 'ape', 'grape']],
                expected=[TrieEntry(TrieId(1), ['tree', 'value', 'ape'])]
            ),
            TestSpec(
                name=("[TGT_TP005] trie.prefixes(['tree', 'value']) "
                      "(NOT exact key in trie, does not have other keys that are prefix)"),
                action=lambda key: list(trie.prefixes(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree', 'value']],
                expected=[]
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_create_trie', 'test_add', 'test_trieid_class'])
    @pytest.mark.dependency(
        name='test_prefixed_by',
        depends=['test_create_trie', 'test_add', 'test_trieid_class'])
    def test_prefixed_by(self) -> None:
        """Test the prefixed_by method of GeneralizedTrie.

        This test checks that the prefixed_by method correctly identifies all keys
        in the trie that are prefixed by the specified key."""
        trie: GeneralizedTrie = GeneralizedTrie()
        tests: list[TestSpec] = [
            TestSpec(
                name="[TGT_TPB001] tree.prefixed_by(['tree']) (empty trie, no possible prefixed keys)",
                action=lambda key: list(trie.prefixed_by(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree']],
                expected=[]
            ),
            TestSpec(
                name="[TGT_TPB002] trie.add(['tree', 'value', 'ape']) (one key in trie)",
                action=trie.add,
                args=[["tree", "value", "ape"]],
                expected=TrieId(1)
            ),
            TestSpec(
                name="[TGT_TPB003] trie.prefixed_by(['tree', 'value', 'ape']) (exact key in trie, no others)",
                action=lambda key: list(trie.prefixed_by(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree', 'value', 'ape']],
                expected=[TrieEntry(TrieId(1), ['tree', 'value', 'ape'])]
            ),
            TestSpec(
                name=("[TGT_TPB004] trie.prefixed_by(['tree']) "
                      "(NOT exact key in trie, but prefixes other keys in the trie)"),
                action=lambda key: list(trie.prefixed_by(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree']],
                expected=[TrieEntry(TrieId(1), ['tree', 'value', 'ape'])]
            ),
            TestSpec(
                name=("[TGT_TPB005] trie.prefixed_by(['tree', 'value', 'ape', 'grape']) "
                      "(NOT exact key in trie, does not have other keys in trie it is a prefix for)"),
                action=lambda key: list(trie.prefixed_by(key)),  # type: ignore[reportUnknownMemberType]
                args=[['tree', 'value', 'ape', 'grape']],
                expected=[]
            ),
            TestSpec(
                name=("[TGT_TPB006] trie.prefixed_by(key=['tree'], depth=0) "
                      "(NO exact key in trie)"),
                action=lambda key, depth: list(trie.prefixed_by(  # pyright: ignore[reportUnknownLambdaType]
                    key=key, depth=depth)),  # type: ignore[reportUnknownMemberType]
                kwargs={'key': ['tree'], 'depth': 0},
                expected=[]
            ),
            TestSpec(
                name=("[TGT_TPB007] trie.prefixed_by(key=['tree'], depth=1) "
                      "(NOT exact key in trie, does not have other keys in trie it is a prefix for within depth 1)"),
                action=lambda key, depth: list(trie.prefixed_by(  # pyright: ignore[reportUnknownLambdaType]
                        key=key, depth=depth)),  # type: ignore[reportUnknownMemberType]
                kwargs={'key': ['tree'], 'depth': 1},
                expected=[]
            ),
            TestSpec(
                name=("[TGT_TPB008] trie.prefixed_by(key=['tree'], depth=2) "
                      "(NOT exact key in trie, has other keys in trie it is a prefix for within depth 2)"),
                action=lambda key, depth: list(trie.prefixed_by(  # pyright: ignore[reportUnknownLambdaType]
                    key=key, depth=depth)),  # type: ignore[reportUnknownMemberType]
                kwargs={'key': ['tree'], 'depth': 2},
                expected=[TrieEntry(TrieId(1), ['tree', 'value', 'ape'])]
            ),
            TestSpec(
                name=("[TGT_TPB009] trie.prefixed_by(key=['tree'], depth=-1) "
                      "(NOT exact key in trie, has other keys in trie it is a prefix for within any depth)"),
                action=lambda key, depth: list(trie.prefixed_by(  # pyright: ignore[reportUnknownLambdaType]
                    key=key, depth=depth)),  # type: ignore[reportUnknownMemberType]
                kwargs={'key': ['tree'], 'depth': -1},
                expected=[TrieEntry(TrieId(1), ['tree', 'value', 'ape'])]
            ),
            TestSpec(
                name=("[TGT_TPB010] trie.prefixed_by(key=['tree'], depth=-2) "
                      "(TrieValueError, TRIE_PREFIXED_BY_BAD_DEPTH_VALUE)"),
                action=lambda key, depth: list(trie.prefixed_by(  # pyright: ignore[reportUnknownLambdaType]
                    key=key, depth=depth)),  # type: ignore[reportUnknownMemberType]
                kwargs={'key': ['tree'], 'depth': -2},
                exception=TrieValueError,
                exception_tag=ErrorTag.TRIE_PREFIXED_BY_BAD_DEPTH_VALUE,
            ),
            TestSpec(
                name=("[TGT_TPB011] trie.prefixed_by(key=['tree'], depth=-1.0) "
                      "(TrieTypeError, TRIE_PREFIXED_BY_BAD_DEPTH_TYPE)"),
                action=lambda key, depth: list(trie.prefixed_by(  # pyright: ignore[reportUnknownLambdaType]
                    key=key, depth=depth)),  # type: ignore[reportUnknownMemberType]
                kwargs={'key': ['tree'], 'depth': -1.0},
                exception=TrieTypeError,
                exception_tag=ErrorTag.TRIE_PREFIXED_BY_BAD_DEPTH_TYPE,
            ),
            TestSpec(
                name=("[TGT_TPB012] trie.prefixed_by([set([1]), 3, 4, 5]) "
                      "(InvalidGeneralizedKeyError, TRIE_PREFIXED_BY_INVALID_GENERALIZED_KEY)"),
                action=lambda key: list(trie.prefixed_by(key)),  # type: ignore[reportUnknownMemberType]
                args=[[set([1]), 3, 4, 5]],
                exception=InvalidGeneralizedKeyError,
                exception_tag=ErrorTag.TRIE_PREFIXED_BY_INVALID_GENERALIZED_KEY,
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after=['test_create_trie', 'test_add', 'test_trieid_class', 'test_contains'])
    @pytest.mark.dependency(
        name='test_deeply_nested_keys',
        depends=['test_create_trie', 'test_add', 'test_trieid_class', 'test_contains'])
    def test_deeply_nested_keys(self):
        """Test that deeply nested keys can be added and queried correctly.

        This test checks that the trie can handle keys with a large number of elements
        and that it correctly identifies prefixes and suffixes for such keys."""
        trie = GeneralizedTrie()
        deep_key = ["a"] * 100
        id1 = trie.add(deep_key)
        self.assertEqual(id1, TrieId(1))
        self.assertTrue(deep_key in trie)
        self.assertEqual(set(trie.prefixes(deep_key)), set([TrieEntry(TrieId(1), deep_key)]))
        self.assertEqual(set(trie.prefixed_by(deep_key)), set([TrieEntry(TrieId(1), deep_key)]))

    @pytest.mark.order(after=['test_create_trie', 'test_add', 'test_trieid_class', 'test_contains'])
    @pytest.mark.dependency(
        name='test_unicode_and_bytes_keys',
        depends=['test_create_trie', 'test_add', 'test_trieid_class', 'test_contains'])
    def test_unicode_and_bytes_keys(self):
        """Test that unicode and bytes keys can coexist in the trie.

        This test checks that the trie can handle both unicode strings and byte strings
        as keys, and that they are treated as distinct entries."""
        trie = GeneralizedTrie()
        unicode_key = ["α", "β", "γ"]
        bytes_key = [b"\xf0\x9f\x92\xa9"]
        id1 = trie.add(unicode_key)
        id2 = trie.add(bytes_key)
        self.assertEqual(id1, TrieId(1))
        self.assertEqual(id2, TrieId(2))
        self.assertTrue(unicode_key in trie)
        self.assertTrue(bytes_key in trie)

    @pytest.mark.order(after=['test_contains', 'test_create_trie', 'test_add', 'test_trieid_class'])
    @pytest.mark.dependency(
        name='test_mutated_key_after_insertion',
        depends=['test_trieid_class', 'test_create_trie', 'test_add', 'test_contains'])
    def test_mutated_key_after_insertion(self):
        """Test that mutating a key after insertion does not affect the trie.

        This test checks that the trie maintains the integrity of the original key.
        """
        trie = GeneralizedTrie()
        key = ["a", "b"]
        _ = trie.add(key)
        key.append("c")  # Mutate after insertion
        # The mutated key should not be found as the original
        self.assertFalse(key in trie)
        # The original key (["a", "b"]) should still be present
        self.assertTrue(["a", "b"] in trie)

    @pytest.mark.order(after=['test_create_trie', 'test_is_generalizedkey'])
    @pytest.mark.dependency(
        name='test_invalid_argument_types_for_prefixes',
        depends=['test_create_trie', 'test_is_generalizedkey'])
    def test_invalid_argument_types_for_prefixes(self):
        """Test that invalid argument types raise correct exceptions."""
        trie = GeneralizedTrie()
        with self.assertRaises(
              InvalidGeneralizedKeyError,
              msg='[TIATFP001] Failed to raise InvalidGeneralizedKeyError for trie.prefixes(12345)'):
            # Attempt to get prefixes for an invalid key type. Because a Generator is
            # returned, it will not raise the error until the generator is consumed.
            _ = set(trie.prefixes(12345))  # type: ignore[reportGeneralTypeIssues]  # int is not a valid key
        with self.assertRaises(
              InvalidGeneralizedKeyError,
              msg='[TIATFP002] Failed to raise InvalidGeneralizedKeyError for trie.prefixes(3.14)'):
            _ = set(trie.prefixes(3.14))   # type: ignore[reportGeneralTypeIssues]  # float is not a valid key

    def test_invalid_argument_types_for_prefixed_by(self):
        """Test that invalid argument types raise TypeError."""
        trie = GeneralizedTrie()
        with self.assertRaises(
              InvalidGeneralizedKeyError,
              msg='[TIATFPB001] Failed to raise InvalidGeneralizedKeyError for trie.prefixed_by(12345)'):
            _ = set(trie.prefixed_by(12345))  # type: ignore[reportGeneralTypeIssues]  # int is not a valid key
        with self.assertRaises(
              InvalidGeneralizedKeyError,
              msg='[TIATFPB002] Failed to raise InvalidGeneralizedKeyError for trie.prefixed_by(3.14)'):
            _ = set(trie.prefixed_by(3.14))   # type: ignore[reportGeneralTypeIssues]  # float is not a valid key

    def test_large_trie_performance(self):
        """Test performance of adding a large number of entries to the trie."""
        trie = GeneralizedTrie()
        for i in range(1000):
            trie.add([i, i+1, i+2])
        self.assertEqual(len(trie), 1000)
        # Spot check a few
        self.assertTrue([10, 11, 12] in trie)
        self.assertTrue([999, 1000, 1001] in trie)

    @pytest.mark.order(after='test_contains')
    @pytest.mark.dependency(name='test_bytes_vs_str',
                            depends=['test_create_trie', 'test_contains'])
    def test_bytes_vs_str(self):
        """Test that adding a string and bytes with the same content generates different IDs.

        This test checks that the trie treats strings and bytes as distinct types."""
        trie = GeneralizedTrie()
        id1 = trie.add("abc")
        id2 = trie.add(b"abc")
        self.assertNotEqual(id1, id2)
        self.assertTrue("abc" in trie)
        self.assertTrue(b"abc" in trie)

    def test_empty_trie_iter(self):
        """Test that an empty trie iterates to an empty list."""
        trie = GeneralizedTrie()
        self.assertEqual(list(trie), [])

    def test_remove_nonexistent_id(self):
        """Test removing a non-existent ID from the trie.

        This test checks that attempting to remove an ID that does not exist
        raises a KeyError.
        """
        trie = GeneralizedTrie()
        self.assertEqual(
            trie.add("abc"),
            TrieId(1),
            msg='[TRNEI001] Add an entry to ensure the trie is not empty. Should have TrieId(1)')
        with self.assertRaises(KeyError,
                               msg='[TRNEI002] Removing a non-existent TrieId(999999) should raise KeyError'):
            trie.remove(TrieId(999999))  # Non-existent TrieId
        with self.assertRaises(
                TypeError,
                msg=('[TRNEI003] Removing 1 should raise a TypError because it is not a '
                     'TrieId or a valid GeneralizedKey')):
            trie.remove(1)  # type: ignore[reportGeneralTypeIssues]

    def test_remove_and_readd(self):
        """Test removing an entry and then re-adding it to ensure a new ID is generated.

        This test checks that after removing an entry, adding the same key again
        generates a new ID, confirming that the trie correctly handles the removal
        and re-adding of entries."""
        trie = GeneralizedTrie()
        key = ["x", "y", "z"]
        id1 = trie.add(key)
        trie.remove(id1)
        id2 = trie.add(key)
        self.assertNotEqual(id1, id2)
        self.assertTrue(key in trie)

    @pytest.mark.order(after='test_add')
    @pytest.mark.dependency(name='test_remove', depends=[
        'test_create_trie', 'test_trieid_class', 'test_add'])
    def test_remove(self) -> None:
        """Test the remove method of GeneralizedTrie.

        This test covers adding, removing, and checking the state of the trie.

        It includes various scenarios such as removing existing entries, handling
        non-existing entries, and checking the length of the trie after removals.

        The test also checks for correct exception handling when trying to remove
        non-existing entries or entries with invalid types.

        This test is designed to ensure that the remove method behaves correctly
        and maintains the integrity of the trie structure."""
        trie: GeneralizedTrie = GeneralizedTrie()
        tests: list[TestSpec] = [
            TestSpec(
                name="[TR001] trie.add('a')", action=trie.add, args=["a"], expected=TrieId(1)
            ),
            TestSpec(
                name="[TR002] trie.add('ab')", action=trie.add, args=["ab"], expected=TrieId(2)
            ),
            TestSpec(
                name="[TR003] trie.add('abc')", action=trie.add, args=["abc"], expected=TrieId(3),
            ),
            TestSpec(
                name="[TR004] trie.add('abe')",
                action=trie.add,
                args=["abe"],
                expected=TrieId(4),
            ),
            TestSpec(
                name="[TR005] trie.add('abef')",
                action=trie.add,
                args=["abef"],
                expected=TrieId(5),
            ),
            TestSpec(
                name="[TR006] trie.add('abcd')",
                action=trie.add,
                args=["abcd"],
                expected=TrieId(6),
            ),
            TestSpec(
                name="[TR007] trie.add('abcde')",
                action=trie.add,
                args=["abcde"],
                expected=TrieId(7),
            ),
            TestSpec(
                name="[TR008] trie.add('abcdf')",
                action=trie.add,
                args=["abcdef"],
                expected=TrieId(8),
            ),
            TestSpec(
                name="[TR009] trie.add('abcdefg')",
                action=trie.add,
                args=["abcdefg"],
                expected=TrieId(9),
            ),
            TestSpec(
                name="[TR010] trie.remove(TrieId(9))",
                action=trie.remove,
                args=[TrieId(9)],
                expected=None,
            ),
            TestSpec(name="[TR011] len(trie)", action=len, args=[trie], expected=8),
            TestSpec(
                name="[TR012] trie.remove(TrieId(9)) (TrieKeyError, REMOVAL_KEY_NOT_FOUND)",
                action=trie.remove,
                args=[TrieId(9)],
                exception=TrieKeyError,
                exception_tag=ErrorTag.REMOVAL_KEY_NOT_FOUND,
            ),
            TestSpec(name="[TR013] len(trie)", action=len, args=[trie], expected=8),
            TestSpec(
                name="[TR014] trie.remove(TrieId(1))",
                action=trie.remove,
                args=[TrieId(1)],
                expected=None,
            ),
            TestSpec(name="[TR015] len(trie)", action=len, args=[trie], expected=7),
            TestSpec(
                name="[TR016] trie.remove(TrieId(2))",
                action=trie.remove,
                args=[TrieId(2)],
                expected=None,
            ),
            TestSpec(name="[TR017] len(trie)", action=len, args=[trie], expected=6),
            TestSpec(
                name="[TR018] trie.remove('defghi') (TrieKeyError, REMOVAL_KEY_NOT_FOUND)",
                action=trie.remove,
                args=["defghi"],
                exception=TrieKeyError,
                exception_tag=ErrorTag.REMOVAL_KEY_NOT_FOUND,
            ),
            TestSpec(
                name="[TR019] trie.remove(TrieId(0)) (TrieKeyError, REMOVAL_KEY_NOT_FOUND)",
                action=trie.remove,
                args=[TrieId(0)],
                exception=TrieKeyError,
                exception_tag=ErrorTag.REMOVAL_KEY_NOT_FOUND,
            ),
            TestSpec(
                name="[TR020] trie.add('qrstuv')",
                action=trie.add,
                args=['qrstuv'],
                expected=TrieId(10),
            ),
            TestSpec(
                name="[TR021] trie.remove(TrieId(10))",
                action=trie.remove,
                args=[TrieId(10)],
                expected=None,
            ),
            TestSpec(
                name="[TR022] len(trie)",
                action=len,
                args=[trie],
                expected=6,
            ),
        ]
        run_tests_list(self, tests)

    def test_str(self) -> None:
        """Test the string representation of GeneralizedTrie.

        This test checks the output of the __str__ method of GeneralizedTrie
        for various string inputs. It verifies that the string representation
        correctly reflects the structure of the trie, including the children,
        parent nodes, and trie IDs.

        The test includes multiple scenarios with different string lengths
        and ensures that the output matches the expected format."""
        trie = GeneralizedTrie()
        test_string = 'a'
        self.assertIsInstance(test_string, TrieKeyToken)
        self.assertIsInstance(test_string, Iterable)

        trie.add(test_string)
        found: str = dedent(str(trie))
        expected: str = dedent("""\
        {
          trie number = 1
          children = {
            'a' = {
              parent = root node
              node token = 'a'
              trie id = TrieId(1)
            }
          }
          trie index = dict_keys([TrieId(1)])
        }""")
        self.assertEqual(found, expected, msg='[TSTR001] str(trie)')

        trie = GeneralizedTrie()
        test_string = 'ab'
        trie.add(test_string)
        found = dedent(str(trie))
        expected = dedent("""\
        {
          trie number = 1
          children = {
            'a' = {
              parent = root node
              node token = 'a'
              children = {
                'b' = {
                  parent = 'a'
                  node token = 'b'
                  trie id = TrieId(1)
                }
              }
            }
          }
          trie index = dict_keys([TrieId(1)])
        }""")
        self.assertEqual(found, expected, msg='[TSTR002] str(trie))')

        trie = GeneralizedTrie()
        test_string = 'abc'
        trie.add(test_string)
        found = dedent(str(trie))
        expected = dedent("""\
        {
          trie number = 1
          children = {
            'a' = {
              parent = root node
              node token = 'a'
              children = {
                'b' = {
                  parent = 'a'
                  node token = 'b'
                  children = {
                    'c' = {
                      parent = 'b'
                      node token = 'c'
                      trie id = TrieId(1)
                    }
                  }
                }
              }
            }
          }
          trie index = dict_keys([TrieId(1)])
        }""")
        self.assertEqual(found, expected, msg='[TSTR003] str(trie))')

    def test_getitem(self) -> None:
        """Test the __getitem__ dunder method of GeneralizedTrie.

        This test checks whether the trie correctly retrieves values for
        existing keys and raises the appropriate errors for non-existing
        keys or invalid key types."""
        trie: GeneralizedTrie = GeneralizedTrie()
        tests: list[TestSpec] = [
            TestSpec(
                name="[TGI001] trie.__getitem__(TrieId(1)) (Empty Trie, TrieKeyError, GETITEM_ID_NOT_FOUND)",
                action=trie.__getitem__,
                args=[TrieId(1)],
                exception=TrieKeyError,
                exception_tag=ErrorTag.GETITEM_ID_NOT_FOUND
            ),
            TestSpec(
                name="[TGI002] trie.add(key='a', value='value')",
                action=trie.add,
                kwargs={"key": "a", "value": "value"},
                expected=TrieId(1)
            ),
            TestSpec(
                name="[TGI003] trie.__getitem__('a') ('a' -> 'value' after add)",
                action=trie.__getitem__,
                args=['a'],
                expected=TrieEntry(ident=TrieId(1), key='a', value='value')
            ),
            TestSpec(
                name="[TGI004] trie.__getitem__('abc') (Non-existent key, TrieKeyError, GETITEM_KEY_NOT_FOUND)",
                action=trie.__getitem__,
                args=['abc'],
                exception=TrieKeyError,
                exception_tag=ErrorTag.GETITEM_KEY_NOT_FOUND
            ),
            TestSpec(
                name="[TGI005] trie.__getitem__(set('a')) (TrieTypeError, GETITEM_INVALID_KEY_TYPE)",
                action=trie.__getitem__,
                args=[set('abc')],
                exception=TrieTypeError,
                exception_tag=ErrorTag.GETITEM_INVALID_KEY_TYPE
            ),
            TestSpec(
                name="[TGI006] trie.add(key='abc', value='another value')",
                action=trie.add,
                kwargs={"key": "abc", "value": "another value"},
                expected=TrieId(2)
            ),
            TestSpec(
                name="[TGI007] trie.__getitem__('ab') (Non-existent key, TrieKeyError, GETITEM_NOT_TERMINAL)",
                action=trie.__getitem__,
                args=['ab'],
                exception=TrieKeyError,
                exception_tag=ErrorTag.GETITEM_NOT_TERMINAL
            ),
        ]
        run_tests_list(self, tests)

    @pytest.mark.order(after='test_add')
    @pytest.mark.dependency(name='test_contains', depends=[
        'test_create_trie', 'test_add'])
    def test_contains(self) -> None:
        """Test the __contains__ dundermethod of GeneralizedTrie.

        This test checks whether the trie correctly identifies the presence
        or absence of various keys. It includes tests for both existing and
        non-existing keys, as well as checks for keys that have been added
        and then removed.

        The test verifies that the __contains__ dunder method returns the expected
        boolean values for each key, ensuring that the trie behaves correctly
        when checking for membership."""
        trie: GeneralizedTrie = GeneralizedTrie()
        tests: list[TestSpec] = [
            TestSpec(
                name="[TC001] trie.__contains__('a') (false)",
                action=trie.__contains__,
                args=['a'],
                expected=False
            ),
            TestSpec(
                name="[TC002] trie.add('a')", action=trie.add, args=["a"], expected=TrieId(1)
            ),
            TestSpec(
                name="[TC003] trie.__contains__('a') (true)",
                action=trie.__contains__,
                args=['a'],
                expected=True
            ),
            TestSpec(
                name="[TC004] trie.remove(TrieId(1))", action=trie.remove, args=[TrieId(1)], expected=None
            ),
            TestSpec(
                name="[TC005] trie.__contains__('a') (false after removal)",
                action=trie.__contains__,
                args=['a'],
                expected=False
            ),
        ]
        run_tests_list(self, tests)

        with self.subTest(msg="[TC006] [1] in trie"):
            self.assertFalse([1] in trie)

        with self.subTest(msg="[TC007] 'a' in trie"):
            trie.add("a")
            self.assertTrue("a" in trie)

        with self.subTest(msg="[TC008] 'abc' in trie"):
            trie.add("abc")
            self.assertTrue("abc" in trie)

        trie = GeneralizedTrie()  # Reset trie for next tests
        test_keys: list[str] = [
            '0123456789ABCDE', '0123456789ABCDF', '0123456789ABCDG', '0123456789ABCDH', '0123456789ABCDI',
            '0123456789ABCDJ', '0123456789ABCDK', '0123456789ABCDL', '0123456789ABCDM', '0123456789ABCDN'
        ]
        for key in test_keys:
            trie[key] = key

        with self.subTest(msg="[TC010] '0123456789ABCDE' in trie"):
            self.assertTrue('0123456789ABCDE' in trie)

    @pytest.mark.order(after='test_remove')
    @pytest.mark.dependency(name='test_keys', depends=[
        'test_create_trie', 'test_add', 'test_contains', 'test_remove'])
    def test_keys(self) -> None:
        """Test the keys method of GeneralizedTrie.

        This test checks the functionality of the keys method, which should
        return an iterable of TrieId objects representing the keys in the trie.

        The test includes scenarios for an empty trie, adding keys, and
        removing keys. It verifies that the keys method returns the expected
        TrieId objects in the correct order."""
        trie: GeneralizedTrie = GeneralizedTrie()

        with self.subTest(msg="[TK001] trie.keys()"):
            expect_id_list: list[TrieId] = []
            found_id_list: list[TrieId] = list(trie.keys())
            self.assertEqual(found_id_list, expect_id_list)

        with self.subTest(msg="[TK002] trie.add('abcdef')"):
            expect_id: TrieId = TrieId(1)
            found_id: TrieId = trie.add("abcdef")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TK003] trie.keys()"):
            expect_id_list: list[TrieId] = [TrieId(1)]
            found_id_list: list[TrieId] = list(trie.keys())
            self.assertEqual(found_id_list, expect_id_list)

        with self.subTest(msg="[TK004] trie.add('abc')"):
            expect_id = TrieId(2)
            found_id = trie.add("abc")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TK005] trie.keys()"):
            expect_id_list = [TrieId(1), TrieId(2)]
            found_id_list = list(sorted(trie.keys()))
            self.assertEqual(found_id_list, expect_id_list)

        with self.assertRaises(TypeError, msg="[TK006] trie.remove('abc')"):
            trie.remove(set('abc'))  # type: ignore[reportGeneralTypeIssues]

        with self.subTest(msg="[TK007] trie.remove(TrieId(1))"):
            trie.remove(TrieId(1))
            expect_id_list = [TrieId(2)]
            found_id_list = list(trie.keys())
            self.assertEqual(found_id_list, expect_id_list)

        with self.subTest(msg="[TK008] trie.remove(TrieId(2))"):
            trie.remove(TrieId(2))
            expect_id_list = []
            found_id_list = list(trie.keys())
            self.assertEqual(found_id_list, expect_id_list)

    @pytest.mark.order(after='test_add')
    @pytest.mark.dependency(name='test_values', depends=['test_create_trie', 'test_trieid_class', 'test_add'])
    def test_values(self) -> None:
        """Test the values method of GeneralizedTrie.

        This test checks the functionality of the values method, which should
        return an iterable of TrieEntry objects representing the values in the trie.
        The test includes scenarios for an empty trie, adding entries, and
        removing entries. It verifies that the values method returns the expected
        TrieEntry objects in the correct order.
        It also checks that the values method behaves correctly when entries are
        added and removed, ensuring that the trie maintains its integrity."""
        trie: GeneralizedTrie = GeneralizedTrie()

        with self.subTest(msg="[TV001] trie.values()"):
            expect_entries_list: list[TrieEntry] = []
            found_entries_list: list[TrieEntry] = list(trie.values())
            self.assertEqual(found_entries_list, expect_entries_list)

        with self.subTest(msg="[TV002] trie.add('abcdef')"):
            expect_id: TrieId = TrieId(1)
            found_id: TrieId = trie.add("abcdef")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TV003] trie.values()"):
            expect_entries_list = [TrieEntry(TrieId(1), 'abcdef')]
            found_entries_list = list(trie.values())
            self.assertEqual(found_entries_list, expect_entries_list)

        with self.subTest(msg="[TV004] trie.add('abc')"):
            expect_id = TrieId(2)
            found_id = trie.add("abc")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TV005] trie.values()"):
            expect_entries_list = [TrieEntry(TrieId(1), 'abcdef'), TrieEntry(TrieId(2), 'abc')]
            found_entries_list = list(sorted(trie.values()))
            self.assertEqual(found_entries_list, expect_entries_list)

        with self.subTest(msg="[TV006] trie.remove(TrieId(1))"):
            trie.remove(TrieId(1))
            expect_entries_list = [TrieEntry(TrieId(2), 'abc')]
            found_entries_list = list(trie.values())
            self.assertEqual(found_entries_list, expect_entries_list)

        with self.subTest(msg="[TV007] trie.remove(TrieId(2))"):
            trie.remove(TrieId(2))
            expect_entries_list = []
            found_entries_list = list(trie.values())
            self.assertEqual(found_entries_list, expect_entries_list)

    def test_items(self) -> None:
        """Test the items method of GeneralizedTrie.

        This test checks the functionality of the items method, which should
        return an iterable of tuples containing TrieId and TrieEntry objects.
        The test includes scenarios for an empty trie, adding entries, and
        removing entries. It verifies that the items method returns the expected
        tuples in the correct order.
        It also checks that the items method behaves correctly when entries are
        added and removed, ensuring that the trie maintains its integrity."""
        trie: GeneralizedTrie = GeneralizedTrie()

        with self.subTest(msg="[TI001] trie.items()"):
            expect_items_list: list[tuple[TrieId, TrieEntry]] = []
            found_items_list: list[tuple[TrieId, TrieEntry]] = list(trie.items())
            self.assertEqual(found_items_list, expect_items_list)

        with self.subTest(msg="[TI002] trie.add('abcdef')"):
            expect_id: TrieId = TrieId(1)
            found_id: TrieId = trie.add("abcdef")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TI003] trie.items()"):
            expect_items_list = [(TrieId(1), TrieEntry(TrieId(1), 'abcdef'))]
            found_items_list = list(sorted(trie.items()))
            self.assertEqual(found_items_list, expect_items_list)

        with self.subTest(msg="[TI004] trie.add('abc')"):
            expect_id = TrieId(2)
            found_id = trie.add("abc")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TI005] trie.items()"):
            expect_items_list = [
                (TrieId(1), TrieEntry(TrieId(1), 'abcdef')),
                (TrieId(2), TrieEntry(TrieId(2), 'abc'))]
            found_items_list = list(sorted(trie.items()))
            self.assertEqual(found_items_list, expect_items_list)

        with self.subTest(msg="[TI006] trie.remove(TrieId(1))"):
            trie.remove(TrieId(1))
            expect_items_list = [(TrieId(2), TrieEntry(TrieId(2), 'abc'))]
            found_items_list = list(sorted(trie.items()))
            self.assertEqual(found_items_list, expect_items_list)

        with self.subTest(msg="[TI007] trie.remove(TrieId(2))"):
            trie.remove(TrieId(2))
            expect_items_list = []
            found_items_list = list(sorted(trie.items()))
            self.assertEqual(found_items_list, expect_items_list)

    @pytest.mark.order(after='test_remove')
    @pytest.mark.dependency(name="test_getitem_dunder", depends=[
        'test_create_trie', 'test_add',
        'test_remove', 'test_trieid_class'])
    def test_getitem_dunder(self) -> None:
        """Test the __getitem__ method of GeneralizedTrie.

        This test checks the functionality of the __getitem__ method, which should
        allow access to TrieEntry objects by their TrieId. The test includes scenarios
        for an empty trie, adding entries, and accessing entries by their IDs.
        It verifies that the __getitem__ method returns the expected TrieEntry objects
        and raises KeyError when trying to access non-existing IDs.
        It also checks that the method behaves correctly when entries are added and
        accessed, ensuring that the trie maintains its integrity."""
        trie: GeneralizedTrie = GeneralizedTrie()

        with self.assertRaises(KeyError, msg="[TGID001] trie[TrieId(1)]"):
            _ = trie[TrieId(1)]

        with self.subTest(msg="[TGID002] trie.add('abcdef')"):
            expect_id: TrieId = TrieId(1)
            found_id: TrieId = trie.add("abcdef")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TGID003] trie[TrieId(1)]"):
            expect_entry: TrieEntry = TrieEntry(TrieId(1), 'abcdef')
            found_entry: TrieEntry = trie[TrieId(1)]
            self.assertEqual(found_entry, expect_entry)

        with self.subTest(msg="[TGID004] trie.add('abc')"):
            expect_id = TrieId(2)
            found_id = trie.add("abc")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TGID005] trie[TrieId(2)]"):
            expect_entry = TrieEntry(TrieId(2), 'abc')
            found_entry = trie[TrieId(2)]
            self.assertEqual(found_entry, expect_entry)

        with self.assertRaises(KeyError, msg="[TGID006] trie[TrieId(3)]"):
            _ = trie[TrieId(3)]

    def test_iter(self) -> None:
        """Test the iteration over GeneralizedTrie."""
        trie: GeneralizedTrie = GeneralizedTrie()

        with self.subTest(msg="[TITER001] for entry in trie:"):
            expect_ids_list: list[TrieId] = []
            found_ids_list: list[TrieId] = []
            for entry in trie:
                found_ids_list.append(entry)
            self.assertEqual(found_ids_list, expect_ids_list)

        with self.subTest(msg="[TITER002] trie.add('abcdef')"):
            expect_id: TrieId = TrieId(1)
            found_id: TrieId = trie.add("abcdef")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TITER003] for ident in trie:"):
            expect_ids_list = [TrieId(1)]
            found_ids_list = []
            for ident in trie:
                found_ids_list.append(ident)
            self.assertEqual(sorted(found_ids_list), expect_ids_list)

        with self.subTest(msg="[TITER004] trie.add('abc')"):
            expect_id = TrieId(2)
            found_id = trie.add("abc")
            self.assertEqual(found_id, expect_id)

        with self.subTest(msg="[TITER005] for entry in trie:"):
            expect_ids_list: list[TrieId] = [TrieId(1), TrieId(2)]
            found_ids_list: list[TrieId] = []
            for entry in trie:
                found_ids_list.append(entry)
            self.assertEqual(sorted(found_ids_list), expect_ids_list)

    @pytest.mark.order(after='test_remove')
    @pytest.mark.dependency(name='test_bool', depends=[
        'test_create_trie', 'test_add',
        'test_remove'])
    def test_bool(self) -> None:
        """Test the __bool__ method of GeneralizedTrie.

        This test checks the functionality of the __bool__ method, which should
        return True if the trie contains any entries, and False if it is empty.
        The test includes scenarios for an empty trie, adding entries, and removing
        entries. It verifies that the __bool__ method returns the expected boolean
        values for each scenario, ensuring that the trie behaves correctly when
        checking its truthiness."""
        trie = GeneralizedTrie()
        tests: list[TestSpec] = [
            TestSpec(
                name="[TB001] bool(trie)", action=bool, args=[trie], expected=False
            ),
            TestSpec(
                name="[TB002] trie.add('a')", action=trie.add, args=["a"], expected=TrieId(1)
            ),
            TestSpec(
                name="[TB003] bool(trie)", action=bool, args=[trie], expected=True
            ),
            TestSpec(
                name="[TB004] trie.remove(TrieId(1))", action=trie.remove, args=[TrieId(1)], expected=None
            ),
            TestSpec(
                name="[TB005] bool(trie)", action=bool, args=[trie], expected=False
            ),
        ]
        run_tests_list(self, tests)


if __name__ == "__main__":
    unittest.main()
