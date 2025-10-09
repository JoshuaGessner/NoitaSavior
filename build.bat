@echo off
echo Noita Savior - Build Executable
echo ================================

echo Installing PyInstaller...
pip install pyinstaller>=5.0.0
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Building executable...
python build.py
if errorlevel 1 (
    echo.
    echo ERROR: Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Build complete! Check the 'dist' folder for NoitaSavior.exe
pause
