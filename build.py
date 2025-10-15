#!/usr/bin/env python3
"""
Build script for Noita Savior executable
This script creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("Noita Savior - Building Executable")
    print("=" * 40)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])
        print("✓ PyInstaller installed")
    
    # Clean previous builds
    if os.path.exists("build"):
        print("Cleaning previous build...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("Cleaning previous dist...")
        shutil.rmtree("dist")
    
    # Clean up any existing spec files
    if os.path.exists("NoitaSavior.spec"):
        print("Cleaning previous spec file...")
        os.remove("NoitaSavior.spec")
    
    # Build the executable
    print("\nBuilding executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # No console window (GUI app)
        "--name=NoitaSavior",           # Executable name
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",  # Icon file (if exists)
        "--add-data=README.md;.",       # Include README
        "--add-data=LICENSE;.",         # Include LICENSE
        "--hidden-import=psutil",       # Explicitly include psutil
        "src/nsav.py"                   # Main script
    ]
    
    # Remove empty icon parameter
    cmd = [arg for arg in cmd if arg]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Build completed successfully!")

        # Copy icon to dist folder for convenience
        icon_path = Path("icon.ico")
        if icon_path.exists():
            dist_path = Path("dist")
            try:
                shutil.copy(icon_path, dist_path / icon_path.name)
                print(f"✓ Icon copied to dist folder: {dist_path / icon_path.name}")
            except Exception as e:
                print(f"⚠ Failed to copy icon: {e}")
        else:
            print("⚠ icon.ico not found, skipping copy.")
        
        # Check if executable was created
        exe_path = Path("dist/NoitaSavior.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ Executable created: {exe_path}")
            print(f"  Size: {size_mb:.1f} MB")
            
            # Verify dependencies are included
            print("\nVerifying dependencies...")
            try:
                import psutil
                print("✓ psutil dependency available")
            except ImportError:
                print("✗ psutil dependency missing")
            
            print("✓ All dependencies should be bundled in the executable")
            
        else:
            print("✗ Executable not found in dist/")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return 1
    
    print("\n" + "=" * 40)
    print("Build complete! Executable is in the 'dist' folder.")
    print("You can now distribute NoitaSavior.exe")
    return 0

if __name__ == "__main__":
    sys.exit(main())
