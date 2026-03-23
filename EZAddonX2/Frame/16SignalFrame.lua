local addonName, addonTable = ...

local DEBUG            = addonTable.DEBUG
local logging          = addonTable.logging
local CreatePixelNode  = addonTable.CreatePixelNode
local CreateStringNode = addonTable.CreateStringNode

-- 初始化配置框架
local function InitializeSignalFrame()
    if DEBUG then logging("InitializeSignalFrame") end
    local nodes = {}

    for i = 1, 8 do
        nodes[i] = CreatePixelNode(i - 1, 0, addonName .. "SignalFrame" .. tostring(i), addonTable.SignalFrame)
        local color = i * 32 - 1
        nodes[i]:SetColorTexture(color / 255, color / 255, color / 255, 1)
    end
    logging("使用 /pd [1-8] [0-255] [0-255] [0-255] 修改信号色块")

    SLASH_PD1 = "/pd"
    SlashCmdList["PD"] = function(msg)
        local arg1, arg2, arg3, arg4 = strsplit(" ", msg, 4)
        nodes[tonumber(arg1)]:SetColorTexture(tonumber(arg2) / 255, tonumber(arg3) / 255, tonumber(arg4 / 255), 1)
    end
    CreateStringNode(51, 3, addonName .. "num_0", addonTable.MainFrame):SetText("0")
    CreateStringNode(51, 4, addonName .. "num_1", addonTable.MainFrame):SetText("1")
    CreateStringNode(51, 5, addonName .. "num_2", addonTable.MainFrame):SetText("2")
    CreateStringNode(51, 6, addonName .. "num_3", addonTable.MainFrame):SetText("3")
    CreateStringNode(51, 7, addonName .. "num_4", addonTable.MainFrame):SetText("4")
    CreateStringNode(51, 8, addonName .. "num_5", addonTable.MainFrame):SetText("5")
    CreateStringNode(51, 9, addonName .. "num_6", addonTable.MainFrame):SetText("6")
    CreateStringNode(51, 10, addonName .. "num_7", addonTable.MainFrame):SetText("7")
    CreateStringNode(51, 11, addonName .. "num_8", addonTable.MainFrame):SetText("8")
    CreateStringNode(51, 12, addonName .. "num_9", addonTable.MainFrame):SetText("9")
    CreateStringNode(51, 13, addonName .. "num_star", addonTable.MainFrame):SetText("*")
    if DEBUG then logging("InitializeSignalFrame...Done") end
end

-- 将初始化配置框架函数添加到初始化函数表
table.insert(addonTable.FrameInitFuncs, InitializeSignalFrame)
