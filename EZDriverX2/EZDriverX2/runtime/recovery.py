"""Recovery executor with retry logic.

Provides utilities for executing operations with retry and backoff.
"""

import time
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

from .exceptions import MaxRetriesExceededException


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Immutable retry policy configuration.

    Defines how many times to retry and with what backoff strategy.
    """
    max_attempts: int
    base_delay: float = 0.1
    max_delay: float = 5.0
    exponential_base: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.

        Args:
            attempt: The attempt number (0-indexed).

        Returns:
            Delay in seconds before next retry.
        """
        if attempt <= 0:
            return self.base_delay

        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


@dataclass(frozen=True, slots=True)
class RetryStats:
    """Immutable statistics for a retry operation."""
    total_attempts: int
    successful: bool
    final_error: str | None
    total_time: float


class RecoveryExecutor:
    """Executes operations with retry logic.

    Supports exponential backoff and configurable retry policies.
    """

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self._policy = policy or RetryPolicy(max_attempts=3)

    @property
    def policy(self) -> RetryPolicy:
        return self._policy

    def execute_with_retry(
        self,
        operation: Callable[[], T],
        operation_name: str = "operation",
    ) -> T:
        """Execute an operation with retry logic.

        Args:
            operation: The operation to execute.
            operation_name: Name for error messages.

        Returns:
            The result of the operation.

        Raises:
            MaxRetriesExceededException: If all retry attempts fail.
        """
        last_error: Exception | None = None
        start_time = time.time()

        for attempt in range(self._policy.max_attempts):
            try:
                result = operation()
                total_time = time.time() - start_time
                return result
            except Exception as e:
                last_error = e
                if attempt < self._policy.max_attempts - 1:
                    delay = self._policy.get_delay(attempt)
                    time.sleep(delay)

        total_time = time.time() - start_time
        raise MaxRetriesExceededException(
            operation=operation_name,
            max_attempts=self._policy.max_attempts,
            cause=last_error,
        )

    def execute_with_retry_async(
        self,
        operation: Callable[[], T],
        operation_name: str = "operation",
    ) -> tuple[T, RetryStats]:
        """Execute an operation and return stats along with result.

        Args:
            operation: The operation to execute.
            operation_name: Name for error messages.

        Returns:
            Tuple of (result, RetryStats).
        """
        last_error: Exception | None = None
        start_time = time.time()

        for attempt in range(self._policy.max_attempts):
            try:
                result = operation()
                total_time = time.time() - start_time
                stats = RetryStats(
                    total_attempts=attempt + 1,
                    successful=True,
                    final_error=None,
                    total_time=total_time,
                )
                return result, stats
            except Exception as e:
                last_error = e
                if attempt < self._policy.max_attempts - 1:
                    delay = self._policy.get_delay(attempt)
                    time.sleep(delay)

        total_time = time.time() - start_time
        stats = RetryStats(
            total_attempts=self._policy.max_attempts,
            successful=False,
            final_error=str(last_error) if last_error else "Unknown error",
            total_time=total_time,
        )

        raise MaxRetriesExceededException(
            operation=operation_name,
            max_attempts=self._policy.max_attempts,
            cause=last_error,
        )


def with_retry(
    policy: RetryPolicy | None = None,
    operation_name: str = "operation",
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """Decorator to add retry logic to a function.

    Args:
        policy: Retry policy to use.
        operation_name: Name for error messages.

    Returns:
        Decorated function with retry logic.
    """
    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        def wrapper() -> T:
            executor = RecoveryExecutor(policy)
            return executor.execute_with_retry(func, operation_name)
        return wrapper
    return decorator


__all__ = [
    "RetryPolicy",
    "RetryStats",
    "RecoveryExecutor",
    "with_retry",
]
