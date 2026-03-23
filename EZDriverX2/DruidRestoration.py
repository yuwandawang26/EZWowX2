"""德鲁伊恢复循环。"""

from __future__ import annotations

from EZDriverX2 import (
    ConfigRegistry,
    MacroRegistry,
    RotationContext,
    RotationProfile,
    SliderConfig,
    run_profile,
)
from EZDriverX2.runtime.data import AttrDict

# 可驱散 debuff 类型
DISPEL_TYPES = {"MAGIC", "CURSE", "POISON"}


class DruidRestoration(RotationProfile):
    ICON = "SPELL_NATURE_HEALINGTOUCH.ico"
    """德鲁伊恢复配置与循环逻辑。"""

    def setup(self, config: ConfigRegistry, macros: MacroRegistry) -> None:
        self._setup_config(config)
        self._setup_macros(macros)

    def _setup_config(self, config: ConfigRegistry) -> None:
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
                key="ironbark_hp_threshold",
                label="铁木树皮血量阈值",
                description="最低目标治疗基线低于该值时施放铁木树皮",
                min_value=30,
                max_value=70,
                step=1,
                default_value=50,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="barkskin_hp_threshold",
                label="树皮术血量阈值",
                description="自身治疗基线低于该值时施放树皮术",
                min_value=30,
                max_value=70,
                step=1,
                default_value=50,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="convoke_party_hp_threshold",
                label="万灵队血阈值",
                description="队伍平均治疗基线低于该值时施放万灵之召",
                min_value=45,
                max_value=85,
                step=1,
                default_value=65,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="convoke_single_hp_threshold",
                label="万灵单体阈值",
                description="最低目标治疗基线低于该值时施放万灵之召",
                min_value=0,
                max_value=40,
                step=1,
                default_value=20,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="wild_growth_count_threshold",
                label="野性成长人数阈值",
                description="低于野性成长血量阈值的人数达到该值时施放",
                min_value=1,
                max_value=5,
                step=1,
                default_value=2,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="wild_growth_hp_threshold",
                label="野性成长血量阈值",
                description="治疗基线低于该值时计入野性成长人数统计",
                min_value=75,
                max_value=100,
                step=1,
                default_value=95,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="tranquility_party_hp_threshold",
                label="宁静队血阈值",
                description="队伍平均治疗基线低于该值时施放宁静",
                min_value=30,
                max_value=70,
                step=1,
                default_value=50,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="nature_swiftness_hp_threshold",
                label="自然迅捷阈值",
                description="最低目标治疗基线低于该值时施放自然迅捷",
                min_value=40,
                max_value=80,
                step=1,
                default_value=60,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="swiftmend_count_threshold",
                label="迅捷治愈人数阈值",
                description="低于迅捷治愈血量阈值的人数达到该值时施放",
                min_value=1,
                max_value=5,
                step=1,
                default_value=3,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="swiftmend_hp_threshold",
                label="迅捷治愈血量阈值",
                description="治疗基线低于该值时计入迅捷治愈人数统计",
                min_value=45,
                max_value=85,
                step=1,
                default_value=65,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="regrowth_hp_threshold",
                label="愈合阈值",
                description="最低目标治疗基线低于该值时施放愈合",
                min_value=50,
                max_value=90,
                step=1,
                default_value=70,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="rejuvenation_hp_threshold",
                label="回春阈值",
                description="目标治疗基线低于该值且回春层数不足时施放回春术",
                min_value=80,
                max_value=100,
                step=1,
                default_value=100,
                value_transform=float,
            )
        )
        config.add(
            SliderConfig(
                key="abundance_stack_threshold",
                label="丰饶阈值",
                description="丰饶层数低于该值时补充回春术",
                min_value=1,
                max_value=10,
                step=1,
                default_value=5,
                value_transform=float,
            )
        )

    def _setup_macros(self, macros: MacroRegistry) -> None:
        macros.set("player铁木树皮", "ALT-NUMPAD1")
        macros.set("party1铁木树皮", "ALT-NUMPAD2")
        macros.set("party2铁木树皮", "ALT-NUMPAD3")
        macros.set("party3铁木树皮", "ALT-NUMPAD4")
        macros.set("party4铁木树皮", "ALT-NUMPAD5")
        macros.set("player自然之愈", "ALT-NUMPAD6")
        macros.set("party1自然之愈", "ALT-NUMPAD7")
        macros.set("party2自然之愈", "ALT-NUMPAD8")
        macros.set("party3自然之愈", "ALT-NUMPAD9")
        macros.set("party4自然之愈", "ALT-NUMPAD0")
        macros.set("player共生关系", "SHIFT-NUMPAD1")
        macros.set("party1共生关系", "SHIFT-NUMPAD2")
        macros.set("party2共生关系", "SHIFT-NUMPAD3")
        macros.set("party3共生关系", "SHIFT-NUMPAD4")
        macros.set("party4共生关系", "SHIFT-NUMPAD5")
        macros.set("player生命绽放", "SHIFT-NUMPAD6")
        macros.set("party1生命绽放", "SHIFT-NUMPAD7")
        macros.set("party2生命绽放", "SHIFT-NUMPAD8")
        macros.set("party3生命绽放", "SHIFT-NUMPAD9")
        macros.set("party4生命绽放", "SHIFT-NUMPAD0")
        macros.set("player野性成长", "ALT-F2")
        macros.set("party1野性成长", "ALT-F3")
        macros.set("party2野性成长", "ALT-F5")
        macros.set("party3野性成长", "ALT-F6")
        macros.set("party4野性成长", "ALT-F7")
        macros.set("player愈合", "ALT-F8")
        macros.set("party1愈合", "ALT-F9")
        macros.set("party2愈合", "ALT-F10")
        macros.set("party3愈合", "ALT-F11")
        macros.set("party4愈合", "ALT-F12")
        macros.set("player回春术", "SHIFT-F2")
        macros.set("party1回春术", "SHIFT-F3")
        macros.set("party2回春术", "SHIFT-F5")
        macros.set("party3回春术", "SHIFT-F6")
        macros.set("party4回春术", "SHIFT-F7")
        macros.set("player树皮术", "SHIFT-F8")
        macros.set("any万灵之召", "SHIFT-F9")
        macros.set("any宁静", "SHIFT-F10")
        macros.set("any自然迅捷", "SHIFT-F11")
        macros.set("any迅捷治愈", "SHIFT-F12")

    def calculate_party_health_score(self, ctx: RotationContext) -> list[AttrDict]:
        spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
        party_members: list[AttrDict] = []

        for member in ctx.state.party_members(include_player=True):
            if (not member.exists) or (not member.in_range) or (not member.is_alive):
                continue

            role = member.role
            hp_pct = member.hp_pct
            damage_absorbs = member.damage_absorbs
            heal_absorbs = member.heal_absorbs
            unit_class = member.unit_class
            rejuv_remaining = member.buff_remaining("回春术")
            rejuv_copy_remaining = member.buff_remaining("萌芽")
            regrowth_remaining = member.buff_remaining("愈合")
            wildgrowth_remaining = member.buff_remaining("野性成长")
            lifebloom_remaining = member.buff_remaining("生命绽放")
            rejuv_count = 0
            if rejuv_remaining > spell_queue_window:
                rejuv_count += 1
            if rejuv_copy_remaining > spell_queue_window:
                rejuv_count += 1

            # 血量基线: 当前血量 - 治疗吸收
            health_base = hp_pct - heal_absorbs

            # 缺口 = 就是加满血所需要的治疗。
            health_deficit = 100 - health_base

            # 坦克允许配置“缺口忽略值”，避免轻微掉血就抢占治疗优先级。
            if role == "TANK":
                health_deficit = max(
                    health_deficit - float(ctx.cfg("tank_deficit_ignore_pct") or 0.0),
                    0.0,
                )

            # 即健康分数 = 血量基线 + 伤害吸收
            health_score = health_base + damage_absorbs

            # 角色修正：可通过系数调高坦克优先级、调低治疗职业优先级。
            if role == "TANK":
                health_score *= float(ctx.cfg("tank_health_score_mul") or 1.0)
            elif role == "HEALER":
                health_score *= float(ctx.cfg("healer_health_score_mul") or 1.0)

            dispel_list = [debuff.title for debuff in member.debuff_sequence if (debuff.type in DISPEL_TYPES)]

            debuff_list = [debuff.title for debuff in member.debuff_sequence]

            unit_dict = AttrDict(
                {
                    "unitToken": member.unitToken,                      # 单位 token
                    "role": role,                                       # 角色
                    "hp_pct": hp_pct,                                   # 血量百分比
                    "damage_absorbs": damage_absorbs,                   # 伤害吸收
                    "heal_absorbs": heal_absorbs,                       # 治疗吸收
                    "unit_class": unit_class,                           # 职业
                    "rejuv_remaining": rejuv_remaining,                 # 回春术剩余时间
                    "rejuv_copy_remaining": rejuv_copy_remaining,       # 萌芽剩余时间
                    "regrowth_remaining": regrowth_remaining,           # 愈合剩余时间
                    "wildgrowth_remaining": wildgrowth_remaining,       # 野性成长剩余时间
                    "lifebloom_remaining": lifebloom_remaining,         # 生命绽放剩余时间
                    "health_score": health_score,                       # 健康分数（职责有加成）
                    "health_base": health_base,                             # 治疗基线（血量百分比 - 治疗吸收）
                    "health_deficit": health_deficit,                       # 治疗缺口（坦克有忽略）
                    "dispel_list": dispel_list,                         # 可驱散 debuff 列表
                    "debuff_list": debuff_list,                         # 所有 debuff 列表
                    "rejuv_count": rejuv_count,                         # 回春术/萌芽数量
                    "ctx": member                                       # 上下文对象
                }
            )

            party_members.append(unit_dict)

        party_members.sort(key=lambda x: x.health_score, reverse=False)
        return party_members

    def main_rotation(self, ctx: RotationContext):
        # 获取配置
        data = ctx.raw_data
        spell_queue_window = float(ctx.cfg("spell_queue_window") or 0.2)
        gcd_ready = data.player.spell.公共冷却时间.remaining <= spell_queue_window
        player = ctx.player
        target = ctx.target

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

        party_members = self.calculate_party_health_score(ctx)  # 队伍计算
        # 区别于ctx.player ，player_member 是经过计算的
        player_member = [member for member in party_members if member.unitToken == "player"][0]
        # 队伍平均治疗基线
        party_avg_health_base = sum(member.health_base for member in party_members) / len(party_members)
        # 最低血量的队员
        lowest_health_base = min(party_members, key=lambda member: member.health_base)
        # 丰饶，回复德鲁伊核心机制
        abundance_stack = player.buff_stack("丰饶")
        # 猫形态
        in_cat_form = player.has_buff("猎豹形态")
        del in_cat_form  # 未完成猫形态逻辑前以此规避type hint检查。

        player_in_movement = player.status.unit_in_movement
        player_is_stand = not player_in_movement
        # ========================================
        #  猫形态逻辑（伪代码） 暂未实现，注释保留
        # ========================================
        # if is_in_cat_form():
        #     # 团队血量 < 93% 或 丰饶层数 <= 5 -> 变回人形态
        #     grove_stacks = get_buff_stacks(BUFF.GroveGuardians, "player")
        #     if (avg_hp < 93 and lowest_hp <= 95) or grove_stacks <= 5:
        #         if spell_ready(SPELL.ShapeShift):
        #             return cast_spell(SPELL.ShapeShift)
        #
        #     combo_points = get_combo_points()
        #
        #     # 1. 割裂：连击点 >= 4
        #     if combo_points >= 4 and spell_ready(SPELL.Rip):
        #         # 优先找 5 码内没有割裂 debuff 的敌人
        #         no_rip_target = get_enemy_without_debuff(DEBUFF.Rip, 5, require_los=True)
        #         if no_rip_target:
        #             return cast_instant(SPELL.Rip, no_rip_target)
        #         # 都有 debuff，则对当前目标
        #         if unit_exists("target") and not unit_is_dead("target") and unit_can_attack("player", "target"):
        #             return cast_instant(SPELL.Rip, "target")
        #
        #     # 2. 斜掠：优先找 5 码内没有斜掠 debuff 的敌人
        #     if spell_ready(SPELL.Rake):
        #         no_rake_target = get_enemy_without_debuff(DEBUFF.Rake, 5, require_los=True)
        #         if no_rake_target:
        #             return cast_instant(SPELL.Rake, no_rake_target)
        #         # 都有 debuff，则对当前目标
        #         if unit_exists("target") and not unit_is_dead("target") and unit_can_attack("player", "target"):
        #             return cast_instant(SPELL.Rake, "target")
        #
        #     return None

        # ========================================
        #  人形态治疗逻辑（伪代码）
        # ========================================

        # 还有猫形态 buff 说明正在变形中，等待
        # if has_buff(BUFF.CatForm, "player"):
        #     return None

        # # 团队血量 >= 95% -> 变猫输出

        # if party_avg_health_base >= 95:
        #     return

        # 0. 复生：有队友死亡时战斗复活（检查射程） （保留注释，手动操作）

        # 0.1 铁木树皮：最低血量 < `铁木树皮血量阈值(默认50)`
        if (ctx.spell_usable("铁木树皮") and ctx.spell_cooldown_ready("铁木树皮", spell_queue_window)):
            if lowest_health_base:
                if (lowest_health_base.health_base < float(ctx.cfg("ironbark_hp_threshold") or 50)):
                    return ctx.cast(lowest_health_base.unitToken, "铁木树皮")

        # 0.1 树皮术：自己血量 < `树皮术血量阈值(默认50)`
        if (ctx.spell_usable("树皮术") and ctx.spell_cooldown_ready("树皮术", spell_queue_window)):
            if (player_member.health_base < float(ctx.cfg("barkskin_hp_threshold") or 50)):
                return ctx.cast("player", "树皮术")

        # 0.2 驱散：友方有可驱散 debuff（诅咒/毒/魔法）
        party_members.sort(key=lambda x: len(x.dispel_list), reverse=True)
        need_dispel_member = [member for member in party_members if (len(member.dispel_list) > 0)]
        if need_dispel_member:
            if (ctx.spell_usable("自然之愈") and (ctx.spell_charges("自然之愈") > 0) and gcd_ready):
                return ctx.cast(need_dispel_member[0].unitToken, "自然之愈")

        tank_members = [member for member in party_members if member.role == "TANK"]
        if tank_members:
            tank_member = tank_members[0]
        else:
            tank_member = None

        # 1. [共生关系] 坦克没有共生关系 buff 时释放
        if (ctx.spell_usable("共生关系") and ctx.spell_cooldown_ready("共生关系", spell_queue_window) and player_is_stand):
            if tank_member:
                if (not tank_member.ctx.has_buff("共生关系")):
                    return ctx.cast(tank_member.unitToken, "共生关系")

        # 2. [生命绽放] 对坦克
        if (ctx.spell_usable("生命绽放") and ctx.spell_cooldown_ready("生命绽放", spell_queue_window)):
            if tank_member:
                if (not tank_member.ctx.has_buff("生命绽放")):
                    return ctx.cast(tank_member.unitToken, "生命绽放")

        # 3. [万灵之召]  队伍血量 <= `万灵队血阈值(默认65)` 或最低血量 <= `万灵单体阈值(默认20)`
        if (ctx.spell_usable("万灵之召") and ctx.spell_cooldown_ready("万灵之召", spell_queue_window)):
            if (party_avg_health_base <= float(ctx.cfg("convoke_party_hp_threshold") or 65)):
                return ctx.cast("any", "万灵之召")
            if lowest_health_base:
                if (lowest_health_base.health_base <= float(ctx.cfg("convoke_single_hp_threshold") or 20)):
                    return ctx.cast("any", "万灵之召")

        # 4. [野性成长] 有至少'野性成长人数阈值(默认2)'个的血量 < `野性成长血量阈值(95)`
        need_growth_member = [member for member in party_members if (member.health_base < float(ctx.cfg("wild_growth_hp_threshold") or 95))]
        if (ctx.spell_usable("野性成长") and ctx.spell_cooldown_ready("野性成长", spell_queue_window) and player_is_stand):
            if (len(need_growth_member) >= int(float(ctx.cfg("wild_growth_count_threshold") or 2))):
                return ctx.cast(lowest_health_base.unitToken, "野性成长")

        # 5.[宁静] 队伍血量 <= `宁静队血阈值(默认50)`
        if (ctx.spell_usable("宁静") and ctx.spell_cooldown_ready("宁静", spell_queue_window) and player_is_stand):
            if (party_avg_health_base <= float(ctx.cfg("tranquility_party_hp_threshold") or 50)):
                return ctx.cast("any", "宁静")

        # 6. [自然迅捷] 最低血量 < `自然迅捷阈值(默认60)`
        if (ctx.spell_usable("自然迅捷") and ctx.spell_cooldown_ready("自然迅捷", spell_queue_window)):
            if lowest_health_base:
                if (lowest_health_base.health_base < float(ctx.cfg("nature_swiftness_hp_threshold") or 60)):
                    return ctx.cast("any", "自然迅捷")

        # 7. [迅捷治愈] 有至少'迅捷治愈人数阈值(默认3)'个的血量 < `迅捷治愈血量阈值(65)` ，且丰饶 >= 1
        need_swiftmend_member = [member for member in party_members if (member.health_base < float(ctx.cfg("swiftmend_hp_threshold") or 65))]
        if (ctx.spell_usable("迅捷治愈") and (ctx.spell_charges("迅捷治愈") > 0) and gcd_ready):
            if (len(need_swiftmend_member) >= int(float(ctx.cfg("swiftmend_count_threshold") or 3))):
                if (abundance_stack >= 1):
                    return ctx.cast("any", "迅捷治愈")

        # 8. [愈合] 最低血量 < '愈合阈值(默认70)'
        if (ctx.spell_usable("愈合") and ctx.spell_cooldown_ready("愈合", spell_queue_window) and player_is_stand):
            if lowest_health_base:
                if (lowest_health_base.health_base < float(ctx.cfg("regrowth_hp_threshold") or 70)):
                    return ctx.cast(lowest_health_base.unitToken, "愈合")

        rejuvenation_hp_threshold = float(ctx.cfg("rejuvenation_hp_threshold") or 100)

        # 9. [回春术] 对health_base < "回春阈值(默认100)" 且回春数量小于2的人
        need_rejuv_member = [member for member in party_members if (member.rejuv_count < 2) and (member.health_base < rejuvenation_hp_threshold)]
        if (ctx.spell_usable("回春术") and ctx.spell_cooldown_ready("回春术", spell_queue_window)):
            if need_rejuv_member:
                return ctx.cast(need_rejuv_member[0].unitToken, "回春术")

        # 10. [回春术]
        # 给没回春的人至少一个回春
        party_members.sort(key=lambda x: x.health_base, reverse=False)
        need_rejuv_member = [member for member in party_members if (member.rejuv_count < 1)]
        if (ctx.spell_usable("回春术") and ctx.spell_cooldown_ready("回春术", spell_queue_window)):
            if need_rejuv_member:
                return ctx.cast(need_rejuv_member[0].unitToken, "回春术")

        # 当丰饶数量小于`丰饶阈值(默认5)`时，给最低分数的单回春玩家补回春。丰饶数量不会超过队伍人数x2
        party_members.sort(key=lambda x: x.health_score, reverse=False)
        need_rejuv_member = [member for member in party_members if (member.rejuv_count == 1)]
        abundance_limit = min(int(float(ctx.cfg("abundance_stack_threshold") or 5)), len(party_members) * 2)
        if (abundance_stack < abundance_limit):
            if need_rejuv_member:
                return ctx.cast(need_rejuv_member[0].unitToken, "回春术")

        return ctx.idle("无所事事")


if __name__ == "__main__":
    raise SystemExit(run_profile(DruidRestoration()))
