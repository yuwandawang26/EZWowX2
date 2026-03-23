"""Profile-facing runtime context."""

from __future__ import annotations

from typing import Any, cast

from ..config.registry import ConfigRegistry
from ..contracts.actions import CastAction, IdleAction
from .data import AttrDict
from .state_adapter import GameStateView, UnitView


class RotationContext:
    def __init__(self, raw_data: AttrDict, config: ConfigRegistry) -> None:
        self.raw_data = raw_data
        self._config = config
        self.state = GameStateView(raw_data)

    @property
    def player(self) -> UnitView:
        return self.state.player

    @property
    def target(self) -> UnitView:
        return self.state.target

    @property
    def focus(self) -> UnitView:
        return self.state.focus

    def cfg(self, key: str) -> Any:
        return self._config.get_or_default(key)

    @property
    def is_chatting(self) -> bool:
        return bool(self.raw_data.misc.get("on_chat", False))

    def cast(self, unitToken: str, spell: str) -> CastAction:
        return CastAction(unitToken=unitToken, spell=spell)

    def idle(self, reason: str) -> IdleAction:
        return IdleAction(reason=reason)

    @property
    def spell(self) -> AttrDict:
        spell_data = self.player.raw.get("spell", {})
        if not isinstance(spell_data, (AttrDict, dict)):
            return AttrDict({})
        spell_map = cast(dict[str, Any], spell_data)
        normalized: dict[str, AttrDict] = {}
        for name, value in spell_map.items():
            spell_name = str(name)
            if isinstance(value, AttrDict):
                normalized[spell_name] = value
            elif isinstance(value, dict):
                normalized[spell_name] = AttrDict(cast(dict[str, Any], value))
        return AttrDict(normalized)

    def spell_known(self, spell_name: str) -> bool:
        spell = self.spell.get(spell_name)
        if not isinstance(spell, AttrDict):
            return False
        return bool(spell.get("known", False))

    def spell_usable(self, spell_name: str) -> bool:
        if not self.spell_known(spell_name):
            return False
        spell = self.spell.get(spell_name)
        if not isinstance(spell, AttrDict):
            return False
        return bool(spell.get("usable", False))

    def spell_charges(self, spell_name: str) -> int:
        if not self.spell_usable(spell_name):
            return 0
        spell = self.spell.get(spell_name)
        if not isinstance(spell, AttrDict):
            return 0
        charge = spell.get("charge", 0)
        try:
            return int(cast(int | float | str | bool, charge))
        except (TypeError, ValueError):
            return 0

    def spell_remaining(self, spell_name: str) -> float:
        if not self.spell_usable(spell_name):
            return 9999.0
        spell = self.spell.get(spell_name)
        if not isinstance(spell, AttrDict):
            return 9999.0
        remaining = spell.get("remaining", 9999.0)
        try:
            return float(cast(int | float | str | bool, remaining))
        except (TypeError, ValueError):
            return 9999.0

    def spell_cooldown_ready(self, spell_name: str, spell_queue_window: float) -> bool:
        if not self.spell_usable(spell_name):
            return False
        return self.spell_remaining(spell_name) < spell_queue_window
