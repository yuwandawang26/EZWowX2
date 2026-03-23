"""Config item model used by runtime and UI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .registry import ConfigRegistry


def _empty_str_list() -> list[str]:
    return []


@dataclass(slots=True)
class ConfigItem(ABC):
    key: str
    label: str
    description: str = ""
    _owner: "ConfigRegistry | None" = field(default=None, init=False, repr=False)

    @abstractmethod
    def get_value(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def set_value(self, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_default_value(self) -> Any:
        raise NotImplementedError

    def attach_owner(self, owner: "ConfigRegistry") -> None:
        self._owner = owner

    def _ensure_writable(self) -> None:
        if not self._owner or not self._owner.is_gui_write_enabled():
            raise PermissionError("Config values can only be modified via the GUI.")

    def set_value_from_gui(self, value: Any) -> None:
        if not self._owner:
            raise PermissionError("Config item is not attached to a ConfigRegistry.")
        with self._owner.gui_write():
            self.set_value(value)


@dataclass(slots=True)
class SliderConfig(ConfigItem):
    min_value: float = 0.0
    max_value: float = 100.0
    step: float = 1.0
    default_value: float = 50.0
    value_transform: Callable[[float], Any] | None = None
    _value: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        self._value = float(self.default_value)

    def get_value(self) -> Any:
        value = float(self._value)
        if self.value_transform:
            return self.value_transform(value)
        return value

    def set_value(self, value: Any) -> None:
        self._ensure_writable()
        numeric = float(value)
        clamped = max(self.min_value, min(self.max_value, numeric))
        if self.step > 0:
            steps = round((clamped - self.min_value) / self.step)
            snapped = self.min_value + steps * self.step
            self._value = max(self.min_value, min(self.max_value, snapped))
        else:
            self._value = clamped

    def get_default_value(self) -> Any:
        value = float(self.default_value)
        if self.value_transform:
            return self.value_transform(value)
        return value


@dataclass(slots=True)
class ComboConfig(ConfigItem):
    options: list[str] = field(default_factory=_empty_str_list)
    default_index: int = 0
    value_transform: Callable[[str], Any] | None = None
    _current_index: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        self._current_index = self.default_index

    def get_index(self) -> int:
        return self._current_index

    def set_index(self, index: int) -> None:
        self._ensure_writable()
        if 0 <= index < len(self.options):
            self._current_index = index

    def get_value(self) -> Any:
        if 0 <= self._current_index < len(self.options):
            value = self.options[self._current_index]
        else:
            value = ""
        if self.value_transform:
            return self.value_transform(value)
        return value

    def set_value(self, value: Any) -> None:
        self._ensure_writable()
        text = str(value)
        if text in self.options:
            self._current_index = self.options.index(text)

    def set_index_from_gui(self, index: int) -> None:
        if not self._owner:
            raise PermissionError("Config item is not attached to a ConfigRegistry.")
        with self._owner.gui_write():
            self.set_index(index)

    def get_default_value(self) -> Any:
        if 0 <= self.default_index < len(self.options):
            value = self.options[self.default_index]
        else:
            value = ""
        if self.value_transform:
            return self.value_transform(value)
        return value
