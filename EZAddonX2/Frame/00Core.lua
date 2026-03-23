local addonName, addonTable = ...
addonTable.LibRangeCheck    = LibStub:GetLibrary("LibRangeCheck-3.0", true)

addonTable.DEBUG            = false
addonTable.scale            = 1
addonTable.fontFile         = "Interface\\Addons\\" .. addonName .. "\\Fonts\\CustomFont.ttf"
-- 日志输出函数
function addonTable.logging(msg)
    print("|cFFFFBB66[EZ]|r" .. tostring(msg))
end

local logging                              = addonTable.logging
local DEBUG                                = addonTable.DEBUG
local fontFile                             = addonTable.fontFile
local scale                                = addonTable.scale

local gameBuildVersion, GameBuildNumber, _ = GetBuildInfo()
local fullVersion                          = gameBuildVersion .. "." .. GameBuildNumber
local addonVersion                         = C_AddOns.GetAddOnMetadata(addonName, "Version")

if addonVersion ~= fullVersion then
    logging("插件版本" .. addonVersion .. " 游戏版本" .. fullVersion)
    logging("插件版本与游戏版本不一致，可能会导致一些问题")
end


-- 本地化提高性能
local floor = math.floor
local min = math.min
local tostring = tostring

local CreateFrame = CreateFrame
-- C_CurveUtil
local CreateColorCurve = C_CurveUtil.CreateColorCurve
local EvaluateColorFromBoolean = C_CurveUtil.EvaluateColorFromBoolean
-- C_UnitAuras
local GetUnitAuraInstanceIDs = C_UnitAuras.GetUnitAuraInstanceIDs
local GetAuraDataByAuraInstanceID = C_UnitAuras.GetAuraDataByAuraInstanceID
local GetAuraDuration = C_UnitAuras.GetAuraDuration
local GetAuraApplicationDisplayCount = C_UnitAuras.GetAuraApplicationDisplayCount
local GetAuraDispelTypeColor = C_UnitAuras.GetAuraDispelTypeColor
local DoesAuraHaveExpirationTime = C_UnitAuras.DoesAuraHaveExpirationTime
local UnitIsEnemy = UnitIsEnemy
local UnitExists = UnitExists


-- 颜色定义表
addonTable.COLOR = {
    RED = CreateColor(255 / 255, 0, 0, 1),
    GREEN = CreateColor(0, 255 / 255, 0, 1),
    BLUE = CreateColor(0, 0, 255 / 255, 1),
    ICONS = {
        MAGIC = CreateColor(60 / 255, 100 / 255, 220 / 255, 1),                     -- 魔法
        CURSE = CreateColor(100 / 255, 0, 120 / 255, 1),                            -- 诅咒
        DISEASE = CreateColor(160 / 255, 120 / 255, 60 / 255, 1),                   -- 疾病
        POISON = CreateColor(154 / 255, 205 / 255, 50 / 255, 1),                    -- 中毒
        ENRAGE = CreateColor(230 / 255, 120 / 255, 20 / 255, 1),                    -- 激怒
        BLEED = CreateColor(80 / 255, 0, 20 / 255, 1),                              -- 流血
        PLAYER_DEBUFF = CreateColor(255 / 255, 60 / 255, 60 / 255, 1),              -- 无分类减益
        PLAYER_BUFF = CreateColor(80 / 255, 220 / 255, 120 / 255, 1),               -- 友方增益
        PLAYER_SPELL = CreateColor(64 / 255, 158 / 255, 210 / 255, 1),              -- 友方施法
        ENEMY_SPELL_INTERRUPTIBLE = CreateColor(255 / 255, 255 / 255, 60 / 255, 1), -- 可打断
        ENEMY_SPELL_NOT_INTERRUPTIBLE = CreateColor(200 / 255, 0, 0, 1),            -- 不可打断
        ENEMY_DEBUFF = CreateColor(105 / 255, 105 / 255, 210 / 255, 1),             -- 敌方减益
        NONE = CreateColor(0, 0, 0, 0),                                             -- 无
    },
    NEAR_BLACK_1 = CreateColor(15 / 255, 25 / 255, 20 / 255, 1),                    -- 接近黑色
    NEAR_BLACK_2 = CreateColor(25 / 255, 15 / 255, 20 / 255, 1),                    -- 接近黑色
    BLACK = CreateColor(0, 0, 0, 1),
    WHITE = CreateColor(1, 1, 1, 1),
    C0 = CreateColor(0, 0, 0, 1),
    C100 = CreateColor(100 / 255, 100 / 255, 100 / 255, 1),
    C150 = CreateColor(150 / 255, 150 / 255, 150 / 255, 1),
    C200 = CreateColor(200 / 255, 200 / 255, 200 / 255, 1),
    C250 = CreateColor(250 / 255, 250 / 255, 250 / 255, 1),
    C255 = CreateColor(255 / 255, 255 / 255, 255 / 255, 1),
    ROLE = {
        TANK = CreateColor(180 / 255, 80 / 255, 20 / 255, 1),     -- 坦克
        HEALER = CreateColor(120 / 255, 200 / 255, 255 / 255, 1), -- 治疗
        DAMAGER = CreateColor(230 / 255, 200 / 255, 50 / 255, 1), -- 伤害输出
        NONE = CreateColor(0, 0, 0, 1),                           -- 无角色
    },
    CLASS = {
        WARRIOR = CreateColor(199 / 255, 86 / 255, 36 / 255, 1),       -- 战士
        PALADIN = CreateColor(245 / 255, 140 / 255, 186 / 255, 1),     -- 圣骑士
        HUNTER = CreateColor(163 / 255, 203 / 255, 66 / 255, 1),       -- 猎人
        ROGUE = CreateColor(255 / 255, 245 / 255, 105 / 255, 1),       -- 潜行者
        PRIEST = CreateColor(196 / 255, 207 / 255, 207 / 255, 1),      -- 牧师
        DEATHKNIGHT = CreateColor(125 / 255, 125 / 255, 215 / 255, 1), -- 死亡骑士
        SHAMAN = CreateColor(64 / 255, 148 / 255, 255 / 255, 1),       -- 萨满祭司
        MAGE = CreateColor(64 / 255, 158 / 255, 210 / 255, 1),         -- 法师
        WARLOCK = CreateColor(105 / 255, 105 / 255, 210 / 255, 1),     -- 术士
        MONK = CreateColor(0 / 255, 255 / 255, 150 / 255, 1),          -- 武僧
        DRUID = CreateColor(255 / 255, 125 / 255, 10 / 255, 1),        -- 德鲁伊
        DEMONHUNTER = CreateColor(163 / 255, 48 / 255, 201 / 255, 1),  -- 恶魔猎手
        EVOKER = CreateColor(108 / 255, 191 / 255, 246 / 255, 1)       -- 唤魔师
    }
}

local COLOR = addonTable.COLOR

-- 颜色曲线定义
local curve = CreateColorCurve()
curve:SetType(Enum.LuaCurveType.Linear)
curve:AddPoint(0.0, CreateColor(0, 0, 0, 1))
curve:AddPoint(1.0, CreateColor(1, 1, 1, 1))
addonTable.curve = curve

-- 反向颜色曲线定义
local curve_reverse = CreateColorCurve()
curve_reverse:SetType(Enum.LuaCurveType.Linear)
curve_reverse:AddPoint(0.0, CreateColor(1, 1, 1, 1))
curve_reverse:AddPoint(1.0, CreateColor(0, 0, 0, 1))
addonTable.curve_reverse = curve_reverse

-- Debuff颜色曲线定义
local debuff_curve = CreateColorCurve()
debuff_curve:AddPoint(0, COLOR.ICONS.PLAYER_DEBUFF)
debuff_curve:AddPoint(1, COLOR.ICONS.MAGIC)
debuff_curve:AddPoint(2, COLOR.ICONS.CURSE)
debuff_curve:AddPoint(3, COLOR.ICONS.DISEASE)
debuff_curve:AddPoint(4, COLOR.ICONS.POISON)
debuff_curve:AddPoint(9, COLOR.ICONS.ENRAGE)
debuff_curve:AddPoint(11, COLOR.ICONS.BLEED)
addonTable.debuff_curve = debuff_curve

local playerbuff_curve = CreateColorCurve()
playerbuff_curve:AddPoint(0, COLOR.ICONS.PLAYER_BUFF)
playerbuff_curve:AddPoint(1, COLOR.ICONS.MAGIC)
playerbuff_curve:AddPoint(2, COLOR.ICONS.CURSE)
playerbuff_curve:AddPoint(3, COLOR.ICONS.DISEASE)
playerbuff_curve:AddPoint(4, COLOR.ICONS.POISON)
playerbuff_curve:AddPoint(9, COLOR.ICONS.ENRAGE)
playerbuff_curve:AddPoint(11, COLOR.ICONS.BLEED)
addonTable.playerbuff_curve = playerbuff_curve

local targetdebuff_curve = CreateColorCurve()
targetdebuff_curve:AddPoint(0, COLOR.ICONS.ENEMY_DEBUFF)
targetdebuff_curve:AddPoint(1, COLOR.ICONS.MAGIC)
targetdebuff_curve:AddPoint(2, COLOR.ICONS.CURSE)
targetdebuff_curve:AddPoint(3, COLOR.ICONS.DISEASE)
targetdebuff_curve:AddPoint(4, COLOR.ICONS.POISON)
targetdebuff_curve:AddPoint(9, COLOR.ICONS.ENRAGE)
targetdebuff_curve:AddPoint(11, COLOR.ICONS.BLEED)
addonTable.targetdebuff_curve = targetdebuff_curve

-- 剩余时间颜色曲线定义
local remaining_curve = CreateColorCurve()
remaining_curve:SetType(Enum.LuaCurveType.Linear)
remaining_curve:AddPoint(0.0, COLOR.C0)
remaining_curve:AddPoint(5.0, COLOR.C100)
remaining_curve:AddPoint(30.0, COLOR.C150)
remaining_curve:AddPoint(155.0, COLOR.C200)
remaining_curve:AddPoint(375.0, COLOR.C255)
addonTable.remaining_curve              = remaining_curve

-- 框架初始化函数表
addonTable.FrameInitFuncs               = {}
-- 更新函数表
addonTable.OnUpdateFuncs_STD            = {}
-- 低频更新函数表
addonTable.OnUpdateFuncs_LOW            = {}
-- Aura 事件更新函数表（按 unit 分发）
addonTable.OnEventFunc_Aura             = {}
-- 生命上限事件更新函数表（按 unit 分发）
addonTable.OnEventFunc_MaxHealth_Player = {}
addonTable.OnEventFunc_MaxHealth_Party  = {}
-- 技能图标事件更新函数表
addonTable.OnEventFunc_Spell            = {}
-- 技能表，每个技能有两种显示方式："cooldown"和"charge"
addonTable.Spell                        = {}


-- 获取UI缩放因子
function addonTable.GetUIScaleFactor(pixelValue)
    local _, physicalHeight = GetPhysicalScreenSize()
    local logicalHeight = GetScreenHeight()
    return (pixelValue * logicalHeight) / physicalHeight
end

-- 创建标准框架
function addonTable.CreateStandardFrame(name, parent, x, y, w, h, debugColor)
    local node_size = addonTable.nodeSize
    local frame = CreateFrame("Frame", addonName .. name, parent)
    frame:SetFrameLevel(parent:GetFrameLevel() + 1)
    frame:SetPoint("TOPLEFT", parent, "TOPLEFT", x * node_size, -1 * y * node_size)
    frame:SetSize(w * node_size, h * node_size)
    frame:Show()
    frame.bg = frame:CreateTexture(nil, "BACKGROUND")
    frame.bg:SetAllPoints()
    if DEBUG and debugColor then
        frame.bg:SetColorTexture(debugColor:GetRGBA())
    else
        frame.bg:SetColorTexture(0, 0, 0, 1)
    end
    frame.bg:Show()
    return frame
end

-- 创建像素节点
function addonTable.CreatePixelNode(x, y, title, parent_frame)
    local node_size = addonTable.nodeSize
    local nodeFrame = CreateFrame("Frame", addonName .. "Pixel" .. title, parent_frame)
    nodeFrame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", x * node_size, -y * node_size)
    nodeFrame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
    nodeFrame:SetSize(node_size, node_size)
    nodeFrame:Show()
    local nodeTexture = nodeFrame:CreateTexture(nil, "BACKGROUND")
    nodeTexture:SetAllPoints(nodeFrame)
    nodeTexture:SetColorTexture(0, 0, 0, 1)
    nodeTexture:Show()
    return nodeTexture
end

-- 一个包含四个小像素的节点。
function addonTable.CreateMixedNode(x, y, title, parent_frame)
    local node_size = addonTable.nodeSize
    -- 主节点
    local main_frame = CreateFrame("Frame", addonName .. "Pixel" .. title, parent_frame)
    main_frame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", x * node_size, -y * node_size)
    main_frame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
    main_frame:SetSize(node_size, node_size)
    main_frame:Show()
    -- 左上节点
    local TOPLEFT_Frame = CreateFrame("Frame", addonName .. title .. "PixelTOPLEFT", main_frame)
    TOPLEFT_Frame:SetPoint("TOPLEFT", main_frame, "TOPLEFT", 0, 0)
    TOPLEFT_Frame:SetFrameLevel(main_frame:GetFrameLevel() + 1)
    TOPLEFT_Frame:SetSize(node_size / 2, node_size / 2)
    TOPLEFT_Frame:Show()
    local TOPLEFT_Texture = TOPLEFT_Frame:CreateTexture(nil, "BACKGROUND")
    TOPLEFT_Texture:SetAllPoints(TOPLEFT_Frame)
    TOPLEFT_Texture:SetColorTexture(0, 0, 0, 1)
    TOPLEFT_Texture:Show()

    -- 右上节点
    local TOPRIGHT_Frame = CreateFrame("Frame", addonName .. "PixelTOPRIGHT" .. title, main_frame)
    TOPRIGHT_Frame:SetPoint("TOPRIGHT", main_frame, "TOPRIGHT", 0, 0)
    TOPRIGHT_Frame:SetFrameLevel(main_frame:GetFrameLevel() + 1)
    TOPRIGHT_Frame:SetSize(node_size / 2, node_size / 2)
    TOPRIGHT_Frame:Show()
    local TOPRIGHT_Texture = TOPRIGHT_Frame:CreateTexture(nil, "BACKGROUND")
    TOPRIGHT_Texture:SetAllPoints(TOPRIGHT_Frame)
    TOPRIGHT_Texture:SetColorTexture(0, 0, 0, 1)
    TOPRIGHT_Texture:Show()

    -- 左下节点
    local BOTTOMLEFT_Frame = CreateFrame("Frame", addonName .. "PixelBOTTOMLEFT" .. title, main_frame)
    BOTTOMLEFT_Frame:SetPoint("BOTTOMLEFT", main_frame, "BOTTOMLEFT", 0, 0)
    BOTTOMLEFT_Frame:SetFrameLevel(main_frame:GetFrameLevel() + 1)
    BOTTOMLEFT_Frame:SetSize(node_size / 2, node_size / 2)
    BOTTOMLEFT_Frame:Show()
    local BOTTOMLEFT_Texture = BOTTOMLEFT_Frame:CreateTexture(nil, "BACKGROUND")
    BOTTOMLEFT_Texture:SetAllPoints(BOTTOMLEFT_Frame)
    BOTTOMLEFT_Texture:SetColorTexture(0, 0, 0, 1)
    BOTTOMLEFT_Texture:Show()

    -- 右下节点
    local BOTTOMRIGHT_Frame = CreateFrame("Frame", addonName .. "PixelBOTTOMRIGHT" .. title, main_frame)
    BOTTOMRIGHT_Frame:SetPoint("BOTTOMRIGHT", main_frame, "BOTTOMRIGHT", 0, 0)
    BOTTOMRIGHT_Frame:SetFrameLevel(main_frame:GetFrameLevel() + 1)
    BOTTOMRIGHT_Frame:SetSize(node_size / 2, node_size / 2)
    BOTTOMRIGHT_Frame:Show()
    local BOTTOMRIGHT_Texture = BOTTOMRIGHT_Frame:CreateTexture(nil, "BACKGROUND")
    BOTTOMRIGHT_Texture:SetAllPoints(BOTTOMRIGHT_Frame)
    BOTTOMRIGHT_Texture:SetColorTexture(0, 0, 0, 1)
    BOTTOMRIGHT_Texture:Show()

    if DEBUG then
        TOPLEFT_Texture:SetColorTexture(math.random(), math.random(), math.random(), 1)
        TOPRIGHT_Texture:SetColorTexture(math.random(), math.random(), math.random(), 1)
        BOTTOMLEFT_Texture:SetColorTexture(math.random(), math.random(), math.random(), 1)
        BOTTOMRIGHT_Texture:SetColorTexture(math.random(), math.random(), math.random(), 1)
    end
    return TOPLEFT_Texture, TOPRIGHT_Texture, BOTTOMLEFT_Texture, BOTTOMRIGHT_Texture
end

-- 一个包含角标的节点
function addonTable.CreateFootnoteNode(x, y, title, parent_frame)
    local node_size = addonTable.nodeSize
    local footnoteSize = addonTable.footnoteSize
    -- 主节点
    local main_frame = CreateFrame("Frame", addonName .. "Pixel" .. title, parent_frame)
    main_frame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", x * node_size, -y * node_size)
    main_frame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
    main_frame:SetSize(node_size, node_size)
    main_frame:Show()
    -- 主节点的图标
    local main_Texture = main_frame:CreateTexture(nil, "BACKGROUND")
    main_Texture:SetAllPoints(main_frame)
    main_Texture:SetColorTexture(0, 0, 0, 1)
    main_Texture:Show()

    local fn_frame = CreateFrame("Frame", addonName .. "PixelFootnote" .. title, main_frame)
    fn_frame:SetPoint("BOTTOMRIGHT", main_frame, "BOTTOMRIGHT", 0, 0)
    fn_frame:SetFrameLevel(main_frame:GetFrameLevel() + 2)
    fn_frame:SetSize(footnoteSize, footnoteSize)
    fn_frame:Show()
    local fn_Texture = fn_frame:CreateTexture(nil, "BACKGROUND")
    fn_Texture:SetAllPoints(fn_frame)
    fn_Texture:SetColorTexture(0, 0, 0, 0)
    fn_Texture:Show()

    if DEBUG then
        main_Texture:SetColorTexture(math.random(), math.random(), math.random(), 1)
        fn_Texture:SetColorTexture(math.random(), math.random(), math.random(), 1)
    end
    return main_Texture, fn_Texture
end

-- 创建文字节点
function addonTable.CreateStringNode(x, y, title, parent_frame)
    local node_size = addonTable.nodeSize
    local padSize = addonTable.padSize
    local fontSize = addonTable.fontSize
    local nodeFrame = CreateFrame("Frame", addonName .. "String" .. title, parent_frame)
    nodeFrame:SetPoint("TOPLEFT", parent_frame, "TOPLEFT", x * node_size, -y * node_size)
    nodeFrame:SetFrameLevel(parent_frame:GetFrameLevel() + 1)
    nodeFrame:SetSize(node_size, node_size)
    nodeFrame:Show()
    local nodeTexture = nodeFrame:CreateTexture(nil, "BACKGROUND")
    nodeTexture:SetAllPoints(nodeFrame)
    nodeTexture:SetColorTexture(0, 0, 0, 1)
    nodeTexture:Show()


    local nodeString = nodeFrame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
    nodeString:SetAllPoints(nodeFrame)
    nodeString:SetJustifyH("CENTER")
    nodeString:SetJustifyV("MIDDLE")
    nodeString:SetFontObject(GameFontHighlight)
    nodeString:SetTextColor(1, 1, 1, 1)
    nodeString:SetFont(fontFile, fontSize, "MONOCHROME")
    nodeString:SetText("")
    nodeString:Show()
    return nodeString
end

-- 创建白色条
function addonTable.CreateWhiteBar(name, parent, x, y, width, height)
    local node_size = addonTable.nodeSize
    local padSize = addonTable.padSize

    local frame = CreateFrame("Frame", addonName .. name, parent)
    frame:SetFrameLevel(parent:GetFrameLevel() + 1)
    frame:SetPoint("TOPLEFT", parent, "TOPLEFT", x * node_size, -y * node_size - padSize)
    frame:SetSize(width * node_size, height * node_size - 2 * padSize)
    frame:Show()

    local tex = frame:CreateTexture(nil, "BACKGROUND")
    tex:SetAllPoints(frame)
    tex:SetColorTexture(0, 0, 0, 1)

    local bar = CreateFrame("StatusBar", nil, frame)
    bar:SetAllPoints(frame)
    bar:SetStatusBarTexture("Interface\\Buttons\\WHITE8X8")
    bar:SetStatusBarColor(1, 1, 1, 1)
    bar:SetMinMaxValues(0, 100)
    bar:SetValue(50)
    return bar
end

-- 创建光环序列
function addonTable.CreateAuraSequence(unit, filter, maxCount, name_prefix, parent, sortRule, sortDirection)
    if DEBUG then logging("CreateAuraSequence[" .. unit .. "][" .. filter .. "]") end
    sortRule = sortRule or Enum.UnitAuraSortRule.Default
    sortDirection = sortDirection or Enum.UnitAuraSortDirection.Normal

    local start_idx, end_idx = string.find(filter, "HELPFUL")
    local isBuff = false
    local isDebuff = false
    if start_idx then
        isBuff = true
    else
        isDebuff = true
    end

    local CreateFootnoteNode = addonTable.CreateFootnoteNode
    local CreateMixedNode = addonTable.CreateMixedNode
    local CreateStringNode = addonTable.CreateStringNode

    local auraTextures = {}

    -- 创建光环序列元素
    for i = 1, maxCount do
        local iconTexture, fnTexture = CreateFootnoteNode((i - 1), 0, addonName .. name_prefix .. "IconFrame" .. i, parent)
        local durationTexture, dispelTexture, foreverTexture, _ = CreateMixedNode((i - 1), 1, addonName .. name_prefix .. "DurationFrame" .. i, parent)

        local countString = CreateStringNode((i - 1), 2, addonName .. name_prefix .. "CountFrame" .. i, parent)
        table.insert(auraTextures, {
            icon = iconTexture,
            dispel = dispelTexture,
            duration = durationTexture,
            count = countString,
            fn = fnTexture,
            forever = foreverTexture
        })
    end

    local previousDisplayCount = 0
    local previousAuraInstanceIDs = {}

    local function wipeTexture(index)
        local tex = auraTextures[index]
        tex.icon:SetColorTexture(0, 0, 0, 1)
        tex.duration:SetColorTexture(0, 0, 0, 1)
        tex.count:SetText("")
        tex.dispel:SetColorTexture(0, 0, 0, 1)
        tex.fn:SetColorTexture(0, 0, 0, 0)
        tex.forever:SetColorTexture(0, 0, 0, 1)
        previousAuraInstanceIDs[index] = nil
    end

    -- 清除纹理函数
    local function wipeTextures()
        for i = 1, maxCount do
            wipeTexture(i)
        end
        previousDisplayCount = 0
    end

    -- 更新纹理函数
    local function UpdateStatus_event_UNIT_AURA()
        if not UnitExists(unit) then
            if previousDisplayCount > 0 then
                for i = 1, previousDisplayCount do
                    wipeTexture(i)
                end
                previousDisplayCount = 0
            end
            return
        end

        local isEnemy = UnitIsEnemy("player", unit)
        local isPlayer = not isEnemy
        local auraInstanceIDs = GetUnitAuraInstanceIDs(unit, filter, maxCount, sortRule, sortDirection) or {}
        local displayIndex = 0
        for i = 1, #auraInstanceIDs do
            local auraInstanceID = auraInstanceIDs[i]
            local aura = GetAuraDataByAuraInstanceID(unit, auraInstanceID)
            if aura ~= nil then
                displayIndex = displayIndex + 1
                local auraTexture = auraTextures[displayIndex]
                local isSlotChanged = previousAuraInstanceIDs[displayIndex] ~= auraInstanceID
                previousAuraInstanceIDs[displayIndex] = auraInstanceID

                local duration = GetAuraDuration(unit, auraInstanceID)
                local foreverBoolen = DoesAuraHaveExpirationTime(unit, auraInstanceID)
                local count = GetAuraApplicationDisplayCount(unit, auraInstanceID, 1, 9)

                if isSlotChanged then
                    auraTexture.icon:SetTexture(aura.icon, "CLAMPTOBLACK", "CLAMPTOBLACK")
                end
                auraTexture.count:SetText(count)

                if duration ~= nil then
                    local result = duration:EvaluateRemainingDuration(remaining_curve)
                    auraTexture.duration:SetColorTexture(result:GetRGBA())
                else
                    auraTexture.duration:SetColorTexture(COLOR.BLACK:GetRGBA())
                end

                if foreverBoolen ~= nil then
                    local foreverColor = EvaluateColorFromBoolean(foreverBoolen, COLOR.BLACK, COLOR.WHITE) -- 白色是永久buff
                    auraTexture.forever:SetColorTexture(foreverColor:GetRGBA())
                else
                    auraTexture.forever:SetColorTexture(COLOR.BLACK:GetRGBA())
                end

                if isPlayer and isDebuff then
                    local dispelTypeColor = GetAuraDispelTypeColor(unit, auraInstanceID, debuff_curve)
                    auraTexture.fn:SetColorTexture(dispelTypeColor:GetRGBA())
                    auraTexture.dispel:SetColorTexture(dispelTypeColor:GetRGBA())
                end
                if isPlayer and isBuff then
                    local dispelTypeColor = GetAuraDispelTypeColor(unit, auraInstanceID, playerbuff_curve)
                    auraTexture.fn:SetColorTexture(COLOR.ICONS.PLAYER_BUFF:GetRGBA())
                    auraTexture.dispel:SetColorTexture(dispelTypeColor:GetRGBA())
                end
                if isEnemy and isDebuff then
                    local dispelTypeColor = GetAuraDispelTypeColor(unit, auraInstanceID, targetdebuff_curve)
                    auraTexture.fn:SetColorTexture(COLOR.ICONS.ENEMY_DEBUFF:GetRGBA())
                    auraTexture.dispel:SetColorTexture(dispelTypeColor:GetRGBA())
                end
            end
        end

        if displayIndex < previousDisplayCount then
            for i = displayIndex + 1, previousDisplayCount do
                wipeTexture(i)
            end
        end
        previousDisplayCount = displayIndex
    end

    local function UpdateStatus_freq_std()
        if previousDisplayCount == 0 then
            return
        end
        if not UnitExists(unit) then
            for i = 1, previousDisplayCount do
                wipeTexture(i)
            end
            previousDisplayCount = 0
            return
        end

        for i = 1, previousDisplayCount do
            local auraTexture = auraTextures[i]
            local auraInstanceID = previousAuraInstanceIDs[i]
            if auraInstanceID then
                local duration = GetAuraDuration(unit, auraInstanceID)
                if duration ~= nil then
                    local result = duration:EvaluateRemainingDuration(remaining_curve)
                    auraTexture.duration:SetColorTexture(result:GetRGBA())
                else
                    auraTexture.duration:SetColorTexture(COLOR.BLACK:GetRGBA())
                end
            else
                auraTexture.duration:SetColorTexture(COLOR.BLACK:GetRGBA())
            end
        end
    end

    wipeTextures()
    UpdateStatus_event_UNIT_AURA()
    table.insert(addonTable.OnEventFunc_Aura, { unit = unit, func = UpdateStatus_event_UNIT_AURA })
    table.insert(addonTable.OnUpdateFuncs_STD, UpdateStatus_freq_std)
    if DEBUG then logging("CreateAuraSequence[" .. unit .. "]...Done") end
end
