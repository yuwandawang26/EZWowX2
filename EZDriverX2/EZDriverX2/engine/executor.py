"""Action execution layer."""

from __future__ import annotations

from typing import Callable

from ..config.macros import MacroRegistry
from ..contracts.actions import Action, IdleAction
from ..input.win32_sender import Win32Sender


class ActionExecutor:
    def __init__(self, macros: MacroRegistry, sender: Win32Sender) -> None:
        self._macros = macros
        self._sender = sender
        self._target_hwnd: int | None = None
        self._log_callback: Callable[[str], None] | None = None

    def set_log_callback(self, callback: Callable[[str], None] | None) -> None:
        self._log_callback = callback

    def set_target_window(self, hwnd: int | None) -> None:
        self._target_hwnd = hwnd

    def get_target_window(self) -> int | None:
        return self._target_hwnd

    def _log(self, message: str) -> None:
        if self._log_callback:
            self._log_callback(message)

    def execute(self, action: Action) -> None:
        if isinstance(action, IdleAction):
            self._log(f"空闲: {action.reason}")
            return

        logical_key = f"{action.unitToken}{action.spell}"
        self._execute_macro(logical_key, f"{action.spell} -> {action.unitToken}")

    def _execute_macro(self, logical_key: str, message: str) -> None:
        hotkey = self._macros.get(logical_key)
        if not hotkey:
            self._log(f"未找到 macro: {logical_key}")
            return
        hwnd = self._target_hwnd
        if hwnd is None:
            self._log(f"发送按键失败: 未选择窗体 ({hotkey})")
            return
        ok = self._sender.send_key_to_window(hwnd, hotkey)
        if ok:
            self._log(f"施法: {message} (按键: {hotkey})")
            return
        self._log(f"发送按键失败: {hotkey}")
