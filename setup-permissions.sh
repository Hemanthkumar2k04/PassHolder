#!/bin/bash

# PassHolder Permission Setup Script
# Run this script if you encounter git permission conflicts during updates

echo "🔧 Setting up PassHolder file permissions..."

# Configure git to ignore file mode changes
if [ -d ".git" ]; then
    git config core.filemode false
    echo "✅ Git configured to ignore file mode changes"
fi

# Make shell scripts executable
if [ -f "install.sh" ]; then
    chmod +x install.sh
    echo "✅ Made install.sh executable"
fi

if [ -f "setup-permissions.sh" ]; then
    chmod +x setup-permissions.sh
    echo "✅ Made setup-permissions.sh executable"
fi

# Set proper permissions for Python files
find . -name "*.py" -type f -exec chmod 644 {} \; 2>/dev/null
echo "✅ Set permissions for Python files"

# Set proper permissions for configuration files
find . -name "*.toml" -o -name "*.txt" -o -name "*.md" -type f -exec chmod 644 {} \; 2>/dev/null
echo "✅ Set permissions for configuration files"

echo ""
echo "🎉 Permission setup complete!"
echo ""
echo "You can now run:"
echo "   git pull origin main    # Update without conflicts"
echo "   python3 install_venv.py # Reinstall if needed"
