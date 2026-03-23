# EZDriverX2

`EZDriverX2` 是 EZPixel 链路中的最终驱动层：

1. `EZPixelAddonX2`：游戏内采集
2. `EZPixelBridgeX2`：状态桥接为 JSON
3. `EZDriverX2`：轮询状态、做决策、发送按键

本文档已对齐当前源码实现，重点参考：

- `src/DruidGuardian.py`
- `src/EZDriverX2/runtime/context.py`
- `src/EZDriverX2/runtime/state_adapter.py`
- `HowToWriteProfile.md`

## 快速开始

```powershell
uv sync
uv run python src/PriestDiscipline.py
```

## Profile 契约

每个职业/专精脚本继承 `RotationProfile` 并实现两个方法：

- `setup(config, macros)`：注册配置项与宏映射
- `main_rotation(ctx)`：每个 tick 返回一个动作（`ctx.cast(...)` 或 `ctx.idle(...)`）

入口由 `run_profile(profile)` 驱动。

## 当前可用 API（按源码）

### RotationContext

`RotationContext` 当前公开可用能力如下：

**属性**

- `ctx.raw_data`：完整原始状态（`AttrDict`）
- `ctx.state`：`GameStateView`，可用 `ctx.state.party_members(include_player=True)` 读取队伍视图
- `ctx.player` / `ctx.target` / `ctx.focus`：常用 `UnitView`
- `ctx.is_chatting`：是否聊天中
- `ctx.spell`：玩家技能表（标准化后的 `AttrDict`）

**方法**

- `ctx.cfg(key)`：读取配置值（优先当前值，否则默认值）
- `ctx.cast(unitToken, spell)`：返回 `CastAction`
- `ctx.idle(reason)`：返回 `IdleAction`
- `ctx.spell_known(spell_name)`：是否已学会
- `ctx.spell_usable(spell_name)`：是否可用（已学会 + usable）
- `ctx.spell_charges(spell_name)`：层数（不可用时返回 `0`）
- `ctx.spell_remaining(spell_name)`：剩余 CD（不可用/异常时返回 `9999.0`）
- `ctx.spell_cooldown_ready(spell_name, spell_queue_window)`：CD 是否进入可释放窗口

> 历史文档里出现过的 `ctx.in_combat()`、`ctx.is_dead()`、`ctx.global_cooldown_ready()`、`ctx.spell_ready()`、`ctx.lowest_hp_member()`、`ctx.auto_attack_target()` 在当前实现中不存在，请不要再使用。

### UnitView

`UnitView`（`ctx.player/target/focus`）常用字段与方法：

**状态属性**

- `exists` / `is_self` / `in_range` / `can_attack` / `in_combat`
- `hp_pct` / `role` / `damage_absorbs` / `heal_absorbs` / `unit_class`

**光环与施法属性**

- `aura` / `buff` / `debuff` / `debuff_sequence`
- `cast_icon` / `cast_duration` / `cast_interruptible`
- `channel_icon` / `channel_duration` / `channel_interruptible`
- `spell_icon` / `spell_duration` / `spell_interruptible`（注意：当前源码字段名就是 `spell`）

**方法**

- `has_buff(title)` / `buff_remaining(title)` / `buff_stack(title)`
- `has_debuff(title)` / `debuff_remaining(title)` / `debuff_stack(title)`

## 最小可运行示例（与当前 API 一致）

```python
from EZDriverX2 import (
    ConfigRegistry,
    MacroRegistry,
    RotationContext,
    RotationProfile,
    SliderConfig,
    run_profile,
)


class DemoProfile(RotationProfile):
    def setup(self, config: ConfigRegistry, macros: MacroRegistry) -> None:
        config.add(
            SliderConfig(
                key="dot_refresh_window",
                label="DoT补刷窗口",
                min_value=1,
                max_value=8,
                step=1,
                default_value=3,
                value_transform=float,
            )
        )
        macros.set("target月火术", "ALT-NUMPAD1")
        macros.set("focus月火术", "ALT-NUMPAD2")
        macros.set("any切换目标", "SHIFT-F8")

    def main_rotation(self, ctx: RotationContext):
        data = ctx.raw_data
        player = ctx.player
        target = ctx.target
        focus = ctx.focus

        spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
        gcd_remaining = float(data.player.spell.公共冷却时间.remaining or 9999.0)
        gcd_ready = gcd_remaining <= spell_queue_window

        if (player.spell_icon != "") and (player.spell_duration <= 95):
            return ctx.idle("在施法")
        if not player.in_combat:
            return ctx.idle("不在战斗中")
        if ctx.is_chatting:
            return ctx.idle("在聊天中")
        if player.status.unit_is_dead_or_ghost:
            return ctx.idle("已死亡")

        target_ok = bool(target.exists and target.in_range and target.can_attack)
        focus_ok = bool(focus.exists and focus.in_range and focus.can_attack)
        main_target = target if target_ok else (focus if focus_ok else None)

        if not main_target:
            return ctx.cast("any", "切换目标")

        if (
            ctx.spell_usable("月火术")
            and ctx.spell_cooldown_ready("月火术", spell_queue_window)
            and gcd_ready
        ):
            return ctx.cast(main_target.unitToken, "月火术")

        return ctx.idle("无所事事")


if __name__ == "__main__":
    raise SystemExit(run_profile(DemoProfile()))
```

## 数据读取建议

优先级建议：

1. `ctx.player` / `ctx.target` / `ctx.focus`（语义清晰）
2. `ctx.state.party_members(...)`（队伍遍历）
3. `ctx.raw_data`（最灵活，但要自己兜底）

图像识别场景下字段可能延迟或缺失，建议统一写默认值，例如：

- `float(value or 0.0)`
- `int(value or 0)`
- `bool(value)`

## GCD 与技能窗口建议

推荐写法与当前 `DruidGuardian` 一致：

```python
spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
gcd_ready = float(ctx.raw_data.player.spell.公共冷却时间.remaining or 9999.0) <= spell_queue_window

if ctx.spell_usable("技能") and ctx.spell_cooldown_ready("技能", spell_queue_window) and gcd_ready:
    return ctx.cast("target", "技能")
```

## 宏映射规则

执行器使用 `unitToken + spell` 作为逻辑键：

- `ctx.cast("party1", "快速治疗")` -> 查找宏键 `party1快速治疗`
- `ctx.cast("any", "切换目标")` -> 查找宏键 `any切换目标`

如果未注册对应宏，动作会被记录但不会发送按键。
