#!/usr/bin/env python
"""
PerfScope v1.0.0 - Comprehensive Demo
Shows various profiling scenarios and capabilities.
"""

import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from perfscope import profile

# ============================================================================
# BASIC EXAMPLES
# ============================================================================


@profile()
def simple_function(n: int) -> int:
    """Simple function to demonstrate basic profiling."""
    result = 0
    for i in range(n):
        result += i**2
    return result


@profile(trace_memory=True)
def memory_intensive_function(size: int = 1000000) -> int:
    """Function that allocates and uses memory."""
    # Allocate large list
    data = list(range(size))

    # Process data
    result = sum(x for x in data if x % 2 == 0)

    # Create dictionary
    lookup = {i: i**2 for i in range(1000)}

    return result + len(lookup)


# ============================================================================
# NESTED CALLS AND RECURSION
# ============================================================================


@profile(max_depth=20, log_calls=True)
def fibonacci(n: int) -> int:
    """Recursive Fibonacci to show nested call tracking."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_data(data: List[int]) -> Dict[str, Any]:
    """Process data with multiple steps."""
    # Step 1: Filter
    filtered = [x for x in data if x > 0]

    # Step 2: Transform
    transformed = [x**2 for x in filtered]

    # Step 3: Aggregate
    result = {
        "count": len(transformed),
        "sum": sum(transformed),
        "avg": sum(transformed) / len(transformed) if transformed else 0,
        "max": max(transformed) if transformed else 0,
        "min": min(transformed) if transformed else 0,
    }

    return result


@profile(trace_memory=True, log_args=True)
def data_pipeline(size: int = 10000) -> Dict[str, Any]:
    """Complete data processing pipeline."""
    # Generate data
    data = [random.randint(-100, 100) for _ in range(size)]

    # Process in pipeline
    result = process_data(data)

    # Add metadata
    result["size"] = size
    result["timestamp"] = time.time()

    return result


# ============================================================================
# ASYNC/AWAIT EXAMPLES
# ============================================================================


@profile(trace_memory=True)
async def async_io_operation(delay: float = 0.1) -> str:
    """Async I/O operation simulation."""
    await asyncio.sleep(delay)
    return f"Completed after {delay}s"


@profile()
async def parallel_async_tasks(n: int = 5) -> List[str]:
    """Execute multiple async tasks in parallel."""
    tasks = []
    for _i in range(n):
        delay = random.uniform(0.01, 0.1)
        task = async_io_operation(delay)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results


# ============================================================================
# THREADPOOL EXECUTOR EXAMPLE
# ============================================================================


@profile(trace_memory=True, max_depth=50, log_level="INFO")
async def complex_async_workflow(user_id: int, session_id: str) -> Dict[str, Any]:
    """
    Complex async workflow demonstrating ThreadPoolExecutor with asyncio.gather.
    Shows how to profile mixed async/sync operations.
    """

    # Simulate service calls
    async def fetch_user(uid: int) -> Dict:
        await asyncio.sleep(0.01)
        return {"id": uid, "name": f"User_{uid}", "email": f"user{uid}@example.com"}

    async def fetch_session(sid: str) -> Dict:
        await asyncio.sleep(0.01)
        return {"id": sid, "created": time.time(), "active": True}

    def check_permissions(uid: int, sid: str) -> bool:
        """CPU-bound permission check."""
        time.sleep(0.01)  # Simulate computation
        return uid > 0 and len(sid) > 0

    def process_data(user: Dict, session: Dict) -> Dict:
        """CPU-bound data processing."""
        result = {
            "user_id": user["id"],
            "session_id": session["id"],
            "processed_at": time.time(),
        }
        # Simulate heavy computation
        for _i in range(1000):
            result["hash"] = hash(str(result))
        return result

    # Execute with ThreadPoolExecutor for CPU-bound tasks
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Parallel execution of async and sync tasks
        user, session, permission = await asyncio.gather(
            fetch_user(user_id),
            fetch_session(session_id),
            loop.run_in_executor(executor, check_permissions, user_id, session_id),
        )

        if not permission:
            return {"error": "Permission denied"}

        # Process data in thread pool
        processed = await loop.run_in_executor(executor, process_data, user, session)

    # Background tasks
    async def send_notification(email: str):
        await asyncio.sleep(0.01)
        return f"Notified {email}"

    # Create background task (fire and forget)
    asyncio.create_task(send_notification(user["email"]))

    return {"success": True, "user": user, "session": session, "processed": processed}


# ============================================================================
# MULTI-THREADING EXAMPLE
# ============================================================================


@profile(trace_memory=True, log_calls=True)
def thread_worker(worker_id: int, iterations: int = 1000) -> float:
    """Worker function for threading example."""
    result = 0.0
    for i in range(iterations):
        result += (i * worker_id) ** 0.5
        if i % 100 == 0:
            time.sleep(0.001)  # Simulate I/O
    return result


def multi_threaded_processing(num_threads: int = 4) -> List[float]:
    """Execute work in multiple threads."""
    import threading

    results = []
    threads = []

    @profile()
    def run_worker(wid: int):
        result = thread_worker(wid, 500)
        results.append(result)

    # Create and start threads
    for i in range(num_threads):
        thread = threading.Thread(target=run_worker, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    return results


# ============================================================================
# ERROR HANDLING EXAMPLE
# ============================================================================


@profile(log_calls=True)
def function_with_errors(should_fail: bool = False, retry_count: int = 3) -> str:
    """Function that demonstrates error handling and retry logic."""
    for attempt in range(retry_count):
        try:
            if should_fail and attempt < retry_count - 1:
                raise ValueError(f"Attempt {attempt + 1} failed")

            # Simulate work
            time.sleep(0.01)
            return f"Success on attempt {attempt + 1}"

        except ValueError:
            if attempt == retry_count - 1:
                raise
            time.sleep(0.01 * (2**attempt))  # Exponential backoff


# ============================================================================
# CLASS PROFILING EXAMPLE
# ============================================================================


class DataProcessor:
    """Example class with profiled methods."""

    def __init__(self):
        self.data = []
        self.cache = {}

    @profile(trace_memory=True)
    def load_data(self, size: int = 1000):
        """Load data into processor."""
        self.data = list(range(size))
        return len(self.data)

    @profile()
    def process(self) -> Dict[str, Any]:
        """Process loaded data."""
        if not self.data:
            return {"error": "No data loaded"}

        # Check cache
        cache_key = len(self.data)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Process
        result = {
            "count": len(self.data),
            "sum": sum(self.data),
            "squared_sum": sum(x**2 for x in self.data),
            "filtered": len([x for x in self.data if x % 2 == 0]),
        }

        # Cache result
        self.cache[cache_key] = result
        return result


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================


def run_basic_examples():
    """Run basic profiling examples."""
    print("\n" + "=" * 80)
    print("BASIC PROFILING EXAMPLES")
    print("=" * 80)

    # Simple function
    print("\n1. Simple function profiling:")
    result = simple_function(100)
    print(f"   Result: {result}")
    print(f"   Report: {simple_function.profile_report.total_duration:.3f}s")

    # Memory tracking
    print("\n2. Memory-intensive function:")
    result = memory_intensive_function(100000)
    print(f"   Result: {result}")
    report = memory_intensive_function.profile_report
    if report.memory_start and report.memory_end:
        delta = (report.memory_end - report.memory_start) / (1024 * 1024)
        print(f"   Memory delta: {delta:+.2f}MB")

    # Nested calls
    print("\n3. Recursive Fibonacci:")
    result = fibonacci(10)
    print(f"   Result: {result}")
    print(f"   Total calls: {fibonacci.profile_report.total_calls}")

    # Data pipeline
    print("\n4. Data pipeline:")
    result = data_pipeline(1000)
    print(f"   Processed {result['count']} items")
    print(f"   Average: {result['avg']:.2f}")


async def run_async_examples():
    """Run async profiling examples."""
    print("\n" + "=" * 80)
    print("ASYNC/AWAIT PROFILING EXAMPLES")
    print("=" * 80)

    # Simple async
    print("\n5. Simple async operation:")
    result = await async_io_operation(0.05)
    print(f"   Result: {result}")

    # Parallel async
    print("\n6. Parallel async tasks:")
    results = await parallel_async_tasks(3)
    print(f"   Completed {len(results)} tasks")

    # Complex workflow with mixed async/sync
    print("\n7. Complex async workflow (ThreadPoolExecutor + asyncio):")
    result = await complex_async_workflow(123, "session_456")
    if result.get("success"):
        print(f"   Success! Processed user {result['user']['name']}")
    print(f"   CPU efficiency: {complex_async_workflow.profile_report.cpu_efficiency:.1%}")


def run_threading_examples():
    """Run multi-threading examples."""
    print("\n" + "=" * 80)
    print("MULTI-THREADING EXAMPLES")
    print("=" * 80)

    print("\n8. Multi-threaded processing:")
    results = multi_threaded_processing(3)
    print(f"   Completed {len(results)} threads")
    print(f"   Results: {[f'{r:.2f}' for r in results]}")


def run_error_handling_examples():
    """Run error handling examples."""
    print("\n" + "=" * 80)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 80)

    print("\n9. Function with retry logic:")
    # Success case
    result = function_with_errors(should_fail=False)
    print(f"   Success case: {result}")

    # Retry case
    try:
        result = function_with_errors(should_fail=True, retry_count=3)
        print(f"   Retry case: {result}")
    except ValueError as e:
        print(f"   Failed after retries: {e}")


def run_class_examples():
    """Run class profiling examples."""
    print("\n" + "=" * 80)
    print("CLASS PROFILING EXAMPLES")
    print("=" * 80)

    print("\n10. Class method profiling:")
    processor = DataProcessor()

    # Load data
    count = processor.load_data(5000)
    print(f"    Loaded {count} items")

    # Process (first time - no cache)
    result1 = processor.process()
    print(f"    First process: sum={result1['sum']}")

    # Process (second time - cached)
    result2 = processor.process()
    print(f"    Cached process: sum={result2['sum']}")


def print_summary():
    """Print demo summary."""
    print("\n" + "=" * 80)
    print("PERFSCOPE DEMO COMPLETE")
    print("=" * 80)
    print(
        """
Key Features Demonstrated:
✓ Basic function profiling with @profile decorator
✓ Memory tracking and allocation monitoring
✓ Nested function calls and recursion tracking
✓ Async/await function profiling
✓ ThreadPoolExecutor with asyncio.gather for mixed async/sync operations
✓ Multi-threading support
✓ Error handling and retry logic
✓ Class method profiling
✓ Caching and performance optimization tracking

For more details, check the profile_report attribute on any profiled function:
- function.profile_report.total_duration
- function.profile_report.cpu_efficiency
- function.profile_report.memory_peak
- function.profile_report.statistics
"""
    )


def main():
    """Run all demo examples."""
    print("\n" + "=" * 80)
    print("PERFSCOPE v1.0.0 - COMPREHENSIVE DEMO")
    print("=" * 80)

    # Run examples
    run_basic_examples()
    asyncio.run(run_async_examples())
    run_threading_examples()
    run_error_handling_examples()
    run_class_examples()

    # Summary
    print_summary()


if __name__ == "__main__":
    main()
