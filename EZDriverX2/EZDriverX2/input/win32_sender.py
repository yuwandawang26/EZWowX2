"""Win32 key sender and window enumeration."""

from __future__ import annotations

import os
from typing import Any

IS_WINDOWS = os.name == "nt"

try:
    from ctypes import WINFUNCTYPE, create_unicode_buffer, windll, wintypes
except ImportError:  # pragma: no cover - non-Windows runtime
    WINFUNCTYPE = None  # type: ignore[assignment]
    create_unicode_buffer = None  # type: ignore[assignment]
    windll = None  # type: ignore[assignment]
    wintypes = None  # type: ignore[assignment]

USER32 = windll.user32 if IS_WINDOWS and windll is not None else None

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

VK_DICT = {
    "SHIFT": 0x10,
    "CTRL": 0x11,
    "ALT": 0x12,
    "NUMPAD0": 0x60,
    "NUMPAD1": 0x61,
    "NUMPAD2": 0x62,
    "NUMPAD3": 0x63,
    "NUMPAD4": 0x64,
    "NUMPAD5": 0x65,
    "NUMPAD6": 0x66,
    "NUMPAD7": 0x67,
    "NUMPAD8": 0x68,
    "NUMPAD9": 0x69,
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
}


class Win32Sender:
    def list_windows(self) -> list[tuple[int, str]]:
        if (
            not IS_WINDOWS
            or USER32 is None
            or WINFUNCTYPE is None
            or create_unicode_buffer is None
            or wintypes is None
        ):
            return []

        user32 = USER32
        callback_factory = WINFUNCTYPE
        c_buffer = create_unicode_buffer
        win_types = wintypes

        results: list[tuple[int, str]] = []

        callback_type = callback_factory(win_types.BOOL, win_types.HWND, win_types.LPARAM)

        @callback_type
        def enum_proc(hwnd: Any, lparam: Any) -> bool:
            del lparam
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            buffer = c_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value.strip()
            if title:
                results.append((int(hwnd), title))
            return True

        user32.EnumWindows(enum_proc, 0)
        return results

    def send_key_to_window(self, hwnd: int, combo: str) -> bool:
        if not IS_WINDOWS:
            return False
        if hwnd <= 0:
            return False
        if USER32 is None:
            return False
        try:
            self._send_hotkey(hwnd, combo)
            return True
        except Exception:
            return False

    def _press_key(self, hwnd: int, key_name: str) -> None:
        if USER32 is None:
            raise RuntimeError("Win32 API unavailable")
        key = VK_DICT.get(key_name)
        if key is None:
            raise KeyError(f"Virtual key '{key_name}' not found")
        USER32.PostMessageW(hwnd, WM_KEYDOWN, key, 0)

    def _release_key(self, hwnd: int, key_name: str) -> None:
        if USER32 is None:
            raise RuntimeError("Win32 API unavailable")
        key = VK_DICT.get(key_name)
        if key is None:
            raise KeyError(f"Virtual key '{key_name}' not found")
        USER32.PostMessageW(hwnd, WM_KEYUP, key, 0)

    def _send_hotkey(self, hwnd: int, hot_key: str) -> None:
        if windll is None:
            raise RuntimeError("Win32 API unavailable")
        key_parts = hot_key.split("-")
        for key_name in key_parts:
            self._press_key(hwnd, key_name)
        windll.kernel32.Sleep(10)
        for key_name in reversed(key_parts):
            self._release_key(hwnd, key_name)
