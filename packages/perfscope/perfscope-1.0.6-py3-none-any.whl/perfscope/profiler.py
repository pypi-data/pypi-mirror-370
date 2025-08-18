"""Main profiler implementation for PerfScope - Performance monitoring with detailed logging."""

from __future__ import annotations

import asyncio
import functools
import gc
import inspect
import json
import logging
import sys
import threading
import time
import tracemalloc
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from perfscope.config import ProfileConfig

# Configure PerfScope logging
logger = logging.getLogger("perfscope")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s.%(msecs)03d | %(levelname)-8s | [PerfScope] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False


@dataclass
class PerformanceMetrics:
    """Detailed performance metrics for a function call."""

    # Timing metrics
    start_time: float
    end_time: float | None = None
    cpu_time_start: float = field(default_factory=time.process_time)
    cpu_time_end: float | None = None

    # Memory metrics
    memory_start: int | None = None
    memory_end: int | None = None
    memory_peak: int | None = None
    gc_count_start: tuple[int, int, int] | None = None
    gc_count_end: tuple[int, int, int] | None = None

    # Thread info
    thread_id: int = field(default_factory=threading.get_ident)
    thread_name: str = field(default_factory=lambda: threading.current_thread().name)

    # Context
    args_size: int | None = None
    kwargs_size: int | None = None
    return_size: int | None = None
    exception: str | None = None

    @property
    def wall_time(self) -> float:
        """Wall clock time in seconds."""
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    @property
    def cpu_time(self) -> float:
        """CPU time in seconds."""
        if self.cpu_time_end is None:
            return 0.0
        return self.cpu_time_end - self.cpu_time_start

    @property
    def memory_delta(self) -> int:
        """Memory change in bytes."""
        if self.memory_start is None or self.memory_end is None:
            return 0
        return self.memory_end - self.memory_start

    @property
    def gc_collections(self) -> tuple[int, int, int] | None:
        """GC collections that occurred during execution."""
        if self.gc_count_start and self.gc_count_end:
            return tuple(e - s for e, s in zip(self.gc_count_end, self.gc_count_start))  # type: ignore[return-value]
        return None


@dataclass
class CallInfo:
    """Complete information about a function call."""

    # Identity
    name: str
    module: str
    file: str
    line: int
    qualname: str

    # Metrics
    metrics: PerformanceMetrics

    # Hierarchy
    call_depth: int = 0
    children: list[CallInfo] = field(default_factory=list)
    parent_id: int | None = None
    call_id: int = field(default_factory=lambda: id(object()))

    # Additional info
    is_async: bool = False
    is_generator: bool = False
    is_builtin: bool = False

    @property
    def self_time(self) -> float:
        """Time spent in this function excluding children."""
        children_time = sum(child.metrics.wall_time for child in self.children)
        return max(0, self.metrics.wall_time - children_time)

    @property
    def self_cpu_time(self) -> float:
        """CPU time spent in this function excluding children."""
        children_cpu = sum(child.metrics.cpu_time for child in self.children)
        return max(0, self.metrics.cpu_time - children_cpu)


class PerformanceLogger:
    """Handles performance logging with production-ready format."""

    def __init__(self, config: ProfileConfig):
        self.config = config
        self.logger = logger
        # Control detailed call tracing vs summary-only logging
        self.detailed_tracing = config.detailed_tracing

    def log_call_start(self, call_info: CallInfo, args: tuple, kwargs: dict) -> None:
        """Log function call start with production-ready format."""
        if not self.config.log_enabled or not self.config.log_calls:
            return

        # Only log detailed tracing if explicitly enabled
        if not self.detailed_tracing:
            return

        # For detailed tracing, only log root functions to avoid clutter
        if call_info.call_depth == 0:
            self.logger.info(f"PROFILING: {call_info.qualname}")

    def log_call_end(self, call_info: CallInfo, result: Any = None) -> None:
        """Log function call end with production-ready format."""
        if not self.config.log_enabled or not self.config.log_calls:
            return

        # Log all significant function calls (not just root)
        wall_ms = call_info.metrics.wall_time * 1000

        # Only log functions that took meaningful time (>0.1ms) or are root functions
        if wall_ms >= 0.1 or call_info.call_depth == 0:
            cpu_ms = call_info.metrics.cpu_time * 1000

            # Single-line performance summary with function name
            summary_parts = [f"PROFILED[{call_info.qualname}]"]
            summary_parts.append(f"time={wall_ms:.2f}ms")
            summary_parts.append(f"cpu={cpu_ms:.2f}ms")

            # CPU efficiency
            if wall_ms > 0:
                cpu_efficiency = (cpu_ms / wall_ms) * 100
                summary_parts.append(f"efficiency={cpu_efficiency:.1f}%")

            # Memory if significant
            if call_info.metrics.memory_delta:
                delta_mb = call_info.metrics.memory_delta / (1024 * 1024)
                if abs(delta_mb) >= 0.01:  # Only show if >= 10KB
                    sign = "+" if delta_mb >= 0 else ""
                    summary_parts.append(f"mem={sign}{delta_mb:.2f}MB")

            # Nested calls if any
            if call_info.children:
                summary_parts.append(f"nested={len(call_info.children)}")

            # Depth indicator for nested functions
            if call_info.call_depth > 0:
                summary_parts.append(f"depth={call_info.call_depth}")

            self.logger.info(" ".join(summary_parts))

    def log_exception(self, call_info: CallInfo, exception: Exception) -> None:
        """Log function exception."""
        if not self.config.log_enabled:
            return
        self.logger.error(
            f"ERROR[{call_info.qualname}] {exception.__class__.__name__}: {str(exception)} "
            f"after {call_info.metrics.wall_time * 1000:.2f}ms"
        )

    def log_summary(self, report: ProfileReport) -> None:
        """Log production-ready profiling summary."""
        if not self.config.log_enabled:
            return
        # Only log summary for meaningful profiles (>1ms total or with bottlenecks)
        if report.total_duration < 0.001 and not report.statistics:
            return

        # Single-line summary for production
        summary_parts = ["SESSION SUMMARY"]
        summary_parts.append(f"duration={report.total_duration:.3f}s")
        summary_parts.append(f"cpu={report.total_cpu_time:.3f}s")
        summary_parts.append(f"efficiency={report.cpu_efficiency:.1%}")

        if report.total_calls > 0:
            summary_parts.append(f"calls={report.total_calls}")
        if report.unique_functions > 0:
            summary_parts.append(f"functions={report.unique_functions}")

        # Memory if significant
        if report.memory_start and report.memory_end:
            delta = (report.memory_end - report.memory_start) / (1024 * 1024)
            if abs(delta) >= 0.01:  # Only show if >= 10KB
                summary_parts.append(f"mem={delta:+.2f}MB")

        self.logger.info(" ".join(summary_parts))

        # Only log significant bottlenecks (functions taking >15% of total time)
        bottlenecks = [
            (name, stats)
            for name, stats in report.statistics.items()
            if stats["total_duration"] / report.total_duration > 0.15
        ]

        if bottlenecks:
            for name, stats in bottlenecks:
                percentage = (stats["total_duration"] / report.total_duration) * 100
                self.logger.warning(
                    f"BOTTLENECK[{name}] {percentage:.1f}% runtime "
                    f"({stats['total_duration'] * 1000:.1f}ms)"
                )

        # Exception summary
        exceptions = [(n, s) for n, s in report.statistics.items() if s.get("exceptions", 0) > 0]
        if exceptions:
            for name, stats in exceptions:
                self.logger.error(f"ERRORS[{name}] {stats['exceptions']} exceptions")


@dataclass
class ProfileReport:
    """Comprehensive profiling report."""

    total_duration: float
    total_cpu_time: float
    total_calls: int
    unique_functions: int
    call_tree: list[CallInfo]
    statistics: dict[str, dict[str, Any]]
    memory_start: int | None = None
    memory_end: int | None = None
    memory_peak: int | None = None
    thread_stats: dict[str, dict] = field(default_factory=dict)

    @property
    def cpu_efficiency(self) -> float:
        """CPU efficiency ratio (CPU time / wall time)."""
        if self.total_duration == 0:
            return 0
        return min(self.total_cpu_time / self.total_duration, 1.0)

    def to_dict(self) -> dict[str, Any]:
        """Export report as dictionary."""
        return {
            "total_duration": self.total_duration,
            "total_cpu_time": self.total_cpu_time,
            "cpu_efficiency": self.cpu_efficiency,
            "total_calls": self.total_calls,
            "unique_functions": self.unique_functions,
            "memory_start_mb": (self.memory_start / (1024 * 1024) if self.memory_start else None),
            "memory_end_mb": (self.memory_end / (1024 * 1024) if self.memory_end else None),
            "memory_peak_mb": (self.memory_peak / (1024 * 1024) if self.memory_peak else None),
            "statistics": self.statistics,
            "thread_stats": self.thread_stats,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export report as JSON."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save(self, path: str | Path) -> None:
        """Save report to JSON file.

        Args:
            path: Path where to save the report.

        Raises:
            ValueError: If path is invalid or cannot be written.
        """
        try:
            path = Path(path).resolve()
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            # Write with explicit encoding
            path.write_text(self.to_json(), encoding="utf-8")
            logger.info(f"Report saved to: {path}")
        except OSError as e:
            logger.error(f"Failed to save report to {path}: {e}")
            raise ValueError(f"Cannot save report to {path}: {e}") from e


class Profiler:
    """Advanced profiler for comprehensive performance monitoring."""

    def __init__(self, config: ProfileConfig | None = None):
        """Initialize profiler with configuration."""
        self.config = config or ProfileConfig()
        self.performance_logger = PerformanceLogger(self.config)

        # Thread-local storage for call stacks
        self._local = threading.local()

        # Global storage
        self._traces: list[CallInfo] = []
        self._lock = threading.RLock()
        self._active = False
        self._original_trace: Any = None

        # Timing
        self._start_time: float | None = None
        self._start_cpu_time: float | None = None

        # Memory tracking
        self._memory_start: int | None = None
        self._memory_peak: int | None = None

        # Thread statistics
        self._thread_stats: dict[str, dict] = defaultdict(
            lambda: {
                "calls": 0,
                "total_time": 0,
                "cpu_time": 0,
            }
        )

    def _get_call_stack(self) -> deque[CallInfo]:
        """Get thread-local call stack."""
        if not hasattr(self._local, "stack"):
            self._local.stack = deque()
        return self._local.stack  # type: ignore[no-any-return]

    def start(self) -> None:
        """Start profiling."""
        if self._active or not self.config.enabled:
            return

        self._start_time = time.perf_counter()
        self._start_cpu_time = time.process_time()

        # Start memory tracking
        if self.config.trace_memory:
            if not tracemalloc.is_tracing():
                tracemalloc.start()
            self._memory_start = self._get_memory_usage()

        # Set trace function
        if self.config.trace_calls:
            self._original_trace = sys.gettrace()
            sys.settrace(self._trace_calls)  # type: ignore[arg-type]

        self._active = True

    def stop(self) -> None:
        """Stop profiling and clean up resources."""
        if not self._active:
            return

        try:
            # Restore original trace
            if self.config.trace_calls:
                sys.settrace(self._original_trace)
                self._original_trace = None

            # Get final memory usage
            if self.config.trace_memory:
                self._memory_peak = self._get_peak_memory()
                # Note: We don't stop tracemalloc here as other code might be using it
        finally:
            self._active = False
            # Clear thread-local storage to prevent memory leaks
            if hasattr(self._local, "stack"):
                self._local.stack.clear()

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        if tracemalloc.is_tracing():
            return tracemalloc.get_traced_memory()[0]  # type: ignore[no-any-return]
        elif HAS_PSUTIL:
            return psutil.Process().memory_info().rss  # type: ignore[no-any-return]
        return 0

    def _get_peak_memory(self) -> int:
        """Get peak memory usage in bytes."""
        if tracemalloc.is_tracing():
            return tracemalloc.get_traced_memory()[1]  # type: ignore[no-any-return]
        elif HAS_PSUTIL:
            return psutil.Process().memory_info().rss  # type: ignore[no-any-return]
        return 0

    def _get_object_size(self, obj: Any) -> int:
        """Estimate object size in bytes safely.

        Args:
            obj: Object to measure.

        Returns:
            Size in bytes, or 0 if measurement fails.
        """
        try:
            # Avoid infinite recursion for certain object types
            if hasattr(obj, "__sizeof__"):
                return sys.getsizeof(obj)
            return 0
        except (TypeError, RecursionError, AttributeError):
            return 0

    def _should_trace(self, frame: Any) -> bool:
        """Check if frame should be traced."""
        if not frame or not frame.f_code:
            return False

        # Check depth limit
        stack = self._get_call_stack()
        if len(stack) >= self.config.max_depth:
            return False

        filename = frame.f_code.co_filename
        module = frame.f_globals.get("__name__", "")

        # Skip built-ins unless included
        if not self.config.include_builtins:
            if filename.startswith("<") or "site-packages" in filename:
                return False

        # Apply module filters
        if self.config.include_modules:
            if not any(module.startswith(m) for m in self.config.include_modules):
                return False

        # CRITICAL: Always exclude perfscope itself to prevent infinite recursion
        if module.startswith("perfscope"):
            return False

        # Also exclude logging to prevent excessive noise
        if module.startswith("logging"):
            return False

        if any(module.startswith(m) for m in self.config.exclude_modules):
            return False

        return True

    def _trace_calls(self, frame: Any, event: str, arg: Any) -> Callable | None:
        """Trace function for sys.settrace."""
        if event == "call":
            if not self._should_trace(frame):
                return None

            code = frame.f_code
            stack = self._get_call_stack()

            # Create performance metrics
            metrics = PerformanceMetrics(
                start_time=time.perf_counter(),
                cpu_time_start=time.process_time(),
                memory_start=(self._get_memory_usage() if self.config.trace_memory else None),
                gc_count_start=gc.get_count() if self.config.trace_memory else None,
            )

            # Get argument sizes if configured
            if self.config.log_args:
                try:
                    metrics.args_size = sum(
                        self._get_object_size(v) for v in frame.f_locals.values()
                    )
                    metrics.kwargs_size = 0  # Already included in f_locals
                except Exception:
                    # Set defaults if object size calculation fails (e.g., unpicklable objects)
                    metrics.args_size = 0
                    metrics.kwargs_size = 0

            # Create call info
            call_info = CallInfo(
                name=code.co_name,
                module=frame.f_globals.get("__name__", ""),
                qualname=f"{frame.f_globals.get('__name__', '')}.{code.co_name}",
                file=code.co_filename,
                line=frame.f_lineno,
                metrics=metrics,
                call_depth=len(stack),
                is_async=asyncio.iscoroutinefunction(frame.f_globals.get(code.co_name)),
                is_generator=inspect.isgeneratorfunction(frame.f_globals.get(code.co_name)),
                is_builtin=code.co_filename.startswith("<"),
            )

            # Log call start
            self.performance_logger.log_call_start(
                call_info,
                frame.f_locals.get("args", ()),
                frame.f_locals.get("kwargs", {}),
            )

            # Add to hierarchy
            if stack:
                parent = stack[-1]
                parent.children.append(call_info)
                call_info.parent_id = parent.call_id
            else:
                with self._lock:
                    self._traces.append(call_info)

            stack.append(call_info)

            return self._trace_lines if self.config.trace_lines else self._trace_calls

        elif event == "return":
            stack = self._get_call_stack()
            if stack:
                call_info = stack.pop()

                # Complete metrics
                call_info.metrics.end_time = time.perf_counter()
                call_info.metrics.cpu_time_end = time.process_time()

                if self.config.trace_memory:
                    call_info.metrics.memory_end = self._get_memory_usage()
                    call_info.metrics.memory_peak = self._get_peak_memory()
                    call_info.metrics.gc_count_end = gc.get_count()

                # Get return value size
                if self.config.log_args and arg is not None:
                    call_info.metrics.return_size = self._get_object_size(arg)

                # Update thread statistics
                thread_name = call_info.metrics.thread_name
                with self._lock:
                    self._thread_stats[thread_name]["calls"] += 1
                    self._thread_stats[thread_name]["total_time"] += call_info.metrics.wall_time
                    self._thread_stats[thread_name]["cpu_time"] += call_info.metrics.cpu_time

                # Log call end
                self.performance_logger.log_call_end(call_info, arg)

        elif event == "exception":
            stack = self._get_call_stack()
            if stack:
                call_info = stack[-1]
                exc_type, exc_value, _ = arg
                call_info.metrics.exception = f"{exc_type.__name__}: {exc_value}"

                # Log exception
                self.performance_logger.log_exception(call_info, exc_value)

        return self._trace_calls

    def _trace_lines(self, frame: Any, event: str, arg: Any) -> Callable | None:
        """Trace function with line tracking."""
        if event == "line":
            # Could add line-level tracking here if needed
            return self._trace_lines
        return self._trace_calls(frame, event, arg)

    def get_report(self) -> ProfileReport:
        """Generate comprehensive profiling report."""
        total_duration = time.perf_counter() - self._start_time if self._start_time else 0
        total_cpu_time = time.process_time() - self._start_cpu_time if self._start_cpu_time else 0

        # Calculate statistics
        statistics: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "calls": 0,
                "total_duration": 0,
                "total_cpu_time": 0,
                "self_time": 0,
                "self_cpu_time": 0,
                "memory_delta": 0,
                "exceptions": 0,
                "min_duration": float("inf"),
                "max_duration": 0,
            }
        )

        def process_call(call: CallInfo) -> None:
            key = call.qualname
            stats = statistics[key]

            stats["calls"] += 1
            stats["total_duration"] += call.metrics.wall_time
            stats["total_cpu_time"] += call.metrics.cpu_time
            stats["self_time"] += call.self_time
            stats["self_cpu_time"] += call.self_cpu_time
            stats["memory_delta"] += call.metrics.memory_delta
            stats["min_duration"] = min(stats["min_duration"], call.metrics.wall_time)
            stats["max_duration"] = max(stats["max_duration"], call.metrics.wall_time)

            if call.metrics.exception:
                stats["exceptions"] += 1

            for child in call.children:
                process_call(child)

        # Process all traces
        for trace in self._traces:
            process_call(trace)

        # Clean up statistics
        for stats in statistics.values():
            if stats["min_duration"] == float("inf"):
                stats["min_duration"] = 0

        # Filter by min_duration
        if self.config.min_duration > 0:
            statistics = dict(
                {
                    k: v
                    for k, v in statistics.items()
                    if v["total_duration"] >= self.config.min_duration
                }
            )

        total_calls = int(sum(stats["calls"] for stats in statistics.values()))
        unique_functions = len(statistics)

        memory_end = self._get_memory_usage() if self.config.trace_memory else None

        report = ProfileReport(
            total_duration=total_duration,
            total_cpu_time=total_cpu_time,
            total_calls=total_calls,
            unique_functions=unique_functions,
            call_tree=self._traces,
            statistics=dict(statistics),
            memory_start=self._memory_start,
            memory_end=memory_end,
            memory_peak=self._memory_peak,
            thread_stats=dict(self._thread_stats),
        )

        # Log summary
        self.performance_logger.log_summary(report)

        return report

    def __enter__(self) -> Profiler:
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.stop()


def profile(
    func: Callable | None = None,
    *,
    trace_memory: bool = True,
    trace_calls: bool = True,
    trace_lines: bool = False,
    max_depth: int = 100,
    min_duration: float = 0.0,
    include_builtins: bool = False,
    include_modules: set[str] | None = None,
    exclude_modules: set[str] | None = None,
    log_level: str = "INFO",
    log_calls: bool = True,
    log_args: bool = True,
    log_enabled: bool = True,
    detailed_tracing: bool = False,
    report_path: str | Path | None = None,
    enabled: bool = True,
) -> Callable:
    """
    Decorator for comprehensive performance profiling with detailed logging.

    Args:
        trace_memory: Track memory allocations and GC.
        trace_calls: Track function calls (call tree).
        trace_lines: Track line-by-line execution (high overhead).
        max_depth: Maximum call stack depth to trace.
        min_duration: Minimum duration to include in report.
        include_builtins: Include built-in functions.
        include_modules: Only include these modules.
        exclude_modules: Exclude these modules.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_calls: Log function call enter/exit.
        log_args: Log argument and return value sizes.
        detailed_tracing: Enable verbose call tracing (for debugging).
        report_path: Path to save JSON report.
        enabled: Whether profiling is enabled.

    Returns:
        Decorated function with comprehensive profiling.

    Example:
        @profile(trace_memory=True, log_args=True)
        def process_data(data):
            # Your code here
            return result
    """

    def decorator(func: Callable) -> Callable:
        if not enabled:
            return func

        # Validate function is callable
        if not callable(func):
            raise TypeError(
                f"profile decorator can only be applied to callable objects, got {type(func)}"
            )

        # Set logging level
        try:
            logger.setLevel(getattr(logging, log_level.upper()))
        except AttributeError:
            logger.setLevel(logging.INFO)

        config = ProfileConfig(
            enabled=enabled,
            trace_calls=trace_calls,
            trace_memory=trace_memory,
            trace_lines=trace_lines,
            max_depth=max_depth,
            min_duration=min_duration,
            include_builtins=include_builtins,
            include_modules=include_modules,
            exclude_modules=exclude_modules or set(),
            log_calls=log_calls,
            log_args=log_args,
            log_enabled=log_enabled,
            detailed_tracing=detailed_tracing,
            report_path=Path(report_path) if report_path else None,
            auto_report=report_path is not None,
        )

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                profiler = Profiler(config)
                report = None
                exception_occurred = False

                try:
                    profiler.start()
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    exception_occurred = True
                    # Log the exception but don't swallow it
                    logger.error(f"Exception in {func.__name__}: {e.__class__.__name__}: {e}")
                    raise
                finally:
                    try:
                        profiler.stop()
                        report = profiler.get_report()

                        if config.auto_report and config.report_path:
                            try:
                                report.save(config.report_path)
                            except Exception as save_error:
                                logger.error(f"Failed to save report: {save_error}")

                        # Store report as function attribute
                        async_wrapper.profile_report = report
                    except Exception as cleanup_error:
                        logger.error(f"Error during profiler cleanup: {cleanup_error}")
                        # Don't raise cleanup errors if the main function succeeded
                        if not exception_occurred:
                            logger.warning("Profiler cleanup failed but function succeeded")

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                profiler = Profiler(config)
                report = None
                exception_occurred = False

                try:
                    profiler.start()
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    exception_occurred = True
                    # Log the exception but don't swallow it
                    logger.error(f"Exception in {func.__name__}: {e.__class__.__name__}: {e}")
                    raise
                finally:
                    try:
                        profiler.stop()
                        report = profiler.get_report()

                        if config.auto_report and config.report_path:
                            try:
                                report.save(config.report_path)
                            except Exception as save_error:
                                logger.error(f"Failed to save report: {save_error}")

                        # Store report as function attribute
                        wrapper.profile_report = report
                    except Exception as cleanup_error:
                        logger.error(f"Error during profiler cleanup: {cleanup_error}")
                        # Don't raise cleanup errors if the main function succeeded
                        if not exception_occurred:
                            logger.warning("Profiler cleanup failed but function succeeded")

            return wrapper

    # Handle both @profile and @profile() syntax
    if func is None:
        # Called with parentheses: @profile()
        return decorator
    else:
        # Called without parentheses: @profile
        return decorator(func)
