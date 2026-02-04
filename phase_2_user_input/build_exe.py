"""
Script to build executable from CLI test script
Run this to create a standalone .exe file
"""

import subprocess
import sys
import os
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller"""
    print("=" * 60)
    print("Building Executable for Phase 2 CLI")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Get the script path
    script_path = Path(__file__).parent / "test_cli.py"
    
    if not script_path.exists():
        print(f"❌ Error: {script_path} not found")
        return False
    
    print(f"\nBuilding executable from: {script_path}")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--console",  # Console application
        "--name", "ZomatoCLI",  # Name of the executable
        "--add-data", f"src;src",  # Include src directory
        "--hidden-import", "validator",
        "--hidden-import", "cli_handler",
        "--hidden-import", "session_manager",
        str(script_path)
    ]
    
    try:
        print("\nRunning PyInstaller...")
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print(f"\nExecutable created at: dist/ZomatoCLI.exe")
        print("\nYou can now run ZomatoCLI.exe directly!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    build_exe()
