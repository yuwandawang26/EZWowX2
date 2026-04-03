"""Exception hierarchy for EZWowX2.

This module defines a structured exception hierarchy for different
error categories in the application.
"""

from typing import Type


class EZWowException(Exception):
    """Base exception for all EZWowX2 exceptions."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self._cause = cause

    @property
    def cause(self) -> Exception | None:
        """Original cause of this exception."""
        return self._cause


class CaptureException(EZWowException):
    """Base class for capture-related exceptions."""
    pass


class CaptureUnavailableException(CaptureException):
    """Raised when capture device is not available."""

    def __init__(self, message: str = "Capture device unavailable", cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class CaptureTimeoutException(CaptureException):
    """Raised when capture operation times out."""

    def __init__(self, message: str = "Capture operation timed out", cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class BridgeException(EZWowException):
    """Base class for bridge-related exceptions."""
    pass


class BridgeConnectionException(BridgeException):
    """Raised when bridge connection fails."""

    def __init__(self, message: str = "Bridge connection failed", cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class BridgeResponseException(BridgeException):
    """Raised when bridge returns an error response."""

    def __init__(self, message: str, status_code: int = 0, cause: Exception | None = None) -> None:
        super().__init__(message, cause)
        self._status_code = status_code

    @property
    def status_code(self) -> int:
        return self._status_code


class InputException(EZWowException):
    """Base class for input-related exceptions."""
    pass


class InputSendException(InputException):
    """Raised when input cannot be sent to window."""

    def __init__(self, message: str, hwnd: int = 0, cause: Exception | None = None) -> None:
        super().__init__(message, cause)
        self._hwnd = hwnd

    @property
    def hwnd(self) -> int:
        return self._hwnd


class InputWindowNotFoundException(InputException):
    """Raised when target window is not found."""

    def __init__(self, message: str = "Target window not found", hwnd: int = 0, cause: Exception | None = None) -> None:
        super().__init__(message, cause)
        self._hwnd = hwnd

    @property
    def hwnd(self) -> int:
        return self._hwnd


class ConfigurationException(EZWowException):
    """Base class for configuration-related exceptions."""
    pass


class ConfigurationNotFoundException(ConfigurationException):
    """Raised when a configuration key is not found."""

    def __init__(self, key: str, cause: Exception | None = None) -> None:
        super().__init__(f"Configuration key not found: {key}", cause)
        self._key = key

    @property
    def key(self) -> str:
        return self._key


class ConfigurationValidationException(ConfigurationException):
    """Raised when configuration value is invalid."""

    def __init__(self, key: str, message: str, cause: Exception | None = None) -> None:
        super().__init__(f"Configuration validation failed for '{key}': {message}", cause)
        self._key = key

    @property
    def key(self) -> str:
        return self._key


class ExtractionException(EZWowException):
    """Base class for node extraction-related exceptions."""
    pass


class ExtractionFailedException(ExtractionException):
    """Raised when node extraction fails."""

    def __init__(self, message: str, node_id: str = "", cause: Exception | None = None) -> None:
        super().__init__(message, cause)
        self._node_id = node_id

    @property
    def node_id(self) -> str:
        return self._node_id


class OcclusionDetectedException(ExtractionException):
    """Raised when occlusion is detected in a region."""

    def __init__(self, region: str, rules: tuple[str, ...] = tuple(), cause: Exception | None = None) -> None:
        super().__init__(f"Occlusion detected in region: {region}", cause)
        self._region = region
        self._rules = rules

    @property
    def region(self) -> str:
        return self._region

    @property
    def rules(self) -> tuple[str, ...]:
        return self._rules


class RecoveryException(EZWowException):
    """Base class for recovery-related exceptions."""
    pass


class MaxRetriesExceededException(RecoveryException):
    """Raised when maximum retry attempts are exceeded."""

    def __init__(self, operation: str, max_attempts: int, cause: Exception | None = None) -> None:
        super().__init__(f"Max retries ({max_attempts}) exceeded for: {operation}", cause)
        self._operation = operation
        self._max_attempts = max_attempts

    @property
    def operation(self) -> str:
        return self._operation

    @property
    def max_attempts(self) -> int:
        return self._max_attempts


EXCEPTION_HIERARCHY: tuple[Type[EZWowException], ...] = (
    EZWowException,
    CaptureException,
    BridgeException,
    InputException,
    ConfigurationException,
    ExtractionException,
    RecoveryException,
)


def classify_exception(exc: Exception) -> str:
    """Classify an exception into its category.

    Args:
        exc: The exception to classify.

    Returns:
        The exception class name as a string.
    """
    for base in EXCEPTION_HIERARCHY:
        if isinstance(exc, base):
            return base.__name__
    return "UnknownException"


def format_exception_chain(exc: Exception) -> str:
    """Format an exception chain as a readable string.

    Args:
        exc: The exception to format.

    Returns:
        A string representation of the exception chain.
    """
    lines = []
    current = exc
    depth = 0

    while current is not None:
        indent = "  " * depth
        if depth == 0:
            lines.append(f"{current.__class__.__name__}: {current}")
        else:
            lines.append(f"{indent}Caused by {current.__class__.__name__}: {current}")
        if hasattr(current, "_cause") and current._cause:
            current = current._cause
            depth += 1
        else:
            current = None

    return "\n".join(lines)


__all__ = [
    "EZWowException",
    "CaptureException",
    "CaptureUnavailableException",
    "CaptureTimeoutException",
    "BridgeException",
    "BridgeConnectionException",
    "BridgeResponseException",
    "InputException",
    "InputSendException",
    "InputWindowNotFoundException",
    "ConfigurationException",
    "ConfigurationNotFoundException",
    "ConfigurationValidationException",
    "ExtractionException",
    "ExtractionFailedException",
    "OcclusionDetectedException",
    "RecoveryException",
    "MaxRetriesExceededException",
    "EXCEPTION_HIERARCHY",
    "classify_exception",
    "format_exception_chain",
]
