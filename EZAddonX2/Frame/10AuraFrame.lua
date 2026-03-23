local addonName, addonTable = ...

local DEBUG              = addonTable.DEBUG
local logging            = addonTable.logging
local CreateAuraSequence = addonTable.CreateAuraSequence

-- 初始化光环框架
local function InitializeAuraFrame()
    if DEBUG then logging("InitializeAuraFrame") end
    CreateAuraSequence("player", "HELPFUL", 32, "PlayerBuff", addonTable.PlayerBuffFrame, Enum.UnitAuraSortRule.Expiration, Enum.UnitAuraSortDirection.Normal)
    CreateAuraSequence("player", "HARMFUL", 8, "PlayerDebuff", addonTable.PlayerDebuffFrame, Enum.UnitAuraSortRule.Expiration, Enum.UnitAuraSortDirection.Normal)
    CreateAuraSequence("target", "HARMFUL|PLAYER", 16, "TargetDebuff", addonTable.TargetDebuffFrame, Enum.UnitAuraSortRule.Expiration, Enum.UnitAuraSortDirection.Normal)
    CreateAuraSequence("focus", "HARMFUL|PLAYER", 8, "FocusDebuff", addonTable.FocusDebuffFrame, Enum.UnitAuraSortRule.Expiration, Enum.UnitAuraSortDirection.Normal)

    if DEBUG then logging("InitializeAuraFrame...Done") end
end

-- 将初始化光环框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializeAuraFrame)
