"""Macro mapping registry."""

from __future__ import annotations


class MacroRegistry:
    def __init__(self) -> None:
        self._mapping: dict[str, str] = {}

    def set(self, logical_key: str, hotkey: str) -> None:
        self._mapping[logical_key] = hotkey

    def get(self, logical_key: str) -> str | None:
        return self._mapping.get(logical_key)

    def all(self) -> dict[str, str]:
        return dict(self._mapping)

