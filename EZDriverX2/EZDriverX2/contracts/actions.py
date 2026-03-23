"""Action contracts returned by profiles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CastAction:
    unitToken: str
    spell: str


@dataclass(frozen=True, slots=True)
class IdleAction:
    reason: str


Action = CastAction | IdleAction
