"""TestSpec testing framework."""

from collections.abc import Callable
from enum import Enum
import traceback
from typing import Any, NamedTuple, Optional, Sequence
import unittest


# Sentinel value used to indicate that no expected value is set
NO_EXPECTED_VALUE = object()
"""
A sentinel value used to indicate that no expected value is set.
"""


class TestSpec(NamedTuple):
    """A generic unit test specification class.

    It allow tests to be specified declaratively while providing a large amount
    of flexibility.

    Args:
        name (str):
            Identifying name for the test.
        action (Callable[..., Any]):
            A reference to a callable function or method to be invoked for the test.
        args (Sequence[Any], default = []):
            Sequence of positional arguments to be passed to the `action` function or method.
        kwargs (dict[str, Any], default = {}):
            Dictionary containing keyword arguments to be passed to the `action` function or method.
        expected (Any, default=NO_EXPECTED_VALUE ):
            Expected value (if any) that is expected to be returned by the `action` function or method.
            If there is no expected value, the special class NoExpectedValue is used to flag it.
            This is used so that the specific return value of None can be distinguished from no
            particular value or any value at all is expected to be returned from the function or method.
        obj: Optional[Any] = None
        validate_obj: Optional[Callable[[Any], bool]] = None
        validate_result: Optional[Callable[[Any], bool]] = None
        exception: Optional[type[Exception]] = None
        exception_tag: Optional[str] = None
        display_on_fail: Optional[Callable[[], str]] = None
    """
    name: str
    action: Callable[..., Any]
    args: Optional[list[Any]] = None
    kwargs: Optional[dict[str, Any]] = None
    expected: Any = NO_EXPECTED_VALUE
    obj: Optional[Any] = None
    validate_obj: Optional[Callable[[Any], bool]] = None
    validate_result: Optional[Callable[[Any], bool]] = None
    exception: Optional[type[Exception]] = None
    exception_tag: Optional[str | Enum] = None
    display_on_fail: Optional[Callable[[], str]] = None


def run_tests_list(test_case: unittest.TestCase, test_specs: Sequence[TestSpec]) -> None:
    """Run a list of tests based on the provided TestSpec entries.

    This function iterates over the list of TestSpec entries and runs each test using
    the `run_test` function. It allows for a clean and organized way to execute multiple tests.

    Args:
        test_case (unittest.TestCase): The test case instance that will run the tests.
        test_specs (list[TestSpec]): A list of TestSpec entries, each representing a test to be run.
    """
    for spec in test_specs:
        run_test(test_case, spec)


def run_test(test_case: unittest.TestCase, spec: TestSpec) -> None:  # pylint: disable=too-many-branches
    """Run a single test based on the provided TestSpec entry.
    This function executes the action specified in the entry, checks the result against
    the expected value, and reports any errors.

    Args:
        test_case (unittest.TestCase): The test case instance that will run the test.
        spec (TestSpec): The test configuration entry containing all necessary information for the test.
    """
    with test_case.subTest(msg=spec.name):
        test_description: str = f"{spec.name}"
        errors: list[str] = []
        try:
            # Use empty list/dict if the spec field is None
            pos_args = spec.args if spec.args is not None else []
            kw_args = spec.kwargs if spec.kwargs is not None else {}
            found: Any = spec.action(*pos_args, **kw_args)
            if spec.exception:
                errors.append("returned result instead of raising exception")

            else:
                if spec.validate_result and not spec.validate_result(found):
                    errors.append(f"failed result validation: found={found}")
                if spec.validate_obj and not spec.validate_obj(spec.obj):
                    errors.append(f"failed object validation: obj={spec.obj}")
                if spec.expected is not NO_EXPECTED_VALUE and spec.expected != found:
                    errors.append(f"expected={spec.expected}, found={found}")
                    if isinstance(spec.display_on_fail, Callable):
                        errors.append(spec.display_on_fail())
        except Exception as err:  # pylint: disable=broad-exception-caught
            if spec.exception is None:
                errors.append(f"Did not expect exception. Caught exception {repr(err)}")
                errors.append("stacktrace = ")
                errors.append("\n".join(traceback.format_tb(tb=err.__traceback__)))

            elif not isinstance(err, spec.exception):
                errors.append(
                    f"Unexpected exception type: expected={spec.exception}, "
                    f"found = {type(err)}"
                )
            elif spec.exception_tag:
                # Case 1: The expected tag is an Enum member.
                # This requires the exception object to have a 'tag_code' attribute.
                if isinstance(spec.exception_tag, Enum):
                    if not hasattr(err, 'tag_code'):
                        errors.append(
                            "Exception is missing the 'tag_code' attribute required for Enum tag validation.")
                    else:
                        actual_tag = getattr(err, 'tag_code')
                        if actual_tag != spec.exception_tag:
                            errors.append(f"Unexpected exception tag: expected={spec.exception_tag}, "
                                          f"found={actual_tag}")
                # Case 2: The expected tag is a string.
                # This performs a substring search in the exception's string representation.
                else:
                    if str(spec.exception_tag) not in str(err):
                        errors.append(
                            f"Correct exception type, but tag '{spec.exception_tag}' "
                            f"not found in exception message: {repr(err)}"
                        )
        if errors:
            test_case.fail(msg=test_description + ": " + "\n".join(errors))
