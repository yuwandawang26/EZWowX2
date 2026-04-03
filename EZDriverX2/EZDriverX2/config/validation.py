"""Data validation module.

Provides validation utilities for game state data.
"""

from typing import Any
from ..engine.interfaces import AttrDict, ValidationResult


def validate_unit_data(data: AttrDict | None) -> ValidationResult:
    """Validate unit data structure.

    Args:
        data: Unit data to validate.

    Returns:
        ValidationResult indicating success or failure.
    """
    if data is None:
        return ValidationResult.failure(["Unit data is None"])

    errors = []

    health = data.health
    if health is not None and not isinstance(health, (int, float)):
        errors.append(f"health must be numeric, got {type(health).__name__}")
    elif health is not None and (health < 0 or health > 100):
        errors.append(f"health must be 0-100, got {health}")

    name = data.name
    if name is not None and not isinstance(name, str):
        errors.append(f"name must be string, got {type(name).__name__}")

    guid = data.guid
    if guid is not None and not isinstance(guid, str):
        errors.append(f"guid must be string, got {type(guid).__name__}")

    if errors:
        return ValidationResult.failure(errors)

    return ValidationResult.success()


def validate_spell_data(data: AttrDict | None) -> ValidationResult:
    """Validate spell data structure.

    Args:
        data: Spell data to validate.

    Returns:
        ValidationResult indicating success or failure.
    """
    if data is None:
        return ValidationResult.failure(["Spell data is None"])

    errors = []

    spell_id = data.spell_id
    if spell_id is not None and not isinstance(spell_id, int):
        errors.append(f"spell_id must be int, got {type(spell_id).__name__}")

    name = data.name
    if name is not None and not isinstance(name, str):
        errors.append(f"name must be string, got {type(name).__name__}")

    if errors:
        return ValidationResult.failure(errors)

    return ValidationResult.success()


def validate_context_data(data: AttrDict | None) -> ValidationResult:
    """Validate rotation context data structure.

    Args:
        data: Context data to validate.

    Returns:
        ValidationResult indicating success or failure.
    """
    if data is None:
        return ValidationResult.failure(["Context data is None"])

    errors = []

    player = data.player
    if player is not None:
        player_result = validate_unit_data(player)
        if not player_result.is_valid:
            errors.extend(f"player.{e}" for e in player_result.errors)

    target = data.target
    if target is not None:
        target_result = validate_unit_data(target)
        if not target_result.is_valid:
            errors.extend(f"target.{e}" for e in target_result.errors)

    if errors:
        return ValidationResult.failure(errors)

    return ValidationResult.success()


__all__ = [
    "validate_unit_data",
    "validate_spell_data",
    "validate_context_data",
]
