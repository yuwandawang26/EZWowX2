"""Profile base contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .actions import Action

if TYPE_CHECKING:
    from ..config.macros import MacroRegistry
    from ..config.registry import ConfigRegistry
    from ..runtime.context import RotationContext


class RotationProfile(ABC):
    """External profile entrypoint contract."""

    @abstractmethod
    def setup(self, config: "ConfigRegistry", macros: "MacroRegistry") -> None:
        """Register config items and macro mapping."""

    @abstractmethod
    def main_rotation(self, ctx: "RotationContext") -> Action:
        """Return one action for the current tick."""
