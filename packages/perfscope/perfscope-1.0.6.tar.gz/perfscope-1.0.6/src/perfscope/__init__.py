"""
PerfScope - The Ultimate Python Performance Profiler & APM Tool

PerfScope is the most advanced Python performance profiler and application
performance monitoring (APM) tool. Get real-time insights into function execution
time, memory consumption, call hierarchies, and bottleneck detection with zero
configuration.

Perfect for:
- Django, Flask, FastAPI web applications
- Async/await and concurrent applications
- Data science and machine learning pipelines
- Production performance monitoring
- Memory leak detection and analysis
- API performance optimization
- Microservices performance tracking

Key Features:
- Production-ready logging with [PerfScope] identifiers
- Advanced performance analytics (CPU, memory, call frequency)
- Full async/await support for modern Python applications
- Interactive call tree visualization in HTML reports
- Memory leak detection with garbage collection tracking
- Export reports in HTML, JSON, CSV formats
- Minimal overhead (2-5% in production)
- Smart filtering and bottleneck detection
- Zero runtime dependencies
- Enterprise-ready with configurable logging levels

Quick Start:
    >>> from perfscope import profile
    >>>
    >>> @profile()
    >>> def your_function():
    ...     # Your code here
    ...     pass
    >>>
    >>> # Automatically generates performance logs and reports!

Advanced Usage:
    >>> @profile(
    ...     trace_memory=True,
    ...     report_path="performance_analysis.html",
    ...     min_duration=0.001  # Only log functions > 1ms
    ... )
    >>> async def process_data(data):
    ...     # Your async code here
    ...     return processed_data

For more examples and documentation, visit:
https://github.com/sattyamjain/perfscope
"""

from __future__ import annotations

__version__ = "1.0.4"
__author__ = "Sattyam Jain"
__license__ = "MIT"

from perfscope.config import ProfileConfig

# Main decorator - this is what most users will use
# Additional components for advanced usage
from perfscope.profiler import (
    CallInfo,
    PerformanceMetrics,
    Profiler,
    ProfileReport,
    profile,
)

__all__ = [
    "profile",
    "Profiler",
    "ProfileConfig",
    "ProfileReport",
    "CallInfo",
    "PerformanceMetrics",
    "__version__",
]

# Simple usage:
# @profile()
# def your_function():
#     pass

# Advanced usage with logging:
# @profile(trace_memory=True, log_args=True, log_level="DEBUG")
# async def your_async_function():
#     pass
