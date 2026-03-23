local addonName, addonTable = ...

local GetSpellTexture       = C_Spell.GetSpellTexture

local CreateFootnoteNode    = addonTable.CreateFootnoteNode

local InterruptList         = {

    ------12.0 S1大秘必断------
    ----魔导师平台----
    [468966] = "变形术",
    [1254301] = "炎爆术",
    [1264693] = "恐惧浪潮",
    ----执政----
    [248831] = "恐惧尖啸",
    [244750] = "心灵震爆",
    [1262526] = "深渊强化",
    [1277340] = "暗影愈合",
    [1262523] = "召唤虚空",
    ----学院----
    [388392] = "乏味的讲课",
    [388862] = "涌动",
    [1279627] = "奥术箭",
    ----节点----
    [1257601] = "神圣诡计",
    [1258681] = "失效",
    [1282722] = "失效",
    [1285445] = "魔爆术",
    ----萨隆----
    [1262941] = "瘟疫箭",
    [1271479] = "虚空爆发",
    [1271074] = "寒冰冲击",
    [1278893] = "湮灭之箭",
    [1264186] = "暗影束缚",
    [1258997] = "猛拽擒握",
    ----洞窟----
    [1256008] = "妖术",
    [1257716] = "复活",
    [1263292] = "缩小",
    [1254010] = "永恒的痛苦",
    [1266381] = "抓钩诱捕",
    [1259182] = "穿刺尖叫",
    [1250708] = "死疽融合",
    [1264327] = "暗影冰霜冲击",
    ----通天----
    [1255377] = "驱逐",
    [152953] = "盲目之光",
    [154396] = "日光冲击",
    [411958] = "砂石箭",
    [415437] = "弱化",
    ----风行----
    [472724] = "暗影箭",
    [1216592] = "闪电链",
    [473794] = "淬毒利刃",
    [473663] = "脉冲尖啸",

}


local function InitializeIconList1Frame()
    local cooldownIDs = {}
    local i = 1
    for spellID, _ in pairs(InterruptList) do
        local iconID, originalIconID = GetSpellTexture(spellID)
        local iconTexture, fnTexture = CreateFootnoteNode(i - 1, 0, "IconList1" .. i, addonTable.IconListFrame1)
        iconTexture:SetTexture(iconID)
        fnTexture:SetColorTexture(addonTable.COLOR.ICONS.ENEMY_SPELL_INTERRUPTIBLE:GetRGBA())
        i = i + 1
    end
end
table.insert(addonTable.FrameInitFuncs, InitializeIconList1Frame)
