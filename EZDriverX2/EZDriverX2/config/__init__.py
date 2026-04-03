"""Config definitions and registries."""

from .defaults import register_default_config
from .items import ComboConfig, ConfigItem, SliderConfig
from .macros import MacroRegistry
from .registry import ConfigRegistry
from .node_layout import (
    NodeLayout,
    NodeRegion,
    RegionSlice,
    DEFAULT_NODE_LAYOUT,
    validate_layout,
    load_layout_from_dict,
)
from .occlusion_rules import (
    OcclusionRule,
    OcclusionRuleEngine,
    OcclusionCheckResult,
    RuleType,
    create_default_engine,
)
from .validation import (
    validate_unit_data,
    validate_spell_data,
    validate_context_data,
)

__all__ = [
    "ConfigItem",
    "SliderConfig",
    "ComboConfig",
    "ConfigRegistry",
    "MacroRegistry",
    "register_default_config",
    "NodeLayout",
    "NodeRegion",
    "RegionSlice",
    "DEFAULT_NODE_LAYOUT",
    "validate_layout",
    "load_layout_from_dict",
    "OcclusionRule",
    "OcclusionRuleEngine",
    "OcclusionCheckResult",
    "RuleType",
    "create_default_engine",
    "validate_unit_data",
    "validate_spell_data",
    "validate_context_data",
]

