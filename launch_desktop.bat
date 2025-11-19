@echo off
REM Autonomous Zenith Optimizer - Production Desktop Launcher
REM Windows Batch Starter for easy access

title Autonomous Zenith Optimizer v3.0

echo.
echo ============================================================
echo   ^<#^> AUTONOMOUS ZENITH OPTIMIZER - PRODUCTION v3.0
echo   ^<#^> Starting Desktop Application...
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Run the launcher
echo [INFO] Initializing system...
echo.

python launch_desktop.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo [INFO] Application exited successfully
pause
