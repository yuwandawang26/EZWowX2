"""HTTP client for EZPixelBridgeX2 endpoint."""

from __future__ import annotations

from typing import Callable

import requests

from ..runtime.data import AttrDict


class BridgeClient:
    def __init__(self, api_url: str = "http://127.0.0.1:65131/api") -> None:
        self._api_url = api_url
        self._session = requests.Session()
        self._log_callback: Callable[[str], None] | None = None

    def set_log_callback(self, callback: Callable[[str], None] | None) -> None:
        self._log_callback = callback

    def _log(self, message: str) -> None:
        if self._log_callback:
            self._log_callback(message)

    def fetch(self) -> AttrDict | None:
        try:
            response = self._session.get(self._api_url, timeout=1.0)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                self._log("Bridge 返回数据不是 JSON 对象。")
                return None
            return AttrDict(payload)
        except requests.RequestException as exc:
            self._log(f"Bridge 请求失败: {exc}")
            return None
        except Exception as exc:
            self._log(f"Bridge 数据解析失败: {exc}")
            return None
