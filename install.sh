#!/bin/bash

# PassHolder Installation Script for Unix/Linux/macOS
# This script calls the Python installer

echo "🚀 PassHolder Unix/Linux Installation"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again:"
    echo ""
    echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "macOS:         brew install python3"
    echo "Arch Linux:    sudo pacman -S python python-pip"
    exit 1
fi

# Check for externally managed environment and provide guidance
echo "🔍 Checking Python environment..."
if python3 -m pip --version &> /dev/null; then
    echo "✅ pip is available"
else
    echo "⚠️  pip may not be available or environment is externally managed"
    echo "   The installer will try user-local installation if needed"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📁 Installation directory: $SCRIPT_DIR"
echo ""

# Check if install.py exists
if [ ! -f "$SCRIPT_DIR/install.py" ]; then
    echo "❌ Error: install.py not found in $SCRIPT_DIR"
    echo "Please run this script from the PassHolder directory"
    exit 1
fi

# Run the Python installer
echo "🐍 Running Python installer..."
python3 "$SCRIPT_DIR/install.py"

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🔄 To start using PassHolder immediately:"
    echo "   source ~/.bashrc    # if using bash"
    echo "   source ~/.zshrc     # if using zsh"
    echo "   # or restart your terminal"
    echo ""
    echo "Then you can use: passholder --help"
else
    echo ""
    echo "❌ Installation failed."
    echo ""
    echo "🔧 Troubleshooting options:"
    echo ""
    echo "1. Try virtual environment installation:"
    echo "   python3 install_venv.py"
    echo ""
    echo "2. Try user installation:"
    echo "   python3 -m pip install --user -r requirements.txt"
    echo ""
    echo "3. Install system packages (Ubuntu/Debian):"
    echo "   sudo apt install python3-rich python3-cryptography python3-argon2-cffi"
    echo ""
    echo "4. Use pipx (if available):"
    echo "   pipx install -e ."
    echo ""
    exit 1
fi
