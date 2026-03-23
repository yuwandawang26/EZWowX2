local addonName, addonTable = ...

addonTable.macroList = {}
table.insert(addonTable.macroList, { title = "reloadUI", key = "CTRL-F12", text = "/reload" })

-- 设置游戏变量，确保插件正常运行
SetCVar("secretChallengeModeRestrictionsForced", 1)
SetCVar("secretCombatRestrictionsForced", 1)
SetCVar("secretEncounterRestrictionsForced", 1)
SetCVar("secretMapRestrictionsForced", 1)
SetCVar("secretPvPMatchRestrictionsForced", 1)
SetCVar("secretAuraDataRestrictionsForced", 1)
SetCVar("scriptErrors", 1);
SetCVar("doNotFlashLowHealthWarning", 1);
