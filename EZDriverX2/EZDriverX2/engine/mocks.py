"""Mock implementations for core interfaces.

These implementations are used for testing and development.
They provide safe, no-op or simulated behavior.
"""

import time
from typing import Callable
from .interfaces import (
    ICapture,
    IBridgeClient,
    IInputSender,
    INodeExtractor,
    PixelFrame,
    Node,
    AttrDict,
)


class MockCapture(ICapture):
    """Mock implementation of ICapture for testing.

    This capture returns blank frames and is useful for
    testing the capture interface without a real game window.
    """

    def __init__(self, width: int = 64, height: int = 64) -> None:
        self._width = width
        self._height = height
        self._available = True

    def grab_frame(self, timeout_ms: int = 1000) -> PixelFrame | None:
        if not self._available:
            return None
        pixel_count = self._width * self._height
        bgra = b"\x00\x00\x00\xFF" * pixel_count
        return PixelFrame(width=self._width, height=self._height, bgra=bgra)

    def is_available(self) -> bool:
        return self._available

    def set_available(self, available: bool) -> None:
        self._available = available


class MockBridgeClient(IBridgeClient):
    """Mock implementation of IBridgeClient for testing.

    This client returns empty data and is useful for testing
    the bridge interface without a real backend.
    """

    def __init__(self) -> None:
        self._log_callback: Callable[[str], None] | None = None
        self._fetch_count = 0
        self._data = AttrDict({"player": AttrDict({"health": 100, "power": 50}), "target": None})

    def fetch(self, timeout: float = 1.0) -> AttrDict | None:
        self._fetch_count += 1
        if self._log_callback:
            self._log_callback(f"MockBridgeClient.fetch() called (count={self._fetch_count})")
        return self._data

    def set_log_callback(self, callback: Callable[[str], None] | None) -> None:
        self._log_callback = callback

    @property
    def fetch_count(self) -> int:
        return self._fetch_count


class MockInputSender(IInputSender):
    """Mock implementation of IInputSender for testing.

    This sender logs key/mouse events but does not actually
    send input to any window.
    """

    def __init__(self) -> None:
        self._sent_keys: list[tuple[int, str]] = []
        self._sent_mouse: list[tuple[int, int, int]] = []
        self._enabled = True

    def send_key_to_window(self, hwnd: int, key: str) -> bool:
        if not self._enabled:
            return False
        self._sent_keys.append((hwnd, key))
        return True

    def send_mouse_to_window(self, hwnd: int, x: int, y: int) -> bool:
        if not self._enabled:
            return False
        self._sent_mouse.append((hwnd, x, y))
        return True

    @property
    def sent_keys(self) -> list[tuple[int, str]]:
        return list(self._sent_keys)

    @property
    def sent_mouse(self) -> list[tuple[int, int, int]]:
        return list(self._sent_mouse)

    def clear(self) -> None:
        self._sent_keys.clear()
        self._sent_mouse.clear()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled


class MockNodeExtractor(INodeExtractor):
    """Mock implementation of INodeExtractor for testing.

    This extractor returns empty/zero nodes and is useful for
    testing the extractor interface.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._extracted_count = 0

    def node(self, x: int, y: int) -> Node:
        key = f"{x},{y}"
        if key not in self._nodes:
            self._nodes[key] = Node(x=x, y=y, color=(0, 0, 0), is_pure=True, is_black=True)
        return self._nodes[key]

    def extract_all(self) -> dict[str, object]:
        self._extracted_count += 1
        return {
            "player_health": 100,
            "player_power": 50,
            "target_health": None,
            "target_power": None,
        }

    @property
    def extracted_count(self) -> int:
        return self._extracted_count


__all__ = [
    "MockCapture",
    "MockBridgeClient",
    "MockInputSender",
    "MockNodeExtractor",
]
