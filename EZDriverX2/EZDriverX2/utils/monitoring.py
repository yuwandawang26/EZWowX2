"""Structured logging and monitoring module.

Provides structured logging with different log levels, performance
metrics collection, and health check mechanisms.
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable
from collections import defaultdict


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass(frozen=True, slots=True)
class LogEntry:
    """Immutable log entry."""
    timestamp: float
    level: LogLevel
    message: str
    source: str = ""


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    """Immutable performance metrics snapshot."""
    operation_name: str
    count: int
    total_time: float
    min_time: float
    max_time: float
    avg_time: float
    p99_time: float


class StructuredLogger:
    """Structured logger with level filtering and callbacks."""

    def __init__(self, min_level: LogLevel = LogLevel.INFO) -> None:
        self._min_level = min_level
        self._log_callbacks: list[Callable[[LogEntry], None]] = []
        self._history: list[LogEntry] = []
        self._max_history = 1000
        self._lock = threading.Lock()

    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """Add a log callback."""
        self._log_callbacks.append(callback)

    def remove_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """Remove a log callback."""
        if callback in self._log_callbacks:
            self._log_callbacks.remove(callback)

    def set_level(self, level: LogLevel) -> None:
        """Set minimum log level."""
        object.__setattr__(self, "_min_level", level)

    def debug(self, message: str, source: str = "") -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message, source)

    def info(self, message: str, source: str = "") -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message, source)

    def warning(self, message: str, source: str = "") -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message, source)

    def error(self, message: str, source: str = "") -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, message, source)

    def critical(self, message: str, source: str = "") -> None:
        """Log a critical message."""
        self._log(LogLevel.CRITICAL, message, source)

    def _log(self, level: LogLevel, message: str, source: str) -> None:
        if level.value < self._min_level.value:
            return

        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            source=source,
        )

        with self._lock:
            self._history.append(entry)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        for callback in self._log_callbacks:
            try:
                callback(entry)
            except Exception:
                pass

    def get_history(self, level: LogLevel | None = None, limit: int = 100) -> list[LogEntry]:
        """Get log history."""
        with self._lock:
            if level is None:
                return list(self._history[-limit:])
            return [e for e in self._history if e.level == level][-limit:]

    def clear_history(self) -> None:
        """Clear log history."""
        with self._lock:
            self._history.clear()


class PerformanceMonitor:
    """Monitors performance metrics for operations."""

    def __init__(self) -> None:
        self._metrics: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, operation_name: str, duration_ms: float) -> None:
        """Record a performance measurement."""
        with self._lock:
            self._metrics[operation_name].append(duration_ms)
            if len(self._metrics[operation_name]) > 10000:
                self._metrics[operation_name] = self._metrics[operation_name][-5000:]

    def get_metrics(self, operation_name: str) -> PerformanceMetrics | None:
        """Get metrics for an operation."""
        with self._lock:
            if operation_name not in self._metrics:
                return None

            times = sorted(self._metrics[operation_name])
            count = len(times)

            if count == 0:
                return PerformanceMetrics(
                    operation_name=operation_name,
                    count=0,
                    total_time=0.0,
                    min_time=0.0,
                    max_time=0.0,
                    avg_time=0.0,
                    p99_time=0.0,
                )

            total = sum(times)
            return PerformanceMetrics(
                operation_name=operation_name,
                count=count,
                total_time=total,
                min_time=times[0],
                max_time=times[-1],
                avg_time=total / count,
                p99_time=times[int(count * 0.99)] if count > 0 else 0.0,
            )

    def get_all_metrics(self) -> dict[str, PerformanceMetrics]:
        """Get all metrics."""
        return {
            name: self.get_metrics(name)
            for name in self._metrics.keys()
        }

    def clear(self, operation_name: str | None = None) -> None:
        """Clear metrics."""
        with self._lock:
            if operation_name is None:
                self._metrics.clear()
            elif operation_name in self._metrics:
                del self._metrics[operation_name]


class HealthCheck:
    """Health check system for components."""

    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], bool]] = {}

    def register(self, name: str, check: Callable[[], bool]) -> None:
        """Register a health check."""
        self._checks[name] = check

    def unregister(self, name: str) -> None:
        """Unregister a health check."""
        if name in self._checks:
            del self._checks[name]

    def check_all(self) -> tuple[bool, dict[str, bool]]:
        """Run all health checks.

        Returns:
            Tuple of (overall_healthy, individual_results)
        """
        results = {}
        for name, check in self._checks.items():
            try:
                results[name] = check()
            except Exception:
                results[name] = False

        overall = all(results.values())
        return overall, results


class Timer:
    """Context manager for timing operations."""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str) -> None:
        self._monitor = monitor
        self._operation_name = operation_name
        self._start_time: float = 0.0

    def __enter__(self) -> "Timer":
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        duration_ms = (time.perf_counter() - self._start_time) * 1000
        self._monitor.record(self._operation_name, duration_ms)


_global_logger = StructuredLogger()
_global_monitor = PerformanceMonitor()
_global_health_check = HealthCheck()


def get_logger() -> StructuredLogger:
    """Get the global logger instance."""
    return _global_logger


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _global_monitor


def get_health_check() -> HealthCheck:
    """Get the global health check instance."""
    return _global_health_check


__all__ = [
    "LogLevel",
    "LogEntry",
    "PerformanceMetrics",
    "StructuredLogger",
    "PerformanceMonitor",
    "HealthCheck",
    "Timer",
    "get_logger",
    "get_monitor",
    "get_health_check",
]
