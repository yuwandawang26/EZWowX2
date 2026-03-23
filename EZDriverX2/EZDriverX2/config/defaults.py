"""Default runtime config items."""

from __future__ import annotations

from .items import SliderConfig
from .registry import ConfigRegistry


def register_default_config(config: ConfigRegistry) -> None:
    config.add(
        SliderConfig(
            key="fps",
            label="刷新速度",
            description="请求 API 的速度",
            min_value=1,
            max_value=30,
            step=1,
            default_value=15,
            value_transform=float,
        )
    )
    config.add(
        SliderConfig(
            key="interval_jitter",
            label="间隔浮动",
            description="请求间隔随机浮动比例（例如 0.2 表示 ±20%）",
            min_value=0.0,
            max_value=0.5,
            step=0.05,
            default_value=0.2,
            value_transform=float,
        )
    )
    config.add(
        SliderConfig(
            key="spell_queue_window",
            label="延迟容限（秒）",
            description="对 GCD 的延迟容限",
            min_value=0.2,
            max_value=0.6,
            step=0.02,
            default_value=0.4,
            value_transform=float,
        )
    )
