@echo off
chcp 65001 >nul
echo 正在启动 EZAssistedX2...
cd /d "%~dp0bin\Release\net8.0-windows\win-x64\"
if exist EZAssistedX2.NET.exe (
    powershell Start-Process -FilePath ".\EZAssistedX2.NET.exe" -Verb RunAs
) else (
    echo 找不到 EZAssistedX2.NET.exe
    pause
)
