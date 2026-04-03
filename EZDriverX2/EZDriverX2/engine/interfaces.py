"""Core interface definitions for EZWowX2.

This module defines the core interfaces that must be implemented
by various components to ensure loose coupling and testability.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, Callable
from dataclasses import dataclass


@runtime_checkable
class ICapture(Protocol):
    """Screenshot capture interface.

    Defines the contract for capturing screenshots from the game window.
    """

    @abstractmethod
    def grab_frame(self, timeout_ms: int = 1000) -> "PixelFrame | None":
        """Grab a single frame from the capture source.

        Args:
            timeout_ms: Maximum time to wait for a frame in milliseconds.

        Returns:
            PixelFrame if successful, None if capture failed.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the capture source is available.

        Returns:
            True if capture is available and ready.
        """
        ...


@runtime_checkable
class IBridgeClient(Protocol):
    """Data bridge client interface.

    Defines the contract for fetching game state data from the bridge.
    """

    @abstractmethod
    def fetch(self, timeout: float = 1.0) -> "AttrDict | None":
        """Fetch the latest game state data.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            AttrDict containing game state, or None if request failed.
        """
        ...

    @abstractmethod
    def set_log_callback(self, callback: "Callable[[str], None] | None") -> None:
        """Set the logging callback for this client.

        Args:
            callback: Function to call with log messages, or None to disable.
        """
        ...


@runtime_checkable
class IInputSender(Protocol):
    """Input sending interface.

    Defines the contract for sending keyboard/mouse input to the game window.
    """

    @abstractmethod
    def send_key_to_window(self, hwnd: int, key: str) -> bool:
        """Send a key press to the specified window.

        Args:
            hwnd: Window handle to send input to.
            key: Key name (e.g., 'NUMPAD1', 'F1', 'SHIFT+NUMPAD1').

        Returns:
            True if the key was sent successfully.
        """
        ...

    @abstractmethod
    def send_mouse_to_window(self, hwnd: int, x: int, y: int) -> bool:
        """Send mouse click to the specified window.

        Args:
            hwnd: Window handle to send input to.
            x: X coordinate relative to window.
            y: Y coordinate relative to window.

        Returns:
            True if the mouse event was sent successfully.
        """
        ...


@dataclass(frozen=True, slots=True)
class PixelFrame:
    """Immutable pixel frame.

    Represents a captured frame from the game window with
    pixel data stored in BGRA format.
    """
    width: int
    height: int
    bgra: bytes

    def crop(self, left: int, top: int, right: int, bottom: int) -> "PixelFrame":
        """Return a cropped version of this frame.

        Args:
            left: Left boundary (inclusive).
            top: Top boundary (inclusive).
            right: Right boundary (exclusive).
            bottom: Bottom boundary (exclusive).

        Returns:
            New PixelFrame with cropped region.

        Raises:
            ValueError: If boundaries are invalid.
        """
        if left < 0 or top < 0 or right > self.width or bottom > self.height:
            raise ValueError(f"Crop boundaries out of range: ({left},{top},{right},{bottom})")
        if left >= right or top >= bottom:
            raise ValueError(f"Invalid crop region: left={left}, right={right}, top={top}, bottom={bottom}")

        new_width = right - left
        new_height = bottom - top
        new_bgra = bytearray(new_width * new_height * 4)

        for row in range(new_height):
            src_start = ((top + row) * self.width + left) * 4
            src_end = src_start + new_width * 4
            dst_start = row * new_width * 4
            new_bgra[dst_start:dst_start + new_width * 4] = self.bgra[src_start:src_end]

        return PixelFrame(width=new_width, height=new_height, bgra=bytes(new_bgra))


class AttrDict:
    """Dictionary that allows dot notation access.

    Provides transparent access to nested dictionaries using attribute
    notation. This is a compatibility class - prefer immutable designs
    in new code.
    """

    def __init__(self, data: dict) -> None:
        object.__setattr__(self, "_data", data)

    def __getattr__(self, name: str) -> "AttrDict | None":
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        data = object.__getattribute__(self, "_data")
        value = data.get(name)
        if isinstance(value, dict):
            return AttrDict(value)
        if isinstance(value, list):
            return AttrList(value)
        return value

    def __setattr__(self, name: str, value: object) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        data = object.__getattribute__(self, "_data")
        data[name] = value

    def __getitem__(self, key: str) -> object:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default: object = None) -> object:
        return self._data.get(key, default)

    def to_dict(self) -> dict:
        """Convert back to plain dictionary."""
        return self._data


class AttrList:
    """List that converts nested dictionaries to AttrDict."""

    def __init__(self, data: list) -> None:
        object.__setattr__(self, "_data", data)

    def __getitem__(self, index: int) -> "AttrDict | object":
        value = self._data[index]
        if isinstance(value, dict):
            return AttrDict(value)
        if isinstance(value, list):
            return AttrList(value)
        return value

    def __iter__(self):
        for i, v in enumerate(self._data):
            if isinstance(v, dict):
                yield AttrDict(v)
            elif isinstance(v, list):
                yield AttrList(v)
            else:
                yield v

    def __len__(self) -> int:
        return len(self._data)


@runtime_checkable
class INodeExtractor(Protocol):
    """Node extractor interface.

    Defines the contract for extracting game state nodes from pixel frames.
    """

    @abstractmethod
    def node(self, x: int, y: int) -> "Node":
        """Extract a specific node from the current frame.

        Args:
            x: Node X coordinate.
            y: Node Y coordinate.

        Returns:
            Node object containing the extracted data.
        """
        ...

    @abstractmethod
    def extract_all(self) -> dict[str, object]:
        """Extract all nodes from the current frame.

        Returns:
            Dictionary mapping node IDs to their values.
        """
        ...


@dataclass(frozen=True, slots=True)
class Node:
    """Immutable node data.

    Represents a single node extracted from the pixel grid.
    """
    x: int
    y: int
    color: tuple[int, int, int]
    is_pure: bool
    is_black: bool


class ValidationResult:
    """Result of a validation operation."""

    def __init__(
        self,
        is_valid: bool,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    @staticmethod
    def success() -> "ValidationResult":
        """Create a successful validation result."""
        return ValidationResult(is_valid=True)

    @staticmethod
    def failure(errors: list[str], warnings: list[str] | None = None) -> "ValidationResult":
        """Create a failed validation result."""
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)


@runtime_checkable
class IValidator(Protocol):
    """Validator interface."""

    @abstractmethod
    def validate(self, data: AttrDict) -> ValidationResult:
        """Validate the given data.

        Args:
            data: Data to validate.

        Returns:
            ValidationResult indicating success or failure.
        """
        ...


__all__ = [
    "ICapture",
    "IBridgeClient",
    "IInputSender",
    "INodeExtractor",
    "PixelFrame",
    "Node",
    "AttrDict",
    "AttrList",
    "ValidationResult",
    "IValidator",
]
