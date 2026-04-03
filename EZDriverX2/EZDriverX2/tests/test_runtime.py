"""Tests for runtime module components."""

import sys
sys.path.insert(0, ".")

from runtime.immutable import (
    HealthPercent,
    PowerPercent,
    SpellInfo,
    UnitSnapshot,
    RotationContextV2,
)
from runtime.exceptions import (
    EZWowException,
    CaptureException,
    BridgeException,
    MaxRetriesExceededException,
    classify_exception,
    format_exception_chain,
)
from runtime.recovery import RetryPolicy, RecoveryExecutor


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


class TestExceptions:
    """Tests for exception hierarchy."""

    def test_exception_cause(self):
        original = ValueError("original")
        exc = CaptureException("test", cause=original)
        assert exc.cause is original

    def test_classify_exception(self):
        exc = CaptureException("test")
        assert classify_exception(exc) == "CaptureException"

    def test_classify_nested_exception(self):
        original = ValueError("original")
        exc = BridgeException("test", cause=original)
        assert classify_exception(exc) == "BridgeException"

    def test_format_exception_chain(self):
        original = ValueError("original error")
        exc = MaxRetriesExceededException("operation", 3, cause=original)
        formatted = format_exception_chain(exc)
        assert "MaxRetriesExceededException" in formatted
        assert "original error" in formatted


class TestRecoveryExecutor:
    """Tests for RecoveryExecutor."""

    def test_successful_execution(self):
        executor = RecoveryExecutor(RetryPolicy(max_attempts=3))

        def operation():
            return "success"

        result = executor.execute_with_retry(operation, "test_op")
        assert result == "success"

    def test_retry_on_failure(self):
        executor = RecoveryExecutor(RetryPolicy(max_attempts=3))
        attempts = [0]

        def operation():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("temporary error")
            return "success"

        result = executor.execute_with_retry(operation, "test_op")
        assert result == "success"
        assert attempts[0] == 3

    def test_max_retries_exceeded(self):
        executor = RecoveryExecutor(RetryPolicy(max_attempts=3))

        def operation():
            raise ValueError("permanent error")

        try:
            executor.execute_with_retry(operation, "test_op")
            assert False, "Should raise MaxRetriesExceededException"
        except MaxRetriesExceededException as e:
            assert e.max_attempts == 3
            assert e.operation == "test_op"

    def test_retry_policy_delay(self):
        policy = RetryPolicy(max_attempts=3, base_delay=0.1)
        assert policy.get_delay(0) == 0.1
        assert policy.get_delay(1) == 0.2
        assert policy.get_delay(2) == 0.4


def run_tests():
    """Run all tests."""
    test_classes = [
        TestHealthPercent,
        TestSpellInfo,
        TestUnitSnapshot,
        TestRotationContextV2,
        TestExceptions,
        TestRecoveryExecutor,
    ]

    total = 0
    passed = 0
    failed = 0

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
    if failed > 0:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    run_tests()
