"""Runtime config registry."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from .items import ConfigItem


class ConfigRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ConfigItem] = {}
        self._allow_gui_writes = False

    def add(self, item: ConfigItem) -> None:
        if item.key in self._items:
            raise KeyError(f"Config key already exists: {item.key}")
        item.attach_owner(self)
        self._items[item.key] = item

    @contextmanager
    def gui_write(self):
        previous = self._allow_gui_writes
        self._allow_gui_writes = True
        try:
            yield
        finally:
            self._allow_gui_writes = previous

    def is_gui_write_enabled(self) -> bool:
        return self._allow_gui_writes

    def get_item(self, key: str) -> ConfigItem | None:
        return self._items.get(key)

    def get(self, key: str) -> Any:
        item = self._items.get(key)
        if item is None:
            return None
        return item.get_value()

    def get_or_default(self, key: str) -> Any:
        item = self._items.get(key)
        if item is None:
            return None
        value = item.get_value()
        if value is not None:
            return value
        return item.get_default_value()

    def set_value(self, key: str, value: Any) -> None:
        if not self._allow_gui_writes:
            raise PermissionError("Config values can only be modified via the GUI.")
        item = self._items.get(key)
        if item is None:
            raise KeyError(f"Config key does not exist: {key}")
        item.set_value(value)

    def all_items(self) -> dict[str, ConfigItem]:
        return dict(self._items)
