# Noita Savior

A save manager for the game Noita that allows you to create, load, and manage multiple save states with automatic backup functionality. (MAKE SURE YOU DISABLE YOUR STEAM CLOUD SAVES FOR NOITA IN ORDER FOR THIS TO WORK IF USING STEAM VERSION)

## Quick Start

### Option 1: Run from Source
1. Run the program:
   ```bash
   python src/nsav.py
   # or
   python run.py
   ```

2. Use the interface to save, load, or delete save slots

### Option 2: Use Executable
1. Download the latest release from GitHub
2. Run `NoitaSavior.exe` directly
3. No Python installation required!

## Features

- **8 Save Slots**: Create and manage up to 8 different save states
- **Automatic Backup**: Automatically backs up your current save before loading a slot
- **Easy Management**: Simple interface with Save, Load, and Delete buttons for each slot
- **Visual Feedback**: Clear status indicators and folder detection
- **Safe Operations**: Confirmation dialogs prevent accidental data loss

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- Noita game installed

## Building Executable

To create a standalone executable for distribution:

### Method 1: Using Build Script (Recommended)
```bash
# Install PyInstaller
pip install pyinstaller>=5.0.0

# Run the build script
python build.py
```

### Method 2: Using Batch File (Windows)
```bash
# Double-click build.bat or run from command line
build.bat
```

### Method 3: Manual PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller>=5.0.0

# Build executable
pyinstaller --onefile --windowed --name=NoitaSavior src/nsav.py
```

The executable will be created in the `dist/` folder as `NoitaSavior.exe`.

## File Structure

```
NoitaSavior/
├── src/
│   └── nsav.py              # Main application
├── dist/                     # Executable output (after building)
│   └── NoitaSavior.exe      # Standalone executable
├── backups/                  # Directory for save slots and auto-backups (created automatically)
├── build/                    # Build temporary files (created during build)
├── README.md                 # This file
├── LICENSE                   # GNU GPL v3 License
├── requirements.txt          # Dependencies
├── build.py                  # Build script
├── build.bat                 # Windows build script
├── NoitaSavior.spec          # PyInstaller spec file
└── .gitignore               # Git ignore file
```

## Safety Features

- **Automatic Backup**: Before loading any slot, your current save is automatically backed up
- **Confirmation Dialogs**: Delete operations require confirmation
- **Error Handling**: Graceful handling of file operations and missing folders
- **Status Updates**: Real-time feedback on all operations

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

See LICENSE file for full details.