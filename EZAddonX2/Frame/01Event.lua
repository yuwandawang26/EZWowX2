local addonName, addonTable = ...

-- 创建主框架
local frame = CreateFrame("Frame", addonName .. "Frame")

function frame:PLAYER_ENTERING_WORLD()
    C_Timer.After(0, function()
        wipe(addonTable.OnUpdateFuncs_STD)
        wipe(addonTable.OnUpdateFuncs_LOW)
        wipe(addonTable.OnEventFunc_Aura)
        wipe(addonTable.OnEventFunc_MaxHealth_Player)
        wipe(addonTable.OnEventFunc_MaxHealth_Party)
        wipe(addonTable.OnEventFunc_Spell)
        for _, func in ipairs(addonTable.FrameInitFuncs) do
            func()
        end
    end)
    self:UnregisterEvent("PLAYER_ENTERING_WORLD")
end

function frame:UNIT_AURA(unitTarget)
    for i = 1, #addonTable.OnEventFunc_Aura do
        local updaterInfo = addonTable.OnEventFunc_Aura[i]
        if updaterInfo.unit == unitTarget then
            updaterInfo.func()
        end
    end
end

function frame:UNIT_MAXHEALTH(unitTarget)
    if unitTarget == "player" then
        for i = 1, #addonTable.OnEventFunc_MaxHealth_Player do
            addonTable.OnEventFunc_MaxHealth_Player[i]()
        end
        return
    end

    for i = 1, #addonTable.OnEventFunc_MaxHealth_Party do
        local updaterInfo = addonTable.OnEventFunc_MaxHealth_Party[i]
        if updaterInfo.unit == unitTarget then
            updaterInfo.func()
        end
    end
end

function frame:SPELLS_CHANGED()
    for i = 1, #addonTable.OnEventFunc_Spell do
        addonTable.OnEventFunc_Spell[i]()
    end
end

function frame:SPELL_UPDATE_ICON()
    self:SPELLS_CHANGED()
end

function frame:PLAYER_TALENT_UPDATE()
    self:SPELLS_CHANGED()
end

function frame:ACTIVE_TALENT_GROUP_CHANGED()
    self:SPELLS_CHANGED()
end

-- 注册事件
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:RegisterEvent("UNIT_AURA")
frame:RegisterEvent("UNIT_MAXHEALTH")
frame:RegisterEvent("SPELLS_CHANGED")
frame:RegisterEvent("SPELL_UPDATE_ICON")
frame:RegisterEvent("PLAYER_TALENT_UPDATE")
frame:RegisterEvent("ACTIVE_TALENT_GROUP_CHANGED")
frame:SetScript("OnEvent", function(self, event, ...)
    self[event](self, ...)
end)

-- 时间流逝变量
local timeElapsed = 0
local lowFrequencyTimeElapsed = 0
-- 钩子OnUpdate脚本，用于定时更新
frame:HookScript("OnUpdate", function(self, elapsed)
    local tickOffset             = 1.0 / addonTable.FPS;
    local lowFrequencyTickOffset = 1.0 / addonTable.LowFrequencyFPS;
    timeElapsed                  = timeElapsed + elapsed
    lowFrequencyTimeElapsed      = lowFrequencyTimeElapsed + elapsed
    if timeElapsed > tickOffset then
        timeElapsed = 0
        for _, updater in ipairs(addonTable.OnUpdateFuncs_STD) do
            updater()
        end
    end
    if lowFrequencyTimeElapsed > lowFrequencyTickOffset then
        lowFrequencyTimeElapsed = 0
        for _, updater in ipairs(addonTable.OnUpdateFuncs_LOW) do
            updater()
        end
    end
end)
