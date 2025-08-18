"""Configuration for PerfScope profiling."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProfileConfig:
    """Configuration for profiling with detailed logging.

    Attributes:
        enabled: Whether profiling is enabled.
        trace_calls: Track function calls and create call tree.
        trace_memory: Track memory allocations and GC.
        trace_lines: Track line-by-line execution (high overhead).
        max_depth: Maximum call stack depth to trace.
        min_duration: Minimum duration (seconds) to include in report.
        include_builtins: Include built-in functions in traces.
        include_modules: Only include these modules (if specified).
        exclude_modules: Exclude these modules from tracing.
        log_calls: Log function enter/exit with metrics.
        log_args: Log argument and return value sizes.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        detailed_tracing: Enable verbose call tracing (for debugging).
        report_path: Path to save the JSON report (if specified).
        auto_report: Generate report automatically after profiling.
    """

    enabled: bool = True
    trace_calls: bool = True
    trace_memory: bool = True  # Enable memory tracking by default
    trace_lines: bool = False
    max_depth: int = 100  # Increased for deeper analysis
    min_duration: float = 0.0
    include_builtins: bool = False
    include_modules: set[str] | None = None
    exclude_modules: set[str] = field(
        default_factory=lambda: {
            "perfscope",
            "logging",  # Only exclude essentials for clean output
            "_frozen_importlib",
            "_frozen_importlib_external",
            "importlib",
            "encodings",
        }
    )
    log_calls: bool = True
    log_args: bool = True  # Enable argument logging by default
    log_level: str = "INFO"
    log_enabled: bool = True  # Master switch to enable/disable all logging
    detailed_tracing: bool = False  # Enable detailed call tracing (verbose)
    report_path: Path | None = None
    auto_report: bool = True

    def __post_init__(self):
        """Validate and normalize configuration."""
        if self.max_depth < 1:
            raise ValueError("max_depth must be at least 1")

        if self.max_depth > 1000:
            import warnings

            warnings.warn(
                f"max_depth={self.max_depth} is very high and may impact performance",
                stacklevel=2,
            )

        if self.min_duration < 0:
            raise ValueError("min_duration cannot be negative")

        # Validate log level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")

        if self.report_path is not None:
            self.report_path = Path(self.report_path)

        if self.include_modules is not None:
            self.include_modules = set(self.include_modules)

        self.exclude_modules = set(self.exclude_modules)
