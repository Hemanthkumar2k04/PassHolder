#!/bin/bash

# PassHolder Launcher Script for Unix/Linux/macOS
# This script activates the virtual environment and runs PassHolder

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Please run the installer first:"
    echo "   python3 install_venv.py"
    exit 1
fi

# Check if Python executable exists in venv
VENV_PYTHON="$VENV_DIR/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Python executable not found in virtual environment"
    echo "Please reinstall by running:"
    echo "   python3 install_venv.py"
    exit 1
fi

# Check if main script exists
MAIN_SCRIPT="$SCRIPT_DIR/passholder.py"
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "❌ PassHolder script not found at $MAIN_SCRIPT"
    exit 1
fi

# Activate virtual environment and run PassHolder
exec "$VENV_PYTHON" "$MAIN_SCRIPT" "$@"
