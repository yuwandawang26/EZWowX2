# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false, reportUnknownLambdaType=false
"""戒律牧师循环。"""

from __future__ import annotations

from EZDriverX2 import (
    # ComboConfig,
    ConfigRegistry,
    MacroRegistry,
    RotationContext,
    RotationProfile,
    SliderConfig,
    run_profile,
)
# from EZDriverX2.runtime.data import AttrDict

# 高伤害debuff列表
high_damage_debuff = ["张三", "李四", "王五"]


class DruidFeral(RotationProfile):
    ICON = "Ability_Druid_CatForm.ico"
    """德鲁伊野性配置与循环逻辑。"""

    def setup(self, config: ConfigRegistry, macros: MacroRegistry) -> None:
        self._setup_config(config)
        self._setup_macros(macros)

    def _setup_config(self, config: ConfigRegistry) -> None:
        config.add(
            SliderConfig(
                key="self_heal_threshold",
                label="自我治疗阈值 (%)",
                description="低于此血量时使用自我治疗技能",
                min_value=20,
                max_value=80,
                step=2.5,
                default_value=45,
                value_transform=float,
            )
        )

    def _setup_macros(self, macros: MacroRegistry) -> None:

        # macros.set("any渐隐术", "SHIFT-F12")
        pass

    def main_rotation(self, ctx: RotationContext):
        # 主循环遵循“前置拦截 -> 治疗优先 -> 输出补伤害 -> 兜底待机”的顺序。
        # data = ctx.raw_data
        # spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)

        # player = data.player
        # spell = player.spell
        # gcd = spell.公共冷却时间
        # gcd_ready = gcd.remaining <= spell_queue_window
        # target = data.target
        # focus = data.focus

        return ctx.idle("无所事事")


if __name__ == "__main__":
    raise SystemExit(run_profile(DruidFeral()))
