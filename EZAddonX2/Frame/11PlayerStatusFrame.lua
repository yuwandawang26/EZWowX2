local addonName, addonTable = ...

local DEBUG               = addonTable.DEBUG
local logging             = addonTable.logging
local COLOR               = addonTable.COLOR
local curve               = addonTable.curve
local CreatePixelNode     = addonTable.CreatePixelNode
local CreateFootnoteNode  = addonTable.CreateFootnoteNode
local CreateWhiteBar      = addonTable.CreateWhiteBar

local floor = math.floor
local min = math.min
local GetTime = GetTime
local UnitHealthPercent = UnitHealthPercent
local UnitPowerPercent = UnitPowerPercent
local UnitGetTotalHealAbsorbs = UnitGetTotalHealAbsorbs
local UnitGetTotalAbsorbs = UnitGetTotalAbsorbs
local UnitHealthMax = UnitHealthMax
local UnitClass = UnitClass
local UnitGroupRolesAssigned = UnitGroupRolesAssigned
local UnitIsDeadOrGhost = UnitIsDeadOrGhost
local UnitInVehicle = UnitInVehicle
local IsMounted = IsMounted
local GetUnitSpeed = GetUnitSpeed
local UnitAffectingCombat = UnitAffectingCombat
local UnitCastingInfo = UnitCastingInfo
local UnitChannelInfo = UnitChannelInfo
local UnitCastingDuration = UnitCastingDuration
local UnitChannelDuration = UnitChannelDuration
local UnitPowerType = UnitPowerType

-- 初始化玩家状态框架
local function InitializePlayerStatusFrame()
    if DEBUG then logging("InitializePlayerStatusFrame") end
    local x = 0
    local y = 2
    local player_in_combat = CreatePixelNode(x, y, "PlayerInCombat", addonTable.PlayerStatusFrame)
    x = 1
    local player_is_moving = CreatePixelNode(x, y, "PlayerIsMoving", addonTable.PlayerStatusFrame)
    x = 2
    local player_in_vehicle = CreatePixelNode(x, y, "PlayerInVehicle", addonTable.PlayerStatusFrame)
    x = 3
    local player_is_empowered = CreatePixelNode(x, y, "PlayerIsEmpowered", addonTable.PlayerStatusFrame)
    x = 4
    local player_cast_icon, player_cast_fn = CreateFootnoteNode(x, y, "PlayerCastIcon", addonTable.PlayerStatusFrame)
    x = 5
    local player_cast_duration = CreatePixelNode(x, y, "PlayerCastDuration", addonTable.PlayerStatusFrame)
    y = 3
    x = 0
    local player_class = CreatePixelNode(x, y, "PlayerClass", addonTable.PlayerStatusFrame)
    x = 1
    local player_role = CreatePixelNode(x, y, "PlayerRole", addonTable.PlayerStatusFrame)
    x = 2
    local player_deaded = CreatePixelNode(x, y, "PlayerDeaded", addonTable.PlayerStatusFrame)
    x = 3
    local non_combat_timestamp = GetTime()
    local player_combat_time = CreatePixelNode(x, y, "PlayerCombatTime", addonTable.PlayerStatusFrame)
    x = 4
    local player_channel_icon, player_channel_fn = CreateFootnoteNode(x, y, "PlayerChannelIcon", addonTable.PlayerStatusFrame)
    x = 5
    local player_channel_duration = CreatePixelNode(x, y, "PlayerChannelDuration", addonTable.PlayerStatusFrame)


    y = 2
    x = 7
    local player_health = CreatePixelNode(x, y, "PlayerHealth", addonTable.PlayerStatusFrame)
    y = 3
    local player_power = CreatePixelNode(x, y, "PlayerPower", addonTable.PlayerStatusFrame)


    local PlayerDamageAbsorbsBar = CreateWhiteBar("PlayerDamageAbsorbsBar", addonTable.PlayerStatusFrame, 0, 0, 8, 1)
    local PlayerHealAbsorbsBar = CreateWhiteBar("PlayerHealAbsorbsBar", addonTable.PlayerStatusFrame, 0, 1, 8, 1)

    local function RegisterPlayerMaxHealthUpdateFunc(updater)
        table.insert(addonTable.OnEventFunc_MaxHealth_Player, updater)
    end

    local function UpdateStatus_event_UNIT_MAXHEALTH()
        local maxHealth = UnitHealthMax("player")
        PlayerDamageAbsorbsBar:SetMinMaxValues(0, maxHealth)
        PlayerHealAbsorbsBar:SetMinMaxValues(0, maxHealth)
    end

    local function UpdateStatusStandard_freq_low()
        local _, classFilename, _ = UnitClass("player")
        if classFilename then
            player_class:SetColorTexture(COLOR.CLASS[classFilename]:GetRGBA())
        else
            player_class:SetColorTexture(0, 0, 0, 1)
        end
        local role = UnitGroupRolesAssigned("player")
        local roleColor = COLOR.ROLE[role] or COLOR.ROLE.NONE
        player_role:SetColorTexture(roleColor:GetRGBA())
    end

    -- 更新玩家状态函数
    local function UpdateStatus_freq_std()
        if UnitAffectingCombat("player") then
            local combat_time = min(255, floor(GetTime() - non_combat_timestamp))
            player_combat_time:SetColorTexture(combat_time / 255, combat_time / 255, combat_time / 255, 1)
            player_in_combat:SetColorTexture(1, 1, 1, 1)
        else
            non_combat_timestamp = GetTime()
            player_combat_time:SetColorTexture(0, 0, 0, 1)
            player_in_combat:SetColorTexture(0, 0, 0, 1)
        end
        if GetUnitSpeed("player") > 0 then
            player_is_moving:SetColorTexture(1, 1, 1, 1)
        else
            player_is_moving:SetColorTexture(0, 0, 0, 1)
        end

        if UnitInVehicle("player") or IsMounted() then
            player_in_vehicle:SetColorTexture(1, 1, 1, 1)
        else
            player_in_vehicle:SetColorTexture(0, 0, 0, 1)
        end


        local _, _, CastTextureID, _, _, _, _, _, _, _ = UnitCastingInfo("player")
        if CastTextureID then
            player_cast_icon:SetTexture(CastTextureID)
            local duration = UnitCastingDuration("player")
            local result = duration:EvaluateElapsedPercent(curve)
            player_cast_duration:SetColorTexture(result:GetRGBA())
            player_cast_fn:SetColorTexture(COLOR.ICONS.PLAYER_SPELL:GetRGBA())
        else
            player_cast_icon:SetColorTexture(0, 0, 0, 1)
            player_cast_duration:SetColorTexture(0, 0, 0, 1)
            player_cast_fn:SetColorTexture(0, 0, 0, 0)
        end

        local _, _, channelTextureID, _, _, _, _, _, isEmpowered, _, _ = UnitChannelInfo("player")
        if isEmpowered then
            player_is_empowered:SetColorTexture(1, 1, 1, 1)
        else
            player_is_empowered:SetColorTexture(0, 0, 0, 1)
        end

        if channelTextureID then
            player_channel_icon:SetTexture(channelTextureID)
            local duration = UnitChannelDuration("player")
            local result = duration:EvaluateElapsedPercent(curve)
            player_channel_duration:SetColorTexture(result:GetRGBA())
            player_channel_fn:SetColorTexture(COLOR.ICONS.PLAYER_SPELL:GetRGBA())
        else
            player_channel_icon:SetColorTexture(0, 0, 0, 1)
            player_channel_duration:SetColorTexture(0, 0, 0, 1)
            player_channel_fn:SetColorTexture(0, 0, 0, 0)
        end

        if UnitIsDeadOrGhost("player") then
            player_deaded:SetColorTexture(1, 1, 1, 1)
        else
            player_deaded:SetColorTexture(0, 0, 0, 1)
        end

        PlayerDamageAbsorbsBar:SetValue(UnitGetTotalAbsorbs("player"))

        PlayerHealAbsorbsBar:SetValue(UnitGetTotalHealAbsorbs("player"))
        local powerType, _, _, _, _ = UnitPowerType("player")
        player_health:SetColorTexture(UnitHealthPercent("player", true, curve):GetRGBA())
        player_power:SetColorTexture(UnitPowerPercent("player", powerType, true, curve):GetRGBA())
    end
    UpdateStatus_event_UNIT_MAXHEALTH()
    RegisterPlayerMaxHealthUpdateFunc(UpdateStatus_event_UNIT_MAXHEALTH)
    UpdateStatusStandard_freq_low()
    table.insert(addonTable.OnUpdateFuncs_LOW, UpdateStatusStandard_freq_low)
    table.insert(addonTable.OnUpdateFuncs_STD, UpdateStatus_freq_std)
    if DEBUG then logging("InitializePlayerStatusFrame...Done") end
end

-- 将初始化玩家状态框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializePlayerStatusFrame)
