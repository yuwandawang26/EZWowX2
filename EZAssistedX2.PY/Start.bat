@echo off
cd /d "%~dp0"
title EZWowX2 - Game Assistant

:: ============================================
::   EZWowX2 Launcher v2.0
::   Auto-request admin + Custom icon
:: ============================================

:: Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs -WindowStyle Hidden"
    exit /b 0
)

echo [OK] Admin privileges: Granted
echo [OK] Working directory: %cd%

:: Set console icon (if supported)
if exist "%~dp0EZAssistedX2.ico" (
    echo [OK] Custom icon found
) else (
    echo [INFO] No custom icon file (EZAssistedX2.ico)
)

echo.
echo [STARTING] Launching EZWowX2...
echo.

:: Use pythonw to hide console window with icon hint
start "" /B pythonw EZAssistedX2.py

set EXIT_CODE=%errorlevel%

if %EXIT_CODE% equ 0 (
    echo [DONE] Program launched successfully
) else (
    echo [WARNING] Exit code: %EXIT_CODE%
)

echo.
exit /b 0
