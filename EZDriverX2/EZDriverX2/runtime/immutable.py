"""Immutable data classes for runtime state.

These classes represent core game state data structures that are
designed to be immutable for thread safety and predictability.
"""

from dataclasses import dataclass
from typing import Final


MIN_HEALTH: Final[float] = 0.0
MAX_HEALTH: Final[float] = 100.0
MIN_POWER: Final[float] = 0.0
MAX_POWER: Final[float] = 100.0


@dataclass(frozen=True, slots=True)
class HealthPercent:
    """Immutable health percentage value.

    Health values are automatically clamped to the valid range [0, 100].
    """
    _value: float

    def __post_init__(self) -> None:
        if self._value < MIN_HEALTH:
            object.__setattr__(self, "_value", MIN_HEALTH)
        elif self._value > MAX_HEALTH:
            object.__setattr__(self, "_value", MAX_HEALTH)

    @property
    def value(self) -> float:
        return self._value

    def is_below(self, threshold: float) -> bool:
        """Check if health is below threshold."""
        return self._value < threshold

    def is_above(self, threshold: float) -> bool:
        """Check if health is above threshold."""
        return self._value > threshold

    def is_between(self, low: float, high: float) -> bool:
        """Check if health is between low and high (exclusive)."""
        return low < self._value < high

    def is_at_least(self, threshold: float) -> bool:
        """Check if health is at or above threshold."""
        return self._value >= threshold

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HealthPercent):
            return abs(self._value - other._value) < 0.001
        if isinstance(other, (int, float)):
            return abs(self._value - other) < 0.001
        return NotImplemented

    def __repr__(self) -> str:
        return f"HealthPercent({self._value:.1f})"


@dataclass(frozen=True, slots=True)
class PowerPercent:
    """Immutable power percentage value.

    Power values are automatically clamped to the valid range [0, 100].
    """
    _value: float

    def __post_init__(self) -> None:
        if self._value < MIN_POWER:
            object.__setattr__(self, "_value", MIN_POWER)
        elif self._value > MAX_POWER:
            object.__setattr__(self, "_value", MAX_POWER)

    @property
    def value(self) -> float:
        return self._value

    def is_below(self, threshold: float) -> bool:
        """Check if power is below threshold."""
        return self._value < threshold

    def is_above(self, threshold: float) -> bool:
        """Check if power is above threshold."""
        return self._value > threshold

    def is_at_least(self, threshold: float) -> bool:
        """Check if power is at or above threshold."""
        return self._value >= threshold

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PowerPercent):
            return abs(self._value - other._value) < 0.001
        if isinstance(other, (int, float)):
            return abs(self._value - other) < 0.001
        return NotImplemented

    def __repr__(self) -> str:
        return f"PowerPercent({self._value:.1f})"


@dataclass(frozen=True, slots=True)
class SpellInfo:
    """Immutable spell information.

    Represents the current state of a spell including its
    availability and cooldown status.
    """
    name: str
    spell_id: int
    known: bool
    usable: bool
    remaining: float
    charges: int
    max_charges: int

    def __post_init__(self) -> None:
        if self.remaining < 0.0:
            object.__setattr__(self, "remaining", 0.0)

    def is_ready(self) -> bool:
        """Check if spell is ready to cast (not on cooldown)."""
        if not self.known or not self.usable:
            return False
        return self.remaining <= 0.001

    def charges_ready(self) -> int:
        """Number of charges currently available."""
        if self.charges < 0:
            return 0
        return min(self.charges, self.max_charges)

    def cooldown_ready(self, queue_window: float) -> bool:
        """Check if spell will be ready within the queue window."""
        if not self.known or not self.usable:
            return False
        return self.remaining <= queue_window

    def __repr__(self) -> str:
        status = "ready" if self.is_ready() else f"cd:{self.remaining:.1f}s"
        return f"SpellInfo({self.name}, {status}, charges={self.charges}/{self.max_charges})"


@dataclass(frozen=True, slots=True)
class UnitSnapshot:
    """Immutable snapshot of a unit's state at a point in time.

    This is a pure data container with no external dependencies.
    All fields are required to ensure complete snapshots.
    """
    guid: str
    name: str
    health: HealthPercent
    power: PowerPercent
    level: int
    race: str
    class_: str
    spec: str
    buffs: tuple[str, ...]
    debuffs: tuple[str, ...]

    @classmethod
    def create(
        cls,
        guid: str = "",
        name: str = "",
        health: float = 0.0,
        power: float = 0.0,
        level: int = 0,
        race: str = "",
        class_: str = "",
        spec: str = "",
        buff_list: list[str] | None = None,
        debuff_list: list[str] | None = None,
    ) -> "UnitSnapshot":
        """Factory method to create a UnitSnapshot with health/power as raw values."""
        return cls(
            guid=guid,
            name=name,
            health=HealthPercent(health),
            power=PowerPercent(power),
            level=level,
            race=race,
            class_=class_,
            spec=spec,
            buffs=tuple(buff_list) if buff_list else tuple(),
            debuffs=tuple(debuff_list) if debuff_list else tuple(),
        )

    def has_buff(self, buff_name: str) -> bool:
        """Check if unit has a specific buff."""
        return buff_name in self.buffs

    def has_debuff(self, debuff_name: str) -> bool:
        """Check if unit has a specific debuff."""
        return debuff_name in self.debuffs

    def is_alive(self) -> bool:
        """Check if unit is alive."""
        return self.health.value > 0

    def is_enemy(self) -> bool:
        """Check if unit is an enemy (non-player)."""
        return bool(self.guid) and not self.guid.endswith("-Player")

    def __repr__(self) -> str:
        return f"UnitSnapshot({self.name}, hp={self.health.value:.0f}%, power={self.power.value:.0f}%)"


@dataclass(frozen=True, slots=True)
class RotationContextV2:
    """Immutable rotation context.

    Contains a complete snapshot of game state for decision making.
    This object is thread-safe and can be shared freely.
    """
    player: UnitSnapshot
    target: UnitSnapshot | None
    focus: UnitSnapshot | None
    misc: tuple[tuple[str, object], ...]
    timestamp: float

    @classmethod
    def from_raw_data(
        cls,
        raw_data: dict,
        timestamp: float | None = None,
    ) -> "RotationContextV2":
        """Create a RotationContextV2 from raw game data dictionary."""
        import time

        if timestamp is None:
            timestamp = time.time()

        player_data = raw_data.get("player", {})
        target_data = raw_data.get("target", {})
        focus_data = raw_data.get("focus", {})
        misc_data = raw_data.get("misc", {})

        player = UnitSnapshot.create(
            guid=str(player_data.get("guid", "")),
            name=str(player_data.get("name", "")),
            health=float(player_data.get("health", 0)),
            power=float(player_data.get("power", 0)),
            level=int(player_data.get("level", 0)),
            race=str(player_data.get("race", "")),
            class_=str(player_data.get("class", "")),
            spec=str(player_data.get("spec", "")),
            buff_list=cls._extract_list(player_data, "buffs"),
            debuff_list=cls._extract_list(player_data, "debuffs"),
        )

        target = None
        if target_data and target_data.get("guid"):
            target = UnitSnapshot.create(
                guid=str(target_data.get("guid", "")),
                name=str(target_data.get("name", "")),
                health=float(target_data.get("health", 0)),
                power=float(target_data.get("power", 0)),
                level=int(target_data.get("level", 0)),
                race=str(target_data.get("race", "")),
                class_=str(target_data.get("class", "")),
                spec=str(target_data.get("spec", "")),
                buff_list=cls._extract_list(target_data, "buffs"),
                debuff_list=cls._extract_list(target_data, "debuffs"),
            )

        focus = None
        if focus_data and focus_data.get("guid"):
            focus = UnitSnapshot.create(
                guid=str(focus_data.get("guid", "")),
                name=str(focus_data.get("name", "")),
                health=float(focus_data.get("health", 0)),
                power=float(focus_data.get("power", 0)),
                level=int(focus_data.get("level", 0)),
                race=str(focus_data.get("race", "")),
                class_=str(focus_data.get("class", "")),
                spec=str(focus_data.get("spec", "")),
                buff_list=cls._extract_list(focus_data, "buffs"),
                debuff_list=cls._extract_list(focus_data, "debuffs"),
            )

        misc_items = tuple(
            (str(k), v)
            for k, v in misc_data.items()
        )

        return cls(
            player=player,
            target=target,
            focus=focus,
            misc=misc_items,
            timestamp=timestamp,
        )

    @staticmethod
    def _extract_list(data: dict, key: str) -> list[str]:
        """Extract a list from data dict safely."""
        value = data.get(key, [])
        if isinstance(value, (list, tuple)):
            return [str(item) for item in value]
        return []

    def get_misc(self, key: str, default: object = None) -> object:
        """Get miscellaneous data by key."""
        for k, v in self.misc:
            if k == key:
                return v
        return default

    def has_target(self) -> bool:
        """Check if there is a valid target."""
        return self.target is not None and self.target.is_alive()

    def has_focus(self) -> bool:
        """Check if there is a valid focus."""
        return self.focus is not None and self.focus.is_alive()

    def __repr__(self) -> str:
        target_name = self.target.name if self.target else "None"
        return f"RotationContextV2(player={self.player.name}, target={target_name}, time={self.timestamp:.2f})"


__all__ = [
    "HealthPercent",
    "PowerPercent",
    "SpellInfo",
    "UnitSnapshot",
    "RotationContextV2",
    "MIN_HEALTH",
    "MAX_HEALTH",
    "MIN_POWER",
    "MAX_POWER",
]
