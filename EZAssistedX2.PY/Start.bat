@echo off
cd /d "%~dp0"

:: Use pythonw to hide console window
start /B "" pythonw EZAssistedX2.py

:: Exit immediately (no pause)
exit /b 0
