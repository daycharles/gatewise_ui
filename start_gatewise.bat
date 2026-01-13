@echo off
REM GateWise Access Control - Startup Script
REM This script starts the GateWise UI application

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Set environment variables
set "GATEWISE_ADMIN_PASSWORD=admin"
set "RFID_SERVER_PORT=8080"

REM Change to the application directory
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at .venv\Scripts\python.exe
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Run the application
echo Starting GateWise Access Control...
".venv\Scripts\python.exe" main.py

REM If Python exits with an error, show the error
if errorlevel 1 (
    echo.
    echo Error: Application exited with error code %errorlevel%
    pause
)

endlocal
