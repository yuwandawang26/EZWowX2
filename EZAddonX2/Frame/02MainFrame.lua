local addonName, addonTable = ...

local DEBUG                = addonTable.DEBUG
local logging              = addonTable.logging
local scale                = addonTable.scale
local COLOR                = addonTable.COLOR
local GetUIScaleFactor     = addonTable.GetUIScaleFactor
local CreateStandardFrame  = addonTable.CreateStandardFrame

-- 初始化主框架
local function InitializeMainFrame()
    -- 计算UI元素尺寸
    addonTable.nodeSize = GetUIScaleFactor(8 * scale)
    -- addonTable.innerSize = GetUIScaleFactor(8 * scale)
    addonTable.padSize = GetUIScaleFactor(1 * scale)
    addonTable.fontSize = GetUIScaleFactor(6 * scale)
    addonTable.footnoteSize = GetUIScaleFactor(2 * scale)

    -- 创建主框架
    addonTable.MainFrame = CreateFrame("Frame", addonName .. "MainFrame", UIParent)
    addonTable.MainFrame:SetPoint("TOPRIGHT", UIParent, "TOPRIGHT", 0, 0)
    addonTable.MainFrame:SetSize(addonTable.nodeSize * 52, addonTable.nodeSize * 18)
    addonTable.MainFrame:SetFrameStrata("TOOLTIP")
    addonTable.MainFrame:SetFrameLevel(900)
    addonTable.MainFrame:Show()

    -- 创建主框架背景
    addonTable.MainFrame.bg = addonTable.MainFrame:CreateTexture(nil, "BACKGROUND")
    addonTable.MainFrame.bg:SetAllPoints()
    addonTable.MainFrame.bg:SetColorTexture(0, 0, 0, 1)
    addonTable.MainFrame.bg:Show()

    -- 定义调试颜色
    local debugColors = {
        blue = CreateColor(91 / 255, 155 / 255, 213 / 255, 1),
        yellow = CreateColor(255 / 255, 192 / 255, 0 / 255, 1),
        gray = CreateColor(165 / 255, 165 / 255, 165 / 255, 1),
        orange = CreateColor(237 / 255, 125 / 255, 49 / 255, 1),
        green = CreateColor(84 / 255, 130 / 255, 53 / 255, 1),
        lightGreen = CreateColor(112 / 255, 173 / 255, 71 / 255, 1),
    }
    addonTable.PlayerSpellFrame = CreateStandardFrame("PlayerSpellFrame", addonTable.MainFrame, 2, 2, 36, 3, debugColors.green)
    -- 使用CreateStandardFrame创建子框架
    addonTable.PlayerBuffFrame = CreateStandardFrame("PlayerBuffFrame", addonTable.MainFrame, 2, 5, 32, 3, debugColors.blue)
    addonTable.PlayerDebuffFrame = CreateStandardFrame("PlayerDebuffFrame", addonTable.MainFrame, 2, 8, 8, 3, debugColors.yellow)
    addonTable.TargetDebuffFrame = CreateStandardFrame("TargetDebuffFrame", addonTable.MainFrame, 10, 8, 16, 3, debugColors.orange)
    addonTable.FocusDebuffFrame = CreateStandardFrame("FocusDebuffFrame", addonTable.MainFrame, 26, 8, 8, 3, debugColors.lightGreen)
    addonTable.PlayerStatusFrame = CreateStandardFrame("PlayerStatusFrame", addonTable.MainFrame, 38, 2, 8, 4, debugColors.gray)
    addonTable.TargetStatusFrame = CreateStandardFrame("TargetStatusFrame", addonTable.MainFrame, 38, 6, 8, 2, debugColors.blue)
    addonTable.FocusStatusFrame = CreateStandardFrame("FocusStatusFrame", addonTable.MainFrame, 38, 8, 8, 2, debugColors.yellow)
    addonTable.MiscFrame = CreateStandardFrame("MiscFrame", addonTable.MainFrame, 34, 5, 4, 3, debugColors.orange)
    addonTable.SpecFrame = CreateStandardFrame("SpecFrame", addonTable.MainFrame, 34, 8, 4, 3, debugColors.lightGreen)
    addonTable.SignalFrame = CreateStandardFrame("SignalFrame", addonTable.MainFrame, 38, 10, 8, 1, debugColors.blue)
    addonTable.IconListFrame1 = CreateStandardFrame("IconListFrame1", addonTable.MainFrame, 2, 0, 48, 1, debugColors.blue)
    addonTable.IconListFrame2 = CreateStandardFrame("IconListFrame2", addonTable.MainFrame, 2, 1, 48, 1, debugColors.blue)
    addonTable.IconListFrame3 = CreateStandardFrame("IconListFrame3", addonTable.MainFrame, 2, 16, 48, 1, debugColors.blue)
    addonTable.IconListFrame4 = CreateStandardFrame("IconListFrame4", addonTable.MainFrame, 2, 17, 48, 1, debugColors.blue)

    -- 创建队伍框架
    local partyDebugColor = CreateColor(127 / 255, 127 / 255, 127 / 255, 1)
    for i = 1, 4 do
        local UnitKey = string.format("%s%d", "party", i)
        addonTable["PartyFrame" .. UnitKey] = CreateStandardFrame("PartyFrame" .. UnitKey, addonTable.MainFrame, 12 * i - 10, 11, 12, 5, partyDebugColor)
    end

    -- 创建方块函数
    local node_size = addonTable.nodeSize
    local function create_square(x, y, color)
        local frame = CreateFrame("Frame", addonName .. "Frame" .. x .. y, addonTable.MainFrame)
        frame:SetFrameLevel(addonTable.MainFrame:GetFrameLevel() + 5)
        frame:SetPoint("TOPLEFT", addonTable.MainFrame, "TOPLEFT", x * node_size, -y * node_size)
        frame:SetSize(node_size, node_size)
        frame:Show()
        frame.bg = frame:CreateTexture(nil, "BACKGROUND")
        frame.bg:SetAllPoints()
        frame.bg:SetColorTexture(color:GetRGBA())
        frame.bg:Show()
    end

    -- 创建角落方块
    create_square(0, 0, COLOR.NEAR_BLACK_1)
    create_square(1, 0, COLOR.NEAR_BLACK_2)
    create_square(0, 1, COLOR.NEAR_BLACK_2)
    create_square(1, 1, COLOR.NEAR_BLACK_1)
    create_square(50, 16, COLOR.NEAR_BLACK_1)
    create_square(50, 17, COLOR.NEAR_BLACK_2)
    create_square(51, 16, COLOR.NEAR_BLACK_2)
    create_square(51, 17, COLOR.NEAR_BLACK_1)
    if DEBUG then logging("MainFrame created") end
end

-- 将初始化主框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializeMainFrame)
