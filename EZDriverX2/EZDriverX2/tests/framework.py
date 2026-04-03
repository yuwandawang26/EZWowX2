"""Test framework utilities.

Provides basic test infrastructure including assertions,
test discovery, and test runner utilities.
"""

import time
import traceback
from dataclasses import dataclass, field
from typing import Callable
from enum import Enum, auto


class TestStatus(Enum):
    """Test execution status."""
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


@dataclass(frozen=True, slots=True)
class TestResult:
    """Immutable test result."""
    name: str
    status: TestStatus
    duration_ms: float
    message: str = ""
    traceback: str = ""


class AssertionError(Exception):
    """Raised when an assertion fails."""
    pass


class TestCase:
    """Base test case class.

    Subclass this and implement test methods starting with 'test_'.
    """

    def set_up(self) -> None:
        """Set up before each test."""
        pass

    def tear_down(self) -> None:
        """Tear down after each test."""
        pass

    def run(self, test_name: str) -> TestResult:
        """Run a single test method."""
        start_time = time.perf_counter()
        try:
            self.set_up()
            method = getattr(self, test_name, None)
            if method is None:
                return TestResult(
                    name=test_name,
                    status=TestStatus.ERROR,
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                    message=f"Test method {test_name} not found",
                )
            method()
            self.tear_down()
            return TestResult(
                name=test_name,
                status=TestStatus.PASSED,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )
        except AssertionError as e:
            self.tear_down()
            return TestResult(
                name=test_name,
                status=TestStatus.FAILED,
                duration_ms=(time.perf_counter() - start_time) * 1000,
                message=str(e),
                traceback=traceback.format_exc(),
            )
        except Exception as e:
            self.tear_down()
            return TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                duration_ms=(time.perf_counter() - start_time) * 1000,
                message=f"{e.__class__.__name__}: {e}",
                traceback=traceback.format_exc(),
            )


class TestSuite:
    """Test suite for grouping test cases."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._tests: list[tuple[TestCase, str]] = []

    def add(self, test_case: TestCase, test_name: str) -> None:
        """Add a test to the suite."""
        self._tests.append((test_case, test_name))

    def run(self) -> list[TestResult]:
        """Run all tests in the suite."""
        results = []
        for test_case, test_name in self._tests:
            result = test_case.run(test_name)
            results.append(result)
        return results


class TestRunner:
    """Test runner with reporting."""

    def __init__(self) -> None:
        self._results: list[TestResult] = []

    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self._results.append(result)

    def run_suite(self, suite: TestSuite) -> list[TestResult]:
        """Run a test suite."""
        results = suite.run()
        self._results.extend(results)
        return results

    def get_summary(self) -> tuple[int, int, int, int]:
        """Get test counts.

        Returns:
            Tuple of (passed, failed, skipped, error)
        """
        passed = sum(1 for r in self._results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self._results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self._results if r.status == TestStatus.SKIPPED)
        error = sum(1 for r in self._results if r.status == TestStatus.ERROR)
        return passed, failed, skipped, error

    def print_report(self) -> None:
        """Print test report."""
        passed, failed, skipped, error = self.get_summary()
        total = len(self._results)

        print(f"\n{'='*60}")
        print(f"Test Results: {total} total")
        print(f"  Passed:  {passed}")
        print(f"  Failed:  {failed}")
        print(f"  Skipped: {skipped}")
        print(f"  Error:   {error}")
        print(f"{'='*60}\n")

        for result in self._results:
            if result.status != TestStatus.PASSED:
                status_symbol = {
                    TestStatus.FAILED: "FAIL",
                    TestStatus.ERROR: "ERR",
                    TestStatus.SKIPPED: "SKIP",
                }.get(result.status, "???")

                print(f"[{status_symbol}] {result.name} ({result.duration_ms:.2f}ms)")
                if result.message:
                    print(f"  {result.message}")
                if result.traceback:
                    print(result.traceback)
                print()


def assert_equal(actual: object, expected: object, message: str = "") -> None:
    """Assert that two values are equal."""
    if actual != expected:
        msg = f"Expected {expected!r}, got {actual!r}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)


def assert_true(condition: bool, message: str = "") -> None:
    """Assert that a condition is True."""
    if not condition:
        msg = "Expected True, got False"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)


def assert_false(condition: bool, message: str = "") -> None:
    """Assert that a condition is False."""
    if condition:
        msg = "Expected False, got True"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)


def assert_none(value: object, message: str = "") -> None:
    """Assert that a value is None."""
    if value is not None:
        msg = f"Expected None, got {value!r}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)


def assert_not_none(value: object, message: str = "") -> None:
    """Assert that a value is not None."""
    if value is None:
        msg = "Expected not None"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)


def assert_raises(exception_type: type[Exception], callable_: Callable, *args: object, **kwargs: object) -> None:
    """Assert that an exception is raised."""
    try:
        callable_(*args, **kwargs)
        raise AssertionError(f"Expected {exception_type.__name__} to be raised")
    except exception_type:
        pass


__all__ = [
    "TestStatus",
    "TestResult",
    "TestCase",
    "TestSuite",
    "TestRunner",
    "AssertionError",
    "assert_equal",
    "assert_true",
    "assert_false",
    "assert_none",
    "assert_not_none",
    "assert_raises",
]
