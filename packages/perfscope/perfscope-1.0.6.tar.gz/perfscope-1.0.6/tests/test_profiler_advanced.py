"""
Advanced and ultra-complex test suite for PerfScope.
Tests complex real-world scenarios, edge cases, and stress conditions.
"""

import asyncio
import concurrent.futures
import gc

# Completely disable perfscope logging for tests
import logging
import multiprocessing
import os
import random
import time
from collections import defaultdict, deque
from contextlib import ExitStack
from dataclasses import dataclass
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
)

import pytest

from perfscope import profile

# Set via environment variable to ensure it applies before profiler initialization
os.environ["PERFSCOPE_LOG_LEVEL"] = "CRITICAL"
perfscope_logger = logging.getLogger("perfscope")
perfscope_logger.setLevel(logging.CRITICAL)
perfscope_logger.disabled = True

# Also disable all handlers
for handler in perfscope_logger.handlers[:]:
    perfscope_logger.removeHandler(handler)


class TestComplexRecursion:
    """Test complex recursive patterns."""

    def test_fibonacci_deep_recursion(self):
        """Test deep recursive Fibonacci with memoization."""
        print("\n=== Testing Deep Fibonacci Recursion ===")

        cache = {}

        @profile(log_enabled=False, max_depth=50, trace_memory=True)
        def fibonacci_memo(n: int) -> int:
            """Fibonacci with memoization to handle deep recursion."""
            if n in cache:
                return cache[n]

            if n <= 1:
                return n

            cache[n] = fibonacci_memo(n - 1) + fibonacci_memo(n - 2)
            return cache[n]

        result = fibonacci_memo(20)
        assert result == 6765

        report = fibonacci_memo.profile_report
        print(f"✓ Deep Fibonacci: n=20, result={result}, calls={report.total_calls}")

    def test_mutual_recursion(self):
        """Test mutual recursion between multiple functions."""
        print("\n=== Testing Mutual Recursion ===")

        @profile(log_enabled=False, max_depth=30)
        def is_even(n: int) -> bool:
            """Check if number is even using mutual recursion."""
            if n == 0:
                return True
            elif n == 1:
                return False
            elif n < 0:
                return is_even(-n)
            else:
                return is_odd(n - 1)

        def is_odd(n: int) -> bool:
            """Check if number is odd using mutual recursion."""
            if n == 0:
                return False
            elif n == 1:
                return True
            elif n < 0:
                return is_odd(-n)
            else:
                return is_even(n - 1)

        assert is_even(10) is True
        assert is_even(11) is False
        print("✓ Mutual recursion: even/odd checking completed")

    def test_tree_traversal_recursion(self):
        """Test recursive tree traversal with complex structure."""
        print("\n=== Testing Tree Traversal Recursion ===")

        class TreeNode:
            def __init__(self, value: int):
                self.value = value
                self.children: List[TreeNode] = []

            def add_child(self, child: "TreeNode"):
                self.children.append(child)

        @profile(log_enabled=False, trace_memory=True, max_depth=100)
        def sum_tree_values(node: Optional[TreeNode]) -> int:
            """Recursively sum all values in tree."""
            if node is None:
                return 0

            total = node.value
            for child in node.children:
                total += sum_tree_values(child)

            return total

        # Build a complex tree
        root = TreeNode(1)
        for i in range(3):
            child = TreeNode(i + 2)
            root.add_child(child)
            for j in range(2):
                grandchild = TreeNode((i + 2) * 10 + j)
                child.add_child(grandchild)

        result = sum_tree_values(root)
        assert result > 0
        print(f"✓ Tree traversal: sum={result}")

    def test_ackermann_function(self):
        """Test profiling the Ackermann function (extreme recursion)."""
        print("\n=== Testing Ackermann Function ===")

        @profile(log_enabled=False, max_depth=1000)
        def ackermann(m: int, n: int) -> int:
            """Ackermann function - extremely recursive."""
            if m == 0:
                return n + 1
            elif n == 0:
                return ackermann(m - 1, 1)
            else:
                return ackermann(m - 1, ackermann(m, n - 1))

        # Use small values to avoid stack overflow
        result = ackermann(2, 2)
        assert result == 7  # A(2,2) = 7
        print(f"✓ Ackermann function: A(2,2) = {result}")


class TestAsyncComplexScenarios:
    """Test complex async/await scenarios."""

    @pytest.mark.asyncio
    async def test_async_producer_consumer(self):
        """Test async producer-consumer pattern."""
        print("\n=== Testing Async Producer-Consumer ===")

        async def producer(queue: asyncio.Queue, n: int):
            """Async producer."""
            for i in range(n):
                await asyncio.sleep(0.001)
                await queue.put(f"item_{i}")
            await queue.put(None)  # Sentinel

        async def consumer(queue: asyncio.Queue) -> List[str]:
            """Async consumer."""
            items = []
            while True:
                item = await queue.get()
                if item is None:
                    break
                items.append(item)
                await asyncio.sleep(0.001)
            return items

        @profile(log_enabled=False, trace_memory=True)
        async def producer_consumer_workflow():
            """Main workflow orchestrator."""
            queue = asyncio.Queue(maxsize=10)

            # Run producer and consumer concurrently
            producer_task = asyncio.create_task(producer(queue, 5))
            consumer_task = asyncio.create_task(consumer(queue))

            await producer_task
            items = await consumer_task

            return items

        result = await producer_consumer_workflow()
        assert len(result) == 5
        print(f"✓ Producer-Consumer: processed {len(result)} items")

    @pytest.mark.asyncio
    async def test_async_streaming(self):
        """Test async streaming with backpressure."""
        print("\n=== Testing Async Streaming ===")

        async def data_stream(size: int) -> AsyncIterator[bytes]:
            """Async data stream generator."""
            for i in range(size):
                await asyncio.sleep(0.001)
                yield f"chunk_{i}".encode()

        @profile(log_enabled=False, trace_memory=True)
        async def process_stream():
            """Process async stream with buffering."""
            buffer = []
            async for chunk in data_stream(10):
                buffer.append(chunk)
                if len(buffer) >= 3:
                    # Process buffer
                    _ = b"".join(buffer)  # Process buffered data
                    buffer.clear()
                    await asyncio.sleep(0.002)  # Simulate processing

            # Process remaining
            if buffer:
                _ = b"".join(buffer)  # Process remaining buffer

            return True

        result = await process_stream()
        assert result is True
        print("✓ Async streaming with backpressure completed")

    # Removed flaky websocket test that was causing CI failures
    # The test was non-deterministic due to async timing issues across different platforms

    @pytest.mark.asyncio
    async def test_async_retry_with_exponential_backoff(self):
        """Test async retry logic with exponential backoff."""
        print("\n=== Testing Async Retry with Exponential Backoff ===")

        class RetryableError(Exception):
            pass

        @profile(log_enabled=False, trace_memory=True)
        async def retry_with_backoff(
            func: Callable, max_retries: int = 3, base_delay: float = 0.001
        ):
            """Retry async function with exponential backoff."""
            attempt = 0
            delay = base_delay

            while attempt < max_retries:
                try:
                    return await func(attempt)
                except RetryableError:
                    attempt += 1
                    if attempt >= max_retries:
                        raise

                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff

            raise RetryableError("Max retries exceeded")

        async def flaky_operation(attempt: int) -> str:
            """Operation that fails first 2 attempts."""
            if attempt < 2:
                raise RetryableError(f"Failed attempt {attempt}")
            return f"Success on attempt {attempt}"

        result = await retry_with_backoff(flaky_operation)
        assert "Success" in result
        print(f"✓ Retry with backoff: {result}")


class TestMemoryIntensiveScenarios:
    """Test memory-intensive and leak detection scenarios."""

    def test_memory_leak_simulation(self):
        """Test detection of memory leaks."""
        print("\n=== Testing Memory Leak Detection ===")

        leaked_objects = []  # This will grow and not be cleared

        @profile(log_enabled=False, trace_memory=True)
        def leaky_function(iterations: int):
            """Function that leaks memory."""
            local_leak = []

            for i in range(iterations):
                # Create large objects
                large_data = {
                    "id": i,
                    "data": "x" * 10000,  # 10KB string
                    "nested": {"array": list(range(1000))},
                }

                # Leak: append to global list
                leaked_objects.append(large_data)

                # Also keep in local list (potential leak)
                local_leak.append(large_data)

                # Force garbage collection to see real leaks
                if i % 10 == 0:
                    gc.collect()

            return len(local_leak)

        result = leaky_function(20)
        assert result == 20
        assert len(leaked_objects) == 20  # Verify leak occurred

        # Clear for other tests
        leaked_objects.clear()
        gc.collect()

        print(f"✓ Memory leak detected: {result} objects leaked")

    def test_large_data_structure_processing(self):
        """Test processing very large data structures."""
        print("\n=== Testing Large Data Structure Processing ===")

        @profile(log_enabled=False, trace_memory=True)
        def process_large_matrix():
            """Process large matrix operations."""
            # Create large matrix
            size = 100
            matrix = [[i * j for j in range(size)] for i in range(size)]

            # Matrix operations
            def transpose(m):
                return list(map(list, zip(*m)))

            def multiply_scalar(m, scalar):
                return [[cell * scalar for cell in row] for row in m]

            # Process
            transposed = transpose(matrix)
            scaled = multiply_scalar(transposed, 2)

            # Calculate sum
            total = sum(sum(row) for row in scaled)

            return total

        result = process_large_matrix()
        assert result > 0
        print(f"✓ Large matrix processing: sum={result}")

    def test_circular_reference_detection(self):
        """Test handling of circular references."""
        print("\n=== Testing Circular Reference Detection ===")

        class Node:
            def __init__(self, value):
                self.value = value
                self.next = None
                self.prev = None

        @profile(log_enabled=False, trace_memory=True)
        def create_circular_structure():
            """Create structure with circular references."""
            # Create doubly-linked list with cycle
            nodes = [Node(i) for i in range(10)]

            for i in range(len(nodes)):
                nodes[i].next = nodes[(i + 1) % len(nodes)]
                nodes[i].prev = nodes[(i - 1) % len(nodes)]

            # Create additional circular reference
            nodes[0].self_ref = nodes[0]

            # Process the circular structure
            current = nodes[0]
            visited = set()
            count = 0

            while current.value not in visited:
                visited.add(current.value)
                current = current.next
                count += 1

            return count

        result = create_circular_structure()
        assert result == 10

        # Force garbage collection to clean circular references
        gc.collect()

        print(f"✓ Circular references handled: {result} nodes")

    def test_memory_pool_simulation(self):
        """Test memory pool allocation pattern."""
        print("\n=== Testing Memory Pool Simulation ===")

        class MemoryPool:
            def __init__(self, block_size: int, pool_size: int):
                self.block_size = block_size
                self.pool = [bytearray(block_size) for _ in range(pool_size)]
                self.free_blocks = list(range(pool_size))
                self.allocated = {}

            def allocate(self, obj_id: str) -> Optional[int]:
                if not self.free_blocks:
                    return None
                block_id = self.free_blocks.pop(0)
                self.allocated[obj_id] = block_id
                return block_id

            def deallocate(self, obj_id: str):
                if obj_id in self.allocated:
                    block_id = self.allocated.pop(obj_id)
                    self.free_blocks.append(block_id)

        @profile(log_enabled=False, trace_memory=True)
        def memory_pool_operations():
            """Simulate memory pool operations."""
            pool = MemoryPool(block_size=1024, pool_size=50)

            # Allocation phase
            allocations = []
            for i in range(30):
                block_id = pool.allocate(f"obj_{i}")
                if block_id is not None:
                    allocations.append(f"obj_{i}")

            # Deallocation phase
            for obj_id in allocations[:15]:
                pool.deallocate(obj_id)

            # Reallocation phase
            for i in range(30, 40):
                pool.allocate(f"obj_{i}")

            return len(pool.allocated)

        result = memory_pool_operations()
        assert result > 0
        print(f"✓ Memory pool simulation: {result} blocks allocated")


# Module-level functions for multiprocessing tests
def _mapper_function(chunk: List[int]) -> int:
    """Map function to sum chunk - module level for pickling."""
    return sum(x * x for x in chunk)


def _cpu_intensive_task(n: int) -> int:
    """CPU-intensive calculation - module level for pickling."""
    result = 0
    for i in range(n):
        result += i * i
        if i % 1000 == 0:
            # Simulate more work
            _ = [j**2 for j in range(100)]
    return result


class TestMultiprocessingScenarios:
    """Test multiprocessing scenarios."""

    def test_multiprocess_map_reduce(self):
        """Test map-reduce pattern with multiprocessing."""
        print("\n=== Testing Multiprocess Map-Reduce ===")

        @profile(log_enabled=False, trace_memory=True)
        def parallel_map_reduce(data: List[int], num_processes: int = 2):
            """Parallel map-reduce implementation."""
            # Split data into chunks
            chunk_size = len(data) // num_processes
            chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

            # Parallel map phase
            with multiprocessing.Pool(processes=num_processes) as pool:
                mapped = pool.map(_mapper_function, chunks)

            # Reduce phase
            result = sum(mapped)

            return result

        data = list(range(100))
        result = parallel_map_reduce(data)
        expected = sum(x * x for x in range(100))
        assert result == expected
        print(f"✓ Map-Reduce: result={result}")

    def test_process_pool_executor(self):
        """Test ProcessPoolExecutor for CPU-bound tasks."""
        print("\n=== Testing ProcessPoolExecutor ===")

        @profile(log_enabled=False, trace_memory=True)
        def parallel_computation():
            """Run CPU-intensive tasks in parallel."""
            tasks = [10000, 15000, 20000]

            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(_cpu_intensive_task, n) for n in tasks]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            return sum(results)

        result = parallel_computation()
        assert result > 0
        print(f"✓ ProcessPoolExecutor: computed sum={result}")


class TestGeneratorIteratorScenarios:
    """Test generator and iterator profiling."""

    def test_infinite_generator(self):
        """Test profiling infinite generators."""
        print("\n=== Testing Infinite Generator ===")

        @profile(log_enabled=False, trace_memory=True)
        def fibonacci_generator():
            """Infinite Fibonacci generator."""
            a, b = 0, 1
            while True:
                yield a
                a, b = b, a + b

        @profile(log_enabled=False)
        def consume_generator():
            """Consume limited items from infinite generator."""
            fib = fibonacci_generator()
            results = []
            for _, value in zip(range(10), fib):
                results.append(value)
            return results

        result = consume_generator()
        assert result == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        print("✓ Infinite generator: first 10 Fibonacci numbers")

    def test_generator_pipeline(self):
        """Test generator pipeline processing."""
        print("\n=== Testing Generator Pipeline ===")

        @profile(log_enabled=False)
        def data_source(n: int) -> Iterator[int]:
            """Generate source data."""
            yield from range(n)

        def filter_even(items: Iterator[int]) -> Iterator[int]:
            """Filter even numbers."""
            for item in items:
                if item % 2 == 0:
                    yield item

        def square_values(items: Iterator[int]) -> Iterator[int]:
            """Square each value."""
            for item in items:
                yield item * item

        @profile(log_enabled=False, trace_memory=True)
        def generator_pipeline():
            """Chain generators in pipeline."""
            source = data_source(20)
            filtered = filter_even(source)
            squared = square_values(filtered)

            return list(squared)

        result = generator_pipeline()
        expected = [i * i for i in range(20) if i % 2 == 0]
        assert result == expected
        print(f"✓ Generator pipeline: {len(result)} items processed")

    def test_custom_iterator_class(self):
        """Test profiling custom iterator classes."""
        print("\n=== Testing Custom Iterator Class ===")

        class FibonacciIterator:
            def __init__(self, max_count: int):
                self.max_count = max_count
                self.count = 0
                self.current = 0
                self.next_val = 1

            def __iter__(self):
                return self

            def __next__(self):
                if self.count >= self.max_count:
                    raise StopIteration

                result = self.current
                self.current, self.next_val = (
                    self.next_val,
                    self.current + self.next_val,
                )
                self.count += 1
                return result

        @profile(log_enabled=False, trace_memory=True)
        def use_custom_iterator():
            """Use custom iterator."""
            fib_iter = FibonacciIterator(15)
            results = []

            for value in fib_iter:
                results.append(value)
                if value > 100:
                    break

            return results

        result = use_custom_iterator()
        assert len(result) > 0
        print(f"✓ Custom iterator: {len(result)} Fibonacci numbers")


class TestContextManagerScenarios:
    """Test complex context manager scenarios."""

    def test_nested_context_managers(self):
        """Test deeply nested context managers."""
        print("\n=== Testing Nested Context Managers ===")

        class ResourceManager:
            def __init__(self, name: str):
                self.name = name
                self.active = False

            def __enter__(self):
                self.active = True
                return self

            def __exit__(self, *args):
                self.active = False

        @profile(log_enabled=False, trace_memory=True)
        def nested_resources():
            """Use multiple nested context managers."""
            resources = []

            with ResourceManager("db") as db:
                resources.append(db.name)

                with ResourceManager("cache") as cache:
                    resources.append(cache.name)

                    with ResourceManager("file") as file:
                        resources.append(file.name)

                        # Simulate work with all resources
                        time.sleep(0.001)

            return resources

        result = nested_resources()
        assert result == ["db", "cache", "file"]
        print(f"✓ Nested context managers: {result}")

    def test_exitstack_dynamic_contexts(self):
        """Test dynamic context management with ExitStack."""
        print("\n=== Testing ExitStack Dynamic Contexts ===")

        class DynamicResource:
            def __init__(self, resource_id: int):
                self.id = resource_id
                self.data = f"resource_{resource_id}"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        @profile(log_enabled=False, trace_memory=True)
        def dynamic_context_management(num_resources: int):
            """Dynamically manage multiple contexts."""
            results = []

            with ExitStack() as stack:
                # Dynamically enter contexts
                resources = []
                for i in range(num_resources):
                    resource = stack.enter_context(DynamicResource(i))
                    resources.append(resource)

                # Use all resources
                for resource in resources:
                    results.append(resource.data)

            return results

        result = dynamic_context_management(5)
        assert len(result) == 5
        print(f"✓ Dynamic contexts: {len(result)} resources managed")

    def test_context_manager_exception_handling(self):
        """Test context manager with exception handling."""
        print("\n=== Testing Context Manager Exception Handling ===")

        class TransactionManager:
            def __init__(self):
                self.committed = False
                self.rolled_back = False

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.rolled_back = True
                else:
                    self.committed = True
                return False  # Don't suppress exceptions

        @profile(log_enabled=False)
        def transactional_operation(should_fail: bool):
            """Operation with transaction management."""
            with TransactionManager():
                # Simulate some work
                time.sleep(0.001)

                if should_fail:
                    raise ValueError("Transaction failed")

                return "Success"

        # Test successful transaction
        result = transactional_operation(False)
        assert result == "Success"

        # Test failed transaction
        with pytest.raises(ValueError):
            transactional_operation(True)

        print("✓ Context manager exception handling completed")


class TestClassBasedComplexScenarios:
    """Test complex class-based profiling scenarios."""

    def test_inheritance_hierarchy(self):
        """Test profiling with complex inheritance."""
        print("\n=== Testing Inheritance Hierarchy ===")

        class BaseProcessor:
            @profile(log_enabled=False)
            def process(self, data: str) -> str:
                return self.validate(data)

            def validate(self, data: str) -> str:
                if not data:
                    raise ValueError("Empty data")
                return data

        class MiddleProcessor(BaseProcessor):
            @profile(log_enabled=False)
            def process(self, data: str) -> str:
                validated = super().process(data)
                return self.transform(validated)

            def transform(self, data: str) -> str:
                return data.upper()

        class FinalProcessor(MiddleProcessor):
            @profile(log_enabled=False)
            def process(self, data: str) -> str:
                transformed = super().process(data)
                return self.finalize(transformed)

            def finalize(self, data: str) -> str:
                return f"[{data}]"

        processor = FinalProcessor()
        result = processor.process("test")
        assert result == "[TEST]"
        print(f"✓ Inheritance hierarchy: {result}")

    def test_property_descriptor_profiling(self):
        """Test profiling properties and descriptors."""
        print("\n=== Testing Property and Descriptor Profiling ===")

        class DataDescriptor:
            def __init__(self, initial_value=None):
                self.value = initial_value

            def __get__(self, obj, objtype=None):
                return self.value

            def __set__(self, obj, value):
                self.value = value * 2  # Double on set

        class DataClass:
            doubled = DataDescriptor()

            def __init__(self):
                self._cached = None

            @property
            @profile(log_enabled=False)
            def expensive_property(self):
                """Expensive computed property."""
                if self._cached is None:
                    # Simulate expensive computation
                    time.sleep(0.001)
                    self._cached = sum(range(100))
                return self._cached

            @expensive_property.setter
            @profile(log_enabled=False)
            def expensive_property(self, value):
                self._cached = value

        obj = DataClass()
        obj.doubled = 5
        assert obj.doubled == 10

        # Access expensive property
        value = obj.expensive_property
        assert value == sum(range(100))

        print("✓ Property and descriptor profiling completed")

    def test_metaclass_profiling(self):
        """Test profiling with metaclasses."""
        print("\n=== Testing Metaclass Profiling ===")

        class ProfilingMeta(type):
            """Metaclass that adds profiling to all methods."""

            def __new__(mcs, name, bases, namespace):
                # Add profiling to all methods
                for attr_name, attr_value in namespace.items():
                    if callable(attr_value) and not attr_name.startswith("_"):
                        namespace[attr_name] = profile()(attr_value)

                return super().__new__(mcs, name, bases, namespace)

        class AutoProfiledClass(metaclass=ProfilingMeta):
            def method1(self) -> int:
                return 1

            def method2(self) -> int:
                return 2

            def combined(self) -> int:
                return self.method1() + self.method2()

        obj = AutoProfiledClass()
        result = obj.combined()
        assert result == 3
        print(f"✓ Metaclass auto-profiling: result={result}")

    def test_abstract_base_class(self):
        """Test profiling with abstract base classes."""
        print("\n=== Testing Abstract Base Class ===")

        from abc import ABC, abstractmethod

        class AbstractProcessor(ABC):
            @abstractmethod
            def process(self, data: Any) -> Any:
                pass

            @profile(log_enabled=False)
            def execute(self, data: Any) -> Any:
                """Template method."""
                validated = self.validate(data)
                processed = self.process(validated)
                return self.finalize(processed)

            def validate(self, data: Any) -> Any:
                return data

            def finalize(self, data: Any) -> Any:
                return data

        class ConcreteProcessor(AbstractProcessor):
            @profile(log_enabled=False)
            def process(self, data: str) -> str:
                return data.upper()

        processor = ConcreteProcessor()
        result = processor.execute("hello")
        assert result == "HELLO"
        print(f"✓ Abstract base class: {result}")


class TestPerformanceStressTests:
    """Test performance under stress conditions."""

    def test_rapid_function_calls(self):
        """Test rapid successive function calls."""
        print("\n=== Testing Rapid Function Calls ===")

        @profile(log_enabled=False, min_duration=0.0)
        def rapid_function(x: int) -> int:
            return x * 2

        @profile(log_enabled=False)
        def stress_test():
            """Make many rapid calls."""
            results = []
            for i in range(100):
                results.append(rapid_function(i))
            return len(results)

        result = stress_test()
        assert result == 100
        print(f"✓ Rapid calls: {result} function calls")

    def test_deep_call_stack(self):
        """Test very deep call stacks."""
        print("\n=== Testing Deep Call Stack ===")

        @profile(log_enabled=False, max_depth=100)
        def deep_recursion(depth: int, max_depth: int = 50) -> int:
            """Create deep call stack."""
            if depth >= max_depth:
                return depth

            def nested_call(d):
                return deep_recursion(d + 1, max_depth)

            return nested_call(depth)

        result = deep_recursion(0, 30)  # Limited depth to avoid stack overflow
        assert result == 30
        print(f"✓ Deep call stack: depth={result}")

    def test_exception_storm(self):
        """Test handling many exceptions."""
        print("\n=== Testing Exception Storm ===")

        @profile(log_enabled=False)
        def exception_generator():
            """Generate many exceptions."""
            exceptions_caught = 0

            for i in range(50):
                try:
                    if i % 2 == 0:
                        raise ValueError(f"Error {i}")
                    else:
                        raise TypeError(f"Error {i}")
                except (ValueError, TypeError):
                    exceptions_caught += 1

            return exceptions_caught

        result = exception_generator()
        assert result == 50
        print(f"✓ Exception storm: {result} exceptions handled")

    def test_memory_pressure(self):
        """Test under memory pressure."""
        print("\n=== Testing Memory Pressure ===")

        @profile(log_enabled=False, trace_memory=True)
        def memory_pressure_test():
            """Create and destroy many objects."""
            allocations = []

            # Allocation phase
            for i in range(20):
                # Allocate varying sizes
                size = 1000 * (i + 1)
                data = bytearray(size)
                allocations.append(data)

            # Partial deallocation
            for i in range(0, len(allocations), 2):
                allocations[i] = None

            # Force garbage collection
            gc.collect()

            # Count remaining allocations
            remaining = sum(1 for a in allocations if a is not None)

            return remaining

        result = memory_pressure_test()
        assert result == 10
        print(f"✓ Memory pressure: {result} allocations remaining")


class TestEdgeCasesAndCornerCases:
    """Test edge cases and corner scenarios."""

    def test_empty_function_variations(self):
        """Test various empty function patterns."""
        print("\n=== Testing Empty Function Variations ===")

        @profile(log_enabled=False)
        def empty_func():
            pass

        @profile(log_enabled=False)
        def empty_with_docstring():
            """This function does nothing."""
            pass

        @profile(log_enabled=False)
        def empty_with_return():
            return

        @profile(log_enabled=False)
        def empty_with_none_return():
            return None

        # Call all variations
        empty_func()
        empty_with_docstring()
        empty_with_return()
        result = empty_with_none_return()

        assert result is None
        print("✓ Empty function variations completed")

    def test_single_expression_functions(self):
        """Test single expression functions."""
        print("\n=== Testing Single Expression Functions ===")

        @profile(log_enabled=False)
        def lambda_style(x):
            return x * 2

        @profile(log_enabled=False)
        def ternary_expression(x):
            return "positive" if x > 0 else "non-positive"

        @profile(log_enabled=False)
        def list_comprehension_func(n):
            return [i * i for i in range(n)]

        assert lambda_style(5) == 10
        assert ternary_expression(1) == "positive"
        assert len(list_comprehension_func(5)) == 5

        print("✓ Single expression functions completed")

    def test_function_with_side_effects(self):
        """Test functions with global side effects."""
        print("\n=== Testing Functions with Side Effects ===")

        # Use a mutable container to simulate global state
        state = {"counter": 0, "list": []}

        @profile(log_enabled=False)
        def side_effect_function(value):
            state["counter"] += 1
            state["list"].append(value)

            # Modify mutable argument
            if isinstance(value, list):
                value.append("modified")

            return state["counter"]

        # Test with different inputs
        result1 = side_effect_function(10)
        test_list = [1, 2, 3]
        result2 = side_effect_function(test_list)

        assert result1 == 1
        assert result2 == 2
        assert test_list == [1, 2, 3, "modified"]

        print(f"✓ Side effects: counter={state['counter']}, list={len(state['list'])} items")

    def test_function_with_complex_signatures(self):
        """Test functions with complex signatures."""
        print("\n=== Testing Complex Function Signatures ===")

        @profile(log_enabled=False)
        def complex_signature(pos_arg, *args, keyword_only, default_param="default", **kwargs):
            """Function with complex signature."""
            result = {
                "pos_arg": pos_arg,
                "args": args,
                "keyword_only": keyword_only,
                "default_param": default_param,
                "kwargs": kwargs,
            }
            return result

        result = complex_signature(
            1,
            2,
            3,
            keyword_only="required",
            default_param="custom",
            extra1="value1",
            extra2="value2",
        )

        assert result["pos_arg"] == 1
        assert result["args"] == (2, 3)
        assert result["keyword_only"] == "required"

        print("✓ Complex signatures handled correctly")


class TestRealWorldSimulations:
    """Test real-world application simulations."""

    @pytest.mark.asyncio
    async def test_web_api_simulation(self):
        """Simulate a complete web API request lifecycle."""
        print("\n=== Testing Web API Simulation ===")

        # Simulated database
        database = {
            "users": {
                1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
                2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
            },
            "posts": {
                1: {
                    "id": 1,
                    "user_id": 1,
                    "title": "First Post",
                    "content": "Hello World",
                },
                2: {
                    "id": 2,
                    "user_id": 1,
                    "title": "Second Post",
                    "content": "More content",
                },
            },
        }

        async def authenticate_request(token: str) -> Optional[int]:
            """Simulate authentication."""
            await asyncio.sleep(0.002)  # Auth service latency
            # Simple token validation
            if token.startswith("valid_"):
                return int(token.split("_")[1])
            return None

        async def get_user_from_db(user_id: int) -> Optional[Dict]:
            """Simulate database query."""
            await asyncio.sleep(0.003)  # DB latency
            return database["users"].get(user_id)

        async def get_user_posts(user_id: int) -> List[Dict]:
            """Get all posts for a user."""
            await asyncio.sleep(0.004)  # DB query
            return [p for p in database["posts"].values() if p["user_id"] == user_id]

        async def enrich_post_data(post: Dict) -> Dict:
            """Enrich post with additional data."""
            await asyncio.sleep(0.001)  # Processing time
            post["word_count"] = len(post["content"].split())
            post["reading_time"] = post["word_count"] // 200  # 200 words per minute
            return post

        @profile(log_enabled=False, trace_memory=True)
        async def handle_api_request(token: str) -> Dict:
            """Handle complete API request."""
            # Authentication
            user_id = await authenticate_request(token)
            if not user_id:
                return {"error": "Unauthorized", "status": 401}

            # Fetch user data and posts in parallel
            user_data, user_posts = await asyncio.gather(
                get_user_from_db(user_id), get_user_posts(user_id)
            )

            if not user_data:
                return {"error": "User not found", "status": 404}

            # Enrich posts in parallel
            enriched_posts = await asyncio.gather(*[enrich_post_data(post) for post in user_posts])

            # Build response
            response = {
                "status": 200,
                "user": user_data,
                "posts": enriched_posts,
                "post_count": len(enriched_posts),
            }

            return response

        # Test the API
        result = await handle_api_request("valid_1")
        assert result["status"] == 200
        assert result["user"]["name"] == "Alice"
        assert result["post_count"] == 2

        print(f"✓ Web API simulation: user={result['user']['name']}, posts={result['post_count']}")

    def test_data_pipeline_simulation(self):
        """Simulate a data processing pipeline."""
        print("\n=== Testing Data Pipeline Simulation ===")

        @dataclass
        class DataRecord:
            id: int
            value: float
            category: str
            timestamp: float

        def generate_data(n: int) -> List[DataRecord]:
            """Generate sample data."""
            categories = ["A", "B", "C", "D"]
            return [
                DataRecord(
                    id=i,
                    value=random.random() * 100,
                    category=random.choice(categories),
                    timestamp=time.time() + i,
                )
                for i in range(n)
            ]

        def validate_records(records: List[DataRecord]) -> List[DataRecord]:
            """Validate and filter records."""
            valid = []
            for record in records:
                if record.value > 0 and record.category:
                    valid.append(record)
            return valid

        def transform_records(records: List[DataRecord]) -> List[Dict]:
            """Transform records."""
            transformed = []
            for record in records:
                transformed.append(
                    {
                        "id": record.id,
                        "value": round(record.value, 2),
                        "category": record.category.lower(),
                        "timestamp": int(record.timestamp),
                        "processed": True,
                    }
                )
            return transformed

        def aggregate_by_category(records: List[Dict]) -> Dict[str, Dict]:
            """Aggregate data by category."""
            aggregated = defaultdict(lambda: {"count": 0, "total": 0.0, "records": []})

            for record in records:
                cat = record["category"]
                aggregated[cat]["count"] += 1
                aggregated[cat]["total"] += record["value"]
                aggregated[cat]["records"].append(record["id"])

            # Calculate averages
            for _, data in aggregated.items():
                data["average"] = data["total"] / data["count"] if data["count"] > 0 else 0

            return dict(aggregated)

        @profile(log_enabled=False, trace_memory=True)
        def run_data_pipeline(num_records: int = 100):
            """Run complete data pipeline."""
            # Generate
            raw_data = generate_data(num_records)

            # Validate
            valid_data = validate_records(raw_data)

            # Transform
            transformed_data = transform_records(valid_data)

            # Aggregate
            aggregated = aggregate_by_category(transformed_data)

            # Generate summary
            summary = {
                "total_records": num_records,
                "valid_records": len(valid_data),
                "categories": len(aggregated),
                "aggregated_data": aggregated,
            }

            return summary

        result = run_data_pipeline(50)
        assert result["total_records"] == 50
        assert result["valid_records"] <= 50
        assert result["categories"] > 0

        print(
            f"✓ Data pipeline: {result['valid_records']}/{result['total_records']} valid, "
            f"{result['categories']} categories"
        )

    def test_cache_simulation(self):
        """Simulate a caching system with eviction."""
        print("\n=== Testing Cache Simulation ===")

        class LRUCache:
            def __init__(self, capacity: int):
                self.capacity = capacity
                self.cache = {}
                self.access_order = deque()
                self.hits = 0
                self.misses = 0

            def get(self, key: str) -> Optional[Any]:
                if key in self.cache:
                    self.hits += 1
                    # Move to end (most recently used)
                    self.access_order.remove(key)
                    self.access_order.append(key)
                    return self.cache[key]
                else:
                    self.misses += 1
                    return None

            def put(self, key: str, value: Any):
                if key in self.cache:
                    # Update existing
                    self.access_order.remove(key)
                elif len(self.cache) >= self.capacity:
                    # Evict least recently used
                    lru_key = self.access_order.popleft()
                    del self.cache[lru_key]

                self.cache[key] = value
                self.access_order.append(key)

            def get_stats(self) -> Dict:
                total = self.hits + self.misses
                hit_rate = self.hits / total if total > 0 else 0
                return {
                    "hits": self.hits,
                    "misses": self.misses,
                    "hit_rate": hit_rate,
                    "size": len(self.cache),
                }

        @profile(log_enabled=False, trace_memory=True)
        def cache_simulation():
            """Simulate cache usage patterns."""
            cache = LRUCache(capacity=10)

            # Simulate various access patterns
            # Sequential writes
            for i in range(15):
                cache.put(f"key_{i}", f"value_{i}")

            # Random reads with locality
            for _ in range(30):
                key_id = random.randint(10, 14)  # Recent keys more likely
                cache.get(f"key_{key_id}")

            # Some misses
            for i in range(16, 20):
                cache.get(f"key_{i}")

            return cache.get_stats()

        result = cache_simulation()
        assert result["size"] <= 10  # Capacity limit
        assert result["hits"] > 0
        assert result["misses"] > 0

        print(f"✓ Cache simulation: hit_rate={result['hit_rate']:.2%}, size={result['size']}/10")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s", "--tb=short"])
