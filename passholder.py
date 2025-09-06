#!/usr/bin/env python3
"""
PassHolder wrapper script
Automatically chooses between UI and CLI mode based on arguments
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import after path setup
    from main import run_gui, main_cli

    # Check if any arguments were provided (excluding script name)
    if len(sys.argv) == 1:
        # No arguments provided → Enter UI mode
        run_gui()
    else:
        # Arguments provided → Enter CLI mode
        main_cli()
