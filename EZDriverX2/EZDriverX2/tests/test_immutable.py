"""Tests for runtime module components - standalone version.

Tests the immutable data classes without triggering full package imports.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.immutable import (
    HealthPercent,
    PowerPercent,
    SpellInfo,
    UnitSnapshot,
    RotationContextV2,
)


class TestHealthPercent:
    """Tests for HealthPercent."""

    def test_creation(self):
        hp = HealthPercent(50.0)
        assert hp.value == 50.0

    def test_clamp_low(self):
        hp = HealthPercent(-10.0)
        assert hp.value == 0.0

    def test_clamp_high(self):
        hp = HealthPercent(150.0)
        assert hp.value == 100.0

    def test_is_below(self):
        hp = HealthPercent(30.0)
        assert hp.is_below(40.0) is True
        assert hp.is_below(20.0) is False

    def test_is_above(self):
        hp = HealthPercent(70.0)
        assert hp.is_above(60.0) is True
        assert hp.is_above(80.0) is False

    def test_equality(self):
        hp1 = HealthPercent(50.0)
        hp2 = HealthPercent(50.0)
        assert hp1 == hp2


class TestSpellInfo:
    """Tests for SpellInfo."""

    def test_creation(self):
        spell = SpellInfo(
            name="Power Word: Shield",
            spell_id=17,
            known=True,
            usable=True,
            remaining=0.0,
            charges=2,
            max_charges=2,
        )
        assert spell.name == "Power Word: Shield"
        assert spell.spell_id == 17

    def test_is_ready(self):
        spell = SpellInfo(
            name="Smite",
            spell_id=1,
            known=True,
            usable=True,
            remaining=0.0,
            charges=1,
            max_charges=1,
        )
        assert spell.is_ready() is True

    def test_is_not_ready(self):
        spell = SpellInfo(
            name="Smite",
            spell_id=1,
            known=True,
            usable=True,
            remaining=5.0,
            charges=1,
            max_charges=1,
        )
        assert spell.is_ready() is False

    def test_not_known(self):
        spell = SpellInfo(
            name="Unknown",
            spell_id=0,
            known=False,
            usable=False,
            remaining=0.0,
            charges=0,
            max_charges=0,
        )
        assert spell.is_ready() is False

    def test_cooldown_ready(self):
        spell = SpellInfo(
            name="Smite",
            spell_id=1,
            known=True,
            usable=True,
            remaining=0.3,
            charges=1,
            max_charges=1,
        )
        assert spell.cooldown_ready(0.5) is True
        assert spell.cooldown_ready(0.2) is False


class TestUnitSnapshot:
    """Tests for UnitSnapshot."""

    def test_creation(self):
        unit = UnitSnapshot.create(
            guid="player-guid",
            name="Player",
            health=80.0,
            power=50.0,
            level=70,
            race="Human",
            class_="Priest",
            spec="Discipline",
        )
        assert unit.name == "Player"
        assert unit.health.value == 80.0
        assert unit.power.value == 50.0
        assert unit.is_alive() is True

    def test_not_alive(self):
        unit = UnitSnapshot.create(
            guid="dead-guid",
            name="Dead",
            health=0.0,
            power=0.0,
        )
        assert unit.is_alive() is False

    def test_has_buff(self):
        unit = UnitSnapshot.create(
            guid="player-guid",
            name="Player",
            health=100.0,
            power=50.0,
            buff_list=["Power Word: Fortitude", "Inner Fire"],
        )
        assert unit.has_buff("Power Word: Fortitude") is True
        assert unit.has_buff("Nonexistent") is False


class TestRotationContextV2:
    """Tests for RotationContextV2."""

    def test_from_raw_data(self):
        raw_data = {
            "player": {
                "guid": "player-1",
                "name": "Hero",
                "health": 100.0,
                "power": 50.0,
                "level": 70,
                "race": "Human",
                "class": "Priest",
                "spec": "Holy",
                "buffs": ["Power Word: Fortitude"],
                "debuffs": [],
            },
            "target": {
                "guid": "target-1",
                "name": "Enemy",
                "health": 50.0,
                "power": 0.0,
                "level": 73,
                "race": "Orc",
                "class": "Warrior",
                "spec": "Arms",
                "buffs": [],
                "debuffs": ["Weakened Soul"],
            },
            "focus": {},
            "misc": {"on_chat": False},
        }

        ctx = RotationContextV2.from_raw_data(raw_data)
        assert ctx.player.name == "Hero"
        assert ctx.player.health.value == 100.0
        assert ctx.has_target() is True
        assert ctx.target is not None
        assert ctx.target.name == "Enemy"

    def test_no_target(self):
        raw_data = {
            "player": {"guid": "p1", "name": "P", "health": 100, "power": 50, "level": 70, "race": "H", "class": "P", "spec": "D"},
            "target": {},
            "focus": {},
            "misc": {},
        }
        ctx = RotationContextV2.from_raw_data(raw_data)
        assert ctx.has_target() is False

    def test_get_misc(self):
        raw_data = {
            "player": {"guid": "p1", "name": "P", "health": 100, "power": 50, "level": 70, "race": "H", "class": "P", "spec": "D"},
            "target": {},
            "focus": {},
            "misc": {"on_chat": True, "in_combat": False},
        }
        ctx = RotationContextV2.from_raw_data(raw_data)
        assert ctx.get_misc("on_chat") is True
        assert ctx.get_misc("nonexistent") is None
        assert ctx.get_misc("nonexistent", "default") == "default"


def run_tests():
    """Run all tests."""
    test_classes = [
        TestHealthPercent,
        TestSpellInfo,
        TestUnitSnapshot,
        TestRotationContextV2,
    ]

    total = 0
    passed = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  PASS: {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"  FAIL: {method_name} - {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        print(f"Failed: {total - passed}")


if __name__ == "__main__":
    run_tests()
