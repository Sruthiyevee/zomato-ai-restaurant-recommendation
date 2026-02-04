@echo off
REM Simple batch script to build executable
echo Building Zomato CLI Executable...

REM Install PyInstaller if needed
python -m pip install pyinstaller --quiet

REM Build the executable from standalone version
pyinstaller --onefile --console --name ZomatoCLI ^
    --add-data "src;src" ^
    --hidden-import validator ^
    --hidden-import cli_handler ^
    --hidden-import session_manager ^
    zomato_cli_standalone.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Executable created at: dist\ZomatoCLI.exe
    echo You can now run ZomatoCLI.exe
) else (
    echo.
    echo Build failed. Please check the error messages above.
)

pause
