"""Adapter layer from raw AttrDict to profile-friendly views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from .data import AttrDict, NoneObject


def _as_attr_dict(value: Any) -> AttrDict:
    if isinstance(value, AttrDict):
        return value
    if isinstance(value, dict):
        return AttrDict(value)
    return AttrDict({})


def _coerce_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, NoneObject):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    if isinstance(value, NoneObject):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, NoneObject):
        return default
    return bool(value)


def _coerce_str(value: Any, default: str = "") -> str:
    if isinstance(value, NoneObject):
        return default
    if value is None:
        return default
    return str(value)


@dataclass(slots=True)
class UnitView:
    unitToken: str
    raw: AttrDict

    @property
    def status(self) -> AttrDict:
        return _as_attr_dict(self.raw.get("status", {}))

    @property
    def exists(self) -> bool:
        default = self.unitToken == "player"
        return _coerce_bool(self.status.get("exists", default), default)

    @property
    def is_self(self) -> bool:
        default = self.unitToken == "player"
        return _coerce_bool(self.status.get("unit_is_self", default), default)

    @property
    def in_range(self) -> bool:
        return _coerce_bool(self.status.get("unit_in_range", False))

    @property
    def is_alive(self) -> bool:
        return _coerce_bool(self.status.get("unit_is_alive", False))

    @property
    def can_attack(self) -> bool:
        return _coerce_bool(self.status.get("unit_can_attack", False))

    @property
    def in_combat(self) -> bool:
        return _coerce_bool(self.status.get("unit_in_combat", False))

    @property
    def hp_pct(self) -> float:
        return _coerce_float(self.status.get("unit_health", 0.0))

    @property
    def role(self) -> str:
        return _coerce_str(self.status.get("unit_role", ""))

    @property
    def damage_absorbs(self) -> float:
        return _coerce_float(self.status.get("unit_damage_absorbs", 0.0))

    @property
    def heal_absorbs(self) -> float:
        return _coerce_float(self.status.get("unit_heal_absorbs", 0.0))

    @property
    def unit_class(self) -> str:
        return _coerce_str(self.status.get("unit_class", ""))

    @property
    def aura(self) -> AttrDict:
        return _as_attr_dict(self.raw.get("aura", {}))

    @property
    def buff(self) -> AttrDict:
        return _as_attr_dict(self.aura.get("buff", {}))

    @property
    def buff_sequence(self) -> list[Any]:
        sequence = self.aura.get("buff_sequence", [])
        if isinstance(sequence, list):
            return cast(list[Any], sequence)
        return []

    @property
    def debuff(self) -> AttrDict:
        return _as_attr_dict(self.aura.get("debuff", {}))

    @property
    def debuff_sequence(self) -> list[Any]:
        sequence = self.aura.get("debuff_sequence", [])
        if isinstance(sequence, list):
            return cast(list[Any], sequence)
        return []

    @property
    def cast_icon(self) -> str:
        return _coerce_str(self.status.get("unit_cast_icon", ""))

    @property
    def cast_duration(self) -> float:
        return _coerce_float(self.status.get("unit_cast_duration", 0.0))

    @property
    def cast_interruptible(self) -> bool:
        if self.unitToken == "player":
            return False
        return _coerce_bool(self.status.get("unit_cast_interruptible", False))

    @property
    def channel_icon(self) -> str:
        return _coerce_str(self.status.get("unit_channel_icon", ""))

    @property
    def channel_duration(self) -> float:
        return _coerce_float(self.status.get("unit_channel_duration", 0.0))

    @property
    def channel_interruptible(self) -> bool:
        if self.unitToken == "player":
            return False
        return _coerce_bool(self.status.get("unit_channel_interruptible", False))

    @property
    def spell_icon(self) -> str:
        if self.cast_icon != "":
            return self.cast_icon
        else:
            return self.channel_icon

    @property
    def spell_duration(self) -> float:
        if self.cast_icon != "":
            return self.cast_duration
        else:
            return self.channel_duration

    @property
    def spell_interruptible(self) -> bool:
        if self.cast_icon != "":
            return self.cast_interruptible
        else:
            return self.channel_interruptible

    def has_buff(self, title: str) -> bool:
        return _coerce_bool(self.buff[title], False)

    def buff_remaining(self, title: str) -> float:
        buff = self.buff[title]
        if isinstance(buff, NoneObject):
            return 0.0
        return _coerce_float(getattr(buff, "remaining", 0.0))

    def buff_stack(self, title: str) -> int:
        buff = self.buff[title]
        if isinstance(buff, NoneObject):
            return 0
        return _coerce_int(getattr(buff, "count", 0))

    def has_debuff(self, title: str) -> bool:
        return _coerce_bool(self.debuff[title], False)

    def debuff_remaining(self, title: str) -> float:
        debuff = self.debuff[title]
        if isinstance(debuff, NoneObject):
            return 0.0
        return _coerce_float(getattr(debuff, "remaining", 0.0))

    def debuff_stack(self, title: str) -> int:
        debuff = self.debuff[title]
        if isinstance(debuff, NoneObject):
            return 0
        return _coerce_int(getattr(debuff, "count", 0))


class GameStateView:
    def __init__(self, raw_data: AttrDict) -> None:
        self.raw_data = raw_data

    def _unit(self, token: str, raw_unit: Any) -> UnitView:
        return UnitView(token, _as_attr_dict(raw_unit))

    @property
    def player(self) -> UnitView:
        return self._unit("player", self.raw_data.get("player", {}))

    @property
    def target(self) -> UnitView:
        return self._unit("target", self.raw_data.get("target", {}))

    @property
    def focus(self) -> UnitView:
        return self._unit("focus", self.raw_data.get("focus", {}))

    def party_members(self, include_player: bool = True) -> list[UnitView]:
        members: list[UnitView] = []
        if include_player:
            members.append(self.player)

        party = self.raw_data.get("party", {})
        if isinstance(party, dict):
            party_map = cast(dict[Any, Any], party)
            for token, raw_unit in party_map.items():
                unitToken = str(token)
                members.append(self._unit(unitToken, raw_unit))
        return members
