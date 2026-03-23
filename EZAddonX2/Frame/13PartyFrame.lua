local addonName, addonTable = ...

local DEBUG              = addonTable.DEBUG
local logging            = addonTable.logging
local COLOR              = addonTable.COLOR
local curve              = addonTable.curve
local LibRangeCheck      = addonTable.LibRangeCheck
local CreatePixelNode    = addonTable.CreatePixelNode
local CreateWhiteBar     = addonTable.CreateWhiteBar
local CreateAuraSequence = addonTable.CreateAuraSequence

local CreateFrame = CreateFrame
local UnitExists = UnitExists
local UnitIsUnit = UnitIsUnit
local UnitIsDeadOrGhost = UnitIsDeadOrGhost
local UnitClass = UnitClass
local UnitGroupRolesAssigned = UnitGroupRolesAssigned
local UnitHealthPercent = UnitHealthPercent
local UnitHealthMax = UnitHealthMax
local UnitGetTotalAbsorbs = UnitGetTotalAbsorbs
local UnitGetTotalHealAbsorbs = UnitGetTotalHealAbsorbs

-- 初始化队伍框架
local function InitializePartyFrame()
    if DEBUG then logging("InitializePartyFrame") end
    local node_size = addonTable.nodeSize

    local function RegisterPartyMaxHealthUpdateFunc(unit, updater)
        table.insert(addonTable.OnEventFunc_MaxHealth_Party, { unit = unit, func = updater })
    end

    for i = 1, 4 do
        local UnitKey = string.format("%s%d", "party", i)
        local parent_frame = addonTable["PartyFrame" .. UnitKey]
        local frame_pre = addonName .. "PartyFrame" .. UnitKey

        -- 创建队伍Debuff框架
        local debuff_frame = CreateFrame("Frame", frame_pre .. "DebuffFrame", parent_frame)
        debuff_frame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
        debuff_frame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", 0, 0)
        debuff_frame:SetSize(node_size * 6, node_size * 3)
        debuff_frame:Show()
        CreateAuraSequence(UnitKey, "HARMFUL", 6, UnitKey .. "Debuff", debuff_frame, Enum.UnitAuraSortRule.Default, Enum.UnitAuraSortDirection.Normal)


        -- 创建队伍Buff框架
        local buff_frame = CreateFrame("Frame", frame_pre .. "BuffFrame", parent_frame)
        buff_frame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
        buff_frame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", 6 * node_size, 0)
        buff_frame:SetSize(node_size * 6, node_size * 3)
        buff_frame:Show()
        CreateAuraSequence(UnitKey, "HELPFUL|PLAYER", 7, UnitKey .. "Buff", buff_frame, Enum.UnitAuraSortRule.Default, Enum.UnitAuraSortDirection.Normal)


        -- 创建队伍条框架
        local bar_frame = CreateFrame("Frame", frame_pre .. "BarFrame", parent_frame)
        bar_frame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
        bar_frame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", 0, -3 * node_size)
        bar_frame:SetSize(node_size * 8, node_size * 2)
        bar_frame:Show()

        -- 创建队伍状态框架
        local status_frame = CreateFrame("Frame", frame_pre .. "StatusFrame", parent_frame)
        status_frame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
        status_frame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", 8 * node_size, -3 * node_size)
        status_frame:SetSize(node_size * 4, node_size * 2)
        status_frame:Show()

        -- 创建队伍状态节点
        local unit_exist = CreatePixelNode(0, 0, addonName .. "PartyExist" .. i, status_frame)
        local unit_in_range = CreatePixelNode(1, 0, addonName .. "PartyInRange" .. i, status_frame)
        local unit_health = CreatePixelNode(2, 0, addonName .. "PartyHealth" .. i, status_frame)
        local unit_is_alive = CreatePixelNode(3, 0, addonName .. "PartyAlive" .. i, status_frame)
        local unit_class = CreatePixelNode(0, 1, addonName .. "PartyClass" .. i, status_frame)
        local unit_role = CreatePixelNode(1, 1, addonName .. "PartyRole" .. i, status_frame)
        local unit_select = CreatePixelNode(2, 1, addonName .. "PartySelect" .. i, status_frame)

        -- 创建队伍吸收条
        local DamageAbsorbsBar = CreateWhiteBar(UnitKey .. "DamageAbsorbsBar", bar_frame, 0, 0, 8, 1)
        local HealAbsorbsBar = CreateWhiteBar(UnitKey .. "HealAbsorbsBar", bar_frame, 0, 1, 8, 1)

        local function UpdateStatus_event_UNIT_MAXHEALTH()
            if UnitExists(UnitKey) then
                local maxHealth = UnitHealthMax(UnitKey)
                DamageAbsorbsBar:SetMinMaxValues(0, maxHealth)
                HealAbsorbsBar:SetMinMaxValues(0, maxHealth)
            else
                DamageAbsorbsBar:SetMinMaxValues(0, 100)
                HealAbsorbsBar:SetMinMaxValues(0, 100)
            end
        end

        -- 更新队伍框架函数
        local function UpdateStatus_freq_std()
            if UnitExists(UnitKey) then
                -- 检查是否存在
                unit_exist:SetColorTexture(1, 1, 1, 1)
                unit_health:SetColorTexture(UnitHealthPercent(UnitKey, true, curve):GetRGBA())

                if UnitIsUnit("target", UnitKey) then
                    unit_select:SetColorTexture(1, 1, 1, 1)
                else
                    unit_select:SetColorTexture(0, 0, 0, 1)
                end

                if UnitIsDeadOrGhost(UnitKey) then
                    unit_is_alive:SetColorTexture(0, 0, 0, 1)
                else
                    unit_is_alive:SetColorTexture(1, 1, 1, 1)
                end

                DamageAbsorbsBar:SetValue(UnitGetTotalAbsorbs(UnitKey))

                HealAbsorbsBar:SetValue(UnitGetTotalHealAbsorbs(UnitKey))
            else
                unit_exist:SetColorTexture(0, 0, 0, 1)
                unit_in_range:SetColorTexture(0, 0, 0, 1)
                unit_health:SetColorTexture(0, 0, 0, 1)
                unit_is_alive:SetColorTexture(0, 0, 0, 1)
                unit_select:SetColorTexture(0, 0, 0, 1)

                DamageAbsorbsBar:SetValue(0)
                HealAbsorbsBar:SetValue(0)
            end
        end

        local function UpdateStatusStandard_freq_low()
            if UnitExists(UnitKey) then
                local maxHealth = UnitHealthMax(UnitKey)
                DamageAbsorbsBar:SetMinMaxValues(0, maxHealth)
                HealAbsorbsBar:SetMinMaxValues(0, maxHealth)
                local _, maxRange = LibRangeCheck:GetRange(UnitKey)
                if maxRange and (maxRange <= addonTable.RangeCheck) then
                    unit_in_range:SetColorTexture(1, 1, 1, 1)
                else
                    unit_in_range:SetColorTexture(0, 0, 0, 1)
                end
                local _, classFilename, _ = UnitClass(UnitKey)
                if classFilename then
                    unit_class:SetColorTexture(COLOR.CLASS[classFilename]:GetRGBA())
                else
                    unit_class:SetColorTexture(0, 0, 0, 1)
                end
                local role = UnitGroupRolesAssigned(UnitKey)
                local roleColor = COLOR.ROLE[role] or COLOR.ROLE.NONE
                unit_role:SetColorTexture(roleColor:GetRGBA())
            else
                unit_in_range:SetColorTexture(0, 0, 0, 1)
                unit_class:SetColorTexture(0, 0, 0, 1)
                unit_role:SetColorTexture(0, 0, 0, 1)
            end
        end

        UpdateStatus_event_UNIT_MAXHEALTH()
        RegisterPartyMaxHealthUpdateFunc(UnitKey, UpdateStatus_event_UNIT_MAXHEALTH)
        UpdateStatusStandard_freq_low()
        table.insert(addonTable.OnUpdateFuncs_LOW, UpdateStatusStandard_freq_low)
        table.insert(addonTable.OnUpdateFuncs_STD, UpdateStatus_freq_std)
    end
    if DEBUG then logging("InitializePartyFrame...Done") end
end

-- 将初始化队伍框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializePartyFrame)
