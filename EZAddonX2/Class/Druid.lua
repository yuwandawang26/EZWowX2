local addonName, addonTable             = ...

local className, classFilename, classId = UnitClass("player")
local currentSpec                       = GetSpecialization()

if classFilename ~= "DRUID" then return end

if currentSpec == 3 then
    table.insert(addonTable.macroList, { title = "target月火术", key = "ALT-NUMPAD1", text = "/cast [@target] 月火术" })
    table.insert(addonTable.macroList, { title = "focus月火术", key = "ALT-NUMPAD2", text = "/cast [@focus] 月火术" })
    table.insert(addonTable.macroList, { title = "target裂伤", key = "ALT-NUMPAD3", text = "/cast [@target] 裂伤" })
    table.insert(addonTable.macroList, { title = "focus裂伤", key = "ALT-NUMPAD4", text = "/cast [@focus] 裂伤" })
    table.insert(addonTable.macroList, { title = "target毁灭", key = "ALT-NUMPAD5", text = "/cast [@target] 毁灭" })
    table.insert(addonTable.macroList, { title = "focus毁灭", key = "ALT-NUMPAD6", text = "/cast [@focus] 毁灭" })
    table.insert(addonTable.macroList, { title = "target摧折", key = "ALT-NUMPAD7", text = "/cast [@target] 摧折" })
    table.insert(addonTable.macroList, { title = "focus摧折", key = "ALT-NUMPAD8", text = "/cast [@focus] 摧折" })
    table.insert(addonTable.macroList, { title = "target重殴", key = "ALT-NUMPAD9", text = "/cast [@target] 重殴" })
    table.insert(addonTable.macroList, { title = "focus重殴", key = "ALT-NUMPAD0", text = "/cast [@focus] 重殴" })
    table.insert(addonTable.macroList, { title = "target赤红之月", key = "SHIFT-NUMPAD1", text = "/cast [@target] 赤红之月" })
    table.insert(addonTable.macroList, { title = "focus赤红之月", key = "SHIFT-NUMPAD2", text = "/cast [@focus] 赤红之月" })
    table.insert(addonTable.macroList, { title = "target明月普照", key = "SHIFT-NUMPAD3", text = "/cast [@target] 明月普照" })
    table.insert(addonTable.macroList, { title = "focus明月普照", key = "SHIFT-NUMPAD4", text = "/cast [@focus] 明月普照" })
    table.insert(addonTable.macroList, { title = "enemy痛击", key = "SHIFT-NUMPAD5", text = "/cast 痛击" })
    table.insert(addonTable.macroList, { title = "enemy横扫", key = "SHIFT-NUMPAD6", text = "/cast 横扫" })
    table.insert(addonTable.macroList, { title = "any切换目标", key = "SHIFT-NUMPAD7", text = "/targetenemy\n/focus\n/targetlasttarget" })
    table.insert(addonTable.macroList, { title = "player狂暴", key = "SHIFT-NUMPAD8", text = "/cast 狂暴" })
    table.insert(addonTable.macroList, { title = "player化身：乌索克的守护者", key = "SHIFT-NUMPAD9", text = "/cast 狂暴" })
    table.insert(addonTable.macroList, { title = "player铁鬃", key = "SHIFT-NUMPAD0", text = "/cast 铁鬃" })
    table.insert(addonTable.macroList, { title = "player狂暴回复", key = "ALT-F2", text = "/cast 狂暴回复" })
    table.insert(addonTable.macroList, { title = "player树皮术", key = "ALT-F3", text = "/cast 树皮术" })
    table.insert(addonTable.macroList, { title = "player生存本能", key = "ALT-F5", text = "/cast 生存本能" })
    table.insert(addonTable.macroList, { title = "target迎头痛击", key = "ALT-F6", text = "/cast [@target] 迎头痛击" })
    table.insert(addonTable.macroList, { title = "focus迎头痛击", key = "ALT-F7", text = "/cast [@focus] 迎头痛击" })
    table.insert(addonTable.macroList, { title = "any熊形态", key = "ALT-F8", text = "/cast [noform:1] 熊形态" })
    table.insert(addonTable.macroList, { title = "nearest裂伤", key = "ALT-F9", text = "/cleartarget \n/targetenemy [noharm][dead][noexists][help] \n/cast [nocombat] 裂伤 \n/stopmacro [channeling] \n/startattack \n/cast [harm]裂伤 \n/targetlasttarget" })
    table.insert(addonTable.macroList, { title = "nearest毁灭", key = "ALT-F10", text = "/cleartarget \n/targetenemy [noharm][dead][noexists][help] \n/cast [nocombat] 毁灭 \n/stopmacro [channeling] \n/startattack \n/cast [harm]毁灭 \n/targetlasttarget" })
    SetCVar("targetNearestDistance", 5);
    DISABLE_EZOK = true
end
if currentSpec == 4 then
    table.insert(addonTable.macroList, { title = "player铁木树皮", key = "ALT-NUMPAD1", text = "/cast [@player] 铁木树皮" })
    table.insert(addonTable.macroList, { title = "party1铁木树皮", key = "ALT-NUMPAD2", text = "/cast [@party1] 铁木树皮" })
    table.insert(addonTable.macroList, { title = "party2铁木树皮", key = "ALT-NUMPAD3", text = "/cast [@party2] 铁木树皮" })
    table.insert(addonTable.macroList, { title = "party3铁木树皮", key = "ALT-NUMPAD4", text = "/cast [@party3] 铁木树皮" })
    table.insert(addonTable.macroList, { title = "party4铁木树皮", key = "ALT-NUMPAD5", text = "/cast [@party4] 铁木树皮" })
    table.insert(addonTable.macroList, { title = "player自然之愈", key = "ALT-NUMPAD6", text = "/cast [@player] 自然之愈" })
    table.insert(addonTable.macroList, { title = "party1自然之愈", key = "ALT-NUMPAD7", text = "/cast [@party1] 自然之愈" })
    table.insert(addonTable.macroList, { title = "party2自然之愈", key = "ALT-NUMPAD8", text = "/cast [@party2] 自然之愈" })
    table.insert(addonTable.macroList, { title = "party3自然之愈", key = "ALT-NUMPAD9", text = "/cast [@party3] 自然之愈" })
    table.insert(addonTable.macroList, { title = "party4自然之愈", key = "ALT-NUMPAD0", text = "/cast [@party4] 自然之愈" })
    table.insert(addonTable.macroList, { title = "player共生关系", key = "SHIFT-NUMPAD1", text = "/cast [@player] 共生关系" })
    table.insert(addonTable.macroList, { title = "party1共生关系", key = "SHIFT-NUMPAD2", text = "/cast [@party1] 共生关系" })
    table.insert(addonTable.macroList, { title = "party2共生关系", key = "SHIFT-NUMPAD3", text = "/cast [@party2] 共生关系" })
    table.insert(addonTable.macroList, { title = "party3共生关系", key = "SHIFT-NUMPAD4", text = "/cast [@party3] 共生关系" })
    table.insert(addonTable.macroList, { title = "party4共生关系", key = "SHIFT-NUMPAD5", text = "/cast [@party4] 共生关系" })
    table.insert(addonTable.macroList, { title = "player生命绽放", key = "SHIFT-NUMPAD6", text = "/cast [@player] 生命绽放" })
    table.insert(addonTable.macroList, { title = "party1生命绽放", key = "SHIFT-NUMPAD7", text = "/cast [@party1] 生命绽放" })
    table.insert(addonTable.macroList, { title = "party2生命绽放", key = "SHIFT-NUMPAD8", text = "/cast [@party2] 生命绽放" })
    table.insert(addonTable.macroList, { title = "party3生命绽放", key = "SHIFT-NUMPAD9", text = "/cast [@party3] 生命绽放" })
    table.insert(addonTable.macroList, { title = "party4生命绽放", key = "SHIFT-NUMPAD0", text = "/cast [@party4] 生命绽放" })
    table.insert(addonTable.macroList, { title = "player野性成长", key = "ALT-F2", text = "/cast [@player] 野性成长" })
    table.insert(addonTable.macroList, { title = "party1野性成长", key = "ALT-F3", text = "/cast [@party1] 野性成长" })
    table.insert(addonTable.macroList, { title = "party2野性成长", key = "ALT-F5", text = "/cast [@party2] 野性成长" })
    table.insert(addonTable.macroList, { title = "party3野性成长", key = "ALT-F6", text = "/cast [@party3] 野性成长" })
    table.insert(addonTable.macroList, { title = "party4野性成长", key = "ALT-F7", text = "/cast [@party4] 野性成长" })
    table.insert(addonTable.macroList, { title = "player愈合", key = "ALT-F8", text = "/cast [@player] 愈合" })
    table.insert(addonTable.macroList, { title = "party1愈合", key = "ALT-F9", text = "/cast [@party1] 愈合" })
    table.insert(addonTable.macroList, { title = "party2愈合", key = "ALT-F10", text = "/cast [@party2] 愈合" })
    table.insert(addonTable.macroList, { title = "party3愈合", key = "ALT-F11", text = "/cast [@party3] 愈合" })
    table.insert(addonTable.macroList, { title = "party4愈合", key = "ALT-F12", text = "/cast [@party4] 愈合" })
    table.insert(addonTable.macroList, { title = "player回春术", key = "SHIFT-F2", text = "/cast [@player] 回春术" })
    table.insert(addonTable.macroList, { title = "party1回春术", key = "SHIFT-F3", text = "/cast [@party1] 回春术" })
    table.insert(addonTable.macroList, { title = "party2回春术", key = "SHIFT-F5", text = "/cast [@party2] 回春术" })
    table.insert(addonTable.macroList, { title = "party3回春术", key = "SHIFT-F6", text = "/cast [@party3] 回春术" })
    table.insert(addonTable.macroList, { title = "party4回春术", key = "SHIFT-F7", text = "/cast [@party4] 回春术" })
    table.insert(addonTable.macroList, { title = "player树皮术", key = "SHIFT-F8", text = "/cast [@player] 树皮术" })
    table.insert(addonTable.macroList, { title = "any万灵之召", key = "SHIFT-F9", text = "/cast [nochanneling] 万灵之召" })
    table.insert(addonTable.macroList, { title = "any宁静", key = "SHIFT-F10", text = "/cast [nochanneling] 宁静" })
    table.insert(addonTable.macroList, { title = "any自然迅捷", key = "SHIFT-F11", text = "/cast [nochanneling] 自然迅捷" })
    table.insert(addonTable.macroList, { title = "any迅捷治愈", key = "SHIFT-F12", text = "/cast [nochanneling] 迅捷治愈" })
    DISABLE_EZOK = true
end

local CreatePixelNode = addonTable.CreatePixelNode

local function InitializeDruidSpecFrame()
    local x = 0
    local y = 0
    local combo_points = CreatePixelNode(x, y, "DruidComboPoints", addonTable.SpecFrame)


    local function UpdateSpec_freq_std()
        local power = UnitPower("player", Enum.PowerType.ComboPoints)
        combo_points:SetColorTexture(power * 51 / 255, power * 51 / 255, power * 51 / 255, 1)
    end
    table.insert(addonTable.OnUpdateFuncs_STD, UpdateSpec_freq_std)
end

table.insert(addonTable.FrameInitFuncs, InitializeDruidSpecFrame)
