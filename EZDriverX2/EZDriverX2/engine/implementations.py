"""Production implementations for core interfaces.

These implementations provide real functionality using
actual system libraries and APIs.
"""

import ctypes
import time
from typing import Callable
from dataclasses import dataclass

try:
    import dxcam
except ImportError:
    dxcam = None

try:
    import requests
except ImportError:
    requests = None

from .interfaces import (
    ICapture,
    IBridgeClient,
    IInputSender,
    INodeExtractor,
    PixelFrame,
    Node,
    AttrDict,
)


@dataclass(frozen=True, slots=True)
class WindowInfo:
    """Information about a window."""
    hwnd: int
    title: str
    rect_left: int
    rect_top: int
    rect_right: int
    rect_bottom: int


def find_wow_window() -> WindowInfo | None:
    """Find the World of Warcraft window.

    Returns:
        WindowInfo if found, None otherwise.
    """
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible
    GetWindowRect = ctypes.windll.user32.GetWindowRect

    result = [None]

    def callback(hwnd, _):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buffer, length + 1)
                title = buffer.value
                if "魔兽世界" in title or "World of Warcraft" in title:
                    rect = ctypes.Structure
                    class RECT(ctypes.Structure):
                        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
                    r = RECT()
                    GetWindowRect(hwnd, ctypes.byref(r))
                    result[0] = WindowInfo(
                        hwnd=int(hwnd),
                        title=title,
                        rect_left=r.left,
                        rect_top=r.top,
                        rect_right=r.right,
                        rect_bottom=r.bottom,
                    )
                    return False
        return True

    EnumWindows(EnumWindowsProc(callback), None)
    return result[0]


class DxCapture(ICapture):
    """Production implementation of ICapture using dxcam.

    This capture uses the dxcam library to capture the game window.
    """

    def __init__(self, target_hwnd: int | None = None) -> None:
        if dxcam is None:
            raise ImportError("dxcam is required for DxCapture: pip install dxcam")

        self._camera = dxcam.create()
        self._target_hwnd = target_hwnd
        self._available = True

        if target_hwnd is None:
            window = find_wow_window()
            if window:
                self._target_hwnd = window.hwnd

    def grab_frame(self, timeout_ms: int = 1000) -> PixelFrame | None:
        if not self._available or self._target_hwnd is None:
            return None

        try:
            img = self._camera.grab(target_hwnd=self._target_hwnd)
            if img is None:
                return None

            if img.shape[2] == 3:
                bgra = img[:, :, [2, 1, 0, 3]] if img.shape[2] == 4 else img[:, :, [2, 1, 0]]
                bgra = bgra.reshape(-1).tobytes()
            else:
                bgra = img.reshape(-1).tobytes()

            height, width = img.shape[:2]
            return PixelFrame(width=width, height=height, bgra=bgra)
        except Exception:
            return None

    def is_available(self) -> bool:
        return self._available and self._target_hwnd is not None

    def release(self) -> None:
        """Release the capture resource."""
        if self._camera:
            self._camera.release()
            self._camera = None
        self._available = False


class HttpBridgeClient(IBridgeClient):
    """Production implementation of IBridgeClient using HTTP.

    This client fetches game state from a REST API endpoint.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8080", api_key: str | None = None) -> None:
        if requests is None:
            raise ImportError("requests is required for HttpBridgeClient: pip install requests")

        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        if api_key:
            self._session.headers.update({"Authorization": f"Bearer {api_key}"})
        self._log_callback: Callable[[str], None] | None = None

    def fetch(self, timeout: float = 1.0) -> AttrDict | None:
        try:
            response = self._session.get(
                f"{self._base_url}/api/v1/state",
                timeout=timeout,
            )
            if response.status_code == 200:
                return AttrDict(response.json())
            else:
                if self._log_callback:
                    self._log_callback(f"HTTP {response.status_code}: {response.text[:200]}")
                return None
        except requests.exceptions.RequestException as e:
            if self._log_callback:
                self._log_callback(f"Request failed: {e}")
            return None

    def set_log_callback(self, callback: Callable[[str], None] | None) -> None:
        self._log_callback = callback

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()


class Win32InputSender(IInputSender):
    """Production implementation of IInputSender using Win32 API.

    This sender uses SendMessage to send input to the game window.
    """

    def __init__(self) -> None:
        self._user32 = ctypes.windll.user32

        self._KEY_MAP = {
            "NUMPAD0": 0x60, "NUMPAD1": 0x61, "NUMPAD2": 0x62, "NUMPAD3": 0x63,
            "NUMPAD4": 0x64, "NUMPAD5": 0x65, "NUMPAD6": 0x66, "NUMPAD7": 0x67,
            "NUMPAD8": 0x68, "NUMPAD9": 0x69,
            "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
            "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
            "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
            "SPACE": 0x20, "ENTER": 0x0D, "ESCAPE": 0x1B, "TAB": 0x09,
            "SHIFT": 0x10, "CTRL": 0x11, "ALT": 0x12,
        }

        self._MODIFIER_KEYS = {"SHIFT", "CTRL", "ALT"}

    def send_key_to_window(self, hwnd: int, key: str) -> bool:
        parts = key.upper().split("+")
        if len(parts) == 1:
            vk = self._get_vk(parts[0])
            if vk is None:
                return False
            return self._send_key(hwnd, vk)
        else:
            vk = self._get_vk(parts[-1])
            if vk is None:
                return False

            modifiers = []
            for mod in parts[:-1]:
                mod_vk = self._get_vk(mod)
                if mod_vk and mod in self._MODIFIER_KEYS:
                    modifiers.append(mod_vk)

            for mod_vk in modifiers:
                self._send_keydown(hwnd, mod_vk)
            time.sleep(0.01)
            result = self._send_key(hwnd, vk)
            time.sleep(0.01)
            for mod_vk in reversed(modifiers):
                self._send_keyup(hwnd, mod_vk)

            return result

    def send_mouse_to_window(self, hwnd: int, x: int, y: int) -> bool:
        lparam = (y << 16) | (x & 0xFFFF)
        self._user32.SendMessageW(hwnd, 0x0201, 0, lparam)
        time.sleep(0.01)
        self._user32.SendMessageW(hwnd, 0x0202, 0, lparam)
        return True

    def _get_vk(self, key: str) -> int | None:
        if key in self._KEY_MAP:
            return self._KEY_MAP[key]
        if len(key) == 1:
            vk = self._user32.VkKeyScanW(key)
            if vk != -1:
                return vk & 0xFF
        return None

    def _send_key(self, hwnd: int, vk: int) -> bool:
        self._send_keydown(hwnd, vk)
        time.sleep(0.01)
        self._send_keyup(hwnd, vk)
        return True

    def _send_keydown(self, hwnd: int, vk: int) -> None:
        self._user32.SendMessageW(hwnd, 0x0100, vk, 0)

    def _send_keyup(self, hwnd: int, vk: int) -> None:
        self._user32.SendMessageW(hwnd, 0x0101, vk, 0)


__all__ = [
    "WindowInfo",
    "find_wow_window",
    "DxCapture",
    "HttpBridgeClient",
    "Win32InputSender",
]
