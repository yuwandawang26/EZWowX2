@echo off
cd /d "%~dp0"

echo ============================================
echo     EZAssistedX2 Helper Tool v2.0
echo ============================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found, please install Python 3.12+
    pause
    exit /b 1
)

:: Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs -Wait"
    exit /b 0
)

echo [OK] Admin privileges: Granted
echo [OK] Working directory: %cd%
echo.

:: Create logs directory if not exists
if not exist "logs" mkdir logs

:: Start program
echo [STARTING] Loading EZAssistedX2...
echo [TIP] Check logs folder if you encounter any issues
echo.

python EZAssistedX2.py

set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo [DONE] Program exited normally
) else (
    echo [WARNING] Exit code: %EXIT_CODE%
)

echo.
pause
