local addonName, addonTable = ...
for _, macro in pairs(addonTable.macroList) do --输出2 test2, 6 test3, 4 test1
    local buttonName = addonName .. "Button" .. macro.title
    local frame = CreateFrame("Button", buttonName, UIParent, "SecureActionButtonTemplate")
    frame:SetAttribute("type", "macro")
    frame:SetAttribute("macrotext", macro.text)
    frame:RegisterForClicks("AnyDown", "AnyUp")
    SetOverrideBindingClick(frame, true, macro.key, buttonName)
    addonTable.logging("RegMacro[" .. macro.title .. "] > " .. macro.key .. " > " .. macro.text)
end
