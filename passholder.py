#!/usr/bin/env python3
"""
PassHolder Wrapper Script - Smart Mode Detection
================================================

This is the main entry point for the PassHolder password manager application.
It provides intelligent mode detection to automatically choose between the
graphical user interface (GUI) and command-line interface (CLI) based on
the arguments provided by the user.

Mode Detection Logic:
- No arguments: Launch interactive GUI mode with Rich terminal interface
- With arguments: Enter CLI mode for scripting and automation

This design provides the best of both worlds:
1. Interactive GUI for casual use and exploration
2. CLI for automation, scripting, and power users

Usage Examples:
    passholder                    # Opens interactive GUI
    passholder add gmail          # CLI mode - add password
    passholder view               # CLI mode - view passwords
    passholder copy github        # CLI mode - copy to clipboard

Benefits of Dual Interface:
- Seamless transition between interfaces
- Consistent data access and security
- Scriptable operations for automation
- User-friendly GUI for complex operations
- Single executable for all use cases

Technical Implementation:
- Automatic path configuration for module imports
- Lazy loading of interface modules
- Consistent error handling across modes
- Memory-efficient operation

Author: PassHolder Team
License: Open Source
"""

import sys
import os

# Add the current directory to the Python path for module imports
# This ensures the script works regardless of installation method
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import after path setup to ensure modules are found
    from main import run_gui, main_cli

    # Intelligent mode detection based on command-line arguments
    if len(sys.argv) == 1:
        # No arguments provided → Launch interactive GUI mode
        # Provides rich terminal interface with menus and navigation
        run_gui()
    else:
        # Arguments provided → Enter CLI mode
        # Enables scripting, automation, and quick operations
        main_cli()
