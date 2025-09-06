# PassHolder - Secure Password Manager

A cross-platform password manager with both GUI and CLI interfaces, featuring military-grade encryption and seamless installation across all platforms.

## ✨ Features

- 🔐 **Military-Grade Encryption**: Fernet (AES 256) with PBKDF2 key derivation (100,000 iterations)
- 🖥️ **Dual Interface**: Rich terminal GUI and command-line interface
- 🌍 **Cross-Platform**: Windows, Linux, macOS with native installation
- 🎨 **Beautiful UI**: Rich terminal interface with themes, tables, and pagination
- 📋 **Clipboard Integration**: One-click password copying with auto-clear
- 🔍 **Smart Search**: Fast service name and username searching
- 🛡️ **Master Password**: Single password protects all your data with Argon2 hashing
- 📦 **Easy Installation**: Multiple installation methods with automatic fallbacks
- 🔄 **Auto-Updates**: Intelligent dependency management and environment detection

## 🚀 Quick Installation

### Option 1: Recommended Installation (All Platforms)

```bash
# Windows
python install.py

# Linux/macOS
chmod +x install.sh
./install.sh
```

### Option 2: Virtual Environment (Isolated Installation)

Perfect for systems with package restrictions or multiple Python environments:

```bash
python3 install_venv.py
```

This creates an isolated environment and automatically sets up shell aliases.

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating Systems**: Windows 10+, Linux (any modern distro), macOS 10.14+
- **Memory**: 50MB RAM minimum
- **Storage**: 10MB disk space

## 🎯 Usage

PassHolder automatically detects whether you want the GUI or CLI interface:

### GUI Mode (Interactive)
```bash
passholder          # Opens rich terminal interface
```

### CLI Mode (Direct Commands)
```bash
passholder add                    # Add new password
passholder view                   # View all passwords (paginated)
passholder remove                 # Remove password interactively
passholder copy <service>         # Copy password to clipboard
passholder search <query>         # Search passwords
passholder get <service>          # Get specific password
passholder --help                 # Show help
```

### Advanced Commands
```bash
# Search with partial matches
passholder search gmail
passholder search @company.com

# Quick access patterns
passholder get github
passholder copy work-email
```

## 🔧 Installation Troubleshooting

### Problem: "externally-managed-environment" Error

**Modern Linux distributions** (Ubuntu 22.04+, Fedora 38+) may restrict global package installation.

**Solutions** (in order of recommendation):

#### 1. Use Virtual Environment Installer (Recommended)
```bash
python3 install_venv.py
# Creates isolated environment, sets up aliases automatically
```

#### 2. User-Level Installation
```bash
python3 -m pip install --user -r requirements.txt
python install.py
```

#### 3. System Package Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-rich python3-cryptography python3-argon2-cffi python3-pyperclip

# Fedora/RHEL
sudo dnf install python3-rich python3-cryptography python3-argon2-cffi python3-pyperclip

# Arch Linux
sudo pacman -S python-rich python-cryptography python-argon2-cffi python-pyperclip
```

#### 4. Using pipx (Isolated Application Install)
```bash
pipx install -e .
```

### Problem: Command Not Found

If `passholder` command isn't found after installation:

```bash
# Reload shell configuration
source ~/.bashrc    # or ~/.zshrc

# Or restart your terminal

# Manual path check
echo $PATH | grep PassHolder

# Use full path temporarily
/path/to/PassHolder/bin/passholder
```

## � Updating PassHolder

PassHolder includes automatic git configuration to prevent permission conflicts during updates.

### Smooth Update Process

```bash
# Update to latest version
git pull origin main

# If you encounter permission conflicts, run:
chmod +x install.sh setup-permissions.sh

# Reinstall if needed (preserves your data)
python3 install_venv.py
```

### Handling Permission Conflicts

If you see git conflicts related to file permissions:

```bash
# Reset file permissions (Unix/Linux/macOS)
git config core.filemode false
chmod +x install.sh setup-permissions.sh

# Then update
git pull origin main
```

### Data Backup Before Updates

Your encrypted database is safe during updates, but for extra security:

```bash
# Backup your data (optional)
cp ~/passholder/secrets.db.enc ~/passholder_backup_$(date +%Y%m%d).db.enc
```

The installer automatically:
- ✅ Configures git to ignore permission changes
- ✅ Sets proper executable permissions for scripts
- ✅ Preserves your existing password database
- ✅ Updates dependencies and wrappers

## �🔒 Security Architecture

### Encryption Details
- **Algorithm**: Fernet (AES 256 in CBC mode with HMAC authentication)
- **Key Derivation**: PBKDF2-SHA256 with 100,000 iterations
- **Salt**: Randomly generated 16-byte salt per database
- **Authentication**: Argon2id for master password verification

### Data Protection
- **Local Only**: No network connections, data never leaves your device
- **Encrypted at Rest**: Database file is completely encrypted
- **Memory Safety**: Sensitive data cleared from memory after use
- **Clipboard Security**: Auto-clear clipboard after 30 seconds

### Database Structure
```
encrypted_database.db (AES encrypted)
├── Schema: CREATE TABLE secrets (id, service, username, password, notes)
├── Encryption: Per-record encryption with global key
└── Integrity: HMAC verification on all operations
```

## 📁 Project Architecture

```
PassHolder/
├── Core Application
│   ├── main.py              # Entry point, GUI/CLI router
│   ├── cli.py               # Command-line interface logic
│   ├── ui.py                # Rich terminal UI components
│   └── passholder.py        # Wrapper script for mode detection
├── Security Layer
│   ├── encryptedSQLiteDB.py # Encrypted database operations
│   └── config.py            # Secure configuration management
├── Installation System
│   ├── install.py           # Cross-platform installer
│   ├── install_venv.py      # Virtual environment installer
│   ├── install.sh           # Unix launcher script
│   └── requirements.txt     # Python dependencies
├── Configuration
│   ├── pyproject.toml       # Project metadata
│   ├── .gitignore           # Version control exclusions
│   └── README.md            # This documentation
└── Generated Files
    ├── bin/                 # Executable wrapper scripts
    ├── .venv/               # Virtual environment (if used)
    └── __pycache__/         # Python bytecode cache
```

## 🔄 Development Setup

### For Contributors

```bash
# Clone repository
git clone <repo-url>
cd PassHolder

# Install in development mode
python3 install_venv.py

# Run tests
python -m pytest tests/

# Code formatting
black *.py
isort *.py
```

### Dependencies Overview
- **rich>=14.1.0**: Terminal UI framework with tables, progress bars, themes
- **cryptography>=41.0.0**: Industry-standard encryption library
- **argon2-cffi>=25.1.0**: Memory-hard password hashing function
- **pyperclip>=1.8.0**: Cross-platform clipboard operations

## 🗑️ Uninstallation

### Complete Removal
```bash
# Remove installation directory
rm -rf /path/to/PassHolder

# Remove shell aliases (Linux/macOS)
# Edit ~/.bashrc and ~/.zshrc, remove PassHolder alias lines

# Windows: Remove from Environment Variables
# System Properties → Environment Variables → Remove PassHolder path
```

### Keep Data, Remove Application
```bash
# Backup your encrypted database first
cp PassHolder/encrypted_database.db ~/passholder_backup.db

# Then follow complete removal steps above
```

## ❓ FAQ

**Q: Can I sync passwords across devices?**  
A: Currently local-only. You can manually copy the encrypted database file to sync.

**Q: What happens if I forget my master password?**  
A: Unfortunately, passwords cannot be recovered. The encryption is designed to be unbreakable.

**Q: Is it safe to store the database in cloud storage?**  
A: Yes, the database file is fully encrypted. However, ensure cloud storage is also secured.

**Q: Can I import from other password managers?**  
A: Not currently supported, but you can manually add entries using the CLI/GUI.

## 🆘 Support & Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated or packages installed globally
2. **Permission errors**: Run installer with appropriate permissions for your system
3. **Command not found**: Check PATH and shell configuration files
4. **Database corruption**: Keep backups; the encryption protects against most corruption

### Getting Help

1. Check this README for common solutions
2. Verify Python version: `python3 --version`
3. Check installation: `which passholder` or `where passholder`
4. Reinstall if needed: `python3 install_venv.py`

---

**⚠️ Security Notice**: Your master password is the key to all your data. Store it safely and never share it. PassHolder cannot recover lost master passwords due to the encryption design.
- Python 3.8 or higher
- pip (or pipx for isolated installation)

## Usage

After installation, restart your terminal and use these commands:

### Automatic Mode Selection

```bash
# Enter interactive UI mode (no arguments)
passholder

# Use CLI mode (with arguments)
passholder add          # Add a new password
passholder view         # View all passwords
passholder remove       # Remove a password
passholder copy         # Copy password to clipboard
passholder search <service_name>  # Search for passwords
passholder get <service_name>     # Get specific password
passholder --help       # Show help
```

The program automatically detects:
- **UI Mode**: When you type just `passholder` (no arguments)
- **CLI Mode**: When you provide any arguments like `passholder view`

## First Time Setup

1. Run `passholder add` to create your first password entry
2. You'll be prompted to create a master password
3. Your master password encrypts all stored data

## Security Features

- **Encryption**: All passwords encrypted with Fernet (AES 128)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Password Hashing**: Argon2 for master password verification
- **Local Storage**: Data stored locally in encrypted database
- **No Network**: No internet connection required or used

## Installation Details

The installer:
1. ✅ Installs packages globally (no virtual environment needed)
2. ✅ Creates a `passholder` command wrapper
3. ✅ Adds the command to your system PATH
4. ✅ Configures shell profile files (bash/zsh)

### Package Requirements
- Python 3.8 or higher
- Global pip installation

## Uninstallation

To remove PassHolder:
1. Remove the installation directory
2. Remove the PATH entry from your shell profile
3. On Windows: Remove from Environment Variables

## Development

### Project Structure
```
PassHolder/
├── main.py              # Main application entry point
├── cli.py               # Command-line interface
├── ui.py                # Rich terminal UI components
├── encryptedSQLiteDB.py # Encrypted database handler
├── config.py            # Configuration management
├── passholder.py        # CLI wrapper script
├── install.py           # Cross-platform installer
├── install.sh           # Unix installation script
├── requirements.txt     # Python dependencies
└── pyproject.toml       # Project configuration
```

### Dependencies
- `rich>=14.1.0` - Terminal UI framework
- `cryptography>=41.0.0` - Encryption library
- `argon2-cffi>=25.1.0` - Password hashing
- `pyperclip>=1.8.0` - Clipboard integration

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues or questions:
1. Check that Python 3.8+ is installed
2. Verify all dependencies are installed
3. Ensure the virtual environment is activated
4. Try reinstalling with the installation script

---

**⚠️ Important**: Keep your master password safe! Without it, your stored passwords cannot be recovered.
