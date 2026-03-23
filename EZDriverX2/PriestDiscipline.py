"""戒律牧师循环。"""

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
from EZDriverX2.runtime.data import AttrDict

# 高伤害debuff列表
high_damage_debuff = ["张三", "李四", "王五"]


class PriestDiscipline(RotationProfile):
    ICON = "spell_holy_powerwordshield.ico"
    """戒律牧师配置与循环逻辑。"""

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
        config.add(
            SliderConfig(
                key="tank_deficit_ignore_pct",
                label="TANK缺口忽略 (%)",
                description="TANK 视为满血的缺口比例（例如 20 代表 80% 视为满血）",
                min_value=0,
                max_value=100,
                step=5,
                default_value=20,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="tank_health_score_mul",
                label="TANK健康分数系数",
                description="用于调整TANK健康分数的加成系数",
                min_value=1.0,
                max_value=1.2,
                step=0.05,
                default_value=1.10,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="healer_health_score_mul",
                label="HEALER健康分数系数",
                description="用于调整HEALER健康分数的系数",
                min_value=0.8,
                max_value=1.0,
                step=0.05,
                default_value=0.95,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="fade_threshold",
                label="渐隐术阈值 (%)",
                description="低于此血量时使用渐隐术",
                min_value=50,
                max_value=100,
                step=2.5,
                default_value=85,
                value_transform=float,
            )
        )
        config.add(
            ComboConfig(
                key="dispel_logic",
                label="驱散逻辑",
                description="在什么情况下驱散",
                options=["黑名单", "白名单", "乱驱"],
                default_index=0,
                value_transform=str,
            )
        )
        config.add(
            ComboConfig(
                key="dispel_types",
                label="驱散类型",
                description="根据天赋选择可驱散的类型",
                options=["MAGIC|DISEASE", "MAGIC"],
                default_index=0,
                value_transform=lambda s: s.split("|") if s else [],
            )
        )
        config.add(
            SliderConfig(
                key="need_heal_deficit_threshold",
                label="最小治疗缺口",
                description="治疗缺口大于该值时视为需要治疗",
                min_value=0,
                max_value=20,
                step=1,
                default_value=10,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="penance_heal_max_targets",
                label="进攻苦修群抬目标数",
                description="需要治疗人数不超过该值时对友方施放苦修",
                min_value=1,
                max_value=4,
                step=1,
                default_value=3,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="flash_heal_deficit_threshold",
                label="快速治疗阈值",
                description="治疗缺口超过该值时施放快速治疗",
                min_value=1,
                max_value=50,
                step=5,
                default_value=25,
                value_transform=float,
            )
        )
        config.add(
            ComboConfig(
                key="penance_logic",
                label="苦修逻辑",
                description="在什么情况下使用苦修",
                options=["攻守兼备", "仅治疗"],
                default_index=0,
                value_transform=str,
            )
        )
        config.add(
            ComboConfig(
                key="plea_logic",
                label="恳求逻辑",
                description="恳求是个高蓝耗, 低收益技能, 除了补救赎没有其他用途, 根据习惯调整。",
                options=["血量大于缺口无救赎", "任意情况补救赎", "不使用"],
                default_index=0,
                value_transform=str,
            )
        )
        config.add(
            ComboConfig(
                key="radiance_logic",
                label="耀逻辑",
                description="耀提供了治疗量，在全员满血时使用耀，还是有点浪费的。",
                options=["有缺口才使用", "满血使用"],
                default_index=0,
                value_transform=str,
            )
        )

    def _setup_macros(self, macros: MacroRegistry) -> None:
        macros.set("target痛", "ALT-NUMPAD1")
        macros.set("focus痛", "ALT-NUMPAD2")
        macros.set("target灭", "ALT-NUMPAD3")
        macros.set("focus灭", "ALT-NUMPAD4")
        macros.set("target心灵震爆", "ALT-NUMPAD5")
        macros.set("focus心灵震爆", "ALT-NUMPAD6")
        macros.set("target惩击", "ALT-NUMPAD7")
        macros.set("focus惩击", "ALT-NUMPAD8")
        macros.set("player盾", "ALT-NUMPAD9")
        macros.set("party1盾", "ALT-NUMPAD0")
        macros.set("party2盾", "SHIFT-NUMPAD1")
        macros.set("party3盾", "SHIFT-NUMPAD2")
        macros.set("party4盾", "SHIFT-NUMPAD3")
        macros.set("target苦修", "SHIFT-NUMPAD4")
        macros.set("focus苦修", "SHIFT-NUMPAD5")
        macros.set("player苦修", "SHIFT-NUMPAD6")
        macros.set("party1苦修", "SHIFT-NUMPAD7")
        macros.set("party2苦修", "SHIFT-NUMPAD8")
        macros.set("party3苦修", "SHIFT-NUMPAD9")
        macros.set("party4苦修", "SHIFT-NUMPAD0")
        macros.set("player恳求", "ALT-F2")
        macros.set("party1恳求", "ALT-F3")
        macros.set("party2恳求", "ALT-F5")
        macros.set("party3恳求", "ALT-F6")
        macros.set("party4恳求", "ALT-F7")
        macros.set("player纯净术", "ALT-F8")
        macros.set("party1纯净术", "ALT-F9")
        macros.set("party2纯净术", "ALT-F10")
        macros.set("party3纯净术", "ALT-F11")
        macros.set("party4纯净术", "ALT-F12")
        macros.set("player快速治疗", "SHIFT-F2")
        macros.set("party1快速治疗", "SHIFT-F3")
        macros.set("party2快速治疗", "SHIFT-F5")
        macros.set("party3快速治疗", "SHIFT-F6")
        macros.set("party4快速治疗", "SHIFT-F7")
        macros.set("any切换目标", "SHIFT-F8")
        macros.set("any耀", "SHIFT-F9")
        macros.set("any绝望祷言", "SHIFT-F10")
        macros.set("any耐力", "SHIFT-F11")
        macros.set("any渐隐术", "SHIFT-F12")

    def calculate_party_health_score(self, ctx: RotationContext) -> list[AttrDict]:
        spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
        party_members: list[AttrDict] = []
        dispel_type_list = ctx.cfg("dispel_types") or []

        for member in ctx.state.party_members(include_player=True):
            if (not member.exists) or (not member.in_range) or (not member.is_alive):
                continue

            role = member.role
            hp_pct = member.hp_pct
            damage_absorbs = member.damage_absorbs
            heal_absorbs = member.heal_absorbs
            unit_class = member.unit_class

            # 血量基线: 当前血量 - 治疗吸收
            health_base = hp_pct - heal_absorbs

            # 缺口 = 加满血所需要的治疗。
            health_deficit = 100 - health_base

            # 坦克允许配置"缺口忽略值"，避免轻微掉血就抢占治疗优先级。
            if role == "TANK":
                health_deficit = max(
                    health_deficit - float(ctx.cfg("tank_deficit_ignore_pct") or 0.0),
                    0.0,
                )

            # 健康分数 = 血量基线 + 伤害吸收；分数越低越危险。
            health_score = health_base + damage_absorbs

            # 角色修正：可通过系数调高坦克优先级、调低治疗职业优先级。
            if role == "TANK":
                health_score *= float(ctx.cfg("tank_health_score_mul") or 1.0)
            elif role == "HEALER":
                health_score *= float(ctx.cfg("healer_health_score_mul") or 1.0)

            dispel_list = [debuff.type for debuff in member.debuff_sequence if debuff.type in dispel_type_list]
            damage_debuff_count = len([debuff for debuff in member.debuff_sequence if debuff.title in high_damage_debuff])

            unit_dict = AttrDict(
                {
                    "unitToken": member.unitToken,
                    "unit_class": unit_class,
                    "role": role,
                    "hp_pct": hp_pct,
                    "damage_absorbs": damage_absorbs,
                    "heal_absorbs": heal_absorbs,
                    "health_deficit": health_deficit,
                    "health_score": health_score,
                    "health_base": health_base,
                    "shield_remaining": member.buff_remaining("真言术：盾"),
                    "atonement_remaining": member.buff_remaining("救赎"),
                    "fortitude_remaining": member.buff_remaining("真言术：韧"),
                    "dispel_list": dispel_list,
                    "damage_debuff_count": damage_debuff_count,
                    "ctx": member,
                }
            )
            party_members.append(unit_dict)

        party_members.sort(key=lambda x: x.health_score, reverse=False)
        return party_members

    def main_rotation(self, ctx: RotationContext):
        # 主循环遵循"前置拦截 -> 治疗优先 -> 输出补伤害 -> 兜底待机"的顺序。
        data = ctx.raw_data
        spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
        gcd_ready = data.player.spell.公共冷却时间.remaining <= spell_queue_window
        player = ctx.player
        target = ctx.target
        focus = ctx.focus

        # 前置拦截：施法/非战斗/聊天/载具/死亡/吃喝时直接待机。
        if (player.spell_icon != ""):
            if (player.spell_duration <= 95):
                return ctx.idle("在施法")

        if (not player.in_combat):
            return ctx.idle("不在战斗中")

        if ctx.is_chatting:
            return ctx.idle("在聊天中")

        if player.status.unit_in_vehicle:
            return ctx.idle("在载具中")

        if player.status.unit_is_dead_or_ghost:
            return ctx.idle("已死亡")

        if player.aura.buff["食物和饮料"]:
            return ctx.idle("食物")

        if target.is_self:
            return ctx.idle("目标是自己")

        party_members = self.calculate_party_health_score(ctx)

        if len(party_members) == 0:
            return ctx.idle("没有队友在视野内")

        player_in_movement = player.status.unit_in_movement
        player_is_stand = not player_in_movement

        # 进攻目标优先级：focus > target，且要求在范围内、可攻击、处于战斗。
        auto_target = None
        if focus.exists and focus.in_range and focus.can_attack and focus.in_combat:
            auto_target = focus
        elif target.exists and target.in_range and target.can_attack and target.in_combat:
            auto_target = target

        # 预计算常用目标列表，后续各技能按这些列表直接取最高优先级目标。
        without_shield = [unit for unit in party_members if unit.shield_remaining <= spell_queue_window]
        without_atonement = [unit for unit in party_members if unit.atonement_remaining <= spell_queue_window]
        with_debuff_members = [unit for unit in party_members if len(unit.dispel_list) > 0]

        need_heal_member = [
            unit
            for unit in party_members
            if unit.health_deficit > float(ctx.cfg("need_heal_deficit_threshold") or 0.0)
        ]
        need_heal_member.sort(key=lambda x: x.health_score, reverse=False)
        need_heal_without_atonement_member = [unit for unit in need_heal_member if unit.atonement_remaining <= spell_queue_window]

        # 1) 自保：先保命，再进行团队循环。
        if ctx.spell_usable("绝望祷言") and ctx.spell_cooldown_ready("绝望祷言", spell_queue_window):
            if player.hp_pct < float(ctx.cfg("self_heal_threshold") or 45):
                return ctx.cast("any", "绝望祷言")

        if ctx.spell_usable("渐隐术") and ctx.spell_cooldown_ready("渐隐术", spell_queue_window):
            if player.hp_pct < float(ctx.cfg("fade_threshold") or 85):
                return ctx.cast("any", "渐隐术")

        # 2) 耀：双充能且可读条时，根据配置决定"有缺口放"或"补救赎放"。
        radiance_ready = ctx.spell_usable("真言术：耀") and (ctx.spell_charges("真言术：耀") == 2) and gcd_ready and player_is_stand
        radiance_logic_1 = (ctx.cfg("radiance_logic") == "有缺口才使用") and (len(need_heal_without_atonement_member) >= 2)
        radiance_logic_2 = (ctx.cfg("radiance_logic") == "满血使用") and (len(without_atonement) >= 2)
        if radiance_ready and (radiance_logic_1 or radiance_logic_2):
            return ctx.cast("any", "耀")

        # 3) 纯净术：有可驱散目标时优先处理。
        if ctx.spell_usable("纯净术") and (ctx.spell_charges("纯净术") >= 1) and gcd_ready:
            if len(with_debuff_members) > 0:
                return ctx.cast(with_debuff_members[0].unitToken, "纯净术")

        # 4) 盾：在[祸福相倚]层数足够时，优先给无盾目标。
        if player.has_buff("祸福相倚") and (player.buff_stack("祸福相倚") >= 4) and gcd_ready:
            if ctx.spell_usable("真言术：盾") and ctx.spell_cooldown_ready("真言术：盾", spell_queue_window):
                if len(without_shield) > 0:
                    return ctx.cast(without_shield[0].unitToken, "盾")
                return ctx.cast(party_members[0].unitToken, "盾")

        # 5) 心灵震爆：有进攻目标、无[阴暗面之力]时优先打输出循环。
        if auto_target and ctx.spell_usable("心灵震爆") and ctx.spell_cooldown_ready("心灵震爆", spell_queue_window) and (not player.has_buff("阴暗面之力")) and gcd_ready and player_is_stand:
            return ctx.cast(auto_target.unitToken, "心灵震爆")

        # 6) 苦修：按配置在治疗与进攻之间切换；治疗人数少时优先抬血。
        penance_logic_1 = ctx.cfg("penance_logic") == "攻守兼备"
        penance_logic_2 = (ctx.cfg("penance_logic") == "仅治疗") and (len(need_heal_member) > 0)
        if ctx.spell_usable("苦修") and (ctx.spell_charges("苦修") >= 1) and gcd_ready and (penance_logic_1 or penance_logic_2):
            if len(need_heal_member) <= int(float(ctx.cfg("penance_heal_max_targets") or 3.0)) and len(need_heal_member) > 0:
                return ctx.cast(need_heal_member[0].unitToken, "苦修")
            if auto_target:
                return ctx.cast(auto_target.unitToken, "苦修")

        # 7) 快速治疗：单抬补刀，站立或有瞬发增益时才会触发。
        can_cast_flash = player_is_stand or player.has_buff("圣光涌动")
        if party_members and (party_members[0].health_deficit > float(ctx.cfg("flash_heal_deficit_threshold") or 25)) and gcd_ready and can_cast_flash:
            return ctx.cast(party_members[0].unitToken, "快速治疗")

        # 8) 恳求：用于补救赎，具体策略由配置决定。
        plea_logic_1 = (ctx.cfg("plea_logic") == "血量大于缺口无救赎") and (len(need_heal_without_atonement_member) > 0)
        if plea_logic_1 and gcd_ready:
            return ctx.cast(need_heal_without_atonement_member[0].unitToken, "恳求")
        plea_logic_2 = (ctx.cfg("plea_logic") == "任意情况补救赎") and (len(without_atonement) > 0)
        if plea_logic_2 and gcd_ready:
            return ctx.cast(without_atonement[0].unitToken, "恳求")

        # 9) 没有有效进攻目标时，先尝试切换目标，再继续后续伤害逻辑。
        if not auto_target:
            return ctx.cast("any", "切换目标")

        # 10) 补 DOT：优先当前自动目标，其次 focus，再次 target。
        if auto_target:
            if (not auto_target.has_debuff("痛")) and gcd_ready:
                return ctx.cast(auto_target.unitToken, "痛")
        if focus.exists and focus.in_range and focus.can_attack and focus.in_combat:
            if (not focus.has_debuff("痛")) and gcd_ready:
                return ctx.cast(focus.unitToken, "痛")
        if target.exists and target.in_range and target.can_attack and target.in_combat:
            if (not target.has_debuff("痛")) and gcd_ready:
                return ctx.cast(target.unitToken, "痛")

        # 11) 斩杀：目标低于 20% 血且可用时打[暗言术：灭]。
        if auto_target and (auto_target.hp_pct < 20) and ctx.spell_usable("暗言术：灭") and ctx.spell_cooldown_ready("暗言术：灭", spell_queue_window):
            return ctx.cast(auto_target.unitToken, "灭")

        # 12) 常规填充：满足条件时对自动目标打[惩击]。
        if auto_target and gcd_ready:
            return ctx.cast(auto_target.unitToken, "惩击")

        # 13) 公共冷却未转好时等待，否则本轮无动作。
        if not gcd_ready:
            return ctx.idle("公共冷却时间")

        return ctx.idle("无所事事")


if __name__ == "__main__":
    raise SystemExit(run_profile(PriestDiscipline()))
