"""Tests for engine interfaces."""

import sys
sys.path.insert(0, ".")

from engine.interfaces import (
    ICapture,
    IBridgeClient,
    IInputSender,
    INodeExtractor,
    PixelFrame,
    Node,
    AttrDict,
    AttrList,
    ValidationResult,
)


class TestPixelFrame:
    """Tests for PixelFrame."""

    def test_creation(self):
        bgra = b"\x00" * 64
        frame = PixelFrame(width=4, height=4, bgra=bgra)
        assert frame.width == 4
        assert frame.height == 4
        assert len(frame.bgra) == 64

    def test_crop_valid(self):
        bgra = bytes(range(256))
        frame = PixelFrame(width=8, height=8, bgra=bgra)
        cropped = frame.crop(left=1, top=1, right=3, bottom=3)
        assert cropped.width == 2
        assert cropped.height == 2

    def test_crop_invalid_boundaries(self):
        bgra = b"\x00" * 64
        frame = PixelFrame(width=4, height=4, bgra=bgra)
        try:
            frame.crop(left=-1, top=0, right=2, bottom=2)
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_crop_invalid_region(self):
        bgra = b"\x00" * 64
        frame = PixelFrame(width=4, height=4, bgra=bgra)
        try:
            frame.crop(left=3, top=0, right=1, bottom=2)
            assert False, "Should raise ValueError"
        except ValueError:
            pass


class TestNode:
    """Tests for Node."""

    def test_creation(self):
        node = Node(x=1, y=2, color=(255, 0, 0), is_pure=True, is_black=False)
        assert node.x == 1
        assert node.y == 2
        assert node.color == (255, 0, 0)
        assert node.is_pure is True
        assert node.is_black is False


class TestAttrDict:
    """Tests for AttrDict."""

    def test_creation(self):
        data = AttrDict({"key": "value"})
        assert data.key == "value"

    def test_nested_access(self):
        data = AttrDict({"outer": {"inner": "value"}})
        assert data.outer.inner == "value"

    def test_nonexistent_key(self):
        data = AttrDict({"key": "value"})
        result = data.nonexistent
        assert result is None

    def test_setattr(self):
        data = AttrDict({})
        data.key = "value"
        assert data.key == "value"

    def test_get_method(self):
        data = AttrDict({"key": "value"})
        assert data.get("key") == "value"
        assert data.get("nonexistent", "default") == "default"


class TestAttrList:
    """Tests for AttrList."""

    def test_creation(self):
        data = AttrList([1, 2, 3])
        assert len(data) == 3

    def test_index_access(self):
        data = AttrList([1, 2, 3])
        assert data[0] == 1
        assert data[1] == 2

    def test_nested_dict_to_attrdict(self):
        data = AttrList([{"key": "value"}])
        item = data[0]
        assert isinstance(item, AttrDict)
        assert item.key == "value"

    def test_iteration(self):
        data = AttrList([1, 2, 3])
        items = list(data)
        assert items == [1, 2, 3]


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_success(self):
        result = ValidationResult.success()
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_failure(self):
        result = ValidationResult.failure(["error1", "error2"], ["warning1"])
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1


def run_tests():
    """Run all tests."""
    test_classes = [
        TestPixelFrame,
        TestNode,
        TestAttrDict,
        TestAttrList,
        TestValidationResult,
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
