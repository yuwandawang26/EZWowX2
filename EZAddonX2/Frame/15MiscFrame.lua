local addonName, addonTable   = ...

local DEBUG                   = addonTable.DEBUG
local logging                 = addonTable.logging
local COLOR                   = addonTable.COLOR
local LibRangeCheck           = addonTable.LibRangeCheck
local CreatePixelNode         = addonTable.CreatePixelNode
local CreateFootnoteNode      = addonTable.CreateFootnoteNode

local UnitExists              = UnitExists
local UnitCanAttack           = UnitCanAttack
local UnitIsDeadOrGhost       = UnitIsDeadOrGhost
local GetSpellTexture         = C_Spell.GetSpellTexture
local GetNextCastSpell        = C_AssistedCombat.GetNextCastSpell
local GetCurrentKeyBoardFocus = GetCurrentKeyBoardFocus
local SpellIsTargeting        = SpellIsTargeting
local GetTime                 = GetTime

-- 初始化杂项框架
local function InitializeMiscFrame()
    if DEBUG then logging("InitializeMiscFrame") end
    local y = 0
    local x = 0
    local assisted_combat, assisted_combat_fn = CreateFootnoteNode(x, y, "AssistedCombat", addonTable.MiscFrame)
    x = 1
    local on_chat = CreatePixelNode(x, y, "OnChat", addonTable.MiscFrame)
    x = 2
    local is_targeting = CreatePixelNode(x, y, "IsTargeting", addonTable.MiscFrame)
    x = 3
    local flash_node = CreatePixelNode(x, y, "FlashNode", addonTable.MiscFrame)
    y = 1
    x = 0
    -- 范围内敌人数量
    local enemy_count_pix = CreatePixelNode(x, y, "EnemyCount", addonTable.MiscFrame) -- 范围内敌人数量
    x = 1
    local delay_pix = CreatePixelNode(x, y, "Delay", addonTable.MiscFrame)            -- 延迟
    local delay_timestamp = GetTime()
    local delay_lastst_statis = false

    local flash_value = true

    SLASH_DELAY1 = "/delay"
    SlashCmdList["DELAY"] = function(msg)
        delay_timestamp = GetTime() + tonumber(msg)
    end

    -- 更新杂项状态函数
    local function UpdateStatus_freq_std()
        local spellID = GetNextCastSpell(false)
        if spellID then
            local iconID, originalIconID = GetSpellTexture(spellID)
            assisted_combat:SetTexture(originalIconID)
            assisted_combat_fn:SetColorTexture(COLOR.ICONS.PLAYER_SPELL:GetRGBA())
        else
            assisted_combat:SetColorTexture(0, 0, 0, 1)
            assisted_combat_fn:SetColorTexture(0, 0, 0, 0)
        end

        local f = GetCurrentKeyBoardFocus()
        if f then
            on_chat:SetColorTexture(1, 1, 1, 1)
        else
            on_chat:SetColorTexture(0, 0, 0, 1)
        end

        if SpellIsTargeting() then
            is_targeting:SetColorTexture(1, 1, 1, 1)
        else
            is_targeting:SetColorTexture(0, 0, 0, 1)
        end

        if flash_value then
            flash_node:SetColorTexture(1, 1, 1, 1)
        else
            flash_node:SetColorTexture(0, 0, 0, 1)
        end
        flash_value = not flash_value

        local dalay_status = delay_timestamp > GetTime() -- 当时间点大于当前事件是为true
        if dalay_status ~= delay_lastst_statis then
            if dalay_status then
                delay_pix:SetColorTexture(1, 1, 1, 1)
            else
                delay_pix:SetColorTexture(0, 0, 0, 1)
            end
            delay_lastst_statis = dalay_status
        end
    end
    local function UpdateStatus_freq_low()
        local enemy_count = 0

        for i = 1, 40 do
            local current_unit_token = "nameplate" .. i -- 当前遍历单位token，范围[string]
            if (UnitExists(current_unit_token)) and (UnitCanAttack("player", current_unit_token)) and (not UnitIsDeadOrGhost(current_unit_token))
            then
                local _, maxRange = LibRangeCheck:GetRange(current_unit_token)
                if maxRange and (maxRange <= addonTable.AOERange) then
                    enemy_count = enemy_count + 1
                end
            end
        end

        enemy_count_pix:SetColorTexture(enemy_count / 51, enemy_count / 51, enemy_count / 51, 1)
    end
    table.insert(addonTable.OnUpdateFuncs_LOW, UpdateStatus_freq_low)
    table.insert(addonTable.OnUpdateFuncs_STD, UpdateStatus_freq_std)
    if DEBUG then logging("InitializeMiscFrame...Done") end
end

-- 将初始化杂项框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializeMiscFrame)
