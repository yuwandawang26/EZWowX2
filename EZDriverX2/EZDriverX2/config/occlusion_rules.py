"""Occlusion detection rules.

Defines rules for detecting when game UI elements are occluded.
"""

from dataclasses import dataclass
from typing import Callable, Final
from enum import Enum, auto


class RuleType(Enum):
    """Types of occlusion rules."""
    MUST_BE_BLACK = auto()
    MUST_NOT_BE_BLACK = auto()
    MUST_MATCH_COLOR = auto()
    MUST_NOT_MATCH_COLOR = auto()
    AVERAGE_BELOW_THRESHOLD = auto()
    AVERAGE_ABOVE_THRESHOLD = auto()


@dataclass(frozen=True, slots=True)
class OcclusionRule:
    """A single occlusion detection rule.

    Rules check specific conditions on pixel data to determine if
    a region is occluded.
    """
    name: str
    rule_type: RuleType
    threshold: float = 0.0
    target_color: tuple[int, int, int] = (0, 0, 0)
    region_name: str = ""


@dataclass(frozen=True, slots=True)
class OcclusionCheckResult:
    """Result of checking occlusion rules."""
    region_name: str
    passed: bool
    failed_rules: tuple[str, ...] = tuple()


class OcclusionRuleEngine:
    """Engine for checking occlusion rules against pixel data."""

    def __init__(self) -> None:
        self._rules: list[OcclusionRule] = list()

    def add_rule(self, rule: OcclusionRule) -> None:
        """Add a rule to the engine.

        Args:
            rule: The rule to add.
        """
        self._rules.append(rule)

    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name.

        Args:
            name: Name of the rule to remove.

        Returns:
            True if the rule was found and removed.
        """
        for i, rule in enumerate(self._rules):
            if rule.name == name:
                del self._rules[i]
                return True
        return False

    def clear_rules(self) -> None:
        """Remove all rules."""
        self._rules.clear()

    def check(self, region_name: str, pixel_data: bytes, width: int, height: int) -> OcclusionCheckResult:
        """Check all rules for a region.

        Args:
            region_name: Name of the region being checked.
            pixel_data: BGRA pixel data.
            width: Width of the region in pixels.
            height: Height of the region in pixels.

        Returns:
            OcclusionCheckResult with pass/fail status.
        """
        failed_rules: list[str] = []

        for rule in self._rules:
            if rule.region_name and rule.region_name != region_name:
                continue

            if not self._check_rule(rule, pixel_data, width, height):
                failed_rules.append(rule.name)

        return OcclusionCheckResult(
            region_name=region_name,
            passed=len(failed_rules) == 0,
            failed_rules=tuple(failed_rules),
        )

    def _check_rule(self, rule: OcclusionRule, pixel_data: bytes, width: int, height: int) -> bool:
        """Check a single rule.

        Args:
            rule: The rule to check.
            pixel_data: BGRA pixel data.
            width: Width in pixels.
            height: Height in pixels.

        Returns:
            True if the rule passes.
        """
        if rule.rule_type == RuleType.MUST_BE_BLACK:
            return self._is_average_black(pixel_data, width, height, rule.threshold)
        elif rule.rule_type == RuleType.MUST_NOT_BE_BLACK:
            return not self._is_average_black(pixel_data, width, height, rule.threshold)
        elif rule.rule_type == RuleType.AVERAGE_BELOW_THRESHOLD:
            avg = self._calculate_average(pixel_data, width, height)
            return avg < rule.threshold
        elif rule.rule_type == RuleType.AVERAGE_ABOVE_THRESHOLD:
            avg = self._calculate_average(pixel_data, width, height)
            return avg > rule.threshold

        return True

    def _is_average_black(self, pixel_data: bytes, width: int, height: int, threshold: float) -> bool:
        """Check if average brightness is below threshold (near black).

        Args:
            pixel_data: BGRA pixel data.
            width: Width in pixels.
            height: Height in pixels.
            threshold: Threshold for "black" detection (0-255).

        Returns:
            True if average brightness is below threshold.
        """
        if not pixel_data or width <= 0 or height <= 0:
            return False

        total = 0
        pixel_count = 0

        for i in range(0, len(pixel_data), 4):
            b, g, r = pixel_data[i], pixel_data[i + 1], pixel_data[i + 2]
            brightness = (b + g + r) / 3
            total += brightness
            pixel_count += 1

        if pixel_count == 0:
            return False

        return (total / pixel_count) < threshold

    def _calculate_average(self, pixel_data: bytes, width: int, height: int) -> float:
        """Calculate average brightness.

        Args:
            pixel_data: BGRA pixel data.
            width: Width in pixels.
            height: Height in pixels.

        Returns:
            Average brightness (0-255).
        """
        if not pixel_data or width <= 0 or height <= 0:
            return 0.0

        total = 0.0
        pixel_count = 0

        for i in range(0, len(pixel_data), 4):
            b, g, r = pixel_data[i], pixel_data[i + 1], pixel_data[i + 2]
            brightness = (b + g + r) / 3
            total += brightness
            pixel_count += 1

        return total / pixel_count if pixel_count > 0 else 0.0


DEFAULT_OCCLUSION_RULES: Final = (
    OcclusionRule(
        name="player_health_must_be_dark",
        rule_type=RuleType.MUST_BE_BLACK,
        threshold=30.0,
        region_name="player_health",
    ),
    OcclusionRule(
        name="player_power_must_not_be_black",
        rule_type=RuleType.MUST_NOT_BE_BLACK,
        threshold=10.0,
        region_name="player_power",
    ),
    OcclusionRule(
        name="target_health_must_be_dark",
        rule_type=RuleType.MUST_BE_BLACK,
        threshold=30.0,
        region_name="target_health",
    ),
    OcclusionRule(
        name="target_power_must_not_be_black",
        rule_type=RuleType.MUST_NOT_BE_BLACK,
        threshold=10.0,
        region_name="target_power",
    ),
)


def create_default_engine() -> OcclusionRuleEngine:
    """Create an occlusion rule engine with default rules.

    Returns:
        OcclusionRuleEngine with default rules loaded.
    """
    engine = OcclusionRuleEngine()
    for rule in DEFAULT_OCCLUSION_RULES:
        engine.add_rule(rule)
    return engine


__all__ = [
    "RuleType",
    "OcclusionRule",
    "OcclusionCheckResult",
    "OcclusionRuleEngine",
    "DEFAULT_OCCLUSION_RULES",
    "create_default_engine",
]
