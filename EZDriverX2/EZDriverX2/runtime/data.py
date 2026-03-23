"""Flexible dictionary access helpers."""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from typing import Any, Self, cast


class NoneObject:
    """Null object for safe chained access."""

    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getattr__(self, name: str) -> Self:
        return self

    def __setattr__(self, name: str, value: Any) -> None:
        return

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return "NoneObject"

    def __repr__(self) -> str:
        return "NoneObject"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NoneObject) or other is None

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __len__(self) -> int:
        return 0


class AttrDict(dict[str, Any]):
    """Dict with dot access and tolerant missing-key behavior."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._convert_nested()

    def _convert_nested(self) -> None:
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = AttrDict(value)
            elif isinstance(value, list):
                self[key] = self._convert_list(cast(list[Any], value))

    def _convert_list(self, items: list[Any]) -> list[Any]:
        converted: list[Any] = []
        for item in items:
            if isinstance(item, dict):
                converted.append(AttrDict(item))
            elif isinstance(item, list):
                converted.append(self._convert_list(cast(list[Any], item)))
            else:
                converted.append(item)
        return converted

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            warnings.warn(
                f"访问不存在的键: '{key}'，返回 NoneObject。",
                UserWarning,
                stacklevel=2,
            )
            return NoneObject()

    def __getitem__(self, key: str) -> Any:
        try:
            return super().__getitem__(key)
        except KeyError:
            warnings.warn(
                f"访问不存在的键: '{key}'，返回 NoneObject。",
                UserWarning,
                stacklevel=2,
            )
            return NoneObject()

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            super().__setattr__(key, value)
            return
        if isinstance(value, dict):
            self[key] = AttrDict(value)
        else:
            self[key] = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"
