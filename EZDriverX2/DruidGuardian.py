"""守护德鲁伊循环。"""

from __future__ import annotations

from EZDriverX2 import (
    ComboConfig,
    ConfigRegistry,
    MacroRegistry,
    RotationContext,
    RotationProfile,
    SliderConfig,
    run_profile,
)


class DruidGuardian(RotationProfile):
    ICON = "Ability_Racial_BearForm.ico"
    """德鲁伊守护配置与循环逻辑。"""

    def setup(self, config: ConfigRegistry, macros: MacroRegistry) -> None:
        # self._last_player_health: float | None = None
        # self._last_attackable_in_range = False
        self._setup_config(config)
        self._setup_macros(macros)

    def _setup_config(self, config: ConfigRegistry) -> None:
        config.add(
            SliderConfig(
                key="aoe_enemy_count",
                label="AOE敌人数量",
                description="设置判定为AOE条件的敌人数量",
                min_value=2,
                max_value=10,
                step=1,
                default_value=4,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="opener_time",
                label="起手时间判定",
                description="设置判定起手状态的战斗时间",
                min_value=5,
                max_value=45,
                step=5,
                default_value=10,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="frenzied_regeneration_threshold",
                label="狂暴回复阈值 (%)",
                description="低于此血量时使用狂暴回复",
                min_value=10,
                max_value=60,
                step=1,
                default_value=45,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="barkskin_threshold",
                label="树皮阈值 (%)",
                description="低于此血量时使用树皮术",
                min_value=10,
                max_value=75,
                step=1,
                default_value=20,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="survival_instincts_threshold",
                label="生存本能阈值 (%)",
                description="低于此血量时使用生存本能",
                min_value=10,
                max_value=50,
                step=1,
                default_value=10,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="rage_overflow_threshold",
                label="怒气溢出阈值",
                description="高于该数值, 不打裂伤",
                min_value=60,
                max_value=120,
                step=5,
                default_value=90,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="rage_maul_threshold",
                label="重殴怒气阈值",
                description="高于该数值打重殴。超过怒气上限就不打了。",
                min_value=60,
                max_value=150,
                step=5,
                default_value=120,
                value_transform=float,
            )
        )
        config.add(
            ComboConfig(
                key="interrupt_logic",
                label="打断逻辑",
                description="什么情况下打断",
                options=["焦点和目标", "仅目标", "不打断"],
                default_index=0,
                value_transform=str,
            )
        )

        config.add(
            ComboConfig(
                key="incarnation_usable",
                label="使用化身",
                description="是否使用爆发",
                options=["否", "是"],
                default_index=0,
                value_transform=str,
            )
        )

        config.add(
            ComboConfig(
                key="ironfur_usable",
                label="使用铁鬃",
                description="是否使用铁鬃",
                options=["是", "否"],
                default_index=0,
                value_transform=str,
            )
        )

    def _setup_macros(self, macros: MacroRegistry) -> None:
        macros.set("target月火术", "ALT-NUMPAD1")
        macros.set("focus月火术", "ALT-NUMPAD2")
        macros.set("target裂伤", "ALT-NUMPAD3")
        macros.set("focus裂伤", "ALT-NUMPAD4")
        macros.set("target毁灭", "ALT-NUMPAD5")
        macros.set("focus毁灭", "ALT-NUMPAD6")
        macros.set("target摧折", "ALT-NUMPAD7")
        macros.set("focus摧折", "ALT-NUMPAD8")
        macros.set("target重殴", "ALT-NUMPAD9")
        macros.set("focus重殴", "ALT-NUMPAD0")
        macros.set("target赤红之月", "SHIFT-NUMPAD1")
        macros.set("focus赤红之月", "SHIFT-NUMPAD2")
        macros.set("target明月普照", "SHIFT-NUMPAD3")
        macros.set("focus明月普照", "SHIFT-NUMPAD4")
        macros.set("enemy痛击", "SHIFT-NUMPAD5")
        macros.set("enemy横扫", "SHIFT-NUMPAD6")
        macros.set("any切换目标", "SHIFT-NUMPAD7")
        macros.set("player狂暴", "SHIFT-NUMPAD8")
        macros.set("player化身：乌索克的守护者", "SHIFT-NUMPAD9")
        macros.set("player铁鬃", "SHIFT-NUMPAD0")
        macros.set("player狂暴回复", "ALT-F2")
        macros.set("player树皮术", "ALT-F3")
        macros.set("player生存本能", "ALT-F5")
        macros.set("target迎头痛击", "ALT-F6")
        macros.set("focus迎头痛击", "ALT-F7")
        macros.set("any熊形态", "ALT-F8")
        macros.set("nearest裂伤", "ALT-F9")
        macros.set("nearest毁灭", "ALT-F10")

    def main_rotation(self, ctx: RotationContext):
        # 主循环遵循“前置拦截 -> 起手与输出 -> 生存与防御 -> 填充 -> 兜底待机”的顺序。
        data = ctx.raw_data
        player = ctx.player
        target = ctx.target
        focus = ctx.focus

        spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
        gcd_ready = data.player.spell.公共冷却时间.remaining <= spell_queue_window

        player_health = float(player.status.unit_health or 0.0)

        # 前置拦截：非战斗/聊天/载具/施法或引导/死亡/吃喝时直接待机。
        # print("player.spell_icon", player.spell_icon)

        if data.misc.delay:
            return ctx.idle("游戏内等待")

        if (player.spell_icon != ""):
            if (player.spell_duration <= 95):
                return ctx.idle("在施法")

        if (not player.in_combat):
            return ctx.idle("不在战斗中")

        if (ctx.is_chatting):
            return ctx.idle("在聊天中")

        if player.has_buff("旅行形态"):
            return ctx.idle("旅行形态")

        if (player.status.unit_in_vehicle):
            return ctx.idle("在载具中")

        if (player.status.unit_is_dead_or_ghost):
            return ctx.idle("已死亡")

        if (player.aura.buff["食物和饮料"]):
            return ctx.idle("食物")

        if (target.is_self):
            return ctx.idle("目标是自己")

        if not player.has_buff("熊形态"):
            return ctx.cast("any", "熊形态")

        rage_max = float(ctx.cfg("rage_max") or 120.0)
        Rage = float(player.status.unit_power or 0.0) * rage_max / 100.0
        IsOpener = float(player.status.combat_time or 0.0) <= float(ctx.cfg("opener_time") or 10.0)
        IsAOE = float(data.misc.enemy_count or 0.0) >= float(ctx.cfg("aoe_enemy_count") or 4.0)
        EnemyInRange = int(data.misc.enemy_count or 0) >= 1         # 近距离有敌人

        # 攻击目标判定：优先 target，其次 focus；都不可攻击则无主目标。
        target_ok = bool(target.exists and target.in_range and target.can_attack)
        focus_ok = bool(focus.exists and focus.in_range and focus.can_attack)

        player_in_movement = player.status.unit_in_movement
        player_is_stand = not player_in_movement

        main_target = None
        if target_ok:
            main_target = target
        elif focus_ok:
            main_target = focus

        if (not main_target):
            # return ctx.cast("any", "切换目标")
            return ctx.idle("需要一个敌对目标")

        # If IsOpener and ([赤红之月] 冷却完毕):  # 起手循环 1 / 单体循环 1
        #     释放[赤红之月]  # 此技能代替 [月火术]
        if (ctx.spell_usable("赤红之月") and ctx.spell_cooldown_ready("赤红之月", spell_queue_window) and gcd_ready):
            if IsOpener:
                return ctx.cast(main_target.unitToken, "赤红之月")

        # If IsOpener and (正在接近目标) and (not [赤红之月] 冷却完毕):  # 起手循环 2
        #     释放[月火术]
        if (not main_target.has_debuff("月火术")):
            if (not ctx.spell_known("赤红之月")):
                if IsOpener:
                    if gcd_ready:
                        return ctx.cast(main_target.unitToken, "月火术")

        # If(血量较低):  # 单体循环 13 / AoE循环 11 / 起手循环 15
        #     释放[狂暴回复]
        # # 填充技能

        if (player_health < float(ctx.cfg("frenzied_regeneration_threshold") or 45.0)):
            if (ctx.spell_usable("狂暴回复") and (ctx.spell_charges("狂暴回复") > 0) and gcd_ready):
                return ctx.cast("player", "狂暴回复")

        # 血线保命：按你的要求，先树皮术，再生存本能。
        if (player_health < float(ctx.cfg("barkskin_threshold") or 20.0)):
            if (ctx.spell_usable("树皮术") and ctx.spell_cooldown_ready("树皮术", spell_queue_window) and gcd_ready):
                return ctx.cast("player", "树皮术")

        if (player_health < float(ctx.cfg("survival_instincts_threshold") or 10.0)):
            if (ctx.spell_usable("生存本能") and ctx.spell_cooldown_ready("生存本能", spell_queue_window) and gcd_ready):
                return ctx.cast("player", "生存本能")

        if str(ctx.cfg("ironfur_usable") or "是") == "是":
            if (not player.has_buff("铁鬃")) or (player.buff_stack("铁鬃") < 2) or (player.buff_remaining("铁鬃") < 3):
                if ctx.spell_cooldown_ready("铁鬃", spell_queue_window):
                    return ctx.cast("player", "铁鬃")

        if (ctx.spell_usable("痛击") and ctx.spell_cooldown_ready("痛击", spell_queue_window) and gcd_ready):
            if IsOpener:
                if EnemyInRange:
                    return ctx.cast("enemy", "痛击")

        if str(ctx.cfg("incarnation_usable") or "否") == "是":
            if (ctx.spell_usable("化身：乌索克的守护者") and ctx.spell_cooldown_ready("化身：乌索克的守护者", spell_queue_window)):
                if IsOpener and player_is_stand:
                    return ctx.cast("player", "化身：乌索克的守护者")

        if (ctx.spell_usable("狂暴") and ctx.spell_cooldown_ready("狂暴", spell_queue_window) and player_is_stand):
            if IsOpener:
                return ctx.cast("player", "狂暴")

        interrupt_logic = ctx.cfg("interrupt_logic") or "焦点和目标"
        # 打断焦点
        if (ctx.spell_usable("迎头痛击") and ctx.spell_cooldown_ready("迎头痛击", spell_queue_window)):
            if focus_ok:
                if focus.spell_interruptible:
                    if (interrupt_logic == "焦点和目标"):
                        return ctx.cast(focus.unitToken, "迎头痛击")
            if target_ok:
                if target.spell_interruptible:
                    if (interrupt_logic in ("焦点和目标", "仅目标")):
                        return ctx.cast(target.unitToken, "迎头痛击")

        if (ctx.spell_usable("明月普照") and ctx.spell_cooldown_ready("明月普照", spell_queue_window) and gcd_ready):
            if IsOpener and player_is_stand:
                return ctx.cast(main_target.unitToken, "明月普照")

        if (ctx.spell_usable("毁灭") and ctx.spell_cooldown_ready("毁灭", spell_queue_window) and gcd_ready):
            if (Rage > 40):
                return ctx.cast("nearest", "毁灭")
                # return ctx.cast(main_target.unitToken, "毁灭")

        # 两层裂伤优先于痛击

        if (ctx.spell_usable("裂伤") and (ctx.spell_charges("裂伤") == 2) and gcd_ready):
            if (Rage < float(ctx.cfg("rage_overflow_threshold") or 90.0)):
                return ctx.cast("nearest", "裂伤")

        if (ctx.spell_usable("痛击") and ctx.spell_cooldown_ready("痛击", spell_queue_window) and gcd_ready):
            if EnemyInRange:
                if ((main_target.debuff_stack("痛击") < 3) or (main_target.debuff_remaining("痛击") < 4)):
                    return ctx.cast("enemy", "痛击")
                if IsAOE:
                    return ctx.cast("enemy", "痛击")

        if (ctx.spell_usable("裂伤") and (ctx.spell_charges("裂伤") > 0) and gcd_ready):
            if IsAOE:
                if (Rage > float(ctx.cfg("rage_overflow_threshold") or 90.0)):
                    pass
                else:
                    return ctx.cast("nearest", "裂伤")
                    # return ctx.cast(main_target.unitToken, "裂伤")
            else:
                # return ctx.cast(main_target.unitToken, "裂伤")
                return ctx.cast("nearest", "裂伤")

        # If(存在[星河守护者] 触发):  # 单体循环 11 / AoE循环 12
        #     If(not IsAOE) or (IsAOE and 触发即将过期):
        #         释放[月火术]
        if player.has_buff("星河守护者"):
            if gcd_ready:
                if (not IsAOE):
                    return ctx.cast(main_target.unitToken, "月火术")
                if IsAOE:
                    if (player.buff_remaining("星河守护者") < 4):
                        return ctx.cast(main_target.unitToken, "月火术")

        # If(not 主目标存在[月火术]):  # 单体循环 2 / AoE循环 1
        #     释放[月火术]
        if (not main_target.has_debuff("月火术")):
            if gcd_ready:
                return ctx.cast(main_target.unitToken, "月火术")

        # # 怒气倾泻逻辑
        # # 设定怒气阈值
        # RageThreshold = 0
        # If 天赋[驾驭怒火]:  # 单体循环 8 / AoE循环 8
        #     RageThreshold = 80
        # If 天赋[致命一击]:  # 单体循环 9 / AoE循环 9
        #     RageThreshold = 60
        # If(怒气 >= RageThreshold) :  # 单体循环 10 / AoE循环 7 / 起手循环 10-12
        #     If IsAOE:
        #         释放[摧折]
        #     Else:
        #         释放[重殴]
        if (Rage > float(ctx.cfg("rage_maul_threshold") or 120.0)):
            if gcd_ready:
                if IsAOE:
                    if (ctx.spell_usable("摧折") and ctx.spell_cooldown_ready("摧折", spell_queue_window)):
                        return ctx.cast("enemy", "摧折")
                elif (ctx.spell_usable("重殴") and ctx.spell_cooldown_ready("重殴", spell_queue_window)):
                    return ctx.cast(main_target.unitToken, "重殴")

        # # 防御与生存
        # If(怒气即将溢出) or (受到物理伤害):  # 单体循环 12 / AoE循环 10 / 起手循环 14
        #     释放[铁鬃]
        if (Rage > float(ctx.cfg("rage_overflow_threshold") or 90.0)):
            return ctx.cast("player", "铁鬃")

        # If(存在空余 GCD):  # 单体循环 14 / AoE循环 13 / 起手循环 16
        #     释放[横扫] 或[月火术]
        if gcd_ready:
            if (not IsAOE):
                return ctx.cast(main_target.unitToken, "月火术")
            if player.has_buff("星河守护者"):
                return ctx.cast(main_target.unitToken, "月火术")
            return ctx.cast("enemy", "横扫")

        return ctx.idle("无所事事")


if __name__ == "__main__":
    raise SystemExit(run_profile(DruidGuardian()))
