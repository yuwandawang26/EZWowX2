"""Engine runtime components."""

from .interfaces import (
    ICapture,
    IBridgeClient,
    IInputSender,
    INodeExtractor,
    PixelFrame,
    Node,
    AttrDict,
    AttrList,
    ValidationResult,
    IValidator,
)
from .mocks import (
    MockCapture,
    MockBridgeClient,
    MockInputSender,
    MockNodeExtractor,
)
from .implementations import (
    WindowInfo,
    find_wow_window,
    DxCapture,
    HttpBridgeClient,
    Win32InputSender,
)

try:
    from .executor import ActionExecutor
    from .loop import RotationLoopEngine
    _HAS_ENGINE_COMPONENTS = True
except ImportError:
    _HAS_ENGINE_COMPONENTS = False

__all__ = [
    "ICapture",
    "IBridgeClient",
    "IInputSender",
    "INodeExtractor",
    "PixelFrame",
    "Node",
    "AttrDict",
    "AttrList",
    "ValidationResult",
    "IValidator",
    "MockCapture",
    "MockBridgeClient",
    "MockInputSender",
    "MockNodeExtractor",
    "WindowInfo",
    "find_wow_window",
    "DxCapture",
    "HttpBridgeClient",
    "Win32InputSender",
]

if _HAS_ENGINE_COMPONENTS:
    __all__.extend(["ActionExecutor", "RotationLoopEngine"])

