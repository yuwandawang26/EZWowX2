local addonName, addonTable = ...

local DEBUG              = addonTable.DEBUG
local logging            = addonTable.logging
local COLOR              = addonTable.COLOR
local curve              = addonTable.curve
local LibRangeCheck      = addonTable.LibRangeCheck
local CreatePixelNode    = addonTable.CreatePixelNode
local CreateFootnoteNode = addonTable.CreateFootnoteNode

local UnitExists = UnitExists
local UnitCanAttack = UnitCanAttack
local UnitIsUnit = UnitIsUnit
local UnitIsDeadOrGhost = UnitIsDeadOrGhost
local UnitAffectingCombat = UnitAffectingCombat
local UnitCastingInfo = UnitCastingInfo
local UnitChannelInfo = UnitChannelInfo
local UnitCastingDuration = UnitCastingDuration
local UnitChannelDuration = UnitChannelDuration
local UnitHealthPercent = UnitHealthPercent
local UnitIsEnemy = UnitIsEnemy
local EvaluateColorFromBoolean = C_CurveUtil.EvaluateColorFromBoolean

-- 初始化单位状态框架
local function InitializeUnitStatusFrame(unit, parent)
    if DEBUG then logging("InitializeUnitStatusFrame[" .. unit .. "]") end
    local x = 0
    local y = 0
    local unit_exist = CreatePixelNode(x, y, unit .. "TargetExist", parent)
    x = 1
    local unit_can_attack = CreatePixelNode(x, y, unit .. "CanAttack", parent)
    x = 2
    local unit_is_self = CreatePixelNode(x, y, unit .. "IsSelf", parent)
    x = 3
    local unit_is_alive = CreatePixelNode(x, y, unit .. "IsAlive", parent)
    x = 4
    local unit_in_combat = CreatePixelNode(x, y, unit .. "InCombat", parent)
    x = 5
    local unit_in_range = CreatePixelNode(x, y, unit .. "InRange", parent)
    x = 7
    local unit_health = CreatePixelNode(x, y, unit .. "Health", parent)
    y = 1
    x = 0
    local unit_cast_icon, unit_cast_fn = CreateFootnoteNode(x, y, unit .. "CastIcon", parent)
    x = 1
    local unit_cast_duration = CreatePixelNode(x, y, unit .. "CastDuration", parent)
    x = 2
    local unit_cast_interruptible = CreatePixelNode(x, y, unit .. "CastInterruptible", parent)
    x = 3
    local unit_channel_icon, unit_channel_fn = CreateFootnoteNode(x, y, unit .. "ChannelIcon", parent)
    x = 4
    local unit_channel_duration = CreatePixelNode(x, y, unit .. "ChannelDuration", parent)
    x = 5
    local unit_channel_interruptible = CreatePixelNode(x, y, unit .. "ChannelInterruptible", parent)

    -- 更新单位状态函数
    local function UpdateStatus_freq_std()
        if UnitExists(unit) then
            unit_exist:SetColorTexture(1, 1, 1, 1)
            local can_attack = UnitCanAttack("player", unit)
            -- local can_attack = UnitCanAttack("player", unit) and UnitIsEnemy("player", unit)
            if can_attack then
                unit_can_attack:SetColorTexture(1, 1, 1, 1)
            else
                unit_can_attack:SetColorTexture(0, 0, 0, 1)
            end

            if UnitIsUnit("player", unit) then
                unit_is_self:SetColorTexture(1, 1, 1, 1)
            else
                unit_is_self:SetColorTexture(0, 0, 0, 1)
            end

            if UnitAffectingCombat(unit) then
                unit_in_combat:SetColorTexture(1, 1, 1, 1)
            else
                unit_in_combat:SetColorTexture(0, 0, 0, 1)
            end

            if UnitIsDeadOrGhost(unit) then
                unit_is_alive:SetColorTexture(0, 0, 0, 1)
            else
                unit_is_alive:SetColorTexture(1, 1, 1, 1)
            end

            local _, _, CastTextureID, _, _, _, _, CastNotInterruptible, _, _ = UnitCastingInfo(unit)
            if CastTextureID then
                unit_cast_icon:SetTexture(CastTextureID)
                unit_cast_interruptible:SetColorTexture(EvaluateColorFromBoolean(CastNotInterruptible, COLOR.BLACK, COLOR.WHITE):GetRGBA())
                local duration = UnitCastingDuration(unit)
                local result = duration:EvaluateElapsedPercent(curve)
                unit_cast_duration:SetColorTexture(result:GetRGBA())
                if can_attack then
                    unit_cast_fn:SetColorTexture(EvaluateColorFromBoolean(CastNotInterruptible, COLOR.ICONS.ENEMY_SPELL_NOT_INTERRUPTIBLE, COLOR.ICONS.ENEMY_SPELL_INTERRUPTIBLE):GetRGBA())
                else
                    unit_cast_fn:SetColorTexture(COLOR.ICONS.PLAYER_SPELL:GetRGBA())
                end
            else
                unit_cast_icon:SetColorTexture(0, 0, 0, 1)
                unit_cast_duration:SetColorTexture(0, 0, 0, 1)
                unit_cast_interruptible:SetColorTexture(0, 0, 0, 1)
                unit_cast_fn:SetColorTexture(0, 0, 0, 0)
            end
            local _, _, textureID, _, _, _, ChannelNotInterruptible = UnitChannelInfo(unit)
            if textureID then
                unit_channel_icon:SetTexture(textureID)
                unit_channel_interruptible:SetColorTexture(EvaluateColorFromBoolean(ChannelNotInterruptible, COLOR.BLACK, COLOR.WHITE):GetRGBA())
                local duration = UnitChannelDuration(unit)
                local result = duration:EvaluateElapsedPercent(curve)
                unit_channel_duration:SetColorTexture(result:GetRGBA())
                if can_attack then
                    unit_channel_fn:SetColorTexture(EvaluateColorFromBoolean(ChannelNotInterruptible, COLOR.ICONS.ENEMY_SPELL_NOT_INTERRUPTIBLE, COLOR.ICONS.ENEMY_SPELL_INTERRUPTIBLE):GetRGBA())
                else
                    unit_channel_fn:SetColorTexture(COLOR.ICONS.PLAYER_SPELL:GetRGBA())
                end
            else
                unit_channel_icon:SetColorTexture(0, 0, 0, 1)
                unit_channel_duration:SetColorTexture(0, 0, 0, 1)
                unit_channel_interruptible:SetColorTexture(0, 0, 0, 1)
                unit_channel_fn:SetColorTexture(0, 0, 0, 0)
            end

            unit_health:SetColorTexture(UnitHealthPercent(unit, true, curve):GetRGBA())
        else
            unit_exist:SetColorTexture(0, 0, 0, 1)
            unit_can_attack:SetColorTexture(0, 0, 0, 1)
            unit_is_self:SetColorTexture(0, 0, 0, 1)
            unit_in_combat:SetColorTexture(0, 0, 0, 1)
            unit_in_range:SetColorTexture(0, 0, 0, 1)
            unit_is_alive:SetColorTexture(0, 0, 0, 1)
            unit_cast_icon:SetColorTexture(0, 0, 0, 1)
            unit_cast_duration:SetColorTexture(0, 0, 0, 1)
            unit_cast_interruptible:SetColorTexture(0, 0, 0, 1)
            unit_channel_icon:SetColorTexture(0, 0, 0, 1)
            unit_channel_duration:SetColorTexture(0, 0, 0, 1)
            unit_channel_interruptible:SetColorTexture(0, 0, 0, 1)
            unit_health:SetColorTexture(0, 0, 0, 1)
            unit_channel_fn:SetColorTexture(0, 0, 0, 0)
            unit_cast_fn:SetColorTexture(0, 0, 0, 0)
        end
    end

    local function UpdateStatusStandard_freq_low()
        if UnitExists(unit) then
            local _, maxRange = LibRangeCheck:GetRange(unit)
            if maxRange and (maxRange <= addonTable.RangeCheck) then
                unit_in_range:SetColorTexture(1, 1, 1, 1)
            else
                unit_in_range:SetColorTexture(0, 0, 0, 1)
            end
        else
            unit_in_range:SetColorTexture(0, 0, 0, 1)
        end
    end

    UpdateStatusStandard_freq_low()
    table.insert(addonTable.OnUpdateFuncs_LOW, UpdateStatusStandard_freq_low)
    table.insert(addonTable.OnUpdateFuncs_STD, UpdateStatus_freq_std)
    if DEBUG then logging("InitializeUnitStatusFrame[" .. unit .. "]...Done") end
end

-- 初始化目标和焦点状态框架
local function InitializeTargetAndFocusStatusFrame()
    InitializeUnitStatusFrame("target", addonTable.TargetStatusFrame)
    InitializeUnitStatusFrame("focus", addonTable.FocusStatusFrame)
end

-- 将初始化目标和焦点状态框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializeTargetAndFocusStatusFrame)
