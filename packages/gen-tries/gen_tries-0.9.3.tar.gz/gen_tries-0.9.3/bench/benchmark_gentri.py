#!env python3
# -*- coding: utf-8 -*-
'''
Benchmark for the Generalized Trie implementation.
This script runs a series of tests to measure the performance of the Generalized Trie
against a set of predefined test cases.
'''
# pylint: disable=wrong-import-position, too-many-instance-attributes
# pylint: disable=too-many-positional-arguments, too-many-arguments, too-many-locals

from dataclasses import dataclass
import gc
import itertools
import time
from typing import Any, Callable, NamedTuple, Sequence


import sys
from pathlib import Path
sys.path.insert(0, str(Path('../src').resolve()))

from gentrie import GeneralizedTrie, GeneralizedKey  # noqa: E402


SYMBOLS: str = '0123'  # Define the symbols for the trie


def generate_test_data(depth: int, symbols: str, max_keys: int) -> list[str]:
    '''Generate test data for the Generalized Trie.

    Args:
        depth (int): The depth of the keys to generate.
        symbols (str): The symbols to use in the keys.
        max_keys (int): The maximum number of keys to generate.'''
    test_data: list[str] = []
    for key in itertools.product(symbols, repeat=depth):
        key_string = ''.join(key)
        test_data.append(key_string)
        if len(test_data) >= max_keys:
            break
    return test_data


def generate_test_trie(depth: int, symbols: str, max_keys: int) -> GeneralizedTrie:
    '''Generate a test Generalized Trie for the given depth and symbols.'''
    test_data = generate_test_data(depth, symbols, max_keys)
    trie = GeneralizedTrie(runtime_validation=False)
    for key in test_data:
        trie[key] = key  # Assign the key to itself
    return trie


class BenchCase(NamedTuple):
    '''Declaration of a benchmark case.

    kwargs_variations are used to describe the variations in keyword arguments for the benchmark.
    All combinations of these variations will be tested.

    Args:
        name (str): The name of the benchmark case.
        description (str): A brief description of the benchmark case.
        action (Callable[..., Any]): The action to perform for the benchmark.
        kwargs_variations (dict[str, list[Any]]): Variations of keyword arguments for the benchmark.
    '''
    name: str
    description: str
    action: Callable[..., Any]
    kwargs_variations: dict[str, list[Any]] = {}


@dataclass
class BenchResults:
    '''Container for the results of a single benchmark test.'''
    name: str
    description: str
    elapsed: int
    n: int
    iterations: int
    per_second: float
    depth: int
    runtime_validation: bool


def null_function() -> None:
    '''A no-op function to simulate work in benchmarks.'''


def benchmark_null_loop(name: str,
                        description: str,
                        iterations: int = 10,
                        size: int = 10_000_000) -> Sequence[BenchResults]:
    '''Benchmark a null loop (no-op function).'''
    elapsed: int = 0
    for _ in range(iterations):
        gc.collect()
        timer_start = time.process_time_ns()
        for _ in range(size):
            null_function()  # A no-op function to simulate work
        timer_end = time.process_time_ns()
        elapsed += (timer_end - timer_start)
    return [BenchResults(
        name=name,
        description=description,
        elapsed=elapsed,
        n=size,
        iterations=iterations,
        per_second=float(iterations * size / (elapsed / 1e9)),
        depth=0,  # Depth is not applicable for a null loop,
        runtime_validation=False  # Validation is not applicable for a null loop
    )]


def benchmark_build_with_add(
                name: str,
                description: str,
                runtime_validation: bool,
                test_data: Sequence[GeneralizedKey],
                iterations: int,
                depth: int) -> Sequence[BenchResults]:
    '''Benchmark the addition of keys to the trie.

    Args:
        name (str): The name of the benchmark case.
        description (str): A brief description of the benchmark case.
        runtime_validation (bool): Whether to enable runtime validation.
        test_data (Sequence[GeneralizedKey]): The test data to use for the benchmark.
        iterations (int): The number of iterations to run the benchmark.
        depth (int): The depth of the trie.

    Returns:
        A list of BenchResults containing the benchmark results.
    '''
    n: int = len(test_data)
    elapsed: int = 0
    for iteration_pass in range(iterations + 1):
        gc.collect()
        trie = GeneralizedTrie(runtime_validation=runtime_validation)
        timer_start = time.process_time_ns()
        for key in test_data:
            trie.add(key)
        timer_end = time.process_time_ns()
        elapsed += (timer_end - timer_start)
        if iteration_pass == 0:
            # Warmup iteration, not included in final stats
            elapsed = 0
    formatted_name = name.format(runtime_validation=runtime_validation, depth=depth, n=n)
    formatted_description = description.format(runtime_validation=runtime_validation, depth=depth, n=n)
    return [BenchResults(
        name=formatted_name,
        description=formatted_description,
        elapsed=elapsed,
        n=n,
        iterations=iterations,
        per_second=n * iterations / (elapsed / 1e9),
        depth=depth,
        runtime_validation=runtime_validation)
    ]


def benchmark_build_with_assign(
        name: str,
        description: str,
        runtime_validation: bool,
        test_data: Sequence[GeneralizedKey],
        iterations: int,
        depth: int) -> Sequence[BenchResults]:
    '''Benchmark the assignment of keys to the trie.

    Args:
        name (str): The name of the benchmark case.
        description (str): A brief description of the benchmark case.
        runtime_validation (bool): Whether to enable runtime validation.
        test_data (Sequence[GeneralizedKey]): The test data to use for the benchmark.
        iterations (int): The number of iterations to run the benchmark.
        depth (int): The depth of the trie.

    Returns:
        A list of BenchResults containing the benchmark results.
    '''
    n: int = len(test_data)
    elapsed: int = 0
    for iteration_pass in range(iterations + 1):
        gc.collect()
        trie = GeneralizedTrie(runtime_validation=runtime_validation)
        timer_start = time.process_time_ns()
        for key in test_data:
            trie[key] = key  # Assign the key to itself
        timer_end = time.process_time_ns()
        elapsed += (timer_end - timer_start)
        if iteration_pass == 0:
            # Warmup iteration, not included in final stats
            elapsed = 0
    formatted_name = name.format(runtime_validation=runtime_validation, depth=depth, n=n)
    formatted_description = description.format(runtime_validation=runtime_validation, depth=depth, n=n)
    return [BenchResults(
        name=formatted_name,
        description=formatted_description,
        elapsed=elapsed,
        n=n,
        iterations=iterations,
        per_second=n * iterations / (elapsed / 1e9),
        depth=depth,
        runtime_validation=runtime_validation)
    ]


def benchmark_build_with_update(name: str,
                                description: str,
                                runtime_validation: bool,
                                test_data: Sequence[GeneralizedKey],
                                iterations: int = 10,
                                depth: int = 3) -> Sequence[BenchResults]:
    '''Benchmark building a trie using update().

    Args:
        name (str): The name of the benchmark case.
        description (str): A brief description of the benchmark case.
        runtime_validation (bool): Whether to enable runtime validation.
        test_data (Sequence[GeneralizedKey]): The test data to use for the benchmark.
        iterations (int): The number of iterations to run the benchmark.
        depth (int): The depth of the trie.

    Returns:
        A list of BenchResults containing the benchmark results.
    '''
    n: int = len(test_data)
    elapsed: int = 0
    for iteration_pass in range(iterations + 1):
        gc.collect()
        trie = GeneralizedTrie(runtime_validation=runtime_validation)
        timer_start = time.process_time_ns()
        for key in test_data:
            trie.update(key, value=key)  # Update the key with itself as value
        timer_end = time.process_time_ns()
        elapsed += (timer_end - timer_start)
        if iteration_pass == 0:
            # Warmup iteration, not included in final stats
            elapsed = 0
    formatted_name = name.format(runtime_validation=runtime_validation, depth=depth, n=n)
    formatted_description = description.format(runtime_validation=runtime_validation, depth=depth, n=n)
    return [BenchResults(
        name=formatted_name,
        description=formatted_description,
        elapsed=elapsed,
        n=n,
        iterations=iterations,
        per_second=n * iterations / (elapsed / 1e9),
        depth=depth,
        runtime_validation=runtime_validation)
    ]


def benchmark_updating_trie(
        name: str,
        description: str,
        runtime_validation: bool,
        test_data: Sequence[GeneralizedKey],
        iterations: int = 10,
        depth: int = 3) -> Sequence[BenchResults]:
    '''Benchmark the update operation on the trie.

    Args:
        name (str): The name of the benchmark case.
        description (str): A brief description of the benchmark case.
        runtime_validation (bool): Whether to enable runtime validation.
        test_data (Sequence[GeneralizedKey]): The test data to use for the benchmark.
        iterations (int): The number of iterations to run the benchmark.
        depth (int): The depth of the trie.

    Returns:
        A list of BenchResults containing the benchmark results.
    '''
    n: int = len(test_data)
    elapsed: int = 0

    # Build the prefix tree
    trie = GeneralizedTrie()
    for key in test_data:
        trie.add(key, value=None)

    trie.runtime_validation = runtime_validation

    # Benchmark the update operation
    for iteration_pass in range(iterations + 1):
        gc.collect()
        timer_start = time.process_time_ns()
        for key in test_data:
            trie.update(key, value=iteration_pass)
        timer_end = time.process_time_ns()
        elapsed += (timer_end - timer_start)
        if iteration_pass == 0:
            # Warmup iteration, not included in final stats
            elapsed = 0
    formatted_name = name.format(runtime_validation=runtime_validation, depth=depth, n=n)
    formatted_description = description.format(runtime_validation=runtime_validation, depth=depth, n=n)
    return [BenchResults(
        name=formatted_name,
        description=formatted_description,
        elapsed=elapsed,
        n=n,
        iterations=iterations,
        per_second=n * iterations / (elapsed / 1e9),
        depth=depth,
        runtime_validation=runtime_validation)
    ]


def benchmark_key_in_trie(
        name: str,
        description: str,
        runtime_validation: bool = True,
        iterations: int = 10,
        depth: int = 3,
        symbols: str = SYMBOLS,
        max_keys: int = 1_000_000) -> Sequence[BenchResults]:
    '''Benchmark using keys with the in operator for GeneralizedTrie.

    Args:
        name (str): The name of the benchmark case.
        description (str): A brief description of the benchmark case.
        runtime_validation (bool): Whether to enable runtime validation.
        iterations (int): The number of iterations to run the benchmark.
        depth (int): The depth of the trie.
        symbols (str): The set of symbols to use for generating test data.
        max_keys (int): The maximum number of keys to generate.

    Returns:
        A list of BenchResults containing the benchmark results.
    '''
    elapsed: int = 0
    trie = generate_test_trie(depth, symbols, max_keys)
    trie.runtime_validation = runtime_validation
    trie_keys: list[GeneralizedKey] = list(entry.key for entry in trie.values())
    n: int = len(trie_keys)
    key: GeneralizedKey
    for iteration_pass in range(iterations + 1):
        gc.collect()
        timer_start = time.process_time_ns()
        for key in trie_keys:
            if key in trie:
                pass  # Just checking membership
            else:
                raise KeyError(f'Key {key} not found in trie')
        timer_end = time.process_time_ns()
        elapsed += (timer_end - timer_start)
        if iteration_pass == 0:
            # Warmup iteration, not included in final stats
            elapsed = 0

    formatted_name = name.format(runtime_validation=runtime_validation)
    formatted_description = description.format(runtime_validation=runtime_validation)
    return [BenchResults(
        name=formatted_name,
        description=formatted_description,
        elapsed=elapsed,
        n=n,
        iterations=iterations,
        per_second=n * iterations / (elapsed / 1e9),
        depth=depth,
        runtime_validation=runtime_validation
    )]


def generate_kwargs_variations(kwargs_variations: dict[str, list[Any]]) -> list[dict[str, Any]]:
    '''Generate all combinations of keyword arguments from the given variations.

    Args:
        kwargs_variations: A dictionary where each key is a parameter name and the
            value is a list of possible values for that parameter.

    Returns:
        A list of dictionaries, each representing a unique combination of keyword arguments.
    '''
    keys = kwargs_variations.keys()
    values = [kwargs_variations[key] for key in keys]
    return [dict(zip(keys, v)) for v in itertools.product(*values)]


if __name__ == '__main__':
    default_depth: int = 15  # Default depth for test data generation
    default_max_keys: int = 10_000_000  # Default maximum number of keys to generate
    default_iterations: int = 1  # Number of iterations for each test case
    default_size: int = 10_000_000  # Number of elements for the tests
    default_test_data = generate_test_data(default_depth, SYMBOLS, default_max_keys)

    benchmark_cases: list[BenchCase] = [
        BenchCase(
            name='null_loop',
            description='Benchmarking a null_loop',
            action=benchmark_null_loop,
            kwargs_variations={
                'iterations': [default_iterations],
                'size': [default_size]}
        ),
        BenchCase(
            name='key in trie (runtime validation: {runtime_validation})',
            description='Benchmarking key lookup in trie using the in operator',
            action=benchmark_key_in_trie,
            kwargs_variations={
                'runtime_validation': [False, True],
                'iterations': [default_iterations],
                'depth': [default_depth],
                'symbols': [SYMBOLS],
                'max_keys': [default_max_keys]}
        ),
        BenchCase(
            name='trie build with add() (runtime validation: {runtime_validation})',
            description='Benchmarking building a trie using the add() method',
            action=benchmark_build_with_add,
            kwargs_variations={
                'runtime_validation': [False, True],
                'test_data': [default_test_data],
                'iterations': [default_iterations],
                'depth': [default_depth]},
        ),
        BenchCase(
            name='trie build using update() method (runtime validation: {runtime_validation})',
            description='Benchmarking building a trie using the update() method',
            action=benchmark_build_with_update,
            kwargs_variations={
                'runtime_validation': [False, True],
                'test_data': [default_test_data],
                'iterations': [default_iterations],
                'depth': [default_depth]},
        ),
        BenchCase(
            name='trie build with trie[key] = key (runtime validation: {runtime_validation})',
            description='Benchmarking building a trie using trie[key] = key assignment',
            action=benchmark_build_with_assign,
            kwargs_variations={
                'runtime_validation': [False, True],
                'test_data': [default_test_data],
                'iterations': [default_iterations],
                'depth': [default_depth]},
        ),
        BenchCase(
            name='trie updating with update() method (runtime validation: {runtime_validation})',
            description='Benchmarking updating a trie using the update() method',
            action=benchmark_updating_trie,
            kwargs_variations={
                'runtime_validation': [False, True],
                'test_data': [default_test_data],
                'iterations': [default_iterations],
                'depth': [default_depth]},
        ),
    ]

    all_results: list[BenchResults] = []
    for case in benchmark_cases:
        for kwargs in generate_kwargs_variations(case.kwargs_variations):
            results: list[BenchResults] = case.action(name=case.name,
                                                      description=case.description,
                                                      **kwargs)
            all_results.extend(results)

    # Display the results
    for result in all_results:
        # Print the results for each test case
        print('=' * 40)
        print(f'{result.name}: {result.description}')
        print(f'  Key depth: {result.depth}')
        print(f'  Data size: {result.n}, Iterations: {result.iterations}')
        print(f'  Elapsed time: {result.elapsed / 1e9:.2f} seconds')
        print(f'  Operations per second: {result.per_second:.0f}\n')
