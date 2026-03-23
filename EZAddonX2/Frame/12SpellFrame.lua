local addonName, addonTable         = ...

local DEBUG                         = addonTable.DEBUG
local logging                       = addonTable.logging
local COLOR                         = addonTable.COLOR
local remaining_curve               = addonTable.remaining_curve
local CreateFootnoteNode            = addonTable.CreateFootnoteNode
local CreateMixedNode               = addonTable.CreateMixedNode
local CreateStringNode              = addonTable.CreateStringNode

local min                           = math.min
local tostring                      = tostring
local GetSpellTexture               = C_Spell.GetSpellTexture
local GetSpellCharges               = C_Spell.GetSpellCharges
local GetSpellChargeDuration        = C_Spell.GetSpellChargeDuration
local GetSpellCooldownDuration      = C_Spell.GetSpellCooldownDuration
local GetSpellLink                  = C_Spell.GetSpellLink
local IsSpellUsable                 = C_Spell.IsSpellUsable
local IsSpellInSpellBook            = C_SpellBook.IsSpellInSpellBook
local EvaluateColorFromBoolean      = C_CurveUtil.EvaluateColorFromBoolean
local GetCooldownViewerCategorySet  = C_CooldownViewer.GetCooldownViewerCategorySet
local GetCooldownViewerCooldownInfo = C_CooldownViewer.GetCooldownViewerCooldownInfo
local IsSpellOverlayed              = C_SpellActivationOverlay.IsSpellOverlayed

-- 初始化技能框架
local function InitializeSpellFrame()
    if DEBUG then logging("InitializeSpellFrame") end
    table.insert(addonTable.Spell, { spellID = 61304, type = "cooldown" })

    local cooldownIDs = GetCooldownViewerCategorySet(Enum.CooldownViewerCategory.Essential, true)
    tAppendAll(cooldownIDs, GetCooldownViewerCategorySet(Enum.CooldownViewerCategory.Utility, true))

    for _, cooldownID in ipairs(cooldownIDs) do
        local cooldownInfo = GetCooldownViewerCooldownInfo(cooldownID)
        if cooldownInfo and cooldownInfo.isKnown then
            table.insert(addonTable.Spell, {
                spellID = cooldownInfo.overrideSpellID,
                type = cooldownInfo.charges and "charge" or "cooldown"
            })
        end
    end


    local MaxFrame = min(36, #addonTable.Spell)
    local spellTextrues = {}

    for i = 1, #addonTable.Spell do
        local SpellID = addonTable.Spell[i].spellID
        local spellLink = GetSpellLink(SpellID)
        logging("技能冷却[" .. i .. "]" .. spellLink .. ",类型:" .. addonTable.Spell[i].type)
    end


    -- 创建技能框架元素
    for i = 1, 36 do
        local iconTexture, fnTexture = CreateFootnoteNode(i - 1, 0, "SpellIconFrame" .. i, addonTable.PlayerSpellFrame)
        local cooldownTexture, usableTexture, highlightTexture, knownTexture = CreateMixedNode(i - 1, 1, "SpellMiscFrame" .. i, addonTable.PlayerSpellFrame)

        local charge_string = CreateStringNode(i - 1, 2, "SpellChargeFrame" .. i, addonTable.PlayerSpellFrame)

        table.insert(spellTextrues, {
            fn = fnTexture,
            icon = iconTexture,
            cooldown = cooldownTexture,
            usable = usableTexture,
            highlight = highlightTexture,
            charge = charge_string,
            known = knownTexture
        })
    end


    -- 更新节点纹理函数
    local function UpdateStatus_event_SPELLS_CHANGED()
        for i = 1, MaxFrame do
            local SpellID = addonTable.Spell[i].spellID
            local spellTex = spellTextrues[i]
            local iconID = GetSpellTexture(SpellID)
            if iconID then
                spellTex.icon:SetTexture(iconID)
                spellTex.fn:SetColorTexture(COLOR.ICONS.PLAYER_SPELL:GetRGBA())
            else
                spellTex.icon:SetColorTexture(0, 0, 0, 1)
                spellTex.fn:SetColorTexture(0, 0, 0, 0)
            end
        end
    end

    local function UpdateStatus_freq_std()
        for i = 1, MaxFrame do
            local SpellID = addonTable.Spell[i].spellID
            local spellTex = spellTextrues[i]


            -- spellTex.cooldown:SetColorTexture(cd_remaining:GetRGBA())
            if addonTable.Spell[i].type == "charge" then
                local duration = GetSpellChargeDuration(SpellID)
                local result = duration:EvaluateRemainingDuration(remaining_curve)
                spellTex.cooldown:SetColorTexture(result:GetRGBA())

                local chargeInfo = GetSpellCharges(SpellID)
                spellTex.charge:SetText(tostring(chargeInfo.currentCharges))
            else
                local duration = GetSpellCooldownDuration(SpellID)
                local result = duration:EvaluateRemainingDuration(remaining_curve)
                spellTex.cooldown:SetColorTexture(result:GetRGBA())
            end

            local isSpellOverlayed = IsSpellOverlayed(SpellID)
            -- print(isSpellOverlayed)
            local highlightValue = EvaluateColorFromBoolean(isSpellOverlayed, COLOR.WHITE, COLOR.BLACK) -- 高亮是
            spellTex.highlight:SetColorTexture(highlightValue:GetRGBA())

            local isUsable, insufficientPower = IsSpellUsable(SpellID)
            local usableValue = EvaluateColorFromBoolean(isUsable, COLOR.WHITE, COLOR.BLACK) -- 无法使用时是黑色，可用是白色。
            spellTex.usable:SetColorTexture(usableValue:GetRGBA())
        end
    end

    local function UpdateStatusStandard_freq_low()
        for i = 1, MaxFrame do
            local SpellID = addonTable.Spell[i].spellID
            local spellTex = spellTextrues[i]
            local isKnown = IsSpellInSpellBook(SpellID)
            local knownValue = EvaluateColorFromBoolean(isKnown, COLOR.WHITE, COLOR.BLACK) -- 不知道时是黑色，会这个技能是白色
            spellTex.known:SetColorTexture(knownValue:GetRGBA())
        end
    end
    UpdateStatus_event_SPELLS_CHANGED()
    table.insert(addonTable.OnEventFunc_Spell, UpdateStatus_event_SPELLS_CHANGED)
    UpdateStatusStandard_freq_low()
    table.insert(addonTable.OnUpdateFuncs_LOW, UpdateStatusStandard_freq_low)
    table.insert(addonTable.OnUpdateFuncs_STD, UpdateStatus_freq_std)
    if DEBUG then logging("InitializeSpellFrame...Done") end
end

-- 将初始化技能框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializeSpellFrame)
