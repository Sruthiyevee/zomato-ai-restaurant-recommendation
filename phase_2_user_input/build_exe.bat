@echo off
REM Batch script to build executable for Windows
echo ============================================================
echo Building Zomato CLI Executable
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not found. Please install Python first.
    pause
    exit /b 1
)

echo.
echo Installing PyInstaller...
python -m pip install pyinstaller

echo.
echo Building executable...
pyinstaller --onefile --console --name ZomatoCLI --add-data "src;src" --hidden-import validator --hidden-import cli_handler --hidden-import session_manager test_cli.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build successful!
echo ============================================================
echo.
echo Executable created at: dist\ZomatoCLI.exe
echo.
echo You can now run ZomatoCLI.exe directly!
echo.
pause
