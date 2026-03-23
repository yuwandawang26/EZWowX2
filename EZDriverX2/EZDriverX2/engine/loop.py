"""Main runtime scheduler loop."""

from __future__ import annotations

import random
import threading
import time
import traceback
from typing import Callable

from ..config.registry import ConfigRegistry
from ..contracts.actions import Action
from ..contracts.profile import RotationProfile
from ..runtime.context import RotationContext
from ..transport.bridge_client import BridgeClient
from .executor import ActionExecutor


class RotationLoopEngine:
    def __init__(
        self,
        profile: RotationProfile,
        config: ConfigRegistry,
        bridge_client: BridgeClient,
        executor: ActionExecutor,
    ) -> None:
        self.profile = profile
        self.config = config
        self.bridge_client = bridge_client
        self.executor = executor

        self._running = False
        self._thread: threading.Thread | None = None
        self._log_callback: Callable[[str], None] | None = None

    def set_log_callback(self, callback: Callable[[str], None] | None) -> None:
        self._log_callback = callback
        self.executor.set_log_callback(callback)
        self.bridge_client.set_log_callback(callback)

    def _log(self, message: str) -> None:
        if self._log_callback:
            self._log_callback(message)

    def set_target_window(self, hwnd: int | None) -> None:
        self.executor.set_target_window(hwnd)

    def get_target_window(self) -> int | None:
        return self.executor.get_target_window()

    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._log("引擎已启动")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._log("引擎已停止")

    def _config_float(self, key: str, fallback: float) -> float:
        value = self.config.get_or_default(key)
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    def _compute_interval(self) -> float:
        fps = max(1.0, self._config_float("fps", 15.0))
        base_interval = 1.0 / fps
        jitter = self._config_float("interval_jitter", 0.2)
        jitter = max(0.0, min(0.9, jitter))
        return base_interval * random.uniform(1 - jitter, 1 + jitter)

    def _loop(self) -> None:
        while self._running:
            interval = self._compute_interval()
            data = self.bridge_client.fetch()
            if data is None:
                time.sleep(interval / 5)
                continue

            if data.get("error"):
                self._log(str(data.error))
                time.sleep(interval / 5)
                continue

            context = RotationContext(data, self.config)
            try:
                action: Action = self.profile.main_rotation(context)
                self.executor.execute(action)
            except Exception as exc:
                self._log(f"循环执行错误: {exc}")
                self._log(traceback.format_exc())

            time.sleep(interval)
