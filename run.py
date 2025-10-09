#!/usr/bin/env python3
"""
Noita Savior - Save Manager for Noita Game
Run this script to start the Noita save manager.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from nsav import NoitaSaveManager

if __name__ == "__main__":
    app = NoitaSaveManager()
    app.run()
