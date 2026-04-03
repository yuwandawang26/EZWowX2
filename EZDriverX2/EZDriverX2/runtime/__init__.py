"""Runtime context and state adapter."""

from .immutable import (
    HealthPercent,
    PowerPercent,
    SpellInfo,
    UnitSnapshot,
    RotationContextV2,
)
from .exceptions import (
    EZWowException,
    CaptureException,
    BridgeException,
    InputException,
    ConfigurationException,
    ExtractionException,
    RecoveryException,
    MaxRetriesExceededException,
)
from .recovery import (
    RetryPolicy,
    RecoveryExecutor,
)

try:
    from .context import RotationContext
    from .state_adapter import GameStateView, UnitView
    _HAS_CONTEXT = True
except ImportError:
    _HAS_CONTEXT = False

__all__ = [
    "HealthPercent",
    "PowerPercent",
    "SpellInfo",
    "UnitSnapshot",
    "RotationContextV2",
    "EZWowException",
    "CaptureException",
    "BridgeException",
    "InputException",
    "ConfigurationException",
    "ExtractionException",
    "RecoveryException",
    "MaxRetriesExceededException",
    "RetryPolicy",
    "RecoveryExecutor",
]

if _HAS_CONTEXT:
    __all__.extend(["RotationContext", "GameStateView", "UnitView"])

