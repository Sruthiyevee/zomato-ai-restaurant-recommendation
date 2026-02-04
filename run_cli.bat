@echo off
TITLE Zomato AI Recommendation CLI
CLS
ECHO Starting Zomato AI Restaurant Recommendation Service (Phase 5 CLI)...
ECHO.

REM Check if Python is available
python --version >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Python is not installed or not in your PATH.
    PAUSE
    EXIT /B
)

REM Set the current directory to the script's location
cd /d "%~dp0"

REM Run the CLI script
python phase_5_display/src/cli.py

PAUSE
